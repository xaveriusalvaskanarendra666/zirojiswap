from web3 import Web3
from eth_account import Account
import json
import random
import time
import datetime
from colorama import Fore, Back, Style, init

# Inisialisasi colorama
init(autoreset=True)

# Fungsi untuk membuat teks pelangi
def rainbow_text(text):
    colors = [Fore.RED, Fore.YELLOW, Fore.GREEN, Fore.CYAN, Fore.BLUE, Fore.MAGENTA]
    rainbow = ""
    for i, char in enumerate(text):
        rainbow += colors[i % len(colors)] + Style.BRIGHT + char
    return rainbow + Style.RESET_ALL

# Header yang lebih sederhana dengan warna kuning
def print_sky_header():
    width = 50
    print(f"{Fore.CYAN}{'='*width}{Style.RESET_ALL}")
    
    # Teks di tengah dengan warna kuning
    title = "0G HUB Swapper (Multi-Account)"
    padding = (width - len(title)) // 2
    print(" " * padding + f"{Fore.YELLOW}{Style.BRIGHT}{title}{Style.RESET_ALL}")
    
    author = "By : SKY"
    padding = (width - len(author)) // 2
    print(" " * padding + f"{Fore.YELLOW}{Style.BRIGHT}{author}{Style.RESET_ALL}")
    
    print(f"{Fore.CYAN}{'='*width}{Style.RESET_ALL}")

