import json
import boto3
import datetime
import pytz
from finnhub_handler import finnhub_handler
from google_rss_handler import google_rss_handler
from datetime import datetime, timedelta
from pathlib import Path

session = boto3.Session(profile_name="")
s3_client = session.client("s3")

bucket_name = ""

save_path = "webpages/"
save_local = True

Path(save_path).mkdir(parents=True, exist_ok=True)



def generate_past_year_weekdays(end_date):
    start_date = end_date - timedelta(days=365)
    current = end_date
    dates = []

    while current > start_date:
        if current.weekday() < 5:  # Weekday: Monday–Friday
            dates.append(current.strftime("%Y-%m-%d"))
        current -= timedelta(days=1)

    return dates


def lambda_handler(event, context):

    end = datetime(2025, 3, 19)
    dates = generate_past_year_weekdays(end)

    keywords_lists = [
        [
            {"finnhub": ["QQQ"],  "google_rss": ["QQQ", "NASDAQ"]},
            {"finnhub": ["AAPL"], "google_rss": ["AAPL", "Apple"]}
        ],
        [
            {"finnhub": ["NVDA"], "google_rss": ["NVDA", "Nvidia"]},
            {"finnhub": ["MSFT"], "google_rss": ["MSFT", "Microsoft"]}
        ],
        [
            {"finnhub": ["AMZN"], "google_rss": ["AMZN", "Amazon"]},
            {"finnhub": ["AVGO"], "google_rss": ["AVGO", "Broadcom"]}
        ],
        [
            {"finnhub": ["TSLA"], "google_rss": ["TSLA", "Tesla", "SpaceX"]},
            {"finnhub": ["META"], "google_rss": ["META", "Meta", "Facebook"]}
        ],
        [
            {"finnhub": ["GOOGL"], "google_rss": ["GOOGL", "Google", "Alphabet"]},
            {"finnhub": ["GOOG"], "google_rss": ["GOOG"]}
        ]
    ]

    for current_date in dates:
        count = 0 # for html page, 1-5 for google news RSS
        for keywords in keywords_lists:
            count += 1
            file_name = f"page-past-{current_date}-{count:02d}.html"
            print(f"Working on {file_name}")
            create_website(keywords, file_name, max_news_each=10, current_date=current_date)


def create_website(keywords, file_name, max_news_each, current_date):

    # toronto_tz = pytz.timezone("America/Toronto")
    # current_time = datetime.datetime.now(toronto_tz).strftime("%Y-%m-%d %H:%M:%S")

    # Initialize HTML content
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta http-equiv="X-UA-Compatible" content="IE=edge">
        <title>QQQ Tech Companies News</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                margin: 20px;
                line-height: 1.6;
            }
            h1 {
                color: #333;
            }
            h2 {
                color: #555;
            }
            .news-section {
                margin-bottom: 40px;
            }
            .news-item {
                margin-bottom: 20px;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 5px;
                background-color: #f9f9f9;
            }
            .news-title {
                font-weight: bold;
                font-size: 1.1em;
            }
            .news-date {
                color: #888;
                font-size: 0.9em;
            }
        </style>
    </head>
    <body>
        <h1>Most Recent News About Tech Companies in the Top Holdings of QQQ</h1>
        <div class="update-time">Last updated: """+current_date+""" (Toronto time)</div>
    """

    for keyword in keywords:

        for symbol in keyword["finnhub"]:
            html_content += finnhub_handler(symbol, max_news_each, current_date)
        for symbol in keyword["google_rss"]:
            html_content += google_rss_handler(symbol, max_news_each, current_date)


    # Close the HTML structure
    html_content += """
    </body>
    </html>
    """

    # Save to local
    if save_local:
        with open(f"{save_path}{file_name}", "w", encoding="utf-8") as f:
            f.write(html_content)

    # Save the content to S3
    try:
        s3_client.put_object(
            Bucket=bucket_name,
            Key=file_name,
            Body=html_content,
            ContentType="text/html"
        )
        print(f"HTML file successfully saved to S3: {bucket_name}/{file_name}")
    except Exception as e:
        print(f"Error saving file to S3: {e}")
        return {
            'statusCode': 500,
            'body': json.dumps("Failed to save the file to S3.")
        }

    return {
        'statusCode': 200,
        'body': json.dumps(f"HTML file successfully saved to S3: {bucket_name}/{file_name}")
    }


if __name__ == "__main__":
    lambda_handler(None, None)