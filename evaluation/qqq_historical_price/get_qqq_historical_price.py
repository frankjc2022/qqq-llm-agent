import json
import csv
from datetime import datetime

def read_csv_as_dict_list(file_path):
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        data = []
        for row in reader:
            converted_row = {
                'Date': datetime.strptime(row['Date'], "%m/%d/%Y").strftime("%Y-%m-%d"),
                'Close/Last': float(row['Close/Last']),
                'Volume': int(row['Volume']),
                'Open': float(row['Open']),
                'High': float(row['High']),
                'Low': float(row['Low'])
            }
            data.append(converted_row)
        return data


if __name__ == '__main__':

    # QQQ historical data downloaded from: # https://www.nasdaq.com/market-activity/etf/qqq/historical
    file_path = "qqq_historical_data_latest_2025-03-19.csv"
    data = read_csv_as_dict_list(file_path)

    with open("historical_qqq.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    res = {}
    for d in data:
        res[d["Date"]] = d["Open"]
    with open("historical_qqq_open.json", "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=2)

    res = {}
    for d in data:
        res[d["Date"]] = d["Close/Last"]
    with open("historical_qqq_close.json", "w", encoding="utf-8") as f:
        json.dump(res, f, ensure_ascii=False, indent=2)