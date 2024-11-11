import utils
import sqlite3


ID_rep=9000

def insert_response(type,link,cursor):
    try:
        query="""INSERT OR IGNORE INTO Response(ID_response,type_response,source_of_response) VALUES (?,?,?)"""
        
        cursor.execute("SELECT MAX(ID_response) FROM Response")
        last_id = cursor.fetchone()[0]

# Si aucun ID n'est trouvé (si la table est vide), on démarre à 1
        if last_id is None:
            new_id=1
        else:
            new_id=last_id+1
        cursor.execute(query,(new_id,type,link))
    except sqlite3.IntegrityError as error:
        print(f"An integrity error occurred while insert the response: {error}")
        return False
    except sqlite3.Error as error:
        print(f"A database error occurred while inserting the response: {error}")
        return False
    return True

def get_response(incident_id,cursor):
    try:
        query = "SELECT * FROM Response WHERE ID_attacks=(?) AND type_response IS NOT NULL AND type_response <> '' "
        cursor.execute(query,incident_id)
    except sqlite3.IntegrityError as error:
        print(f"An integrity error occurred while fetching the responses: {error}")
        return None
    except sqlite3.Error as error:
        print(f"A database error occurred while fetching the responses: {error}")
        return None
    return cursor.fetchall()