class TokenSwapper:
    def __init__(self):
        # Inisialisasi koneksi ke RPC 0G-Newton-Testnet
        self.w3 = Web3(Web3.HTTPProvider('https://og-testnet-evm.itrocket.net'))
        
        # Verifikasi koneksi ke jaringan yang benar
        if self.w3.eth.chain_id != 16600:
            raise Exception("Koneksi tidak terhubung ke 0G-Newton-Testnet")
            
        # Detail kontrak DEX
        self.router_address = "0xD86b764618c6E3C078845BE3c3fCe50CE9535Da7"  # Router address yang benar
        self.router_abi = [
            {
                "inputs": [
                    {
                        "components": [
                            {"internalType": "address", "name": "tokenIn", "type": "address"},
                            {"internalType": "address", "name": "tokenOut", "type": "address"},
                            {"internalType": "uint24", "name": "fee", "type": "uint24"},
                            {"internalType": "address", "name": "recipient", "type": "address"},
                            {"internalType": "uint256", "name": "deadline", "type": "uint256"},
                            {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
                            {"internalType": "uint256", "name": "amountOutMinimum", "type": "uint256"},
                            {"internalType": "uint160", "name": "sqrtPriceLimitX96", "type": "uint160"}
                        ],
                        "internalType": "struct ISwapRouter.ExactInputSingleParams",
                        "name": "params",
                        "type": "tuple"
                    }
                ],
                "name": "exactInputSingle",
                "outputs": [{"internalType": "uint256", "name": "amountOut", "type": "uint256"}],
                "stateMutability": "payable",
                "type": "function"
            }
        ]
        
        # Detail token dengan alamat yang benar
        self.usdt_address = Web3.to_checksum_address("0x9A87C2412d500343c073E5Ae5394E3bE3874F76b")
        self.eth_address = Web3.to_checksum_address("0xce830D0905e0f7A9b300401729761579c5FB6bd6")
        self.btc_address = Web3.to_checksum_address("0x1e0d871472973c562650e991ed8006549f8cbefc")  # Alamat BTC
        
    def swap_usdt_to_eth(self, private_key, amount_in):
        max_retries = 3  # Maksimal percobaan ulang
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                # Buat instance akun
                if private_key.startswith('0x'):
                    private_key_bytes = bytes.fromhex(private_key[2:])
                else:
                    private_key_bytes = bytes.fromhex(private_key)
                    
                account = Account.from_key(private_key_bytes)
                
                # Approve USDT
                usdt_abi = [
                    {
                        "constant": False,
                        "inputs": [
                            {"name": "_spender", "type": "address"},
                            {"name": "_value", "type": "uint256"}
                        ],
                        "name": "approve",
                        "outputs": [{"name": "", "type": "bool"}],
                        "payable": False,
                        "stateMutability": "nonpayable",
                        "type": "function"
                    },
                    {
                        "constant": True,
                        "inputs": [{"name": "_owner", "type": "address"}],
                        "name": "balanceOf",
                        "outputs": [{"name": "balance", "type": "uint256"}],
                        "payable": False,
                        "stateMutability": "view",
                        "type": "function"
                    }
                ]
                
                usdt_contract = self.w3.eth.contract(address=self.usdt_address, abi=usdt_abi)
                
                approve_tx = usdt_contract.functions.approve(
                    self.router_address,
                    amount_in
                ).build_transaction({
                    'from': account.address,
                    'nonce': self.w3.eth.get_transaction_count(account.address),
                    'gas': 100000,
                    'gasPrice': self.w3.eth.gas_price,
                    'chainId': self.w3.eth.chain_id
                })
                
                # Sign dan kirim transaksi approval
                signed_tx = Account.sign_transaction(approve_tx, private_key_bytes)
                tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
                self.w3.eth.wait_for_transaction_receipt(tx_hash)
                
                # Swap tokens
                router_contract = self.w3.eth.contract(address=self.router_address, abi=self.router_abi)
                deadline = self.w3.eth.get_block('latest').timestamp + 300
                
                params = {
                    'tokenIn': self.usdt_address,
                    'tokenOut': self.eth_address,
                    'fee': 3000,  # 0.3%
                    'recipient': account.address,
                    'deadline': deadline,
                    'amountIn': amount_in,
                    'amountOutMinimum': 0,  # Untuk testing
                    'sqrtPriceLimitX96': 0
                }
                
                swap_tx = router_contract.functions.exactInputSingle(
                    params
                ).build_transaction({
                    'from': account.address,
                    'nonce': self.w3.eth.get_transaction_count(account.address),
                    'gas': 300000,
                    'gasPrice': self.w3.eth.gas_price,
                    'chainId': self.w3.eth.chain_id
                })
                
                # Sign dan kirim transaksi swap
                signed_swap = Account.sign_transaction(swap_tx, private_key_bytes)
                swap_tx_hash = self.w3.eth.send_raw_transaction(signed_swap.raw_transaction)
                receipt = self.w3.eth.wait_for_transaction_receipt(swap_tx_hash)
                
                return {
                    'status': 'success',
                    'transaction_hash': swap_tx_hash.hex(),
                    'amount_in': amount_in
                }
                
            except Exception as e:
                retry_count += 1
                print(f"{Fore.RED}Error: {str(e)}. Mencoba ulang ({retry_count}/{max_retries})...{Style.RESET_ALL}")
                time.sleep(5)  # Jeda sebelum mencoba ulang
        
        return {
            'status': 'error',
            'message': f"Gagal setelah {max_retries} percobaan"
        }

    def swap_usdt_to_btc(self, private_key, amount_in):
        max_retries = 3  # Maksimal percobaan ulang
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                # Buat instance akun
                if private_key.startswith('0x'):
                    private_key_bytes = bytes.fromhex(private_key[2:])
                else:
                    private_key_bytes = bytes.fromhex(private_key)
                    
                account = Account.from_key(private_key_bytes)
                
                # Approve USDT
                usdt_abi = [
                    {
                        "constant": False,
                        "inputs": [
                            {"name": "_spender", "type": "address"},
                            {"name": "_value", "type": "uint256"}
                        ],
                        "name": "approve",
                        "outputs": [{"name": "", "type": "bool"}],
                        "payable": False,
                        "stateMutability": "nonpayable",
                        "type": "function"
                    },
                    {
                        "constant": True,
                        "inputs": [{"name": "_owner", "type": "address"}],
                        "name": "balanceOf",
                        "outputs": [{"name": "balance", "type": "uint256"}],
                        "payable": False,
                        "stateMutability": "view",
                        "type": "function"
                    }
                ]
                
                usdt_contract = self.w3.eth.contract(address=self.usdt_address, abi=usdt_abi)
                
                approve_tx = usdt_contract.functions.approve(
                    self.router_address,
                    amount_in
                ).build_transaction({
                    'from': account.address,
                    'nonce': self.w3.eth.get_transaction_count(account.address),
                    'gas': 100000,
                    'gasPrice': self.w3.eth.gas_price,
                    'chainId': self.w3.eth.chain_id
                })
                
                # Sign dan kirim transaksi approval
                signed_tx = Account.sign_transaction(approve_tx, private_key_bytes)
                tx_hash = self.w3.eth.send_raw_transaction(signed_tx.raw_transaction)
                self.w3.eth.wait_for_transaction_receipt(tx_hash)
                
                # Swap tokens
                router_contract = self.w3.eth.contract(address=self.router_address, abi=self.router_abi)
                deadline = self.w3.eth.get_block('latest').timestamp + 300
                
                params = {
                    'tokenIn': self.usdt_address,
                    'tokenOut': self.btc_address,
                    'fee': 3000,  # 0.3%
                    'recipient': account.address,
                    'deadline': deadline,
                    'amountIn': amount_in,
                    'amountOutMinimum': 0,  # Untuk testing
                    'sqrtPriceLimitX96': 0
                }
                
                swap_tx = router_contract.functions.exactInputSingle(
                    params
                ).build_transaction({
                    'from': account.address,
                    'nonce': self.w3.eth.get_transaction_count(account.address),
                    'gas': 300000,
                    'gasPrice': self.w3.eth.gas_price,
                    'chainId': self.w3.eth.chain_id
                })
                
                # Sign dan kirim transaksi swap
                signed_swap = Account.sign_transaction(swap_tx, private_key_bytes)
                swap_tx_hash = self.w3.eth.send_raw_transaction(signed_swap.raw_transaction)
                receipt = self.w3.eth.wait_for_transaction_receipt(swap_tx_hash)
                
                return {
                    'status': 'success',
                    'transaction_hash': swap_tx_hash.hex(),
                    'amount_in': amount_in
                }
                
            except Exception as e:
                retry_count += 1
                print(f"{Fore.RED}Error: {str(e)}. Mencoba ulang ({retry_count}/{max_retries})...{Style.RESET_ALL}")
                time.sleep(5)  # Jeda sebelum mencoba ulang
        
        return {
            'status': 'error',
            'message': f"Gagal setelah {max_retries} percobaan"
        }

    def swap_eth_to_usdt(self, private_key, amount_in):
        max_retries = 3  # Maksimal percobaan ulang
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                # Buat instance akun
                if private_key.startswith('0x'):
                    private_key_bytes = bytes.fromhex(private_key[2:])
                else:
                    private_key_bytes = bytes.fromhex(private_key)
                    
                account = Account.from_key(private_key_bytes)
                
                # Approve ETH
                eth_abi = [
                    {
                        "constant": False,
                        "inputs": [
                            {"name": "_spender", "type": "address"},
                            {"name": "_value", "type": "uint256"}
                        ],
                        "name": "approve",
                        "outputs": [{"name": "", "type": "bool"}],
                        "payable": False,
                        "stateMutability": "nonpayable",
                        "type": "function"
                    }
                ]
                
                eth_contract = self.w3.eth.contract(address=self.eth_address, abi=eth_abi)
                
                approve_tx = eth_contract.functions.approve(
                    self.router_address,
                    amount_in
                ).build_transaction({
                    'from': account.address,
                    'nonce': self.w3.eth.get_transaction_count(account.address),
                    'gas': 100000,
                    'gasPrice': self.w3.eth.gas_price,
                    'chainId': self.w3.eth.chain_id
                })
                
                # Sign dan kirim transaksi approval
                signed_approve = Account.sign_transaction(approve_tx, private_key_bytes)
                tx_approve_hash = self.w3.eth.send_raw_transaction(signed_approve.raw_transaction)
                self.w3.eth.wait_for_transaction_receipt(tx_approve_hash)
                
                # Swap tokens
                router_contract = self.w3.eth.contract(address=self.router_address, abi=self.router_abi)
                deadline = self.w3.eth.get_block('latest').timestamp + 300
                
                params = {
                    'tokenIn': self.eth_address,
                    'tokenOut': self.usdt_address,
                    'fee': 3000,  # 0.3%
                    'recipient': account.address,
                    'deadline': deadline,
                    'amountIn': amount_in,
                    'amountOutMinimum': 0,  # Untuk testing
                    'sqrtPriceLimitX96': 0
                }
                
                swap_tx = router_contract.functions.exactInputSingle(
                    params
                ).build_transaction({
                    'from': account.address,
                    'nonce': self.w3.eth.get_transaction_count(account.address),
                    'gas': 500000,  # Meningkatkan gas limit
                    'gasPrice': self.w3.eth.gas_price,
                    'chainId': self.w3.eth.chain_id
                })
                
                # Sign dan kirim transaksi swap
                signed_swap = Account.sign_transaction(swap_tx, private_key_bytes)
                swap_tx_hash = self.w3.eth.send_raw_transaction(signed_swap.raw_transaction)
                receipt = self.w3.eth.wait_for_transaction_receipt(swap_tx_hash)
                
                return {
                    'status': 'success',
                    'transaction_hash': swap_tx_hash.hex(),
                    'amount_in': amount_in
                }
                
            except Exception as e:
                retry_count += 1
                print(f"{Fore.RED}Error: {str(e)}. Mencoba ulang ({retry_count}/{max_retries})...{Style.RESET_ALL}")
                time.sleep(5)  # Jeda sebelum mencoba ulang
        
        return {
            'status': 'error',
            'message': f"Gagal setelah {max_retries} percobaan"
        }

    def swap_btc_to_usdt(self, private_key, amount_in):
        max_retries = 3  # Maksimal percobaan ulang
        retry_count = 0
        
        while retry_count < max_retries:
            try:
                # Buat instance akun
                if private_key.startswith('0x'):
                    private_key_bytes = bytes.fromhex(private_key[2:])
                else:
                    private_key_bytes = bytes.fromhex(private_key)
                    
                account = Account.from_key(private_key_bytes)
                
                # Approve BTC
                btc_abi = [
                    {
                        "constant": False,
                        "inputs": [
                            {"name": "_spender", "type": "address"},
                            {"name": "_value", "type": "uint256"}
                        ],
                        "name": "approve",
                        "outputs": [{"name": "", "type": "bool"}],
                        "payable": False,
                        "stateMutability": "nonpayable",
                        "type": "function"
                    }
                ]
                
                btc_contract = self.w3.eth.contract(address=self.btc_address, abi=btc_abi)
                
                approve_tx = btc_contract.functions.approve(
                    self.router_address,
                    amount_in
                ).build_transaction({
                    'from': account.address,
                    'nonce': self.w3.eth.get_transaction_count(account.address),
                    'gas': 100000,
                    'gasPrice': self.w3.eth.gas_price,
                    'chainId': self.w3.eth.chain_id
                })
                
                # Sign dan kirim transaksi approval
                signed_approve = Account.sign_transaction(approve_tx, private_key_bytes)
                tx_approve_hash = self.w3.eth.send_raw_transaction(signed_approve.raw_transaction)
                self.w3.eth.wait_for_transaction_receipt(tx_approve_hash)
                
                # Swap tokens
                router_contract = self.w3.eth.contract(address=self.router_address, abi=self.router_abi)
                deadline = self.w3.eth.get_block('latest').timestamp + 300
                
                params = {
                    'tokenIn': self.btc_address,
                    'tokenOut': self.usdt_address,
                    'fee': 3000,  # 0.3%
                    'recipient': account.address,
                    'deadline': deadline,
                    'amountIn': amount_in,
                    'amountOutMinimum': 0,  # Untuk testing
                    'sqrtPriceLimitX96': 0
                }
                
                swap_tx = router_contract.functions.exactInputSingle(
                    params
                ).build_transaction({
                    'from': account.address,
                    'nonce': self.w3.eth.get_transaction_count(account.address),
                    'gas': 500000,  # Meningkatkan gas limit
                    'gasPrice': self.w3.eth.gas_price,
                    'chainId': self.w3.eth.chain_id
                })
                
                # Sign dan kirim transaksi swap
                signed_swap = Account.sign_transaction(swap_tx, private_key_bytes)
                swap_tx_hash = self.w3.eth.send_raw_transaction(signed_swap.raw_transaction)
                receipt = self.w3.eth.wait_for_transaction_receipt(swap_tx_hash)
                
                return {
                    'status': 'success',
                    'transaction_hash': swap_tx_hash.hex(),
                    'amount_in': amount_in
                }
                
            except Exception as e:
                retry_count += 1
                print(f"{Fore.RED}Error: {str(e)}. Mencoba ulang ({retry_count}/{max_retries})...{Style.RESET_ALL}")
                time.sleep(5)  # Jeda sebelum mencoba ulang
        
        return {
            'status': 'error',
            'message': f"Gagal setelah {max_retries} percobaan"
        }

def read_private_keys():
    try:
        with open('priv.txt', 'r') as file:
            private_keys = file.readlines()
            private_keys = [key.strip() for key in private_keys if key.strip()]
            
            # Validasi setiap private key
            valid_keys = []
            for key in private_keys:
                if key.startswith('0x'):
                    key = key[2:]
                if len(key) == 64 and all(c in '0123456789abcdefABCDEF' for c in key):
                    valid_keys.append('0x' + key)
                else:
                    print(f"{Fore.RED}Private key tidak valid: {key[:6]}...{key[-4:]}{Style.RESET_ALL}")
            
            if not valid_keys:
                raise Exception("Tidak ada private key yang valid di file priv.txt")
            
            return valid_keys
            
    except FileNotFoundError:
        raise Exception("File priv.txt tidak ditemukan")
    except Exception as e:
        raise Exception(f"Error membaca private key: {str(e)}")

# Contoh penggunaan
if __name__ == "__main__":
    try:
        print_sky_header()
        print(f"{Fore.CYAN}Memulai program swap otomatis untuk multi-akun...{Style.RESET_ALL}\n")
        
        swapper = TokenSwapper()
        private_keys = read_private_keys()
        print(f"{Fore.GREEN}Berhasil memuat {len(private_keys)} private key.{Style.RESET_ALL}")
        
        while True:
            # Loop untuk setiap akun
            for idx, private_key in enumerate(private_keys):
                print(f"\n{Fore.YELLOW}{Style.BRIGHT}Memproses Akun #{idx + 1}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}Alamat Akun: {Account.from_key(bytes.fromhex(private_key[2:])).address}{Style.RESET_ALL}")
                
                # Generate nominal random untuk USDT ke ETH (5-10 USDT)
                usdt_decimals = 18
                random_amount_eth = round(random.uniform(5, 10), 2)  # Random antara 5-10 USDT
                amount_to_swap_eth = int(random_amount_eth * (10 ** usdt_decimals))
                
                # Generate nominal random untuk USDT ke BTC (5-10 USDT, berbeda dengan USDT ke ETH)
                random_amount_btc = round(random.uniform(5, 10), 2)  # Random antara 5-10 USDT
                while random_amount_btc == random_amount_eth:  # Pastikan nominal berbeda
                    random_amount_btc = round(random.uniform(5, 10), 2)
                amount_to_swap_btc = int(random_amount_btc * (10 ** usdt_decimals))
                
                # Timestamp untuk log
                current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                print(f"\n{Fore.CYAN}{Style.BRIGHT}[{current_time}] Transaksi #{1}{Style.RESET_ALL}")
                print(f"{Fore.CYAN}{'='*50}{Style.RESET_ALL}")
                
                # Swap USDT ke ETH
                print(f"{Fore.MAGENTA}Menukar {random_amount_eth} USDT ke ETH...{Style.RESET_ALL}")
                result_eth = swapper.swap_usdt_to_eth(private_key, amount_to_swap_eth)
                
                if result_eth['status'] == 'success':
                    tx_hash = result_eth['transaction_hash']
                    if not tx_hash.startswith('0x'):
                        tx_hash = '0x' + tx_hash
                        
                    print(f"{Fore.GREEN}Status: {result_eth['status']}")
                    print(f"Hash Transaksi: {tx_hash}")
                    print(f"Jumlah USDT: {random_amount_eth}")
                    print(f"{Fore.BLUE}Block Explorer URL: https://chainscan-newton.0g.ai/tx/{tx_hash}{Style.RESET_ALL}")
                    
                    # Swap ETH ke USDT (50% dari jumlah USDT ke ETH)
                    eth_amount_to_swap = int((random_amount_eth / 2) * (10 ** usdt_decimals))
                    print(f"\n{Fore.MAGENTA}Menukar {random_amount_eth / 2} ETH ke USDT...{Style.RESET_ALL}")
                    result_eth_back = swapper.swap_eth_to_usdt(private_key, eth_amount_to_swap)
                    
                    if result_eth_back['status'] == 'success':
                        back_tx_hash = result_eth_back['transaction_hash']
                        if not back_tx_hash.startswith('0x'):
                            back_tx_hash = '0x' + back_tx_hash
                            
                        print(f"{Fore.GREEN}Status: {result_eth_back['status']}")
                        print(f"Hash Transaksi: {back_tx_hash}")
                        print(f"Jumlah ETH: {random_amount_eth / 2}")
                        print(f"{Fore.BLUE}Block Explorer URL: https://chainscan-newton.0g.ai/tx/{back_tx_hash}{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.RED}Status: {result_eth_back['status']}")
                        print(f"{Fore.RED}Error: {result_eth_back['message']}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}Status: {result_eth['status']}")
                    print(f"{Fore.RED}Error: {result_eth['message']}{Style.RESET_ALL}")
                
                # Swap USDT ke BTC
                print(f"\n{Fore.MAGENTA}Menukar {random_amount_btc} USDT ke BTC...{Style.RESET_ALL}")
                result_btc = swapper.swap_usdt_to_btc(private_key, amount_to_swap_btc)
                
                if result_btc['status'] == 'success':
                    tx_hash = result_btc['transaction_hash']
                    if not tx_hash.startswith('0x'):
                        tx_hash = '0x' + tx_hash
                        
                    print(f"{Fore.GREEN}Status: {result_btc['status']}")
                    print(f"Hash Transaksi: {tx_hash}")
                    print(f"Jumlah USDT: {random_amount_btc}")
                    print(f"{Fore.BLUE}Block Explorer URL: https://chainscan-newton.0g.ai/tx/{tx_hash}{Style.RESET_ALL}")
                    
                    # Swap BTC ke USDT (50% dari jumlah USDT ke BTC)
                    btc_amount_to_swap = int((random_amount_btc / 2) * (10 ** usdt_decimals))
                    print(f"\n{Fore.MAGENTA}Menukar {random_amount_btc / 2} BTC ke USDT...{Style.RESET_ALL}")
                    result_btc_back = swapper.swap_btc_to_usdt(private_key, btc_amount_to_swap)
                    
                    if result_btc_back['status'] == 'success':
                        back_tx_hash = result_btc_back['transaction_hash']
                        if not back_tx_hash.startswith('0x'):
                            back_tx_hash = '0x' + back_tx_hash
                            
                        print(f"{Fore.GREEN}Status: {result_btc_back['status']}")
                        print(f"Hash Transaksi: {back_tx_hash}")
                        print(f"Jumlah BTC: {random_amount_btc / 2}")
                        print(f"{Fore.BLUE}Block Explorer URL: https://chainscan-newton.0g.ai/tx/{back_tx_hash}{Style.RESET_ALL}")
                    else:
                        print(f"{Fore.RED}Status: {result_btc_back['status']}")
                        print(f"{Fore.RED}Error: {result_btc_back['message']}{Style.RESET_ALL}")
                else:
                    print(f"{Fore.RED}Status: {result_btc['status']}")
                    print(f"{Fore.RED}Error: {result_btc['message']}{Style.RESET_ALL}")
                
                # Jeda random antara akun (1-2 menit)
                sleep_time = random.randint(60, 120)
                print(f"\n{Fore.YELLOW}Menunggu {sleep_time} detik sebelum melanjutkan ke akun berikutnya...{Style.RESET_ALL}")
                time.sleep(sleep_time)
            
            # Jeda setelah semua akun selesai (24 jam)
            next_run_time = datetime.datetime.now() + datetime.timedelta(hours=24)
            print(f"\n{Fore.YELLOW}{Style.BRIGHT}Semua akun telah diproses. Istirahat selama 24 jam.")
            print(f"{Fore.YELLOW}Akan melanjutkan pada: {next_run_time.strftime('%Y-%m-%d %H:%M:%S')}")
            time.sleep(24 * 3600)  # Konversi jam ke detik
            
    except Exception as e:
        print(f"{Fore.RED}{Style.BRIGHT}Error: {str(e)}{Style.RESET_ALL}")
