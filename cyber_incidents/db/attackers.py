import utils
import sqlite3


def insert_attacker(affiliation,sponsor,cursor):
    try:
        query="""INSERT OR IGNORE INTO Attackers VALUES (?,?)"""
        query1="""INSERT OR IGNORE INTO Affiliation VALUES (?,?)"""
        
        cursor.execute("SELECT MAX(ID_attackers) FROM Attackers")
        last_id = cursor.fetchone()[0]

# Si aucun ID n'est trouvé (si la table est vide), on démarre à 1
        if last_id is None:
            new_id=1
        else:
            new_id=last_id+1
        cursor.execute(query,(new_id,affiliation))
        cursor.execute(query1,(affiliation,sponsor))
    except sqlite3.IntegrityError as error:
        print(f"An integrity error occurred while insert the attacker: {error}")
        return False
    except sqlite3.Error as error:
        print(f"A database error occurred while inserting the attacker: {error}")
        return False
    return True

def update_attacker_sponsor(affiliation, sponsor,cursor):
    cursor.execute('''UPDATE Affiliation SET country= ? WHERE affiliation_name = ?''', (sponsor,affiliation))

    # Vérification des lignes affectées (pour savoir si l'attacker existe)
    if cursor.rowcount > 0:
        print(f"Le pays de l'attaquant '{affiliation}' a été mis à jour.")
        return True
    else:
        print(f"Aucun agent trouvé avec le nom d'utilisateur '{affiliation}'.")
        return False

def get_attackers(cursor):
    try:
        query = "SELECT DISTINCT affiliation_name FROM Attackers"
        cursor.execute(query, [])
    except sqlite3.IntegrityError as error:
        print(f"An integrity error occurred while fetching the attackers: {error}")
        return None
    except sqlite3.Error as error:
        print(f"A database error occurred while fetching the attackers: {error}")
        return None
    return cursor.fetchall()
