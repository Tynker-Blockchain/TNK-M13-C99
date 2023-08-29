# SA1 : Students will set up the firebase to store the newly created addresses
# SA2 : Get all the accounts from firebase and Display on Wallet
# SA3 : Login based Etherum account Creation

from flask import Flask, render_template, request, redirect, session
import os
from time import time
from wallet import Wallet
from wallet import Account
# Import firebase_admin and credentials
import firebase_admin
from firebase_admin import credentials

# Define function firebaseInitialization
def firebaseInitialization():
    # Create cred variable ans use credentials.Certificate() to store key 
    cred = credentials.Certificate("config/serviceAccountKey.json")
    # Call firebase_admin.initialize_app with cred and db url
    firebase_admin.initialize_app(cred, {'databaseURL': 'https://blockchain-wallet-a2812-default-rtdb.firebaseio.com'})
    # Print firebase connected
    print("🔥🔥🔥🔥🔥 Firebase Connected! 🔥🔥🔥🔥🔥")

# Call firebaseInitialization() function
firebaseInitialization()

STATIC_DIR = os.path.abspath('static')

app = Flask(__name__, static_folder=STATIC_DIR)
app.use_static_for_root = True

myWallet =  Wallet()
account = None

@app.route("/", methods= ["GET", "POST"])
def home():
    global myWallet, account
    isConnected = myWallet.checkConnection()
    balance = "No Balance"
    transactions = None

    if(account):
        balance = myWallet.getBalance(account.address)
        transactions = myWallet.getTransactions(account.address)

    return render_template('index.html', isConnected=isConnected,  account= account, balance = balance, transactions = transactions)


@app.route("/makeTransaction", methods = ["GET", "POST"])
def makeTransaction():
    global myWallet, account

    sender = request.form.get("senderAddress")
    receiver = request.form.get("receiverAddress")
    amount = request.form.get("amount")

    senderType = 'ganache'
    if(sender == account.address):
        senderType = 'newAccountAddress'

    tnxHash= myWallet.makeTransactions(sender, receiver, amount, senderType, account.privateKey)
    myWallet.addTransactionHash(tnxHash, sender, receiver, amount)
    return redirect("/")


@app.route("/createAccount", methods= ["GET", "POST"])
def createAccount(): 
    global myWallet, account
    account = Account()
    return redirect("/")

if __name__ == '__main__':
    app.run(debug = True, port=4000)
