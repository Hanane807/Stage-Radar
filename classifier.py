# C'est le cerveau du projet. Il envoie le contenu d'un email à Groq et demande si c'est une réponse de stage
from groq import Groq
from config import GROQ_API_KEY

# On crée un client Groq — c'est lui qui va envoyer les requêtes HTTP à l'API Groq
client = Groq(api_key=GROQ_API_KEY)

def is_stage_response(email_subject , email_from , email_body):

    # On construit le prompt qu'on envoie au modèle
    prompt = f"""
    Tu es un assistant qui analyse des emails.
    
    Voici un email reçu :
    - Expéditeur : {email_from}
    - Objet : {email_subject}
    - Contenu : {email_body[:500]}  
    
    Est-ce que cet email est une réponse à une candidature de stage ?
    (acceptation, refus, demande d'entretien, demande d'informations supplémentaires)
    
    Réponds UNIQUEMENT par OUI ou NON, rien d'autre.
    """

    # On envoie la requête HTTP à l'API Groq
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",  
        messages=[
            {"role": "user", "content": prompt}
        ],
        max_tokens=10,  
        temperature=0   
    )

    result = response.choices[0].message.content.strip().upper()
    
    return result == "OUI"