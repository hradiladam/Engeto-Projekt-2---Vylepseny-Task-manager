import pytest
from tests.test_init import create_test_db, create_test_table, drop_test_db, drop_test_table
from src.config import connect_to_test_db
from src.task_manager import pridat_ukol_db, aktualizovat_ukol_db, odstranit_ukol_db
import mysql.connector
from mysql.connector import Error


# Fixture pro vytvoreni a smazani testovaci databaze a tabulky na urovni cele testovaci session 
@pytest.fixture(scope="session", autouse=True)
def db_connection():
    create_test_db()
    connection = connect_to_test_db()
    yield connection
    connection.close()
    drop_test_db()


# Fixture na urovni kazde testovaci funkce pro praci s kurzorem
@pytest.fixture(scope="function", autouse=True)
def db_cursor(db_connection):
    create_test_table()
    cursor = db_connection.cursor()
    yield cursor
    cursor.close()
    drop_test_table()


"""TESTY"""


# Test: overi, ze platny ukol je spravne vlozen do db
def test_pridat_ukol_db_platny(db_connection, db_cursor):
    nazev = "Testovací úkol"
    popis = "Popis testovacího úkolu"

    pridat_ukol_db(db_connection, nazev, popis)

    db_cursor.execute("SELECT nazev, popis FROM ukoly ORDER BY id DESC LIMIT 1")
    result = db_cursor.fetchone()

    assert result == (nazev, popis)


# Test: overi, ze pokus o vlzoeni ukolu s NULL nazvem selze na urovni databaze
def test_pridat_ukol_db_odmitne_null(db_connection, db_cursor): # db_cursor zajisti, ze tabulka existuje a pote je smazana
    nazev = None
    popis = "Testovaci popis"

    # Zjisti pocet ukolu pred pokusem o pridani
    db_cursor.execute("SELECT COUNT(*) FROM ukoly")
    count_before = db_cursor.fetchone()[0]

    # Ocekavame, ze bude vyhozena chyba kvuli NULL hodnote
    with pytest.raises(mysql.connector.Error):
        pridat_ukol_db(db_connection, nazev, popis)
    
    # Zjisti pocet ukolu po pokusu
    db_cursor.execute("SELECT COUNT(*) FROM ukoly")
    count_after = db_cursor.fetchone()[0]

    # Overi, ze pocvet ukolu je stejny
    assert count_before == count_after


# Test: overi, ze db odmitne ukolu s prazdnym nazvem (i když Python validace je už ve vstupu)
@pytest.mark.parametrize("invalid_nazev", ["", "   "])
def test_pridat_ukol_db_odmitne_prazdny_nazev(db_connection, db_cursor, invalid_nazev):
    popis = "Testovací popis"

    # Zjisti pocet ukolu pred pokusem
    db_cursor.execute("SELECT COUNT(*) FROM ukoly")
    count_before = db_cursor.fetchone()[0]
    
    # Ocekavame, ze bude vyhozena chyba kvuli prazdnym hodnotam
    with pytest.raises(mysql.connector.Error):
        pridat_ukol_db(db_connection, invalid_nazev, popis)

    # Zjisti pocet ukolu po pokusu
    db_cursor.execute("SELECT COUNT(*) FROM ukoly")
    count_after = db_cursor.fetchone()[0]

    # Overi, ze pocvet ukolu je stejny
    assert count_before == count_after


