from flask import Flask, request, jsonify
import json
from datetime import datetime
import os

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
        except FileNotFoundError:
            existing = []

        existing.append(data)

        with open("sessions.json", "w", encoding="utf-8") as f:
            json.dump(existing, f, indent=2, ensure_ascii=False)

        print("✅ Nouvelle session enregistrée :", data)

    return '', 200

@app.route('/sessions', methods=['GET'])
def get_sessions():
    if not os.path.exists("sessions.json"):
        return jsonify([])
    try:
        with open("sessions.json", "r", encoding="utf-8") as f:
            data = json.load(f)
            return jsonify(data)
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
