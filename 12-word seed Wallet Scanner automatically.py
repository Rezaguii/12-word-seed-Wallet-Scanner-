import sys
import os
import requests
import logging
import time
from dotenv import load_dotenv
from bip_utils import (
    Bip39MnemonicGenerator,
    Bip39SeedGenerator,
    Bip44,
    Bip44Coins,
    Bip44Changes,
    Bip39WordsNum,
)

from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QTextEdit, QLabel, QVBoxLayout, QWidget, QMessageBox
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from concurrent.futures import ThreadPoolExecutor, as_completed

# Constants
LOG_FILE_NAME = "Wallet-Scanner.log"
ENV_FILE_NAME = "Crackert.env"
WALLETS_FILE_NAME = "wallets_balance.txt"
MAX_WORKERS = 5

# Global counter for the number of wallets scanned
wallets_scanned = 0

# Get the absolute path of the directory where the script is located
directory = os.path.dirname(os.path.abspath(__file__))
# Initialize directory paths
log_file_path = os.path.join(directory, LOG_FILE_NAME)
env_file_path = os.path.join(directory, ENV_FILE_NAME)
wallets_file_path = os.path.join(directory, WALLETS_FILE_NAME)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler(log_file_path),  # Log to a file
        logging.StreamHandler(sys.stdout),  # Log to standard output
    ],
)

# Load environment variables from .env file
load_dotenv(env_file_path)

# Environment variable validation
required_env_vars = ["ETHERSCAN_API_KEY"]
missing_vars = [var for var in required_env_vars if not os.getenv(var)]
if missing_vars:
    raise EnvironmentError(f"Missing environment variables: {', '.join(missing_vars)}")

def bip():
    """Generate a 12-word BIP39 mnemonic."""
    return Bip39MnemonicGenerator().FromWordsNumber(Bip39WordsNum.WORDS_NUM_12)

def bip44_ETH_wallet_from_seed(seed):
    """Generate an Ethereum wallet address from a BIP39 seed."""
    seed_bytes = Bip39SeedGenerator(seed).Generate()
    bip44_mst_ctx = Bip44.FromSeed(seed_bytes, Bip44Coins.ETHEREUM)
    bip44_acc_ctx = (
        bip44_mst_ctx.Purpose()
        .Coin()
        .Account(0)
        .Change(Bip44Changes.CHAIN_EXT)
        .AddressIndex(0)
    )
    return bip44_acc_ctx.PublicKey().ToAddress()

def bip44_BTC_seed_to_address(seed):
    """Generate a Bitcoin wallet address from a BIP39 seed."""
    seed_bytes = Bip39SeedGenerator(seed).Generate()
    bip44_mst_ctx = Bip44.FromSeed(seed_bytes, Bip44Coins.BITCOIN)
    bip44_acc_ctx = bip44_mst_ctx.Purpose().Coin().Account(0)
    bip44_chg_ctx = bip44_acc_ctx.Change(Bip44Changes.CHAIN_EXT)
    bip44_addr_ctx = bip44_chg_ctx.AddressIndex(0)
    return bip44_addr_ctx.PublicKey().ToAddress()

def check_ETH_balance(address, etherscan_api_key, retries=3, delay=5):
    """Check the Ethereum balance of an address."""
    api_url = f"https://api.etherscan.io/api?module=account&action=balance&address={address}&tag=latest&apikey={etherscan_api_key}"
    session = requests.Session()  # Use a session for better performance
    for attempt in range(retries):
        try:
            response = session.get(api_url)
            data = response.json()
            if data["status"] == "1":
                
                balance = int(data["result"]) / 1e18
                
                return balance
            elif data["status"] == "0": 
                error_message = f"ERROR - Invalid ETHERSCAN_API_KEY or rate limit exceeded. ETHERSCAN_API_KEY=[your_api_key_here]"
                logging.error(f"ERROR - Error getting balance: {data['message']}")
                show_message_box("Error", "Invalid ETHERSCAN_API_KEY or rate limit exceeded. Please replace ETHERSCAN_API_KEY with your own API key in Crackert.env")
                return error_message
            else:
                logging.error("Error getting balance: %s", data["message"])
                return 0
        except Exception as e:
            if attempt < retries - 1:
                logging.error(f"Error checking ETH balance, retrying in {delay} seconds: {str(e)}")
                time.sleep(delay)
            else:
                logging.error("Error checking ETH balance: %s", str(e)) 
                return 0

def check_BTC_balance(address, retries=3, delay=5):
    """Check the Bitcoin balance of an address."""
    session = requests.Session()  # Use a session for better performance
    for attempt in range(retries):
        try:
            response = session.get(f"https://blockchain.info/balance?active={address}")
            data = response.json()
            balance = data[address]["final_balance"]
            return balance / 100000000
        except Exception as e:
            if attempt < retries - 1:
                
                logging.error(f"Error checking BTC balance, retrying in {delay} seconds: {str(e)}")
                time.sleep(delay)
            else:
                
                logging.error("Error checking BTC balance: %s", str(e)) 
                return 0

