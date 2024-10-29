# setup.py
from setuptools import setup, find_packages

setup(
    name='fox_scraper',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'scrapy>=2.11.0',
        'sqlalchemy',
        'psycopg2-binary',
        'python-dotenv',
    ],
)