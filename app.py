from flask import Flask, render_template, request
import yfinance as yf
import datetime
import matplotlib.pyplot as plt
import io
import base64
import feedparser

app = Flask(__name__)

COMPANIES = {
    "RELIANCE": "RELIANCE.BO",
    "TCS": "TCS.BO",
    "INFY": "INFY.BO",
    "HDFC BANK": "HDFCBANK.BO",
    "ITC": "ITC.BO"
}

def create_price_chart(hist):
    plt.figure(figsize=(6,3))
    plt.plot(hist.index, hist['Close'], marker='o')
    plt.title('Last 5 Days - Close Price')
    plt.xlabel('Date')
    plt.ylabel('₹ Price')
    plt.grid(True)

    img = io.BytesIO()
    plt.tight_layout()
    plt.savefig(img, format='png')
    img.seek(0)
    chart_url = base64.b64encode(img.getvalue()).decode()
    plt.close()
    return chart_url

def get_company_news(name):
    url = "https://www.moneycontrol.com/rss/MCtopnews.xml"
    feed = feedparser.parse(url)
    company_news = [entry for entry in feed.entries if name.lower() in entry.title.lower()]
    return company_news[:5]

@app.route("/", methods=["GET", "POST"])
def index():
    selected = request.form.get("company") if request.method == "POST" else "RELIANCE"
    ticker = COMPANIES.get(selected, "RELIANCE.BO")

    stock = yf.Ticker(ticker)
    info = stock.info
    hist = stock.history(period="5d")
    chart_url = create_price_chart(hist)
    news = get_company_news(selected)

    return render_template("index.html", companies=COMPANIES.keys(), selected=selected, info=info, hist=hist, chart_url=chart_url, news=news)

@app.route("/admin", methods=["GET", "POST"])
def admin():
    msg = ""
    if request.method == "POST":
        name = request.form["name"].upper()
        symbol = request.form["symbol"]
        COMPANIES[name] = symbol
        msg = f"Added {name} with symbol {symbol}"
    return render_template("admin.html", companies=COMPANIES, message=msg)

if __name__ == "__main__":
    app.run(debug=True)
