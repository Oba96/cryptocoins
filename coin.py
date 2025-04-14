import requests
import schedule
import time
import hashlib
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
import time
from datetime import datetime


# Settings
CHAINS = ["ethereum", "solana", "bsc", "base", "arbitrum"]
VOLUME_THRESHOLD = 10000  # Minimum 24h volume
GAIN_THRESHOLD = 50       # Minimum 24h gain %
EMAIL_SENDER = "jjuniormvila@gmail.com"
EMAIL_RECEIVER = "jjuniormvila@gmail.com"
EMAIL_PASSWORD = "crqecwoxsuzlcofn" # Use app password if Gmail
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

def get_top_tokens(chain):
    url = f"https://api.dexscreener.com/latest/dex/pairs/{chain}"
    response = requests.get(url)
    data = response.json()
    tokens = []

    for token in data['pairs']:
        try:
            volume = float(token['volume']['h24'])
            gain = float(token['priceChange']['h24'])
            liquidity = float(token['liquidity']['usd'])

            if volume > VOLUME_THRESHOLD and gain > GAIN_THRESHOLD:
                tokens.append({
                    "name": token['baseToken']['name'],
                    "symbol": token['baseToken']['symbol'],
                    "volume": volume,
                    "gain": gain,
                    "liquidity": liquidity,
                    "url": token['url']
                })
        except Exception as e:
            continue

    return sorted(tokens, key=lambda x: x['gain'], reverse=True)

def format_email(tokens):
    if not tokens:
        return "No tokens found today that meet the criteria."

    message = "🚀 Top Gainers Today:\n\n"
    for token in tokens:
        message += (
            f"🔹 {token['name']} ({token['symbol']})\n"
            f"📈 Gain: {token['gain']}%\n"
            f"💰 Volume: ${token['volume']:,.0f}\n"
            f"💦 Liquidity: ${token['liquidity']:,.0f}\n"
            f"🔗 Link: {token['url']}\n\n"
        )
    return message

def send_email(subject, body):
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = EMAIL_SENDER
    msg["To"] = EMAIL_RECEIVER

    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(EMAIL_SENDER, EMAIL_PASSWORD)
        server.send_message(msg)

def job():
    print(f"[{datetime.now()}] Running DEX Screener scan...")
    all_tokens = []
    for chain in CHAINS:
        tokens = get_top_tokens(chain)
        all_tokens.extend(tokens)
    email_body = format_email(all_tokens[:10])
    send_email("🚀 DEX Screener Morning Alpha", email_body)
    print("Email sent!")

# Schedule to run at 9 AM every day
if __name__ == "__main__":
    job()

