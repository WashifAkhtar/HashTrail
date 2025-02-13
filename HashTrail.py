import requests
import pandas as pd
import time
import threading
import customtkinter as ctk
import tkinter as tk
from datetime import datetime, timedelta
from api_key import API_KEY

# Initialize CustomTkinter
ctk.set_appearance_mode("dark")  # Dark Mode
ctk.set_default_color_theme("dark-blue")  # Built-in theme

# Transaction tracking variables
traced_transactions = []
layer = 1  # Transaction depth tracker
running = False  # Flag to stop tracking safely

# Create main window
root = ctk.CTk()
root.title("HashTrail")

# Get screen size for dynamic scaling
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()

root.geometry("900x600")  # Default size
# root.geometry(f"{screen_width}x{screen_height}")
# root.geometry(f"{screen_width}x{screen_height}")
# root.minsize(800, 500)  # Minimum size to prevent extreme resizing

# Configure row/column weights to make UI **responsive**
root.grid_rowconfigure(0, weight=1)  # Terminal output expands
root.grid_columnconfigure(0, weight=1)  # Whole frame expands

# UI Theme Colors
BG_COLOR = "#1e1e1e"  # Dark Background
TEXT_COLOR = "#ffffff"  # White Text
START_COLOR = "#228B22"  # Green
STOP_COLOR = "#d63031"  # Red

# Frame container (makes UI dynamic)
frame = ctk.CTkFrame(root, fg_color=BG_COLOR, corner_radius=15)
frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
frame.grid_rowconfigure(4, weight=1)  # Terminal output expands
frame.grid_columnconfigure(1, weight=1)  # Inputs expand

# Title Label
title_label = ctk.CTkLabel(frame, text="🔍 HashTrail ", font=("Arial", 22, "bold"), text_color=TEXT_COLOR)
title_label.grid(row=0, column=0, columnspan=2, pady=(10, 20))

# Transaction Hash Input
label_tx = ctk.CTkLabel(frame, text="Transaction Hash:", font=("Arial", 16), text_color=TEXT_COLOR)
label_tx.grid(row=1, column=0, padx=10, pady=10, sticky="w")

