import requests
import pandas as pd
import time
from datetime import datetime, timedelta
from api_key import API_KEY

# Put the Transaction hash you want to trace
TX_HASH = "4ca5ea121cc26854299d02128738612ce948a6fddcbce781925237c50bf9e5ad"
chainShortName="TRON"      #ChainName and protocolName can be found in oklink.com
protocolType="token_20"    #USDT
num_transactions = 10 


# Global storage for transactions
traced_transactions = []

# Function to save transactions to Excel
def save_to_excel(output_file=f"{TX_HASH}.xlsx"):
    """ Saves the collected transactions to an Excel file before exiting. """
    if traced_transactions:
        df = pd.DataFrame(traced_transactions)
        df.to_excel(output_file, index=False)
        print(f"📁 Data saved to {output_file} ✅")
    else:
        print("⚠ No transactions to save.")
    
# Function to fetch transaction details
def get_transaction_details(tx_hash):
    """ Fetch transaction details including sender, receiver, date, token type, and amount. """
    url = f"https://www.oklink.com/api/v5/explorer/transaction/token-transaction-detail?chainShortName={chainShortName}&txId={tx_hash}&limit=1"
    headers = {
        "Ok-Access-Key": API_KEY,
        "Accept": "application/json"
    }

    try:
        response = requests.get(url, headers=headers)
        time.sleep(0.35)  # Rate limit (3 calls per second)

        if response.status_code == 200:
            data = response.json()
 
            if "data" in data and len(data["data"]) > 0:
                token_transfers = data["data"][0].get("tokenTransferDetails", [])

                if token_transfers:
                    transactions = []
                    for transfer in token_transfers:
                        from_address = transfer.get("from", "N/A")
                        to_address = transfer.get("to", "N/A")
                        timestamp = transfer.get("transactionTime", "N/A")
                        token_amount = transfer.get("amount", "N/A")
                        token_type = transfer.get("symbol", "N/A")

                        # Convert timestamp to IST (GMT+5:30) and format as MM/DD/YYYY HH:MM:SS (24-hour)
                        date = "N/A"
                        if timestamp != "N/A":
                            utc_time = datetime.utcfromtimestamp(int(timestamp) / 1000)
                            ist_time = utc_time + timedelta(hours=5, minutes=30)
                            date = ist_time.strftime('%m/%d/%Y %H:%M:%S')

                        transactions.append({
                            "from": from_address,
                            "to": to_address,
                            "date": date,
                            "token_amount": token_amount,
                            "transaction_hash": tx_hash,
                            "token_type": token_type
                        })

                    return transactions  # Return list of transactions
                else:
                    return {"error": "No token transfers found"}
            else:
                return {"error": "Transaction not found"}
        else:
            return {"error": f"API Error {response.status_code}: {response.text}"}
    except Exception as e:
        return {"error": f"Exception: {str(e)}"}

# Function to get the first non-zero outgoing transaction for the same token
def get_next_outgoing_transaction(address, token_type, initial_txid):
    page = 1
    found_incoming = False  # Track when we locate the "in" transaction

    try:
        while True:
            url = f"https://www.oklink.com/api/v5/explorer/address/token-transaction-list?chainShortName={chainShortName}&address={address}&protocolType={protocolType}&limit=50&page={page}"
            headers = {
                "Ok-Access-Key": API_KEY,
                "Accept": "application/json"
            }

            response = requests.get(url, headers=headers)
            time.sleep(0.35)  # Rate limit (3 calls per second)

            if response.status_code == 200:
                data = response.json()
                print(f"🔍 Checking Page {page}...")  

                if "data" in data and len(data["data"]) > 0:
                    transactions = data["data"][0].get("transactionList", [])

                    # Handle missing totalPage
                    total_pages = data["data"][0].get("totalPage", "1")
                    total_pages = int(total_pages) if total_pages.isdigit() else 100  # Default to 100 if empty

                    # Reverse the list to check transactions **backward**
                    transactions.reverse()

                    for tx in transactions:
                        txid = tx.get("txId", "N/A")
                        from_address = tx.get("from", "N/A")
                        to_address = tx.get("to", "N/A")
                        amount = tx.get("amount", "0")
                        transaction_symbol = tx.get("symbol", "N/A")
                        timestamp = int(tx.get("transactionTime", "0"))
                        # block = tx.get("height", "N/A")  # Extract block number

                        print(f"🔹 Checking TXID: {txid}")  

                        # Step 1: Locate the "in" transaction in history
                        if txid == initial_txid:
                            print(f"✅ Found Initial TXID: {initial_txid}")  
                            found_incoming = True
                            continue  

                        # Step 2: If "in" transaction is found, look for the immediate "out"
                        if found_incoming and transaction_symbol == token_type and float(amount) > 0 and from_address == address:
                            ist_time = datetime.utcfromtimestamp(timestamp / 1000) + timedelta(hours=5, minutes=30)
                            date = ist_time.strftime('%m/%d/%Y %H:%M:%S')

                            print(f"✅ Found Outgoing TX: {txid}")  

                            return {
                                "txid": txid,
                                # "block": block,
                                "from": from_address,
                                "to": to_address,
                                "date": date,
                                "amount": amount,
                                "token_type": transaction_symbol
                            }

                    # If `initial_txid` was not found on this page, keep searching
                    if not found_incoming and page < total_pages:
                        print(f"🔄 Moving to Next Page {page + 1}")  
                        page += 1
                    elif found_incoming:
                        print(f"🔄 Found initial transaction but no outgoing transaction yet. Checking Next Page {page + 1}")  
                        page += 1
                    else:
                        print("❌ No valid outgoing transaction found.")  
                        return None 

            else:
                print(f"❌ API Error: {response.status_code}")  
                return None  
    except KeyboardInterrupt:
        print("\n⚠ Interrupted! Saving data before exit...")  
        save_to_excel()
        exit(0)  

# Function to trace 10 transactions and save to Excel
def trace_transactions(tx_hash, num_transactions, output_file="transactions.xlsx"):
    try:
        transaction_details = get_transaction_details(tx_hash)

        if not isinstance(transaction_details, list) or not transaction_details:
            print("Error fetching initial transaction details.")
            return

        to_address = transaction_details[0]["to"]
        token_type = transaction_details[0]["token_type"]
        initial_txid = transaction_details[0]["transaction_hash"]

        for _ in range(num_transactions):
            next_transaction = get_next_outgoing_transaction(to_address, token_type, initial_txid)
            if next_transaction:
                traced_transactions.append(next_transaction)
                print(next_transaction)
                to_address = next_transaction["to"]  
                initial_txid = next_transaction["txid"]
            else:
                print("No further outgoing transactions found.")
                break

        save_to_excel(output_file)
    except KeyboardInterrupt:
        print("\n⚠ Interrupted! Saving data before exit...")  
        save_to_excel(output_file)
        exit(0)  

# Usage
trace_transactions(TX_HASH)
