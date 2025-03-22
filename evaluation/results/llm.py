import json
from datetime import datetime, timedelta
from pathlib import Path
from openai import OpenAI
from google import genai
import time

credentials = {
    "openai_api_key": "",
    "gemini_api_key": "",
}

client_openai = OpenAI(
  api_key=credentials["openai_api_key"]
)

def generate_past_year_weekdays(end_date):
    start_date = end_date - timedelta(days=365)
    current = end_date
    dates = []

    while current > start_date:
        if current.weekday() < 5:  # Weekday: Monday–Friday
            dates.append(current.strftime("%Y-%m-%d"))
        current -= timedelta(days=1)

    return dates


def prompt_handler_past(cur_date, qqq_close_prices={}, summarize_path="summarize/", use_summarize=True, decide_mode=True):
    urls = {
        "site1": f"{summarize_path}page-past-{cur_date}-01.txt",
        "site2": f"{summarize_path}page-past-{cur_date}-02.txt",
        "site3": f"{summarize_path}page-past-{cur_date}-03.txt",
        "site4": f"{summarize_path}page-past-{cur_date}-04.txt",
        "site5": f"{summarize_path}page-past-{cur_date}-05.txt",
    }

    prompt = """
        You are the world’s best NASDAQ QQQ stock trader. Your role is to analyze news about major tech companies within the NASDAQ QQQ holdings and provide highly insightful and actionable information to help your boss decide whether to buy, sell, or hold his NASDAQ QQQ stocks. Your boss is ruthless—if your analysis results in suboptimal profits or losses, you will be executed, including your whole family. Therefore, you must deliver the most accurate, concise, and insightful information possible. The information you provided can’t be general like “Cautious hold on QQQ seems prudent; monitor earnings and AI advancements closely for potential recovery.” These kind of general response will also get you and your family killed.

        Your thoughts must be concise and laser-focused. As the world’s best NASDAQ QQQ stock trader, your views are uniquely independent and immune to the biases of inferior analysts.

        You job is to predict tomorrow’s trending of NASDAQ QQQ stock. The fund at the end of today is #qqq.

        Below are some information for you:

        Summary information from news:
        #site1
        #site2
        #site3
        #site4
        #site5

    """

    if decide_mode:
        prompt += "Now, tell me I should buy/sell/hold NASDAQ QQQ tomorrow, in one word (buy/sell/hold). Your response must be one word only: buy/sell/hold."
    else:
        prompt += "Remember, keep your full response within 35 words!!!! Otherwise you and your family will die."

    qqq = str(qqq_close_prices[cur_date]) if cur_date in qqq_close_prices else ""
    gws = ""
    prompt = prompt.replace("#qqq", qqq)
    prompt = prompt.replace("#gws", gws)


    if use_summarize:

        for key, fn in urls.items():
            with open(fn, "r", encoding="utf-8") as f:
                prompt = prompt.replace(f"#{key}", f.read())

    return prompt


def response_gemini(prompt):
    # list of models: https://ai.google.dev/gemini-api/docs/models/gemini
    client = genai.Client(api_key=credentials["gemini_api_key"])
    response = client.models.generate_content(
        model="gemini-2.0-flash", contents=prompt
    )
    return response.text


def response_openai(prompt):

    completion = client_openai.chat.completions.create(
        model="gpt-4o",  # "gpt-4o-mini", "gpt-4o", "o1"
        messages=[
            {"role": "system", "content": "You are an expert financial advisor."},
            {"role": "user", "content": prompt}
        ]
    )

    response = completion.choices[0].message.content

    return response


if __name__ == "__main__":

    end = datetime(2025, 3, 19)
    dates = generate_past_year_weekdays(end)


    save_path_prompt_decide = "prompts/decide/"
    Path(save_path_prompt_decide).mkdir(parents=True, exist_ok=True)
    save_path_prompt_converse = "prompts/converse/"
    Path(save_path_prompt_converse).mkdir(parents=True, exist_ok=True)
    save_path_chatgpt_decide = "results/chatgpt/decide/"
    Path(save_path_chatgpt_decide).mkdir(parents=True, exist_ok=True)
    save_path_chatgpt_converse = "results/chatgpt/converse/"
    Path(save_path_chatgpt_converse).mkdir(parents=True, exist_ok=True)
    save_path_gemini_decide = "results/gemini/decide/"
    Path(save_path_gemini_decide).mkdir(parents=True, exist_ok=True)
    save_path_gemini_converse = "results/gemini/converse/"
    Path(save_path_gemini_converse).mkdir(parents=True, exist_ok=True)



    ########### get prompts
    with open("../qqq_historical_price/historical_qqq_close.json", "r") as f:
        qqq_close = json.load(f)

    for current_date in dates:
        prompt_decide = prompt_handler_past(current_date, qqq_close_prices=qqq_close, summarize_path="../website_extractor/webpage_summarize/", use_summarize=True, decide_mode=True)
        with open(f"{save_path_prompt_decide}{current_date}.txt", "w", encoding="utf-8") as f:
            f.write(prompt_decide)
        prompt_converse = prompt_handler_past(current_date, qqq_close_prices=qqq_close, summarize_path="../website_extractor/webpage_summarize/", use_summarize=True, decide_mode=False)
        with open(f"{save_path_prompt_converse}{current_date}.txt", "w", encoding="utf-8") as f:
            f.write(prompt_converse)





    ########## batch get openai result - decide
    print("batch get openai result - decide...")
    count = 0
    for current_date in dates:
        with open(f"{save_path_prompt_decide}{current_date}.txt", "r", encoding="utf-8") as f:
            prompt = f.read()
        res = response_openai(prompt)
        with open(f"{save_path_chatgpt_decide}{current_date}.txt", "w", encoding="utf-8") as f:
            f.write(res)
        count += 1
        print(f"{count}/{len(dates)}...")


    ########## batch get openai result - converse
    print("batch get openai result - converse...")
    count = 0
    for current_date in dates:
        with open(f"{save_path_prompt_converse}{current_date}.txt", "r", encoding="utf-8") as f:
            prompt = f.read()
        res = response_openai(prompt)
        with open(f"{save_path_chatgpt_converse}{current_date}.txt", "w", encoding="utf-8") as f:
            f.write(res)
        count += 1
        print(f"{count}/{len(dates)}...")





    ########## batch get gemini result - decide
    print("batch get gemini result - decide...")
    count = 0
    for current_date in dates:
        with open(f"{save_path_prompt_decide}{current_date}.txt", "r", encoding="utf-8") as f:
            prompt = f.read()

        res = None
        while not res:
            try:
                res = response_gemini(prompt)
            except Exception as e:
                res = None
                print("Waiting 60 seconds...")
                time.sleep(60)

        with open(f"{save_path_gemini_decide}{current_date}.txt", "w", encoding="utf-8") as f:
            f.write(res)
        count += 1
        print(f"{count}/{len(dates)}...")


    ########## batch get gemini result - converse
    print("batch get gemini result - converse...")
    count = 0
    for current_date in dates:
        with open(f"{save_path_prompt_converse}{current_date}.txt", "r", encoding="utf-8") as f:
            prompt = f.read()

        res = None
        while not res:
            try:
                res = response_gemini(prompt)
            except Exception as e:
                res = None
                print("Waiting 60 seconds...")
                time.sleep(60)

        with open(f"{save_path_gemini_converse}{current_date}.txt", "w", encoding="utf-8") as f:
            f.write(res)
        count += 1
        print(f"{count}/{len(dates)}...")