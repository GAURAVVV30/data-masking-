from flask import Flask, request, jsonify, render_template_string
from flask_cors import CORS
from pymongo import MongoClient
import re
import ipaddress

app = Flask(__name__)
CORS(app)  

try:
    client = MongoClient("mongodb://localhost:27017/")
    db = client["data_masking_db"]
    collection = db["masked_data"]
    client.server_info() 
except Exception as e:
    raise SystemExit(f"MongoDB connection failed: {e}")

template = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Data Masking Tool</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px; }
        .container {
            max-width: 600px; margin: 0 auto; padding: 20px;
            background-color: #fff; border-radius: 8px;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        }
        h1 { text-align: center; color: #333; }
        form { display: flex; flex-direction: column; gap: 15px; }
        label { font-weight: bold; color: #333; }
        input {
            padding: 10px; border: 1px solid #ccc;
            border-radius: 4px; font-size: 16px;
        }
        button {
            padding: 10px; background-color: #007bff;
            color: white; border: none; border-radius: 4px;
            cursor: pointer; font-size: 16px;
        }
        button:hover { background-color: #0056b3; }
        #result {
            margin-top: 20px; background-color: #f8f9fa;
            padding: 15px; border-radius: 5px;
            box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        }
        pre {
            background-color: #e9ecef;
            padding: 10px; border-radius: 5px; font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>Data Masking Tool</h1>
        <form id="data-form">
            <label for="email">Email:</label>
            <input type="email" id="email" name="email" required>

            <label for="phone">Phone:</label>
            <input type="text" id="phone" name="phone" required>

            <label for="ip">IP Address:</label>
            <input type="text" id="ip" name="ip" required>

            <button type="submit">Mask Data</button>
        </form>

        <div id="result" style="display: none;">
            <h2>Masked Data</h2>
            <pre id="masked-data"></pre>
        </div>
    </div>

    <script>
        const form = document.getElementById("data-form");
        const resultDiv = document.getElementById("result");
        const maskedDataPre = document.getElementById("masked-data");
        const button = form.querySelector("button");

        form.addEventListener("submit", function(event) {
            event.preventDefault();

            const email = document.getElementById("email").value;
            const phone = document.getElementById("phone").value;
            const ip = document.getElementById("ip").value;

            button.disabled = true;
            button.textContent = "Masking...";

            fetch('/mask', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ email: email, phone: phone, ip: ip })
            })
            .then(response => response.json())
            .then(data => {
                if (data.error) {
                    maskedDataPre.textContent = "Error: " + data.error;
                } else {
                    const maskedData = `
Original Email: ${data.original_email}
Masked Email: ${data.masked_email}

Original Phone: ${data.original_phone}
Masked Phone: ${data.masked_phone}

Original IP: ${data.original_ip}
Masked IP: ${data.masked_ip}
                    `;
                    maskedDataPre.textContent = maskedData;
                }
                resultDiv.style.display = "block";
            })
            .catch(error => {
                maskedDataPre.textContent = "An error occurred: " + error.message;
                resultDiv.style.display = "block";
            })
            .finally(() => {
                button.disabled = false;
                button.textContent = "Mask Data";
            });
        });
    </script>
</body>
</html>
"""
def mask_email(email):
    return re.sub(r'(^[a-zA-Z0-9]{1})(.*)(@[a-zA-Z0-9]+\.[a-z]{2,})', r'\1****\3', email)

def mask_phone(phone):
    digits = re.sub(r'\D', '', phone)
    if len(digits) == 10:
        return f"{digits[:3]}-***-****"
    return "Invalid phone format"

def mask_ip(ip):
    try:
        ipaddress.ip_address(ip)
        return re.sub(r'(\d{1,3}\.\d{1,3}\.\d{1,3})\.\d{1,3}', r'\1.***', ip)
    except ValueError:
        return "Invalid IP format"

@app.route('/')
def index():
    return render_template_string(template)

@app.route('/mask', methods=['POST'])
def mask_data():
    data = request.get_json()
    email = data.get("email")
    phone = data.get("phone")
    ip = data.get("ip")

    if not email or not phone or not ip:
        return jsonify({"error": "All fields are required"}), 400

    masked_email = mask_email(email)
    masked_phone = mask_phone(phone)
    masked_ip = mask_ip(ip)

    if "Invalid" in masked_phone or "Invalid" in masked_ip:
        return jsonify({"error": "Invalid phone or IP format"}), 400

    try:
        collection.insert_one({
            "original_email": email,
            "masked_email": masked_email,
            "original_phone": phone,
            "masked_phone": masked_phone,
            "original_ip": ip,
            "masked_ip": masked_ip
        })
    except Exception as e:
        return jsonify({"error": f"MongoDB insert error: {e}"}), 500

    return jsonify({
        "original_email": email,
        "masked_email": masked_email,
        "original_phone": phone,
        "masked_phone": masked_phone,
        "original_ip": ip,
        "masked_ip": masked_ip
    })

if __name__ == '__main__':
    app.run(debug=True, use_reloader=False)
