import random
from datetime import datetime

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# Flask packages 
from flask import Flask, render_template, request, redirect, url_for,session

# Initialise FLask APP
app = Flask(__name__, template_folder='templateFiles', static_folder='staticFiles')

# Initialise Firebase connection
cred = credentials.Certificate("fyp-c20432946-firebase-adminsdk-lsyrj-812580293a.json")
firebaseapp = firebase_admin.initialize_app(cred)
db = firestore.client()
collection_ref  = db.collection("Receipts")


#Import NFC file
from NFC import writeNFC

@app.route('/', methods=['GET', 'POST'])
def index():
    # Render the HTML file (assuming it's in a folder named 'templates' in the same directory)
    return render_template('index.html')

@app.route('/generate_receipt_data', methods=['POST'])
def generate_receipt_data():
    # Generate a unique receipt ID between 1 and 250,000
    receipt_id = generate_receipt_id()

    # Generate random price below 100
    price = round(random.uniform(1, 100), 2)

    # Get today's date
    today_date = datetime.now().strftime("%d-%m-%Y")

    # List of random shop locations in Ireland
    shop_locations = ["Dublin", "Cork", "Galway", "Limerick", "Waterford", "Belfast", "Derry", "Kilkenny", "Sligo", "Athlone"]
    shop_names = ["Gala", "Centra", "Tesco", "Supervalu", "Lidl"]
    # Randomly choose a shop location
    shop_location = random.choice(shop_locations)
    shop_name = random.choice(shop_names)

    shopinformation = shop_name + " " + shop_location

    receipt_info = {
        "Date": firestore.SERVER_TIMESTAMP,
        "Price": price,
        "Shop Location": shopinformation,
        "Receipt ID": receipt_id
    }

    handlereceiptinfo(receipt_info)
    return render_template('receiptinfo.html', Date = today_date, Amount = receipt_info["Price"], Location = receipt_info["Shop Location"], ReceiptID = receipt_info["Receipt ID"])


def generate_receipt_id():
    # Generate a random receipt ID
    receipt_id = str(random.randint(1, 250000))
    
    # Check if the receipt ID is unique
    while not is_receipt_id_unique(receipt_id):
        receipt_id = str(random.randint(1, 250000))
    
    return receipt_id


def is_receipt_id_unique(receipt_id):

    # Query the collection to check if the receipt ID already exists
    query = collection_ref.where('receipt_id', '==', receipt_id).limit(1).stream()
    
    # If the query result is empty, the receipt ID is unique
    return not any(query)

def handlereceiptinfo(receipt_info):

    try:
        #firebaseupload(receipt_info)
        print(f'Document added with ID: ')

        # Add a new document with an auto-generated ID
        read_nfc(receipt_info)
        
    except Exception as e:
        print(f'Error adding document: {e}')
    

def firebaseupload(receipt_info):

    data = {
        'Amount': receipt_info["Price"],
        'Date': receipt_info["Date"],
        'Location': receipt_info["Shop Location"],
        'ReceiptID': receipt_info["Receipt ID"],
    }

    try:
    # Add a new document with an auto-generated ID
        doc_ref = collection_ref.add(data)
        print(f'Document added with ID: {doc_ref}')
    except Exception as e:
        print(f'Error adding document: {e}')

def read_nfc(receipt_info):

    print("Starting NFC transaction....")

    ReceiptID = receipt_info["Receipt ID"]

    try:
        print(ReceiptID)
        # Write to NFC
        writeNFC(ReceiptID)
        print("Transaction complete!!")
    except Exception as e:
        print(e)

# Run application
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001)
