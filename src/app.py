import streamlit as st
import requests
import json
import time
import base64
import os
from datetime import datetime

# Set page config
st.set_page_config(page_title="FireCrawl Scraper", page_icon="🔥", layout="wide")

# Define CSS
st.markdown(
    """
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.5rem;
        font-weight: bold;
        margin-top: 1rem;
        margin-bottom: 0.5rem;
    }
    .result-area {
        background-color: #f0f2f6;
        border-radius: 10px;
        padding: 1rem;
        margin-top: 1rem;
    }
    .api-config {
        background-color: #f9f9f9;
        border-radius: 10px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .download-section {
        background-color: #e6e9ef;
        border-radius: 5px;
        padding: 0.5rem;
        margin-bottom: 1rem;
    }
</style>
""",
    unsafe_allow_html=True,
)

# Initialize session state variables
if "scrape_result" not in st.session_state:
    st.session_state.scrape_result = None
if "batch_results" not in st.session_state:
    st.session_state.batch_results = {}
if "batch_status" not in st.session_state:
    st.session_state.batch_status = {}
if "search_results" not in st.session_state:
    st.session_state.search_results = None

# Function to load settings from local storage
def load_settings():
    if os.path.exists("firecrawl_settings.json"):
        with open("firecrawl_settings.json", "r") as f:
            return json.load(f)
    return {"api_url": "https://api.firecrawl.dev", "api_key": ""}

# Function to save settings to local storage
def save_settings(settings):
    with open("firecrawl_settings.json", "w") as f:
        json.dump(settings, f)

# Load settings
settings = load_settings()

# Header
st.markdown(
    "<div class='main-header'>🔥 FireCrawl Scraper</div>", unsafe_allow_html=True
)

# API Configuration
st.markdown("<div class='sub-header'>API Configuration</div>", unsafe_allow_html=True)
with st.expander("Configure API Settings", expanded=True):
    col1, col2 = st.columns(2)
    with col1:
        api_url = st.text_input("API URL", value=settings["api_url"])
    with col2:
        api_key = st.text_input("API Key", value=settings["api_key"], type="password")

    if st.button("Save Settings"):
        settings["api_url"] = api_url
        settings["api_key"] = api_key
        save_settings(settings)
        st.success("Settings saved successfully!")

# Function to generate download link
def get_download_link(content, filename, link_text):
    if isinstance(content, dict):
        content = json.dumps(content, indent=2, ensure_ascii=False)
    b64 = base64.b64encode(content.encode()).decode()
    return f'<a href="data:text/plain;base64,{b64}" download="{filename}" target="_blank">{link_text}</a>'

# Function to check batch scrape status
def check_batch_status(batch_id):
    headers = {"Authorization": f"Bearer {settings['api_key']}"}
    response = requests.get(
        f"{settings['api_url']}/v1/batch/scrape/{batch_id}", headers=headers
    )
    return response.json()

# Function to handle batch scrape completion
def handle_batch_completion(batch_id):
    tries = 0
    max_tries = 30
    while tries < max_tries:
        status_data = check_batch_status(batch_id)
        st.session_state.batch_status[batch_id] = status_data

        if status_data.get("status") == "completed":
            st.session_state.batch_results[batch_id] = status_data.get("data", [])
            return True
        elif status_data.get("status") == "failed":
            return False

        tries += 1
        time.sleep(2)
    return False

# Tabs for different functionalities
tab1, tab2, tab3 = st.tabs(["Single URL Scrape", "Batch Scrape", "Search"])

