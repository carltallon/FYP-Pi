# Carl Tallon C20432946 Final Year Project eReceipt
# Code for for receipt and barcode generation. Also includes API code.


# General Imports 
import random
import subprocess
from datetime import datetime
from barcode.writer import ImageWriter
import os, barcode
import calendar


# Firebase Imports
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore

# Flask packages 
from flask import Flask, render_template, request, send_file,redirect, url_for

# Initialise FLask APP
app = Flask(__name__, template_folder='templateFiles', static_folder='staticFiles')

# Initialise Firebase connection
cred = credentials.Certificate("/home/carlt/Documents/FinalYearProject/fyp_venv/FYP-Pi/fyp-c20432946-firebase-adminsdk-s2yt1-f2cef0fa06.json")
firebaseapp = firebase_admin.initialize_app(cred)
db = firestore.client()
collection_ref  = db.collection("Receipts")

# Receipt data arrays
receipt_data = {"items": [], "total": 0.0}
receipt_info = {}

# route for /
@app.route('/', methods=['GET', 'POST'])
def index():
    # Render the HTML file (assuming it's in a folder named 'templates' in the same directory)
    return render_template('index.html')

# Path for displaying receipt data after transaction
@app.route('/generate_receipt_data', methods=['POST'])
def generate_receipt_data():

    handlereceiptinfo(receipt_info)
    
    # Redirect and display receipt info
    return redirect(url_for('display_receipt', receiptID=receipt_info['Receipt ID']))

# Route to update items list
@app.route('/update_items', methods=['POST'])
def update_items():

    global receipt_data
    global receipt_info

    data = request.get_json()

    # Get the current date and time
    current_date = datetime.now()

    # Extract the month from the current date
    current_month = current_date.month

    # Convert the numerical month to its corresponding name
    month_name = calendar.month_name[current_month]

    # Access items and total from the received JSON data
    items = data.get('items', [])
    total = data.get('total', 0.0)

    # Generate a unique receipt ID between 1 and 250,000
    receipt_id = generate_receipt_id()

    shopinformation = "Test Shop Location"

    receipt_info = {
        "Date": firestore.SERVER_TIMESTAMP,
        "Price": total,
        "Items": items,
        "Shop Location": shopinformation,
        "Receipt ID": receipt_id,
        "Month": month_name
    }

    return "Items updated successfully", 200 

# Route to display receipt info
@app.route('/display_receipt/<receiptID>', methods=['GET', 'POST'])
def display_receipt(receiptID):

    today_date = datetime.now().strftime("%d-%m-%Y")

    return render_template('receiptinfo.html', Date=today_date, Amount=receipt_info["Price"], Location=receipt_info["Shop Location"], ReceiptID=receiptID)


# API SECTION
# Endpoint to fetch receipt barcode
@app.route('/receipts/<receiptID>', methods=['GET'])
# Function used to manipulate receiptID variable which was passed into the API
def get_receipt_barcode(receiptID):

    # Format the expected filename of the receipt
    receiptfilepath = f'{receiptID}.png'
    oldfilepath = '/home/carlt/Documents/FinalYearProject/fyp_venv/FYP-Pi/barcodes'

    # Format the filepath of where the expected existing barcode should be saved
    filepath = os.path.join(oldfilepath, receiptfilepath)
    
    # Check if the barcode file already exists
    if os.path.exists(filepath):
        # If the barcode exists, Return the barcode file
        print("File exists. Sending..")

        # Send the file using Flask's send_file function, specifiying that it is a png
        return send_file(filepath, mimetype='image/png')
    
    else:
        # If the barcode doesn't already exist, need to generate a new one.
        print("File doesn't exist.. Creating")

        # Call on the function with the original receiptID variable
        receiptbarcode = generate_barcode(receiptID, 'code128')
        print("Sending.. ", receiptID)

        # Now send the file using Flask's send_file function
        return send_file(receiptbarcode, mimetype='image/png')
    
