# fox_scraper/tools/data_viewer.py
import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine, text
import os
from dotenv import load_dotenv
import json

# Load environment variables
load_dotenv()

# Database connection
def get_db_connection():
    return create_engine(
        f"postgresql://{os.getenv('DB_USER', 'postgres')}:"
        f"{os.getenv('DB_PASSWORD', 'Milena84')}@"
        f"{os.getenv('DB_HOST', '192.168.1.164')}:"
        f"{os.getenv('DB_PORT', '5432')}/"
        f"{os.getenv('DB_NAME', 'fox_db')}"
    )

def load_data(query):
    engine = get_db_connection()
    return pd.read_sql_query(query, engine)

def main():
    st.set_page_config(page_title="Fox Scraper Data Viewer", layout="wide")
    
    # Sidebar navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio(
        "Choose a section",
        ["Overview", "Raw Data", "Cleaned Data", "Master Records", "Analysis"]
    )
    
    if page == "Overview":
        show_overview()
    elif page == "Raw Data":
        show_raw_data()
    elif page == "Cleaned Data":
        show_cleaned_data()
    elif page == "Master Records":
        show_master_records()
    else:
        show_analysis()

def show_overview():
    st.title("Database Overview")
    
    # Create columns for metrics
    col1, col2, col3 = st.columns(3)
    
    # Get counts from different tables
    counts = load_data("""
        SELECT
            (SELECT COUNT(*) FROM data_sources) as sources_count,
            (SELECT COUNT(*) FROM raw_data) as raw_count,
            (SELECT COUNT(*) FROM master_records) as master_count
    """)
    
    with col1:
        st.metric("Data Sources", counts['sources_count'].iloc[0])
    with col2:
        st.metric("Raw Records", counts['raw_count'].iloc[0])
    with col3:
        st.metric("Master Records", counts['master_count'].iloc[0])
    
    # Show recent scraping runs
    st.subheader("Recent Scraping Runs")
    runs = load_data("""
        SELECT 
            sr.id,
            ds.name as source,
            sr.start_time,
            sr.end_time,
            sr.status,
            sr.items_processed
        FROM scraping_runs sr
        JOIN data_sources ds ON sr.source_id = ds.id
        ORDER BY sr.start_time DESC
        LIMIT 10
    """)
    st.dataframe(runs)
    
    # Show data source statistics
    st.subheader("Data Source Statistics")
    source_stats = load_data("""
        SELECT 
            ds.name as source,
            COUNT(rd.id) as records,
            MIN(rd.scraped_at) as first_scrape,
            MAX(rd.scraped_at) as last_scrape
        FROM data_sources ds
        LEFT JOIN raw_data rd ON ds.id = rd.source_id
        GROUP BY ds.name
    """)
    st.dataframe(source_stats)

def show_raw_data():
    st.title("Raw Data Explorer")
    
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        source = st.selectbox(
            "Select Data Source",
            options=load_data("SELECT name FROM data_sources")['name'].tolist()
        )
    with col2:
        status = st.selectbox(
            "Processing Status",
            options=['All', 'pending', 'processed', 'failed']
        )
    
    # Build query
    query = """
        SELECT rd.id, rd.url, rd.scraped_at, rd.processing_status, rd.raw_content
        FROM raw_data rd
        JOIN data_sources ds ON rd.source_id = ds.id
        WHERE ds.name = :source
    """
    if status != 'All':
        query += " AND rd.processing_status = :status"
    
    # Load data
    params = {'source': source, 'status': status}
    data = load_data(query)
    
    # Display data
    if not data.empty:
        st.dataframe(data)
    else:
        st.info("No data found for selected filters")

def show_cleaned_data():
    st.title("Cleaned Data Explorer")
    
    # Filters
    col1, col2 = st.columns(2)
    with col1:
        source = st.selectbox(
            "Select Data Source",
            options=load_data("SELECT name FROM data_sources")['name'].tolist(),
            key='cleaned_source'
        )
    with col2:
        validation_status = st.selectbox(
            "Validation Status",
            options=['All', 'valid', 'partial', 'invalid']
        )
    
    # Load data
    query = """
        SELECT 
            cd.id,
            cd.name,
            cd.category,
            cd.address,
            cd.contact,
            cd.cleaned_at,
            cd.validation_status
        FROM cleaned_data cd
        JOIN data_sources ds ON cd.source_id = ds.id
        WHERE ds.name = :source
    """
    if validation_status != 'All':
        query += " AND cd.validation_status = :status"
    
    data = load_data(query)
    
    if not data.empty:
        st.dataframe(data)
    else:
        st.info("No cleaned data found for selected filters")

def show_master_records():
    st.title("Master Records")
    
    # Search functionality
    search_term = st.text_input("Search by name or ID")
    
    if search_term:
        query = """
            SELECT *
            FROM master_records
            WHERE name ILIKE :search
            OR external_id ILIKE :search
        """
        data = load_data(query, {'search': f'%{search_term}%'})
        
        if not data.empty:
            st.dataframe(data)
        else:
            st.info("No records found matching your search")
    else:
        # Show recent records
        st.subheader("Recent Records")
        recent = load_data("""
            SELECT *
            FROM master_records
            ORDER BY updated_at DESC
            LIMIT 100
        """)
        st.dataframe(recent)

def show_analysis():
    st.title("Data Analysis")
    
    # Record counts over time
    st.subheader("Data Collection Progress")
    timeline = load_data("""
        SELECT 
            DATE(scraped_at) as date,
            COUNT(*) as count
        FROM raw_data
        GROUP BY DATE(scraped_at)
        ORDER BY date
    """)
    
    fig = px.line(timeline, x='date', y='count', title='Records Collected per Day')
    st.plotly_chart(fig)
    
    # Validation status distribution
    st.subheader("Data Quality Overview")
    validation_stats = load_data("""
        SELECT 
            validation_status,
            COUNT(*) as count
        FROM cleaned_data
        GROUP BY validation_status
    """)
    
    fig = px.pie(validation_stats, values='count', names='validation_status', 
                 title='Data Validation Status Distribution')
    st.plotly_chart(fig)
    
    # Source distribution
    st.subheader("Data Source Distribution")
    source_stats = load_data("""
        SELECT 
            ds.name as source,
            COUNT(rd.id) as count
        FROM data_sources ds
        LEFT JOIN raw_data rd ON ds.id = rd.source_id
        GROUP BY ds.name
    """)
    
    fig = px.bar(source_stats, x='source', y='count', 
                 title='Records per Data Source')
    st.plotly_chart(fig)

if __name__ == "__main__":
    main()