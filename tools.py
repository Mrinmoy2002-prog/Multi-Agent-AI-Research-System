from langchain.tools import tool 
import requests
from bs4 import BeautifulSoup
from tavily import TavilyClient
import os 
from dotenv import load_dotenv
from rich import print
load_dotenv()

taviley_api_key = os.getenv("TAVILEY_API_KEY")

tavily = TavilyClient(api_key=taviley_api_key)


@tool
def get_web_content(query:str) -> str:
    """Search the web for recent and reliable information on a given topic. Returns Titles, URLs and Snippets"""

    search_results = tavily.search(query = query, max_results=5)
    search_list = []
    for r in search_results['results']:
        search_list.append(f"Title: {r.get('title', 'No title')}\nURL: {r.get('url', '')}\nSnippet: {r.get('content', '')[:300]}\n")

    return "\n----\n".join(search_list)


@tool
def scrape_website_url(url:str) -> str:
    """Scrape the content of a website given its URL. Returns the main text content of the page."""

    try:
        resp = requests.get(url, timeout=7, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(resp.text, 'html.parser')
        for tag in soup(['script', 'style', 'header', 'footer', 'nav', 'aside']):
            tag.decompose()

        return soup.get_text(separator=' ', strip=True)[:3000]  # Return first 3000 chars of text content
    except Exception as e:
        return f"Error fetching URL: {str(e)}"

# print(get_web_content.invoke({"query": "What is the latest news on AI?"}))

# print(scrape_website_url.invoke({"url": "https://www.bbc.com/news/technology-56933733"}))