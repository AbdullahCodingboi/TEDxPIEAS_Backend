from flask import Flask, request, jsonify
import csv
import os
import pandas as pd
from datetime import datetime

app = Flask(__name__)

# Folder and file setup
DATA_FOLDER = "data"
UPLOAD_FOLDER = os.path.join(DATA_FOLDER, "uploads")
CSV_FILE = os.path.join(DATA_FOLDER, "registrations.csv")
EXCEL_FILE = os.path.join(DATA_FOLDER, "registrations.xlsx")

os.makedirs(DATA_FOLDER, exist_ok=True)
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize CSV with headers if not exists
if not os.path.exists(CSV_FILE):
    with open(CSV_FILE, mode="w", newline="", encoding="utf-8") as file:
        writer = csv.writer(file)
        writer.writerow(["Name", "Email", "Phone", "CNIC", "University", "CardImagePath", "Timestamp"])


@app.route("/")
def home():
    return "TEDx PIEAS Registration Backend is Running!"


@app.route("/register", methods=["POST"])
def register():
    try:
        # Get form data (multipart/form-data)
        name = request.form.get("name")
        email = request.form.get("email")
        phone = request.form.get("phone")
        cnic = request.form.get("cnic")
        university = request.form.get("university")
        file = request.files.get("university_card_picture")

        print("\n✅ Received data:")
        print(f"Name: {name}, Email: {email}, Phone: {phone}, CNIC: {cnic}, University: {university}")

        # Validation
        if not all([name, email, phone, cnic, university, file]):
            print("❌ Missing fields or file.")
            return jsonify({"error": "All fields (including image) are required"}), 400

        # Save image file
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{name.replace(' ', '_')}_{timestamp_str}.jpg"
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)

        # Save record to CSV
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(CSV_FILE, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([name, email, phone, cnic, university, filepath, timestamp])

        # Convert CSV to Excel
        df = pd.read_csv(CSV_FILE)
        df.to_excel(EXCEL_FILE, index=False)

        print(f"📸 Image saved at: {filepath}")
        print("✅ Registration saved successfully!")

        return jsonify({"message": "Registration successful!"}), 200

    except Exception as e:
        print("🔥 Error in /register:", e)
        return jsonify({"error": str(e)}), 500


@app.route("/view-registrations", methods=["GET"])
def view_registrations():
    try:
        df = pd.read_csv(CSV_FILE)
        data = df.to_dict(orient="records")
        return jsonify(data), 200
    except FileNotFoundError:
        return jsonify({"error": "No registrations found yet."}), 404


if __name__ == "__main__":
    app.run(debug=True)
