# Stage Radar

Un agent intelligent qui surveille ta boîte Gmail et te notifie instantanément sur Telegram dès qu'une réponse de stage est détectée.

## Problème résolu

Pendant la recherche de stage, les réponses des recruteurs se noient dans les autres emails. Stage Radar surveille ta boîte en permanence et t'alerte en temps réel.

## Architecture

1. L'agent vérifie les nouveaux emails toutes les 5 minutes
2. Groq (Llama 3) analyse chaque email et détecte si c'est une réponse de stage
3. Une notification Telegram est envoyée instantanément

## Stack technique

- **Python** — agent principal
- **Gmail API** — lecture des emails via OAuth 2.0
- **Groq API** — classification intelligente avec Llama 3
- **Telegram Bot API** — notifications en temps réel

## Installation

### 1. Cloner le repo
```bash
git clone https://github.com/Hanane807/Stage-Radar.git
cd stage-radar
```

### 2. Installer les dépendances
```bash
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Mac/Linux
pip install -r requirements.txt
```

### 3. Configuration
```bash
cp config.example.py config.py
```
Remplis `config.py` avec tes clés API.

### 4. Gmail API
- Crée un projet sur [Google Cloud Console](https://console.cloud.google.com)
- Active Gmail API
- Télécharge `credentials.json`

### 5. Lancer l'agent
```bash
python agent.py
```

## Sécurité

- L'agent tourne en **local** sur ta machine
- Les emails ne quittent jamais ton ordinateur sauf les 500 premiers caractères envoyés à Groq pour classification
- OAuth 2.0 — aucun mot de passe Gmail stocké
- `credentials.json` et `token.json` exclus du repo via `.gitignore`

## Notification Telegram