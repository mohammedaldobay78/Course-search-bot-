# search_service.py
import requests
from config import SERPAPI_KEY
from logs import logger

SERPAPI_URL = "https://serpapi.com/search.json"

def search_courses(query, num_results=10, language="ar"):
    """
    Use SerpAPI to search; returns list of results dict:
    {title, link, snippet, source, rating}
    """
    if not SERPAPI_KEY:
        logger.error("SerpAPI key missing")
        raise RuntimeError("SerpAPI key not configured")

    params = {
        "q": query + " course",
        "engine": "google",
        "num": num_results,
        "hl": "en" if language == "en" else "ar",
        "api_key": SERPAPI_KEY,
    }
    try:
        r = requests.get(SERPAPI_URL, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
        serp_results = data.get("organic_results") or data.get("results") or []
        results = []
        for item in serp_results[:num_results]:
            title = item.get("title") or item.get("name") or "بدون عنوان"
            link = item.get("link") or item.get("url") or ""
            snippet = item.get("snippet") or item.get("description") or ""
            source = item.get("source") or ""
            rating = item.get("rating") or item.get("avg_rating") or None
            results.append({
                "title": title,
                "link": link,
                "snippet": snippet,
                "source": source,
                "rating": rating
            })
        return results
    except Exception as e:
        logger.exception("SerpAPI request failed: %s", e)
        raise