from src.config import connect_to_test_db, connect_to_mysql
import mysql.connector

# Pripoji se k mysql, vytvori testovaci databaze a tabulku
def create_test_db():
    try:
        with connect_to_mysql() as connection:  # Pripoji se k mysql | (connection.close() a cursor.close() nejsou treba je li pouzit 'with')
            with connection.cursor() as cursor:
                cursor.execute("CREATE DATABASE IF NOT EXISTS testovaci_spravce_ukolu") # Vytvori testovaci databaze
                connection.commit()

    except mysql.connector.Error as error:
        print(f"\n❌ Chyba při vytváření testovací databáze: {error}")
        raise

    print("\n✔️  Testovací databaze vytvořena.")


# Vytvori testovaci tabulku 
def create_test_table():
    try:
        with connect_to_test_db() as connection:  # Pripoji se k testovaci databazi
            with connection.cursor() as cursor:
                cursor.execute("CREATE TABLE IF NOT EXISTS ukoly LIKE spravce_ukolu.ukoly") # Vytvori testovaci ukoly
                connection.commit()

    except mysql.connector.Error as error:
        print(f"\n❌ Chyba při vytváření testovací tabulky: {error}")
        raise

    print("\n✔️  Testovací tabulka vytvořena.")


# Smaze testovaci databazi
def drop_test_db():
    try:
        with connect_to_mysql() as connection:     # Pripoji se k mysql
            with connection.cursor() as cursor:
                cursor.execute("DROP DATABASE IF EXISTS testovaci_spravce_ukolu")
                connection.commit()

    except mysql.connector.Error as error:
        print(f"\n❌ Chyba při mazání testovací databáze: {error}")
        raise
    
    print("\n✔️  Testovací databáze smazána.")


# Smaze testovaci tabulku
def drop_test_table():
    try:
        with connect_to_test_db() as connection:  # Pripoji se k testovaci databazi
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM ukoly") # Smaze testovaci tabulku
                connection.commit()

    except mysql.connector.Error as error:
        print(f"\n❌ Chyba při mazani testovaci tabulky: {error}")
        raise

    print("\n✔️  Testovací tabulka smazana.")


if __name__ == "__main__":
    create_test_db()
