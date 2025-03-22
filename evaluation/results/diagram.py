import matplotlib.pyplot as plt
import pandas as pd
import json
import glob
from datetime import datetime, timedelta
from pathlib import Path
import plotly.graph_objects as go


with open("../qqq_historical_price/historical_qqq_open.json", "r") as f:
    qqq_data = json.load(f)

def get_action(fn):
    with open(fn) as f:
        txt = f.read()
    txt = txt.strip().lower()
    if "hold" in txt:
        return "hold"
    elif "buy" in txt:
        return "buy"
    elif "sell" in txt:
        return "sell"
    else:
        raise Exception("unknown action")


def get_analysis(fn):
    with open(fn, "r", encoding="utf-8") as f:
        txt = f.read()
    return txt


def generate_actions(decide_files_path, converse_files_path):
    prev_action = "sell"
    fund = 100000
    holdings = 0

    taken_actions = []

    check_dates = glob.glob(decide_files_path + "/*.txt")
    check_dates = list(map(lambda x: Path(x).stem, check_dates))
    check_dates = list(filter(
        lambda x: (datetime.strptime(x, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d") in qqq_data,
        check_dates
    ))
    check_dates.sort()

    dates = []
    open_values = []
    actions = []
    analyses = []

    for d in check_dates:
        next_d = (datetime.strptime(d, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
        p = qqq_data[next_d]
        cur_action = get_action(f"{decide_files_path}{d}.txt")
        cur_analysis = get_analysis(f"{converse_files_path}{d}.txt")
        analyses.append(cur_analysis)

        if cur_action == "buy":
            if prev_action == "sell":
                holdings = fund // p
                fund = fund % p
                prev_action = cur_action
                taken_actions.append((cur_action, next_d))
        elif cur_action == "sell":
            if prev_action == "buy":
                fund += p*holdings
                holdings = 0
                prev_action = cur_action
                taken_actions.append((cur_action, next_d))

        dates.append(next_d)
        open_values.append(p)
        actions.append(cur_action)

        fund = round(fund, 2)
        print(f"date: {d} - action: {cur_action} - holdings: {holdings} - fund: {fund}")

    return {
        "taken_actions": taken_actions,
        "dates": dates,
        "open_values": open_values,
        "actions": actions,
        "analyses": analyses,
    }


def draw_diagram(taken_actions, dates, open_values, actions, show_days=30, title="QQQ Stock Price (Opening Values)"):

    # Convert to DataFrame and sort by date
    show_values = list(zip(dates, open_values))[-show_days:]
    df = pd.DataFrame(show_values, columns=["Date", "USD"])
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date")

    # Convert action dates to match the dataframe format

    plt.figure(figsize=(12, 6))
    plt.plot(df["Date"].astype(str), df["USD"], marker='o', linestyle='-')

    # Add annotations for buy/sell points
    for action, date in taken_actions:
        if date in df["Date"].dt.strftime('%Y-%m-%d').values:
            value = df.loc[df["Date"].dt.strftime('%Y-%m-%d') == date, "USD"].values[0]
            plt.annotate(action.capitalize(),
                         (date, value),
                         textcoords="offset points",
                         xytext=(0, 10),  # Offset text slightly above the point
                         ha='center',
                         fontsize=10,
                         color="red" if action == "sell" else "green",
                         fontweight="bold",
                         arrowprops=dict(arrowstyle="->", color="black"))

    # Formatting
    plt.xlabel("Date")
    plt.ylabel("US Dollar ($)")
    plt.title(title)
    plt.xticks(df["Date"].astype(str), df["Date"].dt.strftime('%Y-%m-%d'), rotation=45, ha='right')
    # plt.grid()
    plt.subplots_adjust(bottom=0.2)  # Ensure date labels are fully visible

    # Show plot
    # plt.show()

    plt.savefig(f"{title}.png")


# Break long analysis into multiple lines (every ~12 words)
def wrap_text(text, words_per_line=12):
    words = text.split()
    return "<br>".join(
        [" ".join(words[i:i+words_per_line]) for i in range(0, len(words), words_per_line)]
    )


def draw_interactive_diagram_with_analysis_and_action(taken_actions, dates, open_values, analyses, model_actions, show_days=30, title="QQQ Stock Price (Opening Values)"):

    # Create dataframe with all relevant columns
    show_values = list(zip(dates, open_values, analyses, model_actions))[-show_days:]
    df = pd.DataFrame(show_values, columns=["Date", "USD", "Analysis", "Action"])
    df["Date"] = pd.to_datetime(df["Date"])
    df = df.sort_values("Date")

    # Base price line with hover showing analysis + action
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df["Date"],
        y=df["USD"],
        mode='lines+markers',
        name="Opening Price",
        line=dict(color='royalblue'),
        marker=dict(size=6),
        text=[
            f"Action: {action}<br>Analysis: {wrap_text(analysis)}"
            for action, analysis in zip(df["Action"], df["Analysis"])
        ],
        hovertemplate="<b>Date:</b> %{x|%Y-%m-%d}<br>" +
                      "<b>Price:</b> $%{y}<br>" +
                      "%{text}<extra></extra>"
    ))

    # Add buy/sell annotations as bold labels
    for action, date in taken_actions:
        match = df[df["Date"].dt.strftime('%Y-%m-%d') == date]
        if not match.empty:
            value = match["USD"].values[0]
            fig.add_trace(go.Scatter(
                x=[date],
                y=[value],
                mode='markers+text',
                name=action.capitalize(),
                marker=dict(color='green' if action == "buy" else 'red', size=10, symbol='circle'),
                text=[action.upper()],
                textposition="top center",
                textfont=dict(color='black', size=12, family="Arial Black"),
                hoverinfo='skip'  # Prevent duplicate hover
            ))

    # Layout
    fig.update_layout(
        title=title,
        xaxis_title="Date",
        yaxis_title="USD ($)",
        xaxis=dict(tickformat="%Y-%m-%d", tickangle=45),
        hovermode='x unified',
        margin=dict(b=100)
    )

    # Export as HTML
    fig.write_html(f"{title}.html")

    # Optional for local viewing
    # fig.show()


if __name__ == "__main__":

    decide_path = f"results/chatgpt/decide/"
    converse_path = f"results/chatgpt/converse/"
    actions_result = generate_actions(decide_path, converse_path)

    taken_actions = actions_result["taken_actions"]
    dates = actions_result["dates"]
    open_values = actions_result["open_values"]
    actions = actions_result["actions"]
    analyses = actions_result["analyses"]

    draw_diagram(taken_actions, dates, open_values, actions, show_days=29, title="QQQ Stock Price (Opening Values) - ChatGPT-4o Action")
    draw_interactive_diagram_with_analysis_and_action(taken_actions, dates, open_values, analyses, actions, show_days=60, title="QQQ Stock Price (Opening Values) - ChatGPT-4o Action")


    decide_path = f"results/gemini/decide/"
    converse_path = f"results/gemini/converse/"
    actions_result = generate_actions(decide_path, converse_path)

    taken_actions = actions_result["taken_actions"]
    dates = actions_result["dates"]
    open_values = actions_result["open_values"]
    actions = actions_result["actions"]
    analyses = actions_result["analyses"]

    draw_diagram(taken_actions, dates, open_values, actions, show_days=29, title="QQQ Stock Price (Opening Values) - gemini-2.0-flash Action")
    draw_interactive_diagram_with_analysis_and_action(taken_actions, dates, open_values, analyses, actions, show_days=60, title="QQQ Stock Price (Opening Values) - emini-2.0-flash Action")