# Single URL Scrape
with tab1:
    st.markdown(
        "<div class='sub-header'>Scrape Single URL</div>", unsafe_allow_html=True
    )

    url = st.text_input("Enter URL to scrape")

    col1, col2, col3 = st.columns(3)
    with col1:
        markdown = st.checkbox("Markdown", value=True)
    with col2:
        html = st.checkbox("HTML", value=False)
    with col3:
        raw_html = st.checkbox("Raw HTML", value=False)

    advanced_options = st.expander("Advanced Options", expanded=False)
    with advanced_options:
        col1, col2 = st.columns(2)
        with col1:
            only_main_content = st.checkbox("Only Main Content", value=True)
            mobile = st.checkbox("Mobile", value=False)
            block_ads = st.checkbox("Block Ads", value=True)
        with col2:
            wait_for = st.number_input("Wait For (ms)", value=1000, min_value=0)
            timeout = st.number_input(
                "Timeout (ms)", value=60000, min_value=1000, step=1000
            )
            remove_base64_images = st.checkbox("Remove Base64 Images", value=True)

    if st.button("Scrape URL"):
        if not url:
            st.error("Please enter a URL")
        else:
            with st.spinner("Scraping URL..."):
                formats = []
                if markdown:
                    formats.append("markdown")
                if html:
                    formats.append("html")
                if raw_html:
                    formats.append("rawHtml")

                if not formats:
                    st.error("Please select at least one format")
                else:
                    headers = {
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {settings['api_key']}",
                    }

                    payload = {
                        "url": url,
                        "formats": formats,
                        "onlyMainContent": only_main_content,
                        "waitFor": wait_for,
                        "mobile": mobile,
                        "timeout": timeout,
                        "removeBase64Images": remove_base64_images,
                        "blockAds": block_ads,
                    }

                    try:
                        response = requests.post(
                            f"{settings['api_url']}/v1/scrape",
                            headers=headers,
                            json=payload,
                        )

                        if response.status_code == 200:
                            st.session_state.scrape_result = response.json()
                            st.success("URL scraped successfully!")
                        else:
                            st.error(f"Error: {response.status_code} - {response.text}")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

    # Display scrape results
    if st.session_state.scrape_result:
        st.markdown(
            "<div class='sub-header'>Scrape Results</div>", unsafe_allow_html=True
        )
        st.markdown("<div class='result-area'>", unsafe_allow_html=True)

        if "data" in st.session_state.scrape_result:
            data = st.session_state.scrape_result["data"]
            
            # Display download section at the top
            st.markdown("<div class='download-section'>", unsafe_allow_html=True)
            st.markdown("### Download Options")
            
            # Download links
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            if "markdown" in data:
                st.markdown(
                    get_download_link(
                        data["markdown"], f"scrape_{timestamp}.md", "⬇️ Download Markdown"
                    ),
                    unsafe_allow_html=True,
                )
            if "html" in data or "rawHtml" in data:
                html_content = data.get("html", "") or data.get("rawHtml", "")
                st.markdown(
                    get_download_link(
                        html_content,
                        f"scrape_full_{timestamp}.html",
                        "⬇️ Download Full HTML",
                    ),
                    unsafe_allow_html=True,
                )
            st.markdown(
                get_download_link(
                    st.session_state.scrape_result,
                    f"scrape_full_{timestamp}.json",
                    "⬇️ Download Full JSON Result",
                ),
                unsafe_allow_html=True,
            )
            st.markdown("</div>", unsafe_allow_html=True)

            # Display metadata
            if "metadata" in data:
                st.markdown("### Metadata")
                st.json(data["metadata"])

            # Display content tabs
            content_tabs = []
            if "markdown" in data:
                content_tabs.append("Markdown")
            if "html" in data:
                content_tabs.append("HTML")
            if "rawHtml" in data:
                content_tabs.append("Raw HTML")

            if content_tabs:
                tabs = st.tabs(content_tabs)

                tab_index = 0
                if "markdown" in data:
                    with tabs[tab_index]:
                        st.markdown(data["markdown"])
                    tab_index += 1

                if "html" in data:
                    with tabs[tab_index]:
                        st.code(data["html"], language="html")
                    tab_index += 1

                if "rawHtml" in data:
                    with tabs[tab_index]:
                        st.code(data["rawHtml"], language="html")

        st.markdown("</div>", unsafe_allow_html=True)

