**

## 12-Word Seed Wallet Scanner

is an advanced and user-friendly tool designed for cryptocurrency enthusiasts and security professionals. It allows you to generate, analyze, and validate cryptocurrency wallets using 12-word seed phrases. The tool also enables you to check wallet balances across major digital currencies, including Bitcoin, Ethereum, and Litecoin.

![enter image description here](https://github.com/Rezaguii/12-word-seed-Wallet-Scanner-/blob/main/ezgif-1.gif)

## 👉**Disclaimer**👈

This script is intended solely for educational and research purposes. 📚🔬

By using this script, you agree to the following terms:

1.  The script must not be used for malicious purposes, including unauthorized activities on third-party systems. 🚫💻
2.  Obtain explicit permission from system owners before running or deploying this script. ✔️🛡️
3.  Be aware of the potential impacts on hardware, including increased wear and power consumption. ⚠️🔋
4.  The script's creator is not responsible for any damages, consequences, or negative outcomes resulting from its use. ❗🚫

If you do not accept these terms, please refrain from using or distributing this script. 🚷

## **How It Works**
To understand how this tool operates, let's break down the underlying concepts:

 -  **Wallet Creation and Seed Phrases:**
    
    -   When a wallet is created on platforms like Exodus, TrustWallet, or similar services, users are provided with a mnemonic phrase (seed phrase) consisting of 12 distinct words. This passphrase is not randomly chosen; instead, it is generated from a predefined wordlist of 2048 possible words. The selection of words follows a specific algorithm that ensures security and randomness. The complete list of these words can be found [HERE](https://www.blockplate.com/pages/bip-39-wordlist).

**Access and Management:**

 - The 12-word seed phrase serves as a secure key to access and manage
   the wallet. With this passphrase, users can restore their wallet and
   access their assets on any compatible device. The mnemonic phrase
   effectively encodes the cryptographic keys required to access and
   control the wallet's contents.

**Brute Force Analysis:**

-   The application utilizes brute force techniques to systematically attempt and decode these seed phrases. This process involves generating and testing numerous combinations of the 12-word passphrases to uncover valid ones. The goal is to identify seed phrases that correspond to wallets with balances.

1.  **Output and Logging:**
    
    -   If the tool successfully discovers a wallet with a balance, it records this information in a file named `wallets_balance.txt`. This file includes details of the found wallets, facilitating further review.
    -   Upon execution, the tool generates a detailed log file named `Wallet-Scanner.log`. This log captures all activities and attempts made during the session, providing a comprehensive record for subsequent analysis.

By employing these techniques, the tool aims to explore and validate potential wallet access points using systematic and methodical approaches.

![enter image description here](https://github.com/Rezaguii/12-word-seed-Wallet-Scanner-/blob/main/b5-030f-816253d.png)

**12-Word Seed Wallet Scanner** is built on the principles of cryptocurrency wallet generation using the Master Seed, based on the BIP 32 standard for Hierarchical Deterministic (HD) Wallets. This Python script creates a 12-word mnemonic phrase, which serves as the Master Seed for deriving all cryptographic keys.

**Key Points:**

-   **Mnemonic Phrase:** The script generates a 12-word BIP39 mnemonic, representing the Master Seed in a human-readable format.
-   **Address Generation:** Using this mnemonic, the script creates addresses for Bitcoin (BTC) and Ethereum (ETH) following the BIP44 protocol, which organizes wallet keys in a hierarchical structure.

For detailed information, refer to the [BIP 32 wiki](https://github.com/bitcoin/bips/blob/master/bip-0032.mediawiki).


## Setup



Install [Python 3.10](https://www.python.org/downloads/release/python-3100/)


 1. Install Dependencies

    pip install -r requirements.txt

### Configuration

1.  **Get an Etherscan API Key**: Follow the [instructions here](https://docs.etherscan.io/getting-started/viewing-api-usage-statistics) to obtain your API key.
2.  **Set Up the API Key**: Go to the script’s directory and add your API key to the `Crackert.env` file.

    #*In EnigmaCracker.env
    ETHERSCAN_API_KEY=your_api_key_here <--- Replace with your own API key*

## explanation

**`generation_seeds_12.py`:**

-   **Purpose:** Generates 12-word seed phrases and derives cryptocurrency addresses (Bitcoin, Ethereum, Litecoin) from them.
-   **Usage:** Run the script to create seed phrases and corresponding wallet addresses, which are saved in `Seed_Phrase.txt`.
**seed phrase is compatible with:**
![enter image description here](https://github.com/Rezaguii/12-word-seed-Wallet-Scanner-/blob/main/Compatible%20address.png)

**`check_balance.py`:**

-   **Purpose:** Checks the balances of the addresses generated by the previous script.
-   **Usage:** Run the script to read addresses from `Seed_Phrase.txt` and fetch their balances. Results are saved in `wallets_with_balance.txt`.

![enter image description here](https://github.com/Rezaguii/12-word-seed-Wallet-Scanner-/blob/main/Grxgr849.png)


**Support & Updates:**

Hey, if you’ve made it this far, you must be as excited about this project as I am! 🎉 If you find this tool useful or just want to cheer me on, there are a few ways you can help out:

1.  **Show Some Love with a ⭐:** If you like the project, why not give it a star on GitHub? It’s like a virtual high-five that lets me know you’re interested in seeing more. Plus, it helps others discover the tool too!
    