# Test: overi, ze zmena stavu ukolu na platnou hodnotu (probíhá / hotovo) probehne spravne
@pytest.mark.parametrize("novy_stav", ["probíhá", "hotovo"])
def test_aktualizovat_stav_db_platny_vstup(db_connection, db_cursor, novy_stav):
    nazev = "Testovací úkol pro aktualizaci"
    popis = "Popis úkolu"
    vychozi_stav = "nezahájeno"

    # Prime vlzoeni testovaciho ukolu do databaze
    db_cursor.execute(
        "INSERT INTO ukoly (nazev, popis, stav) VALUES (%s, %s, %s)",
        (nazev, popis, vychozi_stav)
    )
    db_connection.commit()

    # Ziskani ID nove vlozeneho ukolu
    db_cursor.execute("SELECT id FROM ukoly ORDER BY id DESC LIMIT 1")
    id_ukolu = db_cursor.fetchone()[0]

    # Provedeni aktualizace
    aktualizace_okay = aktualizovat_ukol_db(db_connection, id_ukolu, novy_stav)
    assert aktualizace_okay is True

    # Ocereniu zmeny v databai
    db_cursor.execute("SELECT stav FROM ukoly WHERE id = %s", (id_ukolu,))
    stav_v_db = db_cursor.fetchone()[0]
    assert stav_v_db == novy_stav


# Test: overi, ze pokus o vlozeni neplatne hodnoty do sktualizace stavu vrati false
def test_aktualizovat_stav_db_neplatny_stav(db_connection, db_cursor):
    # Nejprve vloimme ukol, na kterem testujeme
    db_cursor.execute(
        "INSERT INTO ukoly (nazev, popis) VALUES (%s, %s)",
        ("Úkol pro test neplatného stavu", "Popis")
    )
    db_connection.commit()

    db_cursor.execute("SELECT id FROM ukoly ORDER BY id DESC LIMIT 1")
    id_ukolu = db_cursor.fetchone()[0]

    # Ziskame puvodni stav ukolu (default)
    db_cursor.execute("SELECT stav FROM ukoly WHERE id = %s", (id_ukolu,))
    state_before = db_cursor.fetchone()[0]

    # Zkusime aktualizovat na neplatný stav
    invalid_state = "čeká_na_schválení"

    aktualizace_okay = aktualizovat_ukol_db(db_connection, id_ukolu, invalid_state)
    assert aktualizace_okay is False

    # Overime, ze se stav nezmenil
    db_cursor.execute("SELECT stav FROM ukoly WHERE id = %s", (id_ukolu,))
    state_after = db_cursor.fetchone()[0]
    assert state_before == state_after


# Test, ktery overi smazani ukolu z databaze
def test_odstranit_ukol_db_platny_ukol(db_connection, db_cursor):
    nazev = "Úkol k odstranění"
    popis = "Popis odstranitelného úkolu"
    
    db_cursor.execute(
        "INSERT INTO ukoly (nazev, popis) VALUES (%s, %s)",(nazev, popis)
        )
    db_connection.commit()

    db_cursor.execute("SELECT id FROM ukoly ORDER BY id DESC LIMIT 1")
    id_ukolu = db_cursor.fetchone()[0]

    # Overime, ze pokus odstranit ukol probehne
    odstraneni_okay = odstranit_ukol_db(db_connection, id_ukolu)
    assert odstraneni_okay is True

    # Overime, ze ukol byl odstranen
    db_cursor.execute("SELECT COUNT(*) FROM ukoly WHERE id = %s", (id_ukolu,))
    pocet = db_cursor.fetchone()[0]
    assert pocet == 0


# Test, ktery overi, ze vlozeni neplatneho polkusu o odstraneni ukolu vrati false
def test_odstranit_ukol_db_neplatne_id(db_connection, db_cursor):
    neplatne_id = 999999  # Předpokládejme, že takové ID v DB není

    db_cursor.execute("SELECT COUNT(*) FROM ukoly")
    count_before = db_cursor.fetchone()[0]

    # Pokusime se odstranit ukol s neplatnym ID, mame ocekavat False
    odstraneni_okay = odstranit_ukol_db(db_connection, neplatne_id)
    assert odstraneni_okay is False

    db_cursor.execute("SELECT COUNT(*) FROM ukoly")
    count_after = db_cursor.fetchone()[0]

    # Overime, ze pocet ukolu je nezmenen (zadny ukol nebyl smazan)
    assert count_before == count_after

