from flask import Flask, request
import json
from datetime import datetime

app = Flask(__name__)

@app.route('/stripe-webhook', methods=['POST'])
def stripe_webhook():
    event = request.get_json()
    event_type = event.get('type', '')
    session = event.get('data', {}).get('object', {})

    if event_type in ['checkout.session.completed', 'checkout.session.expired']:
        data = {
            "id": session.get("id"),
            "email": session.get("customer_email"),
            "amount": session.get("amount_total", 0) / 100,
            "statut": "paid" if event_type == "checkout.session.completed" else "expired",
            "produit": session.get("metadata", {}).get("produit", "inconnu"),
            "phone": session.get("metadata", {}).get("phone", "—"),
            "date": datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
        }

        try:
            with open("sessions.json", "r", encoding="utf-8") as f:
                existing = json.load(f)
        except:
            existing = []

        existing.append(data)

        with open("sessions.json", "w", encoding="utf-8") as f:
            json.dump(existing, f, indent=2, ensure_ascii=False)

        print("✅ Nouvelle session enregistrée :", data)

    return '', 200
@app.route('/sessions', methods=['GET'])
def get_sessions():
    try:
        with open("sessions.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            return jsonify(data)
    except FileNotFoundError:
        return jsonify([])  # Retourne une liste vide si le fichier n'existe pas


if __name__ == '__main__':
    app.run(port=5000)
