import sqlite3


def insert_target(target_name, category,cursor):
    try:
        query="""INSERT OR IGNORE INTO Victim VALUES (?,?,?)"""
        cursor.execute("SELECT MAX(ID_victim) FROM Victim")
        last_id = cursor.fetchone()[0]

# Si aucun ID n'est trouvé (si la table est vide), on démarre à 1
        if last_id is None:
            new_id=1
        else:
            new_id=last_id+1
        cursor.execute(query,(new_id,target_name,category))
    except sqlite3.IntegrityError as error:
        print(f"An integrity error occurred while insert the target: {error}")
        return False
    except sqlite3.Error as error:
        print(f"A database error occurred while inserting the target: {error}")
        return False
    return True

def get_targets(cursor):
    try:
        query = "SELECT * FROM Victim WHERE nameV IS NOT NULL AND nameV <> ''"
        cursor.execute(query, [])

    except sqlite3.IntegrityError as error:
        print(f"An integrity error occurred while fetching the targets: {error}")
        return None
    except sqlite3.Error as error:
        print(f"A database error occurred while fetching the targets: {error}")
        return None
    return cursor.fetchall()
