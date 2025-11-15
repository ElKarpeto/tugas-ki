# Tugas Keamanan Informasi 3

Tujuan tugas ini adalah untuk menerapkan algoritma kunci asimetrik untuk mengirimkan kunci yang akan digunakan untuk enkripsi DES sehingga memungkinkan komunikasi antar komputer

## Isi Repositori

-   [`des.py`](./des.py), utilitas algoritma DES
-   [`rsa.py`](./rsa.py), utilitas algoritma RSA
-   [`server.py`](./server.py), server yang meng-_handle_ semua message dari _client_ dan mendistribusikannya
-   [`des.py`](./des.py), _client_ untuk berkomunikasi antar komputer

## Cara menjalankan

-   Instalasi

    ```sh
    git clone "https://github.com/ElKarpeto/tugas-ki"
    cd tugas-ki/tugas-3
    pip install sympy # jika tidak memiliki library sympy
    ```

-   Menjalankan _server_

    ```sh
    python3 server.py # linux/mac
    python server.py # windows
    ```

-   Menjalankan _client_
    ```sh
    python3 client.py # linux/mac
    python client.py # windows
    ```
