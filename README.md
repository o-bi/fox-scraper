# Fox Scraper - Enterprise Web Scraping Framework

## Overview
Fox Scraper is an enterprise-grade web scraping framework built with Scrapy and SQLAlchemy, designed to handle multiple data sources, data cleaning, enrichment, and consolidation. The system is built with scalability, maintainability, and data quality in mind.

## Features
- Multi-source data collection
- Data validation and cleaning
- Data enrichment pipeline
- Master record consolidation
- Progress tracking and monitoring
- Error handling and recovery
- Comprehensive logging
- Data quality assurance

## Project Structure
```
fox_scraper/
├── README.md                  # Project documentation
├── setup.py                  # Package setup file
├── requirements.txt          # Project dependencies
├── scrapy.cfg               # Scrapy configuration
├── .env                     # Environment variables
├── .gitignore              # Git ignore file
│
├── fox_scraper/             # Main package directory
│   ├── __init__.py
│   ├── settings.py          # Scrapy settings
│   │
│   ├── core/               # Core functionality
│   │   ├── __init__.py
│   │   ├── database.py     # Database models and connection
│   │   └── config.py       # Configuration management
│   │
│   ├── spiders/           # Scrapy spiders
│   │   ├── __init__.py
│   │   └── vet_spider.py  # Veterinary data spider
│   │
│   ├── items/             # Data models
│   │   ├── __init__.py
│   │   └── vet_items.py
│   │
│   ├── pipelines/         # Data processing pipelines
│   │   ├── __init__.py
│   │   └── db_pipeline.py
│   │
│   ├── middlewares/       # Scrapy middlewares
│   │   ├── __init__.py
│   │   └── custom_middleware.py
│   │
│   └── utils/            # Utility functions
│       ├── __init__.py
│       └── helpers.py
│
├── maintenance/          # Maintenance scripts
│   ├── __init__.py
│   ├── db_reset.py      # Database reset/initialization
│   └── verify_data.py   # Data verification
│
├── tools/               # Helper tools
│   ├── __init__.py
│   ├── data_viewer.py   # Data visualization
│   └── export_data.py   # Data export
│
└── tests/               # Test files
    ├── __init__.py
    ├── conftest.py     # pytest configuration
    └── test_spider.py  # Spider tests
```

## Database Schema

### Data Flow
1. **Data Sources** → Track different data sources and configurations
2. **Scraping Runs** → Monitor scraping sessions and progress
3. **Raw Data** → Store unmodified scraped data
4. **Cleaned Data** → Standardized and validated data
5. **Enriched Data** → Additional data from external sources
6. **Master Records** → Consolidated records from multiple sources

### Tables
- `data_sources`: Configuration and metadata for each data source
- `scraping_runs`: Track individual scraping sessions
- `raw_data`: Original scraped data
- `cleaned_data`: Validated and standardized data
- `enriched_data`: Enhanced data from external sources
- `master_records`: Unified records from all sources

## Setup

### Prerequisites
- Python 3.9+
- PostgreSQL 12+
- virtualenv or conda

### Installation
```bash
# Clone the repository
git clone <repository-url>
cd fox_scraper

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate

# Install dependencies
pip install -e .

# Configure environment
cp .env.example .env
# Edit .env with your database credentials
```

### Database Setup
```bash
# Initialize database
python fox_scraper/maintenance/db_reset.py
```

## Usage

### Running Spiders
```bash
# Run veterinary spider
scrapy crawl vet_spider

# Run with specific settings
scrapy crawl vet_spider -s DOWNLOAD_DELAY=2
```

### Data Management
```bash
# View data
python fox_scraper/tools/data_viewer.py

# Export data
python fox_scraper/tools/export_data.py
```

### Maintenance
```bash
# Reset database
python fox_scraper/maintenance/db_reset.py

# Verify data integrity
python fox_scraper/maintenance/verify_data.py
```

## Configuration

### Environment Variables
```env
DB_HOST=192.168.1.164
DB_PORT=5432
DB_NAME=fox_db
DB_USER=postgres
DB_PASSWORD=your_password
```

### Scrapy Settings
Key settings in `settings.py`:
```python
# Concurrency
CONCURRENT_REQUESTS = 1
DOWNLOAD_DELAY = 2

# Retry Configuration
RETRY_ENABLED = True
RETRY_TIMES = 5
RETRY_HTTP_CODES = [500, 502, 503, 504, 400, 403, 408, 429]

# Pipeline Configuration
ITEM_PIPELINES = {
    'fox_scraper.pipelines.db_pipeline.DatabasePipeline': 300,
}
```

## Data Processing Pipeline

### 1. Data Collection
- Spider collects raw data
- Data is stored with source information
- Initial validation is performed

### 2. Data Cleaning
- Standardize formats
- Remove duplicates
- Validate required fields

### 3. Data Enrichment
- Add geolocation data
- Fetch additional details
- Cross-reference with other sources

### 4. Record Consolidation
- Merge related records
- Resolve conflicts
- Maintain data lineage

## Development

### Adding New Sources
1. Create new spider in `spiders/`
2. Define source-specific items in `items/`
3. Add source configuration in `data_sources` table
4. Implement custom cleaning rules if needed

### Testing
```bash
# Run all tests
pytest

# Run specific test file
pytest tests/test_spider.py

# Run with coverage
pytest --cov=fox_scraper tests/
```

### Code Style
```bash
# Format code
black fox_scraper/

# Check style
flake8 fox_scraper/
```

## Monitoring

### Logs
- Scrapy logs in `scrapy.log`
- Database operations in `db.log`
- Error tracking in `error.log`

### DB Data viewer
```bash
streamlit run tools/data_viewer.py
```

### Metrics
- Items processed
- Success/failure rates
- Processing time
- Data quality scores

## Contributing
1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License
[MIT License](LICENSE)

## Authors
Your Name <your.email@example.com>


