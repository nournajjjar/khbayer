# data.py
import pandas as pd
from textblob import TextBlob
from datetime import datetime
import os
import requests
from typing import List, Dict, Any

# ----------------------------------------------------------------------
# Helper: Normalise a string for duplicate detection (lower-case, strip)
# ----------------------------------------------------------------------
def _norm(s: str) -> str:
    return (s or "").strip().lower()


# ----------------------------------------------------------------------
# Main scraper
# ----------------------------------------------------------------------
def scrape_news(query: str = 'all', num_articles: int = 20) -> pd.DataFrame:
    """
    Fetch news from NewsAPI, run sentiment analysis with TextBlob,
    and **never add duplicate articles** (title + url).

    Returns
    -------
    pd.DataFrame
        Columns: title, summary, text, url, date, source,
                 image_url, sentiment, sentiment_label
    """
    api_key = os.getenv('NEWSAPI_KEY')
    if not api_key:
        print("NEWSAPI_KEY environment variable is not set.")
        return pd.DataFrame()
    today = datetime.utcnow().strftime('%Y-%m-%d')   # real-time today

    # -------------------------------------------------
    # 1. Try top-headlines first
    # -------------------------------------------------
    base_url = 'https://newsapi.org/v2/top-headlines'
    params = {
        'country': 'us',
        'pageSize': min(num_articles, 100),
        'apiKey': api_key
    }
    if query and query != 'all':
        params['q'] = query

    articles = _fetch_articles(base_url, params, query, today, num_articles)

    # -------------------------------------------------
    # 2. If nothing → fallback to /everything
    # -------------------------------------------------
    if not articles:
        print("No results from top-headlines → trying /everything")
        base_url = 'https://newsapi.org/v2/everything'
        params = {
            'q': query if query and query != 'all' else 'all',
            'from': today,
            'to': today,
            'sortBy': 'publishedAt',
            'pageSize': min(num_articles, 100),
            'language': 'en',
            'apiKey': api_key
        }
        articles = _fetch_articles(base_url, params, query, today, num_articles)

    if not articles:
        print("No articles after both attempts.")
        return pd.DataFrame()

    # -------------------------------------------------
    # 3. Process + deduplicate
    # -------------------------------------------------
    processed = []
    seen = set()                     # (norm_title, norm_url) tuples

    for art in articles:
        title = art.get('title', 'Untitled')
        url   = art.get('url', '#')

        key = (_norm(title), _norm(url))
        if key in seen:
            print(f"Duplicate skipped: {title}")
            continue
        seen.add(key)

        # ---- basic fields ----
        summary   = art.get('description') or 'No summary available'
        text      = art.get('description') or 'No text available'
        pub_date  = art.get('publishedAt') or datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
        source    = art['source'].get('name', 'Unknown')
        image_url = art.get('urlToImage') or 'https://via.placeholder.com/150'

        # ---- validate image ----
        if image_url != 'https://via.placeholder.com/150':
            try:
                r = requests.head(image_url, timeout=5)
                if r.status_code != 200 or 'image' not in r.headers.get('content-type', '').lower():
                    image_url = 'https://via.placeholder.com/150'
            except Exception:
                image_url = 'https://via.placeholder.com/150'

        # ---- sentiment (TextBlob) ----
        blob = TextBlob(text if isinstance(text, str) else 'No text available')
        sentiment = blob.sentiment.polarity
        sentiment_label = (
            'Positive' if sentiment > 0.1 else
            'Negative' if sentiment < -0.1 else
            'Neutral'
        )

        # ---- truncate for display (optional) ----
        summary_disp = summary[:200] + '...' if len(summary) > 200 else summary
        text_disp    = text[:500] + '...' if len(text) > 500 else text

        processed.append({
            'title': title,
            'summary': summary_disp,
            'text': text_disp,
            'url': url,
            'date': pub_date,
            'source': source,
            'image_url': image_url,
            'sentiment': sentiment,
            'sentiment_label': sentiment_label
        })

    df_new = pd.DataFrame(processed)
    print(f"New articles after deduplication: {len(df_new)}")

    # -------------------------------------------------
    # 4. Merge with existing CSV (still deduplicate globally)
    # -------------------------------------------------
    csv_path = 'news_data.csv'
    if os.path.exists(csv_path):
        try:
            df_old = pd.read_csv(csv_path, encoding='utf-8')
            if not df_old.empty:
                # Build global seen set from old data
                old_seen = {(_norm(t), _norm(u)) for t, u in zip(df_old['title'], df_old['url'])}
                # Filter out anything already in old data
                df_new = df_new[~df_new.apply(lambda r: (_norm(r['title']), _norm(r['url'])) in old_seen, axis=1)]
                df = pd.concat([df_old, df_new], ignore_index=True)
                print(f"Combined total (no duplicates): {len(df)}")
            else:
                df = df_new
        except Exception as e:
            print(f"CSV read error ({e}) → using only new data")
            df = df_new
    else:
        df = df_new

    # -------------------------------------------------
    # 5. Save & return
    # -------------------------------------------------
    df.to_csv(csv_path, index=False, encoding='utf-8')
    print(f"Saved {len(df)} articles to {csv_path}")
    return df


# ----------------------------------------------------------------------
# Internal fetch helper (DRY)
# ----------------------------------------------------------------------
def _fetch_articles(base_url: str, params: dict, query: str, today: str, limit: int) -> List[Dict[Any, Any]]:
    try:
        print(f"GET {base_url} | params: {params}")
        resp = requests.get(base_url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        if data.get('status') != 'ok':
            print(f"API error: {data.get('message')}")
            return []

        total = data.get('totalResults', 0)
        print(f"API returned {total} articles")
        return data['articles'][:limit]

    except Exception as e:
        print(f"Request failed: {e}")
        return []


# ----------------------------------------------------------------------
# Run when executed directly
# ----------------------------------------------------------------------
if __name__ == '__main__':
    df = scrape_news()
    print(f"Scraped {len(df)} unique articles → news_data.csv")