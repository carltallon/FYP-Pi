from barcode.writer import ImageWriter
import os, barcode
from flask import Flask, send_file

# CORS ( FOR BROWSERS)
from flask_cors import CORS  

# Initialise Flask Application
app = Flask(__name__)

# Enable CORS for all routes of your Flask app
CORS(app)  

# Generate a barcode
def generate_barcode(receiptID, barcode_type):
    # Create barcode class by querying the barcode type
    barcode_class = barcode.get_barcode_class(barcode_type)

    # Create barcode instance by combining the barcode class and the ReceiptID, 
    # & use the image writer to return the parcode as a .png 
    barcode_instance = barcode_class(receiptID, writer=ImageWriter())

    # Define the filename as the ReceiptID
    filename = f'{receiptID}'  
    # Define the filepath of where you want the images to be saved 
    direct_path = '/home/carlt/Documents/FinalYearProject/fyp_venv/barcodes'
    filepath = os.path.join(direct_path, filename) 
    # Save the barcode
    barcode_instance.save(filepath)

    filepath = filepath + ".png"
    return filepath


# Endpoint to fetch receipt barcode
@app.route('/receipts/<receiptID>', methods=['GET'])

# Function used to manipulate receiptID variable which was passed into the API
def get_receipt_barcode(receiptID):

    # Format the expected filename of the receipt
    receiptfilepath = f'{receiptID}.png'
    oldfilepath = '/home/carlt/Documents/FinalYearProject/fyp_venv/barcodes'

    # Format the filepath of where the expected existing barcode should be saved
    filepath = os.path.join(oldfilepath, receiptfilepath)
    
    # Check if the barcode file already exists
    if os.path.exists(filepath):
        # If the barcode exists, Return the barcode file
        print("File exists. Sending..")

        # Send the file using Flask's send_file function, specifiying that it is a png
        return send_file(filepath, mimetype='image/png')
    else:
        # If the barcode doesn't already exist, we need to generate a new one.
        print("File doesn't exist.. Creating")

        # Call on the function with the original receiptID variable, specifying the encoding type.
        receiptbarcode = generate_barcode(receiptID, 'code128')
        print("Sending.. ", receiptID)

        # Now send the file using Flask's send_file function, specifiying that it is a png
        return send_file(receiptbarcode, mimetype='image/png')
    

# Run application
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
