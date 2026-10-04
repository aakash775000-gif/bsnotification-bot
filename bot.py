import os
import requests
import feedparser
import html
import re

BOT_TOKEN = os.environ.get("BOT_TOKEN", "8634954256:AAGO9pCvHJePDOmTwdGStOew0J9qp_Dg_pg")
CHANNEL_ID = "@bsnotifications"
FEED_URL = "https://bsnotification.blogspot.com/feeds/posts/default?alt=rss"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LAST_POST_FILE = os.path.join(BASE_DIR, "last_posted_id.txt")

def clean_html(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, '', raw_html)
    return html.unescape(cleantext).strip()

def send_telegram_message(title, link, summary):
    message = (
        f"📢 <b>नई अपडेट: {title}</b>\n\n"
        f"📌 <b>विवरण:</b>\n{summary[:250]}...\n\n"
        f"👇 <b>पूरी जानकारी और डायरेक्ट लिंक के लिए क्लिक करें:</b>\n"
        f"🔗 <a href='{link}'>यहाँ क्लिक करें (Click Here)</a>\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"⚡ <i>Fastest Updates on @bsnotifications</i>"
    )
    
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": CHANNEL_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": False
    }
    
    response = requests.post(url, json=payload, timeout=20)
    return response.json()

def check_new_posts():
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    try:
        response = requests.get(FEED_URL, headers=headers, timeout=20)
        feed = feedparser.parse(response.content)
    except Exception as e:
        print(f"Feed load error: {e}")
        return

    if not feed.entries:
        print("Feed empty ya load nahi ho paayi.")
        return

    latest_entry = feed.entries[0]
    post_id = latest_entry.id
    post_title = latest_entry.title
    post_link = latest_entry.link
    post_summary = clean_html(latest_entry.get("summary", latest_entry.get("description", "")))

    try:
        with open(LAST_POST_FILE, "r") as f:
            last_id = f.read().strip()
    except FileNotFoundError:
        last_id = ""

    if post_id != last_id:
        print(f"Naya post mila: {post_title}")
        res = send_telegram_message(post_title, post_link, post_summary)
        if res.get("ok"):
            print("Telegram channel par successfully post ho gaya!")
            with open(LAST_POST_FILE, "w") as f:
                f.write(post_id)
        else:
            print("Telegram error:", res)
    else:
        print("Koi naya post nahi mila. Sab updated hai.")

if __name__ == "__main__":
    check_new_posts()