entry_tx = ctk.CTkEntry(frame, width=screen_width // 3, placeholder_text="Transaction Hash")
entry_tx.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

# Chain Name Input
label_chain = ctk.CTkLabel(frame, text="Chain Short Name:", font=("Arial", 16), text_color=TEXT_COLOR)
label_chain.grid(row=2, column=0, padx=10, pady=10, sticky="w")

entry_chain = ctk.CTkEntry(frame, placeholder_text="Chain Name (e.g., TRON)")
entry_chain.grid(row=2, column=1, padx=10, pady=10, sticky="ew")

# Protocol Type Input
label_protocol = ctk.CTkLabel(frame, text="Protocol Type:", font=("Arial", 16), text_color=TEXT_COLOR)
label_protocol.grid(row=3, column=0, padx=10, pady=10, sticky="w")

entry_protocol = ctk.CTkEntry(frame, placeholder_text="Protocol Type (e.g., token_20)")
entry_protocol.grid(row=3, column=1, padx=10, pady=10, sticky="ew")

# Terminal Output Box (Resizable)
terminal_output = ctk.CTkTextbox(frame, height=screen_height // 3, font=("Arial", 14), text_color=TEXT_COLOR)
terminal_output.grid(row=4, column=0, columnspan=2, padx=10, pady=10, sticky="nsew")

# Function to log messages in GUI
def log_message(message):
    terminal_output.insert(tk.END, message + "\n")
    terminal_output.yview_moveto(1)  # Auto-scroll to latest log

# Function to save transactions to Excel
def save_to_excel(output_file):
    """ Saves the collected transactions to an Excel file before exiting. """
    if traced_transactions:
        df = pd.DataFrame(traced_transactions)
        df.to_excel(output_file, index=False)
        log_message(f"📁 Data saved to {output_file} ✅")
    else:
        log_message("⚠ No transactions to save.")

# Function to check if an address belongs to an exchange
def check_if_exchange(address,chainShortName):
    """ Uses OKLink API to check if the given address is an exchange wallet. """
    url = f"https://www.oklink.com/api/v5/explorer/address/address-label?chainShortName={chainShortName}&address={address}"
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
                return data["data"][0].get("labelName", "Unknown Exchange")
    except Exception as e:
        log_message(f"⚠ Error checking exchange: {e}")
    return None  # Address does not belong to a known exchange

# Function to fetch transaction details
def get_transaction_details(tx_hash, chainShortName):
    """ Fetch transaction details including sender, receiver, date, token type, and amount. """
    url = f"https://www.oklink.com/api/v5/explorer/transaction/token-transaction-detail?chainShortName={chainShortName}&txId={tx_hash}&limit=1"
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

                        exchange_name = check_if_exchange(to_address,chainShortName)  # Check if the address belongs to an exchange
                        transactions.append({
                            "from": from_address,
                            "to": to_address,
                            "date": date,
                            "token_amount": token_amount,
                            "transaction_hash": tx_hash,
                            "token_type": token_type,
                            "exchange": exchange_name if exchange_name else "N/A"
                        })

                        traced_transactions.append({
                            "layer": layer,
                            "txid": tx_hash,
                            "from": from_address,
                            "to": to_address,
                            "date": date,
                            "amount": token_amount,
                            "token_type": token_type,
                            "exchange": exchange_name if exchange_name else "N/A"
                        })

                        if exchange_name:  # Stop tracing if transaction goes to an exchange
                            log_message(f"✅ Stopping trace: {to_address} belongs to {exchange_name}.")
                            return None
                    return transactions
        else:
                log_message(f"⚠ API Error {response.status_code}: {response.text}")
    except Exception as e:
        log_message(f"⚠ Error fetching transaction: {e}")
    return None

# Function to get the first non-zero outgoing transaction for the same token
def get_next_outgoing_transaction(address, token_type, initial_txid, chainShortName, protocolType):
    global layer
    page = 1
    found_incoming = False  # Track when we locate the "in" transaction

    try:
        while running:
            if not running:  # Check stop condition
                return None
            url = f"https://www.oklink.com/api/v5/explorer/address/token-transaction-list?chainShortName={chainShortName}&address={address}&protocolType={protocolType}&limit=50&page={page}"
            headers = {
                "Ok-Access-Key": API_KEY,
                "Accept": "application/json"
            }

            response = requests.get(url, headers=headers)
            time.sleep(0.35)  # Rate limit

            if response.status_code == 200:
                data = response.json()
                log_message(f"🔍 Checking Layer {layer}, Page {page}...")

                if "data" in data and len(data["data"]) > 0:
                    transactions = data["data"][0].get("transactionList", [])

                    total_pages = int(data["data"][0].get("totalPage", "1")) if data["data"][0].get("totalPage", "").isdigit() else 100

                    transactions.reverse()

                    for tx in transactions:
                        txid = tx.get("txId", "N/A")
                        from_address = tx.get("from", "N/A")
                        to_address = tx.get("to", "N/A")
                        amount = tx.get("amount", "0")
                        transaction_symbol = tx.get("symbol", "N/A")
                        timestamp = int(tx.get("transactionTime", "0"))

                        if txid == initial_txid:
                            log_message(f"⭕ Found Initial TXID: {initial_txid}")
                            found_incoming = True
                            continue

                        if found_incoming and transaction_symbol == token_type and float(amount) > 0 and from_address == address:
                            ist_time = datetime.utcfromtimestamp(timestamp / 1000) + timedelta(hours=5, minutes=30)
                            date = ist_time.strftime('%m/%d/%Y %H:%M:%S')

                            exchange_name = check_if_exchange(to_address,chainShortName)  # Check if the recipient is an exchange
                            if exchange_name:
                                log_message(f"✅ Stopping trace: {to_address} belongs to {exchange_name}.")
                                return None

                            log_message(f"✅ Found Outgoing TX, from: {from_address}, to: {to_address}")
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
                log_message(f"❌ API Error: {response.status_code}")  
                return None
    except KeyboardInterrupt:
        log_message("\n⚠ Interrupted! Saving data before exit...")
        save_to_excel(output_file)
        exit(0)

# Function to trace transactions until an exchange is found
def trace_transactions():
    global running
    running = True

    tx_hash = entry_tx.get()
    chain_name = entry_chain.get()
    protocol_type = entry_protocol.get()

    global output_file
    output_file = f"{tx_hash}.xlsx"

    if not tx_hash or not chain_name or not protocol_type:
        log_message("⚠ Please enter all required fields before starting.")
        return
    
    try:
        transaction_details = get_transaction_details(tx_hash, chain_name)

        if not transaction_details:
            log_message("Error fetching initial transaction details.")
            return

        while running:  # Keep tracing transactions until an exchange wallet is found
            last_transaction = traced_transactions[-1]
            next_transaction = get_next_outgoing_transaction(last_transaction["to"], last_transaction["token_type"], last_transaction["txid"],chain_name, protocol_type)
            if next_transaction:
                traced_transactions.append(next_transaction)
            else:
                log_message("No further outgoing transactions found.")
                break

        save_to_excel(output_file)
    except KeyboardInterrupt:
        log_message("\n⚠ Interrupted! Saving data before exit...")
        save_to_excel(output_file)
        exit(0)

def toggle_tracking():
    global running
    running = not running
    if running:
        start_button.configure(text="Stop", fg_color=STOP_COLOR)
        tracking_thread = threading.Thread(target=trace_transactions, daemon=True)
        tracking_thread.start()
    else:
        start_button.configure(text="Start", fg_color=START_COLOR)
        time.sleep(1)
        log_message("⚠ Tracking Stopped.")
        
# Buttons
start_button = ctk.CTkButton(frame, text="Start", fg_color=START_COLOR, text_color=TEXT_COLOR, command=toggle_tracking)
start_button.grid(row=5, column=0, columnspan=2, padx=10, pady=20, sticky="ew")

# Run Application
root.mainloop()
