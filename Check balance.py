import requests
import os
from dotenv import load_dotenv
from colorama import init, Fore, Style
from concurrent.futures import ThreadPoolExecutor, as_completed
import random
import time

# Initialize colorama
init(autoreset=True) 

class CryptoBalanceChecker: 
    def __init__(self, etherscan_api_key): 
        self.etherscan_api_key = etherscan_api_key   
        self.session = requests.Session()

    def get_ethereum_balance(self, address): 
        
        url = f"https://api.etherscan.io/api?module=account&action=balance&address={address}&tag=latest&apikey={self.etherscan_api_key}"
        response = self.session.get(url)
        if response.status_code == 200:
            balance_in_wei = int(response.json()['result'])
            balance_in_ether = balance_in_wei / 10**18
            return balance_in_ether
        return None

    def get_bitcoin_balance(self, address):
        url = f"https://blockchain.info/balance?active={address}"
        response = self.session.get(url)
        if response.status_code == 200:
            balance = response.json()[address]["final_balance"] 
            balance_in_bitcoin = balance / 10**8
            return balance_in_bitcoin
        return None

def read_addresses_from_file(file_path): 
    
    addresses = []
    with open(file_path, 'r') as file:
        address_section = []
        for line in file:
            line = line.strip()
            if line.startswith('Seed Phrase'):
                if address_section:
                    addresses.extend(address_section)
                    address_section = []
            elif line:
                if line.startswith('Bitcoin:') or line.startswith('Ethereum:'):  
                    currency, address = map(str.strip, line.split(':'))
                    address_section.append((currency, address))
        if address_section:
            addresses.extend(address_section)
    return addresses

def write_wallet_with_balance(wallet, file_path='wallets_with_balance.txt'):  
    with open(file_path, 'a') as file:  # Open in append mode
        currency, address, balance = wallet
        file.write(f"{currency} balance for address {address}: {balance}\n")  

def fetch_balance(checker, currency, address):
    try:
        if currency.lower() == 'bitcoin':
            time.sleep(random.uniform(1, 1.5))  # Add random delay between 0.5 and 1.5 seconds
            return (currency, address, checker.get_bitcoin_balance(address))
        elif currency.lower() == 'ethereum':
            time.sleep(random.uniform(1, 1.5))  # Add random delay between 0.5 and 1.5 seconds
            return (currency, address, checker.get_ethereum_balance(address))
    except Exception as e:
        print(f"Error fetching {currency} balance for {address}: {e}") 
    return (currency, address, None)

def main():
    load_dotenv("Crackert.env")
    etherscan_api_key = os.getenv("ETHERSCAN_API_KEY")

    checker = CryptoBalanceChecker(etherscan_api_key) 
    
    addresses = read_addresses_from_file('Seed_Phrase.txt')

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = [executor.submit(fetch_balance, checker, currency, address) for currency, address in addresses]
        
        for future in as_completed(futures):
            currency, address, balance = future.result()
            if balance is not None: 
                if balance > 0.0:
                    write_wallet_with_balance((currency, address, balance)) 
                
                balance_color = Fore.GREEN if balance > 0.0 else Fore.RED

                if currency.lower() == 'bitcoin':
                    currency_color = Fore.YELLOW
                elif currency.lower() == 'ethereum':
                    currency_color = Fore.LIGHTBLACK_EX       

                print(f"{currency_color}{currency} balance for address {address}: {balance_color}{balance}")
            else:
                print(f"Failed to retrieve {currency} balance for address {address}")

if __name__ == "__main__":
    main()
