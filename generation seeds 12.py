from mnemonic import Mnemonic
from bip_utils import Bip39SeedGenerator, Bip44, Bip44Coins, Bip44Changes 
import logging  

# Setup logging
logging.basicConfig(level=logging.INFO) 
logger = logging.getLogger(__name__)

# Function to derive addresses using BIP44      
def derive_addresses(seed_bytes, coin, account_index=0, num_addresses=1): 
    
    try:
        addresses = []
        bip44_mst = Bip44.FromSeed(seed_bytes, coin)
        bip44_acc = bip44_mst.Purpose().Coin().Account(account_index)
        bip44_chg = bip44_acc.Change(Bip44Changes.CHAIN_EXT)
        for i in range(num_addresses):
            bip44_addr = bip44_chg.AddressIndex(i)
            addresses.append(bip44_addr.PublicKey().ToAddress())
        return addresses
    except Exception as e:
        logger.error(f"Error deriving addresses for {coin}: {e}")
        return []

# List of cryptocurrencies to derive addresses for 
coins = {
    "Bitcoin": Bip44Coins.BITCOIN,
    "Ethereum": Bip44Coins.ETHEREUM,
    "Litecoin": Bip44Coins.LITECOIN,
    
}

# Ask the user for the number of wallets to generate  
num_wallets = int(input("Enter the number of wallets to generate: ")) 

# Create or open a file to write seed phrases and addresses 
with open("Seed_Phrase.txt", "w") as file:
    # Generate and log seed phrases and addresses for each wallet 
    for wallet_index in range(num_wallets):
        # Generate a seed phrase with 128 bits of entropy 
        mnemo = Mnemonic("english") 
        seed_phrase = mnemo.generate(strength=128)
        logger.info(f"Generated Seed Phrase: {seed_phrase}")
        
        # Write the seed phrase to the file
        file.write(f"Seed Phrase {wallet_index + 1}:\n") 
        
        file.write(f"{seed_phrase}\n")
        
        # Convert seed phrase to seed bytes
        seed_bytes = Bip39SeedGenerator(seed_phrase).Generate()
        
        # Derive and log addresses for each cryptocurrency  
        for coin_name, coin in coins.items(): 
            addresses = derive_addresses(seed_bytes, coin, num_addresses=1) 
            if addresses:
                file.write(f"{coin_name}: {addresses[0]}\n")
            else:
                file.write(f"{coin_name}: No addresses derived\n")
        
        # Write a separator line
        file.write("---\n")
