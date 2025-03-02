---

## **0G HUB Swapper (Multi-Account)**

### **Deskripsi**
Script ini adalah sebuah program Python yang dirancang untuk melakukan **swap token otomatis** pada jaringan blockchain **0G-Newton-Testnet**. Program ini mendukung multi-akun, di mana setiap akun akan melakukan serangkaian transaksi swap antara **USDT**, **ETH**, dan **BTC**. Script ini menggunakan library `web3.py` untuk berinteraksi dengan blockchain dan `eth_account` untuk mengelola akun Ethereum.

Program ini cocok untuk digunakan dalam lingkungan pengujian (testnet) dan dapat diadaptasi untuk kebutuhan lainnya seperti arbitrase atau manajemen portofolio otomatis.

---

### **Fitur Utama**
1. **Multi-Akun Support**:
   - Program dapat memproses banyak akun sekaligus dengan membaca private key dari file `priv.txt`.
   - Setiap akun akan melakukan 4 transaksi swap:
     - USDT ke ETH
     - ETH ke USDT (50% dari jumlah USDT awal)
     - USDT ke BTC
     - BTC ke USDT (50% dari jumlah USDT awal)

2. **Nominal Swap yang Berbeda**:
   - Nominal swap untuk USDT ke ETH dan USDT ke BTC dihasilkan secara acak antara 5-10 USDT, dan dipastikan berbeda untuk setiap transaksi.

3. **Retry Mechanism**:
   - Jika terjadi error saat melakukan swap, program akan mencoba mengulangi proses swap tersebut hingga **3 kali**.
   - Setiap percobaan ulang akan menunggu **5 detik** sebelum mencoba lagi.

4. **Jeda Waktu**:
   - **Antara akun**: 1-2 menit (random).
   - **Setelah semua akun selesai**: 24 jam.

5. **Tampilan Informasi**:
   - Setiap transaksi menampilkan informasi yang jelas, termasuk:
     - Alamat akun.
     - Jenis swap.
     - Jumlah token.
     - Status transaksi (berhasil/gagal).
     - Hash transaksi dan link block explorer.

6. **Keamanan**:
   - Private key disimpan dalam file `priv.txt` dan divalidasi sebelum digunakan.
   - Program tidak menyimpan atau mengirim private key ke luar lingkungan lokal.

---

### **Cara Menggunakan**
1. **Persiapan**:
   - Pastikan Python 3.x sudah terinstal.
   - Install dependency yang diperlukan dengan menjalankan perintah berikut:
     ```bash
     pip install web3 eth_account colorama
     ```

2. **Setup Private Key**:
   - Buat file `priv.txt` di folder yang sama dengan script.
   - Tulis private key Ethereum Anda, satu per baris. Contoh:
     ```
     4f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1d
     5f3edf983ac636a65a842ce7c78d9aa706d3b113bce9c46f30d7d21715b23b1e
     ```

3. **Jalankan Script**:
   - Jalankan script dengan perintah berikut:
     ```bash
     python swapper.py
     ```

4. **Monitor Transaksi**:
   - Program akan menampilkan log transaksi di terminal.
   - Jika terjadi error, program akan mencoba mengulangi proses swap hingga berhasil atau mencapai batas maksimal percobaan.

---

### **Struktur File**
- **`swapper.py`**: File utama yang berisi logika swap dan manajemen akun.
- **`priv.txt`**: File teks yang berisi private key akun Ethereum (satu per baris).

---

### **Detail Teknis**
1. **Library yang Digunakan**:
   - `web3`: Untuk berinteraksi dengan blockchain Ethereum.
   - `eth_account`: Untuk mengelola akun Ethereum dan menandatangani transaksi.
   - `colorama`: Untuk menambahkan warna pada output terminal.
   - `random`: Untuk menghasilkan nominal swap yang acak.
   - `time` dan `datetime`: Untuk mengatur jeda waktu dan mencatat waktu transaksi.

2. **Kontrak yang Digunakan**:
   - **Router DEX**: `0xD86b764618c6E3C078845BE3c3fCe50CE9535Da7`
   - **Token**:
     - USDT: `0x9A87C2412d500343c073E5Ae5394E3bE3874F76b`
     - ETH: `0xce830D0905e0f7A9b300401729761579c5FB6bd6`
     - BTC: `0x1e0d871472973c562650e991ed8006549f8cbefc`

3. **Fungsi Utama**:
   - `swap_usdt_to_eth`: Melakukan swap dari USDT ke ETH.
   - `swap_usdt_to_btc`: Melakukan swap dari USDT ke BTC.
   - `swap_eth_to_usdt`: Melakukan swap dari ETH ke USDT.
   - `swap_btc_to_usdt`: Melakukan swap dari BTC ke USDT.
   - `read_private_keys`: Membaca dan memvalidasi private key dari file `priv.txt`.

---

### **Contoh Output**
```
==================================================
            0G HUB Swapper (Multi-Account)
                  By : SKY
==================================================
Memulai program swap otomatis untuk multi-akun...

Berhasil memuat 2 private key.

Memproses Akun #1
Alamat Akun: 0x123...abc

[2023-10-25 12:34:56] Transaksi #1
==================================================
Menukar 8.50 USDT ke ETH...
Status: success
Hash Transaksi: 0x123...def
Jumlah USDT: 8.50
Block Explorer URL: https://chainscan-newton.0g.ai/tx/0x123...def

Menukar 4.25 ETH ke USDT...
Status: success
Hash Transaksi: 0x456...ghi
Jumlah ETH: 4.25
Block Explorer URL: https://chainscan-newton.0g.ai/tx/0x456...ghi

Menukar 7.20 USDT ke BTC...
Status: success
Hash Transaksi: 0x789...jkl
Jumlah USDT: 7.20
Block Explorer URL: https://chainscan-newton.0g.ai/tx/0x789...jkl

Menukar 3.60 BTC ke USDT...
Status: success
Hash Transaksi: 0xabc...mno
Jumlah BTC: 3.60
Block Explorer URL: https://chainscan-newton.0g.ai/tx/0xabc...mno

Menunggu 90 detik sebelum melanjutkan ke akun berikutnya...

Memproses Akun #2
Alamat Akun: 0x456...def
...
```

---

### **Catatan**
- Script ini hanya untuk **tujuan pengujian** di jaringan testnet. Jangan gunakan private key akun utama Anda.
- Pastikan untuk memahami risiko sebelum menggunakan script ini di jaringan mainnet.
- Script ini tidak bertanggung jawab atas kehilangan dana atau kesalahan penggunaan.

---

### **Lisensi**
Script ini dilisensikan di bawah [MIT License](https://opensource.org/licenses/MIT). Silakan modifikasi dan distribusikan sesuai kebutuhan Anda.

---
