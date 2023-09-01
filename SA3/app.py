
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
allAccounts = []

@app.route("/", methods= ["GET", "POST"])
def home():
    global myWallet, account, allAccounts
    isConnected = myWallet.checkConnection()
    balance = "No Balance"
    transactions = None
    
    allAccounts = myWallet.getAccounts()
    if(account == None and allAccounts):
        account = allAccounts[0]

    if(account):
        if(type(account) == dict):
                balance = myWallet.getBalance(account['address'])
                transactions = myWallet.getTransactions(account['address'])
        else:
            balance = myWallet.getBalance(account.address) 
            transactions = myWallet.getTransactions(account.address) 

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
    # Create privateKey as None
    privateKey = None

    # Check is type of account variable is dict
    if(type(account) == dict):
       # Do same what we have done in else but access account info as keys
       if(sender == account['address']):
            senderType = 'newAccountAddress'
            privateKey = account['privateKey']
    else:
        # Move this to else block
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

# Define /changeAccount path
@app.route("/changeAccount", methods= ["GET", "POST"])
# Define changeAccount() function
def changeAccount(): 
    # Access account and allAccounts as global
    global account, allAccounts
    
    # Access the address argument sent on the path ans store it in newAccountAddress at int value
    newAccountAddress = int(request.args.get("address"))
    # Select the account with newAccountAddress from allAccounts and store it in account variable
    account = allAccounts[newAccountAddress]
    # redirect to "/"
    return redirect("/")

if __name__ == '__main__':
    app.run(debug = True, port=4000)
