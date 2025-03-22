import datetime
import requests
import pytz

# https://finnhub.io/pricing
# On top of all plan's limit, there is a 30 API calls/ second limit.
# 60 API calls/minute

def finnhub_handler(symbol, max_count, current_date):

    today = datetime.datetime.strptime(current_date, '%Y-%m-%d')
    end = today.strftime('%Y-%m-%d')
    start = (today + datetime.timedelta(days=-10)).strftime('%Y-%m-%d')


    url = f"https://finnhub.io/api/v1/company-news?symbol={symbol}&from={start}&to={end}"
    print(f"Working on {url}")

    headers = {
        "X-Finnhub-Token": ""
    }

    news = ""
    count = 0

    try:
        r = requests.get(url, headers=headers)
        data = r.json()

        if r.status_code == 200:
            news += f"<div class='news-section'><h2>News on stock symbol {symbol}</h2>"
            for entry in data:

                dt_naive_utc = datetime.datetime.fromtimestamp(entry['datetime'], datetime.UTC)
                pub_time = dt_naive_utc.replace(tzinfo=pytz.utc)

                count += 1
                news += "<div class='news-item'>"
                news += f"<div class='news-title'>{entry['headline']}</div>"
                news += f"<div class='news-date'>Published on: {pub_time}</div>"
                news += f"<div class='news-description'>{entry['summary']}</div>"
                news += "</div>"
                if count >= max_count:
                    break
            news += "</div>"
        else:
            print(f"Failed to get news feed for {symbol}. Status code:", r.status_code)
    except Exception as e:
        print(f"Error fetching news for {symbol}: {e}")

    return news