# Batch Scrape
with tab2:
    st.markdown(
        "<div class='sub-header'>Batch Scrape Multiple URLs</div>",
        unsafe_allow_html=True,
    )

    urls = st.text_area("Enter URLs (one per line)")

    col1, col2, col3 = st.columns(3)
    with col1:
        batch_markdown = st.checkbox("Markdown", value=True, key="batch_markdown")
    with col2:
        batch_html = st.checkbox("HTML", value=False, key="batch_html")
    with col3:
        batch_raw_html = st.checkbox("Raw HTML", value=False, key="batch_raw_html")

    batch_advanced_options = st.expander("Advanced Options", expanded=False)
    with batch_advanced_options:
        col1, col2 = st.columns(2)
        with col1:
            batch_only_main_content = st.checkbox(
                "Only Main Content", value=True, key="batch_only_main_content"
            )
            batch_mobile = st.checkbox("Mobile", value=False, key="batch_mobile")
            batch_block_ads = st.checkbox(
                "Block Ads", value=True, key="batch_block_ads"
            )
        with col2:
            batch_wait_for = st.number_input(
                "Wait For (ms)", value=1000, min_value=0, key="batch_wait_for"
            )
            batch_timeout = st.number_input(
                "Timeout (ms)",
                value=60000,
                min_value=1000,
                step=1000,
                key="batch_timeout",
            )
            batch_remove_base64_images = st.checkbox(
                "Remove Base64 Images", value=True, key="batch_remove_base64_images"
            )

    if st.button("Batch Scrape URLs"):
        if not urls:
            st.error("Please enter at least one URL")
        else:
            with st.spinner("Submitting batch scrape job..."):
                url_list = [url.strip() for url in urls.split("\n") if url.strip()]

                formats = []
                if batch_markdown:
                    formats.append("markdown")
                if batch_html:
                    formats.append("html")
                if batch_raw_html:
                    formats.append("rawHtml")

                if not formats:
                    st.error("Please select at least one format")
                elif not url_list:
                    st.error("Please enter valid URLs")
                else:
                    headers = {
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {settings['api_key']}",
                    }

                    payload = {
                        "urls": url_list,
                        "formats": formats,
                        "onlyMainContent": batch_only_main_content,
                        "waitFor": batch_wait_for,
                        "mobile": batch_mobile,
                        "timeout": batch_timeout,
                        "removeBase64Images": batch_remove_base64_images,
                        "blockAds": batch_block_ads,
                    }

                    try:
                        response = requests.post(
                            f"{settings['api_url']}/v1/batch/scrape",
                            headers=headers,
                            json=payload,
                        )

                        if response.status_code == 200:
                            batch_job = response.json()
                            batch_id = batch_job.get("id")

                            if batch_id:
                                st.success(
                                    f"Batch scrape job submitted! Job ID: {batch_id}"
                                )
                                st.info("Checking batch status...")

                                # Check batch status
                                if handle_batch_completion(batch_id):
                                    st.success("Batch scrape completed!")
                                else:
                                    st.warning(
                                        "Batch scrape is still processing or failed. Check the status below."
                                    )
                        else:
                            st.error(f"Error: {response.status_code} - {response.text}")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

    # Display batch jobs
    if st.session_state.batch_results:
        st.markdown(
            "<div class='sub-header'>Batch Scrape Results</div>", unsafe_allow_html=True
        )

        for batch_id, batch_data in st.session_state.batch_results.items():
            with st.expander(f"Batch Job: {batch_id}", expanded=True):
                st.markdown("<div class='result-area'>", unsafe_allow_html=True)

                # Display status
                if batch_id in st.session_state.batch_status:
                    status_data = st.session_state.batch_status[batch_id]
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Status", status_data.get("status", "Unknown"))
                    with col2:
                        st.metric(
                            "Completed",
                            f"{status_data.get('completed', 0)}/{status_data.get('total', 0)}",
                        )
                    with col3:
                        st.metric("Credits Used", status_data.get("creditsUsed", 0))

                # Display results
                if batch_data:
                    # Create a combined markdown file with all results
                    combined_markdown = ""
                    for i, result in enumerate(batch_data):
                        metadata = result.get("metadata", {})
                        url = metadata.get("sourceURL", f"URL #{i+1}")
                        if "markdown" in result:
                            combined_markdown += f"# {url}\n\n"
                            combined_markdown += result["markdown"]
                            combined_markdown += "\n\n---\n\n"

                    # Add download links for combined files at the top
                    st.markdown("<div class='download-section'>", unsafe_allow_html=True)
                    st.markdown("### Download Combined Results")
                    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                    
                    # Download combined JSON with proper encoding
                    st.markdown(
                        get_download_link(
                            {"results": batch_data},
                            f"batch_full_{batch_id}_{timestamp}.json",
                            "⬇️ Download Combined JSON Results",
                        ),
                        unsafe_allow_html=True,
                    )

                    # Download combined markdown if markdown was included
                    if combined_markdown:
                        st.markdown(
                            get_download_link(
                                combined_markdown,
                                f"batch_full_{batch_id}_{timestamp}.md",
                                "⬇️ Download Combined Markdown Results",
                            ),
                            unsafe_allow_html=True,
                        )
                    st.markdown("</div>", unsafe_allow_html=True)

                    # Display individual results
                    for i, result in enumerate(batch_data):
                        metadata = result.get("metadata", {})
                        url = metadata.get("sourceURL", f"URL #{i+1}")

                        st.markdown(f"### {url}")
                        
                        # Display metadata in a collapsible container
                        st.markdown("""
                            <details>
                                <summary>Metadata</summary>
                                <div style="margin-left: 1rem;">
                        """, unsafe_allow_html=True)
                        st.json(metadata)
                        st.markdown("</div></details>", unsafe_allow_html=True)

                        # Display content
                        if "markdown" in result:
                            st.markdown("#### Markdown")
                            st.markdown(result["markdown"])

                        if "html" in result:
                            st.markdown("#### HTML")
                            st.code(
                                (
                                    result["html"][:500] + "..."
                                    if len(result["html"]) > 500
                                    else result["html"]
                                ),
                                language="html",
                            )

                        if "rawHtml" in result:
                            st.markdown("#### Raw HTML")
                            st.code(
                                (
                                    result["rawHtml"][:500] + "..."
                                    if len(result["rawHtml"]) > 500
                                    else result["rawHtml"]
                                ),
                                language="html",
                            )

                        # Add separator between items
                        if i < len(batch_data) - 1:
                            st.markdown("---")

                st.markdown("</div>", unsafe_allow_html=True)

    # Check batch status manually
    st.markdown(
        "<div class='sub-header'>Check Batch Status</div>", unsafe_allow_html=True
    )
    col1, col2 = st.columns([3, 1])
    with col1:
        batch_id_input = st.text_input("Enter Batch Job ID")
    with col2:
        if st.button("Check Status"):
            if batch_id_input:
                with st.spinner("Checking batch status..."):
                    status_data = check_batch_status(batch_id_input)
                    st.session_state.batch_status[batch_id_input] = status_data

                    if status_data.get("status") == "completed":
                        st.session_state.batch_results[batch_id_input] = (
                            status_data.get("data", [])
                        )
                        st.success("Batch scrape completed!")
                    else:
                        st.info(f"Status: {status_data.get('status', 'Unknown')}")
                        st.info(
                            f"Completed: {status_data.get('completed', 0)}/{status_data.get('total', 0)}"
                        )
            else:
                st.error("Please enter a batch job ID")

# Search Tab
with tab3:
    st.markdown("<div class='sub-header'>Search</div>", unsafe_allow_html=True)
    
    # Search parameters
    query = st.text_input("Search Query")
    
    col1, col2 = st.columns(2)
    with col1:
        limit = st.number_input("Result Limit", min_value=1, max_value=100, value=5, key="search_limit")
        lang = st.text_input("Language Code", value="en", key="search_lang")
        timeout = st.number_input("Timeout (ms)", value=60000, min_value=1000, step=1000, key="search_timeout")
    with col2:
        country = st.text_input("Country Code", value="us", key="search_country")
        location = st.text_input("Location", key="search_location")
        tbs = st.text_input("Time-based Search (tbs)", key="search_tbs")
    
    # Scrape options
    scrape_options = {}
    with st.expander("Scrape Options"):
        col1, col2 = st.columns(2)
        with col1:
            scrape_options["onlyMainContent"] = st.checkbox("Only Main Content", value=True, key="search_only_main_content")
            scrape_options["mobile"] = st.checkbox("Mobile", value=False, key="search_mobile")
            scrape_options["blockAds"] = st.checkbox("Block Ads", value=True, key="search_block_ads")
        with col2:
            scrape_options["waitFor"] = st.number_input("Wait For (ms)", value=1000, min_value=0, key="search_wait_for")
            scrape_options["removeBase64Images"] = st.checkbox("Remove Base64 Images", value=True, key="search_remove_base64_images")
    
    if st.button("Search"):
        if not query:
            st.error("Please enter a search query")
        else:
            with st.spinner("Searching..."):
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {settings['api_key']}",
                }
                
                payload = {
                    "query": query,
                    "limit": limit,
                    "tbs": tbs if tbs else None,
                    "lang": lang,
                    "country": country,
                    "location": location if location else None,
                    "timeout": timeout,
                    "scrapeOptions": scrape_options
                }
                
                try:
                    response = requests.post(
                        f"{settings['api_url']}/v1/search",
                        headers=headers,
                        json=payload,
                    )
                    
                    if response.status_code == 200:
                        search_results = response.json()
                        st.session_state.search_results = search_results
                        st.success(f"Found {len(search_results.get('data', []))} results!")
                    else:
                        st.error(f"Error: {response.status_code} - {response.text}")
                except Exception as e:
                    st.error(f"Error: {str(e)}")
    
    # Display search results
    if st.session_state.get("search_results"):
        st.markdown("<div class='sub-header'>Search Results</div>", unsafe_allow_html=True)
        st.markdown("<div class='result-area'>", unsafe_allow_html=True)
        
        results = st.session_state.search_results.get("data", [])
        for i, result in enumerate(results):
            st.markdown(f"### Result {i+1}")
            
            # Display metadata
            if "metadata" in result:
                st.markdown("#### Metadata")
                st.json(result["metadata"])
            
            # Display content
            if "markdown" in result:
                st.markdown("#### Markdown")
                st.markdown(result["markdown"])
            
            if "html" in result:
                st.markdown("#### HTML")
                st.code(result["html"], language="html")
            
            if "rawHtml" in result:
                st.markdown("#### Raw HTML")
                st.code(result["rawHtml"], language="html")
            
            if i < len(results) - 1:
                st.markdown("---")
        
        st.markdown("</div>", unsafe_allow_html=True)

# Add footer
st.markdown("---")
st.markdown("FireCrawl Scraper UI - Made with Streamlit")