def write_to_file(seed, BTC_address, BTC_balance, ETH_address, ETH_balance):
    """Write wallet information to a file."""
    with open(wallets_file_path, "a") as f:
        log_message = f"Seed: {seed}\nAddress: {BTC_address}\nBalance: {BTC_balance} BTC\n\nEthereum Address: {ETH_address}\nBalance: {ETH_balance} ETH\n\n"
        f.write(log_message)
        logging.info(f"Written to file: {log_message}")

def show_message_box(title, message):
    
    """Show a message box with a given title and message. """
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Critical)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    msg_box.setStandardButtons(QMessageBox.Ok)
    msg_box.exec_()

class WalletScannerThread(QThread):
    update_log = pyqtSignal(str)
    found_wallet = pyqtSignal(str)
    
    def __init__(self):
        
        super().__init__()
        self._is_running = True
        self.executor = ThreadPoolExecutor(max_workers=MAX_WORKERS)

    def run(self):
        
        global wallets_scanned
        etherscan_api_key = os.getenv("ETHERSCAN_API_KEY")
        if not etherscan_api_key:
            raise ValueError("The Etherscan API key must be set in the environment variables.")
        
        futures = []
        
        while self._is_running:
            seed = bip()
            if self._is_running:  # Check before adding the task
                futures.append(self.executor.submit(self.scan_wallet, seed, etherscan_api_key))
        
        for future in as_completed(futures):
            if not self._is_running:
                break
            future.result()

    def scan_wallet(self, seed, etherscan_api_key):
        
        """Scan a wallet and check balances. """
        BTC_address = bip44_BTC_seed_to_address(seed) 
        BTC_balance = check_BTC_balance(BTC_address)
        self.display_balance('BTC', seed, BTC_address, BTC_balance)

        ETH_address = bip44_ETH_wallet_from_seed(seed)
        ETH_balance = check_ETH_balance(ETH_address, etherscan_api_key)  
        self.display_balance('ETH', seed, ETH_address, ETH_balance)   

        global wallets_scanned
        wallets_scanned += 1

        if BTC_balance > 0 or ETH_balance > 0:
            self.found_wallet.emit("<span style='color: red;'>(!) Wallet with balance found!</span>")
            write_to_file(seed, BTC_address, BTC_balance, ETH_address, ETH_balance)

    def display_balance(self, currency, seed, address, balance):
        
        """Display balance with appropriate color based on amount.""" 
        if isinstance(balance, str) and "ERROR" in balance:
            
            self.update_log.emit(f"<span style='color: red;'>{balance}</span>")
            return
        
        balance_color = 'green' if balance > 0 else 'red'
        self.update_log.emit(f"<span style='color: yellow;'>Seed: {seed}</span>")
        self.update_log.emit(f"<span style='color: cyan;'>{currency} address: {address}</span>")
        self.update_log.emit(f"<span style='color: {balance_color};'>{currency} balance: {balance} {currency}</span>")
        self.update_log.emit("")

    def stop(self):
        
        self._is_running = False
        self.executor.shutdown(wait=True)
        self.quit()
        self.wait()

class MainWindow(QMainWindow):
    def __init__(self):
        
        super().__init__()

        self.setWindowTitle("12-word seed Wallet Scanner")
        self.setGeometry(100, 100, 800, 600)
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)
        
        self.label = QLabel("12-word seed Wallet Scanner - Wallet Scanner", self)
        self.label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.label)
        
        self.start_button = QPushButton("Start Scanning", self)
        self.start_button.clicked.connect(self.start_scanning)
        self.layout.addWidget(self.start_button)
        
        self.stop_button = QPushButton("Stop Scanning", self)
        self.stop_button.clicked.connect(self.stop_scanning)
        self.stop_button.setEnabled(False)
        self.layout.addWidget(self.stop_button)
        
        self.log_output = QTextEdit(self)
        self.log_output.setReadOnly(True)
        self.layout.addWidget(self.log_output)
        
        self.setStyleSheet(self.get_stylesheet())

        self.scanner_thread = None

    def get_stylesheet(self):
        
        return """
            QMainWindow {
                background-color: #2E2E2E;
            }
            QLabel {
                color: #00FF00;
                font-size: 24px;
            }
            QPushButton {
                background-color: #4CAF50;
                color: white;
                font-size: 18px;
                padding: 10px;
                border: none;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:disabled {
                background-color: #757575;
                color: #BDBDBD;
            }
            QTextEdit {
                background-color: #333333;
                color: #00FF00;
                font-family: Consolas, monospace;
                font-size: 14px;
                border: 1px solid #00FF00;
            }
        """

    def start_scanning(self):
        
        self.log_output.append("<span style='color: white;'>Starting wallet scanning...</span>")
        self.scanner_thread = WalletScannerThread()
        self.scanner_thread.update_log.connect(self.update_log_output)
        self.scanner_thread.found_wallet.connect(self.update_log_output)
        self.scanner_thread.start()
        self.start_button.setEnabled(False)
        self.stop_button.setEnabled(True)

    def stop_scanning(self):  
        if self.scanner_thread:
            self.scanner_thread.stop()
        self.start_button.setEnabled(True)
        self.stop_button.setEnabled(False)

    def update_log_output(self, message): 
        self.log_output.append(message)

def main():
    
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
