import mysql.connector
from mysql.connector import Error
from config import connect_to_db 


def create_table(connection):
    if connection:
        try:
            # vytvoreni tabulky, pokud neexistuje
            cursor = connection.cursor()
            sql = """
                CREATE TABLE IF NOT EXISTS ukoly (
                    id INT AUTO_INCREMENT PRIMARY KEY, 
                    nazev VARCHAR(50) NOT NULL,
                    popis TEXT NOT NULL,
                    stav ENUM('nezahájeno', 'hotovo', 'probíhá') NOT NULL DEFAULT 'nezahájeno',
                    datum_vytvoreni DATETIME DEFAULT CURRENT_TIMESTAMP,
                    CHECK (CHAR_LENGTH(TRIM(nazev)) > 0) 
                );
            """
            cursor.execute(sql)
            connection.commit()
        
        except Error as error:
            print(f"\n❌ Chyba při vytváření tabulky: {error}")
        
        finally:
            cursor.close()


# Funkce pro vlozeni ukolu do databaze
def pridat_ukol_db(connection, nazev, popis):
    try:
        with connection.cursor() as cursor:
            cursor.execute("INSERT INTO ukoly (nazev, popis) VALUES (%s, %s)", (nazev, popis))
            connection.commit()
            
            print(f"\n✅  Úkol byl přidán s ID: {cursor.lastrowid}")
    
    except mysql.connector.Error as error:
        print(f"\n❌  Chyba při přidávání úkolu: {error}")
        raise


# Funkce vytvoreni noveho ukolu
def pridat_ukol(connection):
    if not connection:
        return
    
    while True:
        try:
            nazev = input("\nZadejte název úkolu: ").strip()
            popis = input("Zadejte popis úkolu: ").strip()

            if not nazev:
                print("\n⚠️  Název úkolu nesmí být prázdný ani obsahovat pouze mezery. Zkuste znovu.\n")
                continue
            
            if not popis:
                print("\n⚠️  Popis úkolu nesmí být prázdný. Zkuste to znovu.")
                continue

            pridat_ukol_db(connection, nazev, popis)
            break
            
        except Exception as error:
            print("Něco se nepovedlo: ", error)
            break


# Funkce pro nacteni ukolu z databaze
def zobrazit_ukoly_db(connection):
    try: 
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, nazev, popis, stav, datum_vytvoreni FROM ukoly WHERE stav IN ('nezahájeno', 'probíhá')")
            return cursor.fetchall()
    
    except mysql.connector.Error as error:
        print(f"❌  Chyba při vybírání úkolů k zobrazení: {error}")
        raise

# Funkce pro zobrazeni ukolu uzivateli
def zobrazit_ukoly(connection):
    if not connection:
        return
    
    ukoly = zobrazit_ukoly_db(connection)
    
    if not ukoly:
            print(f"\n⚠️  Žádné úkoly k zobrazení.")
    
    else:
       for index, ukol in enumerate(ukoly, 1):
            print(f"{index}. ID: {ukol[0]} | Název: {ukol[1]} | Popis: {ukol[2]} | Stav: {ukol[3]} | Vytvořeno: {ukol[4].strftime('%d.%m.%Y %H:%M')}") 
    

# Pomocna funkce pro vybrani id v databazi  
def vybrat_ukol_id_db(connection):
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT id, nazev FROM ukoly")
            return cursor.fetchall()
    
    except mysql.connector.Error as error:
        print(f"❌  Chyba při vybrani ID úkolů: {error}")
        return []


# Pomocna funkce pro vybrani id
def vybrat_ukol_id(connection):
    ukoly = vybrat_ukol_id_db(connection)
    
    if not ukoly:
        print("\n⚠️  Seznam úkolů je prázdný.")
        return None

    print("\n📋  Seznam úkolů:")
    for index, (id_ukolu, nazev) in enumerate(ukoly, 1):
        print(f"{index}. ID: {id_ukolu} | Název: {nazev}")

    platna_id = {str(id_ukolu) for id_ukolu, _ in ukoly}

    while True:
        volba = input("\nZadejte ID úkolu: ").strip()
        if volba not in platna_id:
            print("\n⚠️  Neplatné ID. Zadejte prosím číslo z výpisu.")
        else:
            return int(volba)


