import requests
from config import PUSHOVER_USER_KEY, PUSHOVER_API_TOKEN
from logger import logger

def send_pushover_alert(message):
    """Send a push notification via Pushover."""
    try:
        res = requests.post("https://api.pushover.net/1/messages.json", data={
            "token": PUSHOVER_API_TOKEN,
            "user": PUSHOVER_USER_KEY,
            "message": message,
            "title": "Job Alert"
        })

        if res.status_code == 200:
            logger.info("✅ Alert sent via Pushover.")
        else:
            logger.warning(f"❌ Alert failed. Status: {res.status_code} | {res.text}")
    except Exception as e:
        logger.error(f"❌ Exception while sending alert: {e}")
