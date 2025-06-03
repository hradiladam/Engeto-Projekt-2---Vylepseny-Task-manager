import mysql.connector
import sys
from mysql.connector import Error

# Konfigurace pripojeni k db  
DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "ABtmdz247!"
}

    # Pripoji se k sql bez specificke databaze
def connect_to_mysql():
    try:
        connection = mysql.connector.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
        )
        return connection
    
    except Error as error:
        print(f"\n❌ Chyba při připojení k MySQL: {error}")
        sys.exit(1)


def connect_to_db():
    # Pripoji se k produkcni databazi a vrati spojeni
    try:
        connection = mysql.connector.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database="spravce_ukolu"
        )
        return connection
    
    except Error as error:
        print(f"\n❌ Chyba při připojení k databázi: {error}")
        sys.exit(1)


def connect_to_test_db():
    # Pripoji se k testovaci databazi a vrati spojeni
    # Az bude testovaci databaze vytvorena v test_init.py, tato config bude zpetne pouzito v testovacich fixturech
    try:
        connection = mysql.connector.connect(
            host=DB_CONFIG["host"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"],
            database="testovaci_spravce_ukolu" # Testovací databáze
        )
        return connection
    
    except Error as error:
        print(f"\n❌  Chyba při připojení k testovací databázi: {error}")
        sys.exit(1)