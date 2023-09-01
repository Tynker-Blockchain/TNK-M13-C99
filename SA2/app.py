from flask import Flask, render_template, request, redirect, session
import os
from time import time
from wallet import Wallet
from wallet import Account
import firebase_admin
from firebase_admin import credentials

def firebaseInitialization():
    cred = credentials.Certificate("config/serviceAccountKey.json")
    firebase_admin.initialize_app(cred, {'databaseURL': 'https://blockchain-wallet-a2812-default-rtdb.firebaseio.com'})
    print("🔥🔥🔥🔥🔥 Firebase Connected! 🔥🔥🔥🔥🔥")

firebaseInitialization()

STATIC_DIR = os.path.abspath('static')

app = Flask(__name__, static_folder=STATIC_DIR)
app.use_static_for_root = True

myWallet =  Wallet()
account = None
# Define allAccounts at empty list 
allAccounts = []

@app.route("/", methods= ["GET", "POST"])
def home():
    # Access allAccounts as global
    global myWallet, account, allAccounts
    isConnected = myWallet.checkConnection()
    balance = "No Balance"
    transactions = None
    
    # Get allAccounts by calling the getAccounts() method on myWallet
    allAccounts = myWallet.getAccounts()
    # Check if account is not None and allAccount exits 
    if(account == None and allAccounts):
        # Select first account from allAccounts and store it in account variable i.e current account
        account = allAccounts[0]

    if(account):
        # Check if data type of account is dict
        if(type(account) == dict):
                # Get use account as dict to get balance and transactions
                balance = myWallet.getBalance(account['address'])
                transactions = myWallet.getTransactions(account['address'])
        # Else
        else:
            # Move this in else block
            balance = myWallet.getBalance(account.address) # This is already in boiler
            transactions = myWallet.getTransactions(account.address) # This is already in boiler

    # Pass allAccounts as allAccounts attribute
    return render_template('index.html', isConnected=isConnected,  
                                        account= account, 
                                        balance = balance, 
                                        transactions = transactions, 
                                        allAccounts =allAccounts)


@app.route("/makeTransaction", methods = ["GET", "POST"])
def makeTransaction():
    global myWallet, account

    sender = request.form.get("senderAddress")
    receiver = request.form.get("receiverAddress")
    amount = request.form.get("amount")

    senderType = 'ganache'
    
    if(sender == account.address):
        senderType = 'newAccountAddress'
        privateKey = account.privateKey

    tnxHash= myWallet.makeTransactions(sender, receiver, amount, senderType, privateKey)
    myWallet.addTransactionHash(tnxHash, sender, receiver, amount)
    return redirect("/")


@app.route("/createAccount", methods= ["GET", "POST"])
def createAccount(): 
    global myWallet, account
    account = Account()
    return redirect("/")

if __name__ == '__main__':
    app.run(debug = True, port=4000)
