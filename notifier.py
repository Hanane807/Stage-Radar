import requests
from config import TELEGRAM_TOKEN, TELEGRAM_CHAT_ID

def send_telegram_notification(email_from, email_subject, email_body, email_link):

    message = f"""
    Nouvelle réponse de stage !

    De : {email_from}

    Objet : {email_subject}

    Aperçu :
{email_body[:300]}...

    [Ouvrir dans Gmail]({email_link})
    """

    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"

    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "disable_web_page_preview": False
    }


    response = requests.post(url, json=payload)

    if response.status_code == 200:
        print(" Notification Telegram envoyée !")
    else:
        print(f" Erreur Telegram : {response.text}")