import requests
from datetime import datetime, timedelta
from pathlib import Path

save_path = "webpage_summarize/"
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

def web_extractor(url):
    url = fr"http://view.pre.cm/agents/link.php?url={url}"
    res = requests.get(url)
    return res


if __name__ == "__main__":

    end = datetime(2025, 3, 19)
    dates = generate_past_year_weekdays(end)

    ######### batch get summarize
    for current_date in dates:
        for count in range(1, 6):
            file_name = f"page-past-{current_date}-{count:02d}"

            print(f"Working on {file_name}...")

            summarize_save_path = f"{save_path}/{file_name}.txt"

            url = fr"https://ece1724ai-feed-website.s3.ca-central-1.amazonaws.com/{file_name}.html"
            text = web_extractor(url).text
            with open(summarize_save_path, "w", encoding="utf-8") as f:
                f.write(text)