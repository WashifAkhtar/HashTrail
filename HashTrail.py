import requests
import pandas as pd
import time
from datetime import datetime, timedelta
from api_key import API_KEY

# Put the Transaction hash you want to trace
TX_HASH = "4ca5ea121cc26854299d02128738612ce948a6fddcbce781925237c50bf9e5ad"
chainShortName = "TRON"  # Chain name (e.g., TRON, ETH, BTC)
protocolType = "token_20"  # USDT

# Global storage for transactions
traced_transactions = []
output_file = f"{TX_HASH}.xlsx"
layer = 1  # Tracks transaction depth

# Function to save transactions to Excel
def save_to_excel(output_file):
    """ Saves collected transactions to an Excel file before exiting. """
    if traced_transactions:
        df = pd.DataFrame(traced_transactions)
        df.to_excel(output_file, index=False)
        print(f"📁 Data saved to {output_file} ✅")
    else:
        print("⚠ No transactions to save.")

# Function to check if an address belongs to an exchange
def check_if_exchange(address):
    """ Uses OKLink API to check if the given address is an exchange wallet. """
    url = f"https://www.oklink.com/api/v5/explorer/address/address-label?chainShortName={chainShortName}&address={address}"
    headers = {
        "Ok-Access-Key": API_KEY,
        "Accept": "application/json"
    }

    try:
        response = requests.get(url, headers=headers)
        time.sleep(0.35)  # Rate limit

        if response.status_code == 200:
            data = response.json()
            if "data" in data and len(data["data"]) > 0:
                return data["data"][0].get("labelName", "Unknown Exchange")
    except Exception as e:
        print(f"⚠ Error checking exchange: {e}")
    return None  # Address does not belong to a known exchange

# Function to fetch transaction details
def get_transaction_details(tx_hash):
    """ Fetch transaction details including sender, receiver, date, token type, and amount. """
    url = f"https://www.oklink.com/api/v5/explorer/transaction/token-transaction-detail?chainShortName={chainShortName}&txId={tx_hash}&limit=1"
    headers = {
        "Ok-Access-Key": API_KEY,
        "Accept": "application/json"
    }

    for _ in range(3):  # Retry up to 3 times in case of failure
        try:
            response = requests.get(url, headers=headers)
            time.sleep(0.35)  # Rate limit

            if response.status_code == 200:
                data = response.json()
                if "data" in data and len(data["data"]) > 0:
                    token_transfers = data["data"][0].get("tokenTransferDetails", [])

                    if token_transfers:
                        for transfer in token_transfers:
                            from_address = transfer.get("from", "N/A")
                            to_address = transfer.get("to", "N/A")
                            timestamp = transfer.get("transactionTime", "N/A")
                            token_amount = transfer.get("amount", "N/A")
                            token_type = transfer.get("symbol", "N/A")

                            # Convert timestamp to IST (GMT+5:30) in 24-hour format
                            date = "N/A"
                            if timestamp != "N/A":
                                utc_time = datetime.utcfromtimestamp(int(timestamp) / 1000)
                                ist_time = utc_time + timedelta(hours=5, minutes=30)
                                date = ist_time.strftime('%m/%d/%Y %H:%M:%S')

                            exchange_name = check_if_exchange(to_address)

                            # Store transaction data
                            transaction = {
                                "layer": layer,
                                "txid": tx_hash,
                                "from": from_address,
                                "to": to_address,
                                "date": date,
                                "amount": token_amount,
                                "token_type": token_type,
                                "exchange": exchange_name if exchange_name else "N/A"
                            }
                            traced_transactions.append(transaction)

                            if exchange_name:  
                                print(f"✅ Stopping trace: {to_address} belongs to {exchange_name}.")
                                return None

                        return traced_transactions
            else:
                print(f"⚠ API Error {response.status_code}: {response.text}")
                time.sleep(1)  # Wait before retrying
        except Exception as e:
            print(f"⚠ Error fetching transaction details: {e}")
            time.sleep(1)  # Wait before retrying
    return None

# Function to get the first non-zero outgoing transaction for the same token
def get_next_outgoing_transaction(address, token_type, initial_txid):
    global layer
    page = 1
    found_incoming = False  

    try:
        while True:
            url = f"https://www.oklink.com/api/v5/explorer/address/token-transaction-list?chainShortName={chainShortName}&address={address}&protocolType={protocolType}&limit=50&page={page}"
            headers = {
                "Ok-Access-Key": API_KEY,
                "Accept": "application/json"
            }

            response = requests.get(url, headers=headers)
            time.sleep(0.35)  # Rate limit

            if response.status_code == 200:
                data = response.json()
                print(f"🔍 Checking Layer {layer}, Page {page}...")

                if "data" in data and len(data["data"]) > 0:
                    transactions = data["data"][0].get("transactionList", [])
                    total_pages = int(data["data"][0].get("totalPage", "1")) if data["data"][0].get("totalPage", "").isdigit() else 100

                    transactions.reverse()  # Reverse for correct order

                    for tx in transactions:
                        txid = tx.get("txId", "N/A")
                        from_address = tx.get("from", "N/A")
                        to_address = tx.get("to", "N/A")
                        amount = tx.get("amount", "0")
                        transaction_symbol = tx.get("symbol", "N/A")
                        timestamp = int(tx.get("transactionTime", "0"))

                        if txid == initial_txid:
                            print(f"⭕ Found Initial TXID: {initial_txid}")
                            found_incoming = True
                            continue

                        if found_incoming and transaction_symbol == token_type and float(amount) > 0 and from_address == address:
                            ist_time = datetime.utcfromtimestamp(timestamp / 1000) + timedelta(hours=5, minutes=30)
                            date = ist_time.strftime('%m/%d/%Y %H:%M:%S')

                            exchange_name = check_if_exchange(to_address)  
                            if exchange_name:
                                print(f"✅ Stopping trace: {to_address} belongs to {exchange_name}.")
                                return None
                            
                            print(f"✅ Found Outgoing TX, from: {from_address}, to: {to_address}")
                            layer += 1  
                            return {
                                "layer": layer,
                                "txid": txid,
                                "from": from_address,
                                "to": to_address,
                                "date": date,
                                "amount": amount,
                                "token_type": transaction_symbol,
                                "exchange": exchange_name if exchange_name else "N/A"
                            }

                    if page < total_pages:
                        page += 1
                    else:
                        return None
            else:
                return None
    except KeyboardInterrupt:
        print("\n⚠ Interrupted! Saving data before exit...")
        save_to_excel(output_file)
        exit(0)

# Main function
def main():
    trace_transactions(TX_HASH, output_file)

def trace_transactions(tx_hash, output_file):
    transaction_details = get_transaction_details(tx_hash)
    while transaction_details:
        last_transaction = traced_transactions[-1]
        transaction_details = get_next_outgoing_transaction(last_transaction["to"], last_transaction["token_type"], last_transaction["txid"])
        if transaction_details:
            traced_transactions.append(transaction_details)

    save_to_excel(output_file)

# Run the script
main()
