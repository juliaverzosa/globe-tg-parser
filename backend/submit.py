from flask import Flask, request, jsonify
import json
import os
import re
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

app = Flask(__name__)

SPREADSHEET_ID = '1jk-hvI6K-DABDtT1hjFdo-dqccUM_jINDv1zhRDBlnk'
RANGE_NAME = 'Sheet1!A2:E'
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']

creds_dict = json.loads(os.environ['GOOGLE_CREDS_JSON'])

credentials = Credentials.from_service_account_info(
    creds_dict,
    scopes=SCOPES
)

service = build("sheets", "v4", credentials=credentials)
sheet = service.spreadsheets()

def extract_data(msg):
    date = re.search(r"Date[:\-]?\s*(\d{4}-\d{2}-\d{2})", msg)
    tech = re.search(r"Technician[:\-]?\s*(.+)", msg)
    dispatch = re.search(r"Dispatch[:\-]?\s*([\w\-]+)", msg)
    order = re.search(r"Order\s*No[:\-]?\s*(\d+)", msg)
    remarks = re.search(r"Remarks[:\-]?\s*(.+?)(?:\n|$)", msg, re.DOTALL)

    return [
        date.group(1).strip() if date else "",
        tech.group(1).strip() if tech else "",
        dispatch.group(1).strip() if dispatch else "",
        order.group(1).strip() if order else "",
        remarks.group(1).strip() if remarks else ""
    ]

@app.route('/', methods=['POST'])
def receive_data():
    data = request.json
    message = data.get("message", "")

    try:
        extracted = extract_data(message)

        sheet.values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE_NAME,
            valueInputOption="USER_ENTERED",
            body={"values": [extracted]}
        ).execute()

        return jsonify({"message": "✅ Submitted!"}), 200
    except Exception as e:
        return jsonify({"message": f"❌ Error: {str(e)}"}), 500

@app.route('/', methods=['GET'])
def home():
    return "✔️ API is working.", 200

