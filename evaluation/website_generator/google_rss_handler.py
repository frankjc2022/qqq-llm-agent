import feedparser
from bs4 import BeautifulSoup


def google_rss_handler(keyword, max_count, current_date):

    rss_url = f'https://news.google.com/rss/search?q={keyword}+before:{current_date}&hl=en-US&gl=US&ceid=US:en'
    print(f"Working on {rss_url}")

    news = ""
    count = 0
    try:
        feed = feedparser.parse(rss_url)
        if feed.status == 200:
            news += f"<div class='news-section'><h2>News on {keyword}</h2>"
            for entry in feed.entries:
                count += 1
                news += "<div class='news-item'>"
                news += f"<div class='news-title'>{entry.title}</div>"
                news += f"<div class='news-date'>Published on: {entry.published}</div>"
                soup = BeautifulSoup(entry.description, "html.parser")
                description_text = ''.join(d.get_text(" ") for d in soup)
                news += f"<div class='news-description'>{description_text}</div>"
                news += "</div>"
                if count >= max_count:
                    break
            news += "</div>"
        else:
            print(f"Failed to get RSS feed for {keyword}. Status code:", feed.status)
    except Exception as e:
        print(f"Error fetching news for {keyword}: {e}")

    return news