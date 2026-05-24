import os
import time
import base64
from datetime import datetime

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from config import GMAIL_SCOPES, CHECK_INTERVAL_MINUTES
from classifier import is_stage_response
from notifier import send_telegram_notification

def get_gmail_service():

    creds = None

    # Si token.json existe déjà → on l'utilise directement (pas besoin de réautoriser)
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", GMAIL_SCOPES)

    # Si pas de token ou token expiré → on redemande l'autorisation
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())  # On rafraîchit le token automatiquement
        else:
            # Ouvre le navigateur pour que tu autorises l'accès Gmail
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", GMAIL_SCOPES)
            creds = flow.run_local_server(port=0)

        # On sauvegarde le token pour la prochaine fois
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    # On retourne le service Gmail prêt à utiliser
    return build("gmail", "v1", credentials=creds)


def get_new_emails(service, last_check_time):

    # On convertit le timestamp en format que Gmail comprend
    query = f"after:{int(last_check_time)} is:unread"

    # Requête à l'API Gmail pour récupérer les IDs des emails
    results = service.users().messages().list(
        userId="me",
        q=query
    ).execute()

    messages = results.get("messages", [])
    emails = []

    for msg in messages:
        # Pour chaque ID on récupère le contenu complet de l'email
        msg_data = service.users().messages().get(
            userId="me",
            id=msg["id"],
            format="full"
        ).execute()

        # On extrait les headers (expéditeur, objet...)
        headers = msg_data["payload"]["headers"]
        email_from = next((h["value"] for h in headers if h["name"] == "From"), "Inconnu")
        email_subject = next((h["value"] for h in headers if h["name"] == "Subject"), "Sans objet")

        # On extrait le corps de l'email
        email_body = ""
        if "parts" in msg_data["payload"]:
            for part in msg_data["payload"]["parts"]:
                if part["mimeType"] == "text/plain":
                    data = part["body"].get("data", "")
                    email_body = base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
                    break
        
        # Le lien direct vers l'email dans Gmail
        email_link = f"https://mail.google.com/mail/u/0/#inbox/{msg['id']}"

        emails.append({
            "from": email_from,
            "subject": email_subject,
            "body": email_body,
            "link": email_link
        })

    return emails

def save_last_check(timestamp):
    """Sauvegarde le timestamp dans un fichier"""
    with open("last_check.txt", "w") as f:
        f.write(str(timestamp))

def load_last_check():
    """Charge le timestamp depuis le fichier"""
    if os.path.exists("last_check.txt"):
        with open("last_check.txt", "r") as f:
            return float(f.read())
    # Si le fichier n'existe pas → première fois → on repart d'il y a 24h
    return time.time() - (24 * 60 * 60)

def run_agent():

    print("Stage Radar démarré !")
    print(f"Vérification toutes les {CHECK_INTERVAL_MINUTES} minutes\n")

    # On se connecte à Gmail
    service = get_gmail_service()
    print("Connecté à Gmail !\n")

    last_check_time = load_last_check()

    while True:
        print(f"[{datetime.now().strftime('%H:%M:%S')}] Vérification des emails...")

        try:
            # On récupère les nouveaux emails
            emails = get_new_emails(service, last_check_time)
            print(f"  → {len(emails)} nouvel(s) email(s) trouvé(s)")

            for email in emails:
                print(f"  → Analyse : {email['subject'][:50]}...")

                # On demande à Groq si c'est une réponse de stage
                if is_stage_response(email["subject"], email["from"], email["body"]):
                    print(f"RÉPONSE DE STAGE DÉTECTÉE !")
                    send_telegram_notification(
                        email["from"],
                        email["subject"],
                        email["body"],
                        email["link"]
                    )

            last_check_time = time.time()
            save_last_check(last_check_time)

        except Exception as e:
            print(f"Erreur : {e}")

        print(f"Prochaine vérification dans {CHECK_INTERVAL_MINUTES} minutes\n")
        time.sleep(CHECK_INTERVAL_MINUTES * 60)


if __name__ == "__main__":
    run_agent()
