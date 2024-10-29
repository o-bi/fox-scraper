# fox_scraper/pipelines/db_pipeline.py
from sqlalchemy.exc import SQLAlchemyError
import logging
import json
import hashlib
from ..core.database import (
    DatabaseManager, 
    RawData, 
    CleanedData,
    DataSource,
    ScrapingRun
)

class DatabasePipeline:
    def __init__(self):
        self.items_count = 0
        self.logger = logging.getLogger(__name__)
        self.db = DatabaseManager()

    def open_spider(self, spider):
        """Initialize database when spider starts"""
        try:
            self.db.create_tables()
            session = self.db.get_session()
            
            # Verify data source exists
            source = session.query(DataSource).filter_by(name=spider.name).first()
            if not source:
                source = DataSource(
                    name=spider.name,
                    url=spider.start_urls[0],
                    description='German veterinary directory scraper',
                    config=spider.custom_settings
                )
                session.add(source)
                session.commit()
            
            # Get current record counts
            raw_count = session.query(RawData).count()
            cleaned_count = session.query(CleanedData).count()
            
            self.logger.info(f"Connected to database. Raw records: {raw_count}, Cleaned records: {cleaned_count}")
            session.close()
            
        except Exception as e:
            self.logger.error(f"Error connecting to database: {str(e)}")
            raise e

    def close_spider(self, spider):
        """Update final stats when spider closes"""
        try:
            session = self.db.get_session()
            
            # Update run status
            run = session.query(ScrapingRun).filter_by(id=spider.run.id).first()
            if run:
                run.status = 'completed'
                run.items_processed = self.items_count
                session.commit()
            
            # Get final counts
            raw_count = session.query(RawData).count()
            cleaned_count = session.query(CleanedData).count()
            
            self.logger.info(f"Spider finished. Raw records: {raw_count}, Cleaned records: {cleaned_count}")
            session.close()
            
        except Exception as e:
            self.logger.error(f"Error closing spider: {str(e)}")

    def process_item(self, item, spider):
        """Process and save scraped items"""
        session = self.db.get_session()
        try:
            # Create content hash for deduplication
            content_hash = hashlib.md5(
                json.dumps(item['raw_content'], sort_keys=True).encode()
            ).hexdigest()

            # Check for existing record
            existing_record = session.query(RawData).filter_by(
                hash=content_hash
            ).first()

            if existing_record:
                self.logger.info(f"Duplicate content found for URL: {item['url']}")
                return item

            # Save raw data
            raw_data = RawData(
                source_id=item['source_id'],
                run_id=item['run_id'],
                url=item['url'],
                raw_content=item['raw_content'],
                hash=content_hash,
                processing_status='pending'
            )
            session.add(raw_data)
            session.flush()  # Get ID without committing

            # Process cleaned data
            try:
                # Extract structured data from raw content
                raw_content = item['raw_content']
                cleaned_data = CleanedData(
                    raw_data_id=raw_data.id,
                    source_id=item['source_id'],
                    name=raw_content.get('name', ''),
                    category=raw_content.get('category', ''),
                    address={
                        'street': raw_content.get('address', {}).get('street', ''),
                        'city': raw_content.get('address', {}).get('city', ''),
                    },
                    contact={
                        'phone': raw_content.get('phone', ''),
                        'hours': raw_content.get('opening_hours', '')
                    },
                    data_json={
                        'page_number': raw_content.get('page_number'),
                        'subtitle': raw_content.get('subtitle', ''),
                        'raw_html': raw_content.get('html', '')
                    },
                    validation_status='valid'
                )
                session.add(cleaned_data)
                
                # Update raw data status
                raw_data.processing_status = 'processed'
                
            except Exception as e:
                self.logger.error(f"Error cleaning data: {str(e)}")
                raw_data.processing_status = 'failed'
                session.add(RawData(
                    source_id=item['source_id'],
                    run_id=item['run_id'],
                    url=item['url'],
                    raw_content={'error': str(e)},
                    processing_status='failed'
                ))

            session.commit()
            self.items_count += 1

            if self.items_count % 100 == 0:
                self.logger.info(f"Processed {self.items_count} items")

            return item

        except SQLAlchemyError as e:
            self.logger.error(f"Database error: {str(e)}")
            session.rollback()
            return item
            
        except Exception as e:
            self.logger.error(f"Error processing item: {str(e)}")
            self.logger.error(f"Failed item: {json.dumps(item, indent=2, ensure_ascii=False)}")
            session.rollback()
            return item
            
        finally:
            session.close()

    def handle_error(self, failure):
        """Handle pipeline errors"""
        self.logger.error(f"Pipeline error: {failure.getErrorMessage()}")
        
        # Try to record error in database
        session = self.db.get_session()
        try:
            error_data = RawData(
                source_id=getattr(failure.request, 'source_id', None),
                run_id=getattr(failure.request, 'run_id', None),
                url=failure.request.url,
                raw_content={'error': failure.getErrorMessage()},
                processing_status='failed'
            )
            session.add(error_data)
            session.commit()
        except Exception as e:
            self.logger.error(f"Error recording failure: {str(e)}")
        finally:
            session.close()