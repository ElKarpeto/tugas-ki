# Tugas Keamanan Informasi 2

Tujuan tugas ini adalah untuk menerapkan enkripsi DES untuk komunikasi antar komputer

## Isi Repositori

-   [`des.py`](./des.py), digunakan sebagai utilitas enkripsi DES
-   [`server.py`](./server.py), server yang meng-_handle_ semua message dari _client_ dan mendistribusikannya
-   [`des.py`](./des.py), _client_ untuk berkomunikasi antar komputer

## Cara menjalankan

-   Instalasi

    ```sh
    git clone "https://github.com/ElKarpeto/tugas-ki"
    cd tugas-ki/tugas-2
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
