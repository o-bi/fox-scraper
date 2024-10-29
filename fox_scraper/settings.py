# fox_scraper/settings.py
BOT_NAME = 'fox_scraper'

SPIDER_MODULES = ['fox_scraper.spiders']
NEWSPIDER_MODULE = 'fox_scraper.spiders'

# Pipeline configuration
ITEM_PIPELINES = {
    'fox_scraper.pipelines.db_pipeline.DatabasePipeline': 300,
}

# Request settings
CONCURRENT_REQUESTS = 1
DOWNLOAD_DELAY = 2
COOKIES_ENABLED = False
DOWNLOAD_TIMEOUT = 60

# Retry configuration
RETRY_ENABLED = True
RETRY_TIMES = 5
RETRY_HTTP_CODES = [500, 502, 503, 504, 400, 403, 408, 429]

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# User agent
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36'

# Request Fingerprinter
REQUEST_FINGERPRINTER_IMPLEMENTATION = '2.7'