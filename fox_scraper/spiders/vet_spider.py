# fox_scraper/spiders/vet_spider.py
import scrapy
from datetime import datetime
import logging
from ..core.database import DatabaseManager, DataSource, ScrapingRun

class VetSpider(scrapy.Spider):
    name = 'vet_spider'
    allowed_domains = ['dasoertliche.de']
    start_urls = ['https://www.dasoertliche.de/Themen/Tierarzt.html']
    
    custom_settings = {
        'CONCURRENT_REQUESTS': 1,
        'DOWNLOAD_DELAY': 2,
        'COOKIES_ENABLED': False,
        'DOWNLOAD_TIMEOUT': 60,
        'RETRY_TIMES': 5,
        'RETRY_HTTP_CODES': [500, 502, 503, 504, 400, 403, 408, 429],
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }

    def __init__(self, *args, **kwargs):
        super(VetSpider, self).__init__(*args, **kwargs)
        self.items_processed = 0
        self.current_page = 1
        self.db = DatabaseManager()
        self.source_id = None
        self.run_id = None

    def start_requests(self):
        """Initialize scraping run and start requests"""
        session = self.db.get_session()
        try:
            # Get or create data source
            source = session.query(DataSource).filter_by(name=self.name).first()
            if not source:
                source = DataSource(
                    name=self.name,
                    url=self.start_urls[0],
                    description='German veterinary directory scraper',
                    config=self.custom_settings,
                    is_active=True
                )
                session.add(source)
                session.commit()
            
            self.source_id = source.id

            # Create new scraping run
            run = ScrapingRun(
                source_id=self.source_id,
                status='running',
                config_snapshot=self.custom_settings
            )
            session.add(run)
            session.commit()
            self.run_id = run.id

            # Start scraping
            for url in self.start_urls:
                yield scrapy.Request(
                    url=url,
                    callback=self.parse,
                    errback=self.errback_httpbin,
                    dont_filter=True,
                    meta={'page': 1}
                )

        except Exception as e:
            self.logger.error(f"Error initializing spider: {str(e)}")
            raise e
        finally:
            session.close()

    def parse(self, response):
        """Parse each page of results"""
        try:
            entries = response.css('div.hit')
            self.logger.info(f"Processing page {self.current_page} - found {len(entries)} entries")
            
            for entry in entries:
                self.items_processed += 1
                
                # Extract address
                address_texts = entry.xpath('.//address//text()').getall()
                address_texts = [text.strip() for text in address_texts if text.strip()]
                
                street = address_texts[0] if address_texts else ''
                city = address_texts[-1] if len(address_texts) > 1 else ''

                item = {
                    'source_id': self.source_id,
                    'run_id': self.run_id,
                    'url': entry.css('h2 a.hitlnk_name::attr(href)').get(),
                    'raw_content': {
                        'name': self.clean_text(entry.css('h2 a.hitlnk_name::text').get()),
                        'subtitle': self.clean_text(entry.css('div.subline::text').get()),
                        'category': self.clean_text(entry.css('div.category::text').get()),
                        'address': {
                            'street': street,
                            'city': city
                        },
                        'phone': self.clean_text(entry.css('div.phoneblock span::text').get()),
                        'opening_hours': self.clean_text(entry.css('div.hitlnk_times::text').get()),
                        'page_number': self.current_page,
                        'html': entry.get()
                    }
                }
                
                yield item

            # Update run statistics
            self.update_run_stats()

            # Handle pagination
            if entries:
                next_page = self.current_page + 1
                next_url = f'https://www.dasoertliche.de/Themen/Tierarzt-Seite-{next_page}.html'
                
                self.logger.info(f"Following next page: {next_url}")
                self.current_page = next_page
                
                yield scrapy.Request(
                    url=next_url,
                    callback=self.parse,
                    errback=self.errback_httpbin,
                    dont_filter=True,
                    meta={'page': next_page}
                )

        except Exception as e:
            self.logger.error(f"Error parsing page: {str(e)}")
            self.record_error(str(e))

    def update_run_stats(self):
        """Update scraping run statistics"""
        session = self.db.get_session()
        try:
            run = session.query(ScrapingRun).get(self.run_id)
            if run:
                run.items_processed = self.items_processed
                session.commit()
        except Exception as e:
            self.logger.error(f"Error updating run stats: {str(e)}")
        finally:
            session.close()

    def record_error(self, error_message):
        """Record error in scraping run"""
        session = self.db.get_session()
        try:
            run = session.query(ScrapingRun).get(self.run_id)
            if run:
                if not run.errors:
                    run.errors = []
                run.errors.append({
                    'timestamp': datetime.utcnow().isoformat(),
                    'error': error_message
                })
                session.commit()
        except Exception as e:
            self.logger.error(f"Error recording error: {str(e)}")
        finally:
            session.close()

    def errback_httpbin(self, failure):
        """Handle failed requests"""
        self.logger.error(f"Request failed: {failure.value}")
        self.record_error(str(failure.value))

    def clean_text(self, text):
        """Clean and normalize text data"""
        if text is None:
            return ''
        return ' '.join(text.strip().split())

    def closed(self, reason):
        """Update run status when spider closes"""
        session = self.db.get_session()
        try:
            run = session.query(ScrapingRun).get(self.run_id)
            if run:
                run.status = 'completed'
                run.end_time = datetime.utcnow()
                run.items_processed = self.items_processed
                session.commit()
        except Exception as e:
            self.logger.error(f"Error closing run: {str(e)}")
        finally:
            session.close()