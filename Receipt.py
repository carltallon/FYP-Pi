import random
import subprocess
from datetime import datetime

import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# Flask packages 
from flask import Flask, render_template, request, redirect, url_for,session

# Initialise FLask APP
app = Flask(__name__, template_folder='templateFiles', static_folder='staticFiles')

# Initialise Firebase connection
cred = credentials.Certificate("fyp-c20432946-firebase-adminsdk-s2yt1-f2cef0fa06.json")
firebaseapp = firebase_admin.initialize_app(cred)
db = firestore.client()
collection_ref  = db.collection("Receipts")


@app.route('/', methods=['GET', 'POST'])
def index():
    # Render the HTML file (assuming it's in a folder named 'templates' in the same directory)
    return render_template('index.html')

@app.route('/generate_receipt_data', methods=['POST'])
def generate_receipt_data():
    # Generate a unique receipt ID between 1 and 250,000

    receipt_id = generate_receipt_id()
    # Get today's dat
    today_date = datetime.now().strftime("%d-%m-%Y")

    shopinformation = request.form['location']
    price = request.form['amount']

    receipt_info = {
        "Date": firestore.SERVER_TIMESTAMP,
        "Price": price,
        "Shop Location": shopinformation,
        "Receipt ID": receipt_id
    }

    flaskhandler(receipt_info)
    handlereceiptinfo(receipt_info)
    # Render the template first
    return render_template('receiptinfo.html', Date=today_date, Amount=receipt_info["Price"], Location=receipt_info["Shop Location"], ReceiptID=receipt_info["Receipt ID"])


    

   
def flaskhandler(receipt_info):
    # Get today's dat
    today_date = datetime.now().strftime("%d-%m-%Y")

    # Render the template first
    template_result = render_template('receiptinfo.html', Date=today_date, Amount=receipt_info["Price"], Location=receipt_info["Shop Location"], ReceiptID=receipt_info["Receipt ID"])

    # Use the template_result variable as needed (e.g., return it to the client)
    return template_result

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
        firebaseupload(receipt_info)

        # Add a new document with an auto-generated ID
        handleNFC(receipt_info)
        
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



def NFC_tag(ndeffilename):

    NFC_command = f"../nfcpy/examples/tagtool.py -l --device ttyS0 emulate ndef/{ndeffilename} tt3"
    print("Use your device to collect your Receipt ID")

    try:
        result = subprocess.run(NFC_command, shell=True, capture_output=True, text=True, check=True)

        print("Command Output = ")
        print(result.stdout)
        if result.stderr:
            print(result.stderr)
    except subprocess.CalledProcessError as e:
        print("NFC COMMAND ERROR")
        if e.stdout:
            print(e.stdout)
        if e.stderr:
            print(e.stderr)

def convertndef(ReceiptID):

    conversion_command = f"ndeftool text '{ReceiptID}' save ndef/{ReceiptID}.ndef"
    filename = ReceiptID + ".ndef"

    try:
        result = subprocess.run(conversion_command, shell=True, capture_output=True, text=True, check=True)

        print("Ndef Command Output = ")
        print(result.stdout)


        if result.stderr:
            print(result.stderr)


    except subprocess.CalledProcessError as e:
        print("NDEF COMMAND ERROR")
        if e.stdout:
            print(e.stdout)
        if e.stderr:
            print(e.stderr)

    return filename


def handleNFC(receipt_info):

    print("Converting to NDEF....")

    ReceiptID = receipt_info["Receipt ID"]

    ndeffilename = convertndef(ReceiptID) 

    try:
        # Write to NFc
        NFC_tag(ndeffilename)
        print("Transaction complete!!")
    except Exception as e:
        print(e)
    
# Run application
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5001, debug=True)


