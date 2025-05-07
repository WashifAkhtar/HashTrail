
<h1><img src="icon.ico" width="30" style="vertical-align:middle;"/> HashTrail</h1>

HashTrail is a cryptocurrency forensics tool designed to trace transactions across blockchain networks. Its primary objective is to assist in digital investigations by analyzing transaction paths, detecting anomalies, and providing clarity in the movement of digital assets.


## 🔍 **About HashTrail**
HashTrail empowers investigators and analysts to:
- Track blockchain transactions step-by-step.
- Detect anomalies and suspicious transfers.
- Identify exchange wallets using OKLink API.
- Generate detailed transcation log for forensic documentation.


## ⚡ **Features**
- **Multi-Chain Support:** Supports major blockchains like Ethereum, Tron, Binance Smart Chain, and more.
- **Exchange Detection:** Automatically checks if an address belongs to an exchange.
- **Real-time Visualization:** View transaction flow in real-time with a custom UI.
- **Exportable Reports:** Save transaction paths as Excel files for offline analysis.
- **Windows Compatibility:** Optimized for Windows OS with a sleek, dark-themed GUI.


## 📦 **Installation**
```bash
# Clone the repository
git clone https://github.com/WashifAkhtar/HashTrail.git

# Navigate into the directory
cd HashTrail

# (Optional) Create a virtual environment
python -m venv venv
.\venv\Scripts\activate  # Activate the virtual environment (Windows)

# Install dependencies
pip install -r requirements.txt
```
## 🔑 API Configuration

Add your OKLink API key in a file named `api_key.py` in the root directory:
```
# api_key.py
API_KEY = 'your_api_key_here'
```
⚡️ Usage
```
# Basic Usage
python src/HashTrail.py

# Enter the transaction hash, chain name, and protocol type in the UI
```
When the application launches:

1. Enter the Transaction Hash.
2. Provide the Chain Name (e.g., TRON, ETH).
3. Specify the Protocol Type (e.g., token_20).
4. Click Start to begin the trace.

## 📝 Supported Chains

Refer to the `docs/supported_chains.docx` for a list of supported blockchain networks and their short names.

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch (`feature/your-feature`).
3. Commit your changes (`git commit -m 'Add your feature'`).
4. Push to the branch (`git push origin feature/your-feature`).
5. Create a Pull Request.

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Contact

For any issues or suggestions, feel free to open an issue or reach out directly:

GitHub: [WashifAkhtar](https://github.com/WashifAkhtar)
#
Crafted with 💡 by Washif Akhtar