# Funkce, ktera zmeni "probiha", "probihá" a "probíha" na "probíhá"
def normalizuj_stav(stav):
    stav = stav.strip().lower()
    if stav in ["probiha", "probihá", "probíha"]:
        return "probíhá"
    return stav


# Funkce, ktera aktualizuje stav ukolu v databazi
def aktualizovat_ukol_db(connection, id_ukolu, novy_stav):
    try:
        with connection.cursor() as cursor:
            cursor.execute("UPDATE ukoly SET stav = %s WHERE id = %s", (novy_stav, id_ukolu))
            connection.commit()
        return True

    except mysql.connector.Error as error:
        print(f"\n❌  Chyba při aktualizaci úkolu: {error}")
        connection.rollback()  # rollback pro vycisteni selhane transakce
        return False


# Funkce, ktera komunikuje s uzivatelem o aktualizovani stavu ukolu
def aktualizovat_ukol(connection):
    if not connection:
        return
   
    try:
        id_ukolu = vybrat_ukol_id(connection)

        if id_ukolu is None:
            return

        while True:
            novy_stav = input("\nZadejte nový stav ('hotovo' nebo 'probíhá'): ")
            novy_stav = normalizuj_stav(novy_stav)
            
            if novy_stav in ['hotovo', 'probíhá']:
                break
            else:
                print("\n⚠️  Neplatný stav. Zadejte pouze 'probíhá' nebo 'hotovo'.")
            
        if aktualizovat_ukol_db(connection, id_ukolu, novy_stav):
            print("\n✅  Stav úkolu byl aktualizován.")

    except Exception as error:
        print(f"\n❌  Něco se nepovedlo: {error}")


# Funkce, ktera odstrani ukol z databaze podle ID
def odstranit_ukol_db(connection, id_ukolu):
    try:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM ukoly WHERE id = %s", (id_ukolu,))
            connection.commit()
        
            if cursor.rowcount == 0:
                # Nevymazan zadny radek => invalidni id
                return False
        
        return True

    except mysql.connector.Error as error:
        print(f"❌  Chyba při odstraňování úkolu: {error}")
        return False
    

# Funkce pro inyeraktivni odstraneni ukolu skrze input uzivatele
def odstranit_ukol(connection):
    if not connection:
        return
    
    try:
        id_ukolu = vybrat_ukol_id(connection)
        if id_ukolu is None:
            return

        confirmation = input(f"\nOpravdu chcete odstranit úkol s ID {id_ukolu}? (a/n): ").strip().lower()
        if confirmation == "a":
            if odstranit_ukol_db(connection, id_ukolu):
                print("\n🗑️  Úkol byl úspěšně odstraněn.")
        else:
            print("\nℹ️  Odstranění zrušeno.")
    
    except Exception as error:
        print(f"❌  Chyba při odstraňování úkolu: {error}")


# Hlavni menu aplikace
def hlavni_menu(connection):
    while True:
        print("""
            =================== Správce úkolů - Hlavní menu ===================
            1. Přidat úkol
            2. Zobrazit úkoly
            3. Aktualizovat úkol
            4. Odstranit úkol
            5. Konec programu
            ===================================================================
          """)
    
        volba = input("\nVyberte možnost (1-5): ")
        
        if volba == "1":
            pridat_ukol(connection)
        elif volba == "2":
            zobrazit_ukoly(connection)  
        elif volba == "3":
            aktualizovat_ukol(connection)
        elif volba == "4":
            odstranit_ukol(connection)
        elif volba == "5":
            print("\n👋  Program ukončen.")
            break 
        else:
            print("\n⚠️  Neplatná volba. Zkuste znovu.")


# Vytvori tabulku ukoly v db a spousti hlavni menu
if __name__ == "__main__":
    connection = connect_to_db()
    if connection:
        try:
            create_table(connection)
            hlavni_menu(connection)
        finally:
            connection.close()
    

