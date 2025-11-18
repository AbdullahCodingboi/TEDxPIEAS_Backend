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
        writer.writerow([
            "Name", 
            "University", 
            "Email", 
            "CNIC", 
            "ContactNumber", 
            "CNIC_Front_Image", 
            "CNIC_Back_Image", 
            "Timestamp"
        ])


@app.route("/")
def home():
    return "TEDx PIEAS Registration Backend is Running!"


@app.route("/register", methods=["POST"])
def register():
    try:
        # Get form data (multipart/form-data)
        name = request.form.get("Name")
        university = request.form.get("University")
        email = request.form.get("Email")
        cnic = request.form.get("CNIC")
        contact = request.form.get("ContactNumber")

        front_img = request.files.get("CNIC_Front_Image")
        back_img = request.files.get("CNIC_Back_Image")

        print("\n✅ Received data:")
        print(f"Name: {name}, University: {university}, Email: {email}, CNIC: {cnic}, Contact: {contact}")

        # Validation
        if not all([name, university, email, cnic, contact, front_img, back_img]):
            print("❌ Missing fields or files.")
            return jsonify({"error": "All fields and both images are required"}), 400

        # ---- Save images ----
        timestamp_str = datetime.now().strftime("%Y%m%d_%H%M%S")

        front_filename = f"{name.replace(' ', '_')}_front_{timestamp_str}.jpg"
        back_filename = f"{name.replace(' ', '_')}_back_{timestamp_str}.jpg"

        front_filepath = os.path.join(UPLOAD_FOLDER, front_filename)
        back_filepath = os.path.join(UPLOAD_FOLDER, back_filename)

        front_img.save(front_filepath)
        back_img.save(back_filepath)

        # ---- Save record to CSV ----
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(CSV_FILE, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                name, university, email, cnic, contact,
                front_filepath, back_filepath, timestamp
            ])

        # ---- Convert CSV to Excel ----
        df = pd.read_csv(CSV_FILE)
        df.to_excel(EXCEL_FILE, index=False)

        print(f"📸 Front image saved at: {front_filepath}")
        print(f"📸 Back image saved at: {back_filepath}")
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