# Generate a barcode
def generate_barcode(receiptID, barcode_type):
    # Create barcode class by querying the barcode type
    barcode_class = barcode.get_barcode_class(barcode_type)

    # Create barcode instance by combining the barcode class and the ReceiptID, 
    # & use the image writer to return the parcode as a .png 
    barcode_instance = barcode_class(receiptID, writer=ImageWriter())

    # Define the filename 
    filename = f'{receiptID}'  

    # Define the filepath 
    direct_path = '/home/carlt/Documents/FinalYearProject/fyp_venv/FYP-Pi/barcodes'

    filepath = os.path.join(direct_path, filename) 
    # Save the barcode
    barcode_instance.save(filepath)

    filepath = filepath + ".png"
    return filepath

# Generate receipt ID
def generate_receipt_id():
    # Generate a random receipt ID
    receipt_id = str(random.randint(1, 2500000))
    
    # Check if the receipt ID is unique
    while not is_receipt_id_unique(receipt_id):
        receipt_id = str(random.randint(1, 2500000))
    
    return receipt_id

# Ensure ID is unique
def is_receipt_id_unique(receipt_id):

    # Query the collection to check if the receipt ID already exists
    query = collection_ref.where('receipt_id', '==', receipt_id).limit(1).stream()
    
    return not any(query)

# NFC & Firebase handler
def handlereceiptinfo(receipt_info):

    try:
        firebaseupload(receipt_info)
        
        handleNFC(receipt_info)
    # Error handling  
    except Exception as e:
        print(f'Error adding document: {e}')
    
# Function to upload receipt details to firebase
def firebaseupload(receipt_info):

    data = {
        'Amount': receipt_info["Price"],
        'Date': receipt_info["Date"],
        'Location': receipt_info["Shop Location"],
        'ReceiptID': receipt_info["Receipt ID"],
        'Items': receipt_info['Items'],
        'Month': receipt_info['Month']
    }

    try:
        # Add a new document with an auto-generated ID
        doc_ref = collection_ref.add(data)
        print(f'Document added with ID: {doc_ref}')
    except Exception as e:
        print(f'Error adding document: {e}')

# NFC function, sends receipt ID to NFC device
def NFC_tag(ndeffilename):

    # Command to pass NDEF filename using NFC
    NFC_command = f"/home/carlt/Documents/FinalYearProject/fyp_venv/nfcpy/examples/tagtool.py -l --device ttyS0 emulate /home/carlt/Documents/FinalYearProject/fyp_venv/FYP-Pi/ndef/{ndeffilename} tt3"

    try:
        # RUN COMMAND
        result = subprocess.run(NFC_command, shell=True, capture_output=True, text=True)

        print(result.stdout)
        if result.stderr:
            print(result.stderr)
    # ERROR HANDLING
    except subprocess.CalledProcessError as e:
        print("NFC COMMAND ERROR")
        if e.stdout:
            print(e.stdout)
        if e.stderr:
            print(e.stderr)

# Function to convert receipt ID to NDEF
def convertndef(ReceiptID):

    conversion_command = f"ndeftool text '{ReceiptID}' save /home/carlt/Documents/FinalYearProject/fyp_venv/FYP-Pi/ndef/{ReceiptID}.ndef"
    filename = ReceiptID + ".ndef"

    try:
        result = subprocess.run(conversion_command, shell=True, capture_output=True, text=True, check=True)
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


# This funcion converts to ndef, and then passes ndef filename to NFC function
def handleNFC(receipt_info):

    print("Converting to NDEF.")

    ReceiptID = receipt_info["Receipt ID"]

    ndeffilename = convertndef(ReceiptID) 

    try:
        # Write to NFc
        NFC_tag(ndeffilename)
        print("Transaction complete.")
    except Exception as e:
        print(e)
    
# Run application
if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
