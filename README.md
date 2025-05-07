# HashTrail

HashTrail is a cryptocurrency forensics tool designed to trace transactions across blockchain networks. Its primary objective is to assist in digital investigations by analyzing transaction paths, detecting anomalies, and providing clarity in the movement of digital assets.

🚀 Features

- Trace transactions across multiple blockchain networks

- Visualize transaction paths and identify potential anomalies

- Export reports for investigation documentation

- Efficient address clustering for deeper analysis

📦 Installation
```
# Clone the repository
git clone https://github.com/WashifAkhtar/HashTrail.git

# Navigate into the directory
cd HashTrail

# (Optional) Create a virtual environment
python3 -m venv venv
source venv/bin/activate   # On Windows use `venv\Scripts\activate`

# Install dependencies
pip install -r requirements.txt
```
🔑 API Configuration

Create a file named api_key.py in the root directory and add your OKLink API key:
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
📝 Supported Chains

Refer to the docs/supported_chains.docx for a list of supported blockchain networks and their short names.

🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.

2. Create a new branch (`feature/your-feature`).

3. Commit your changes (`git commit -m 'Add your feature'`).

4. Push to the branch (`git push origin feature/your-feature`).

5. Create a Pull Request.

📜 License

This project is licensed under the MIT License - see the [LICENSE](#LICENSE) file for details.

📞 Contact

For any issues or suggestions, feel free to open an issue or reach out directly at your email.
#
Crafted with 💡 by Washif Akhtar

