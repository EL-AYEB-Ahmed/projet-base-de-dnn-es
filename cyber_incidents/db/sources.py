import utils
import sqlite3

def insert_source(link,cursor):
    try:
        query="""INSERT INTO Source(ID_info,source) VALUES (?,?)"""
        
        cursor.execute("SELECT MAX(ID_info) FROM Source")
        last_id = cursor.fetchone()[0]

# Si aucun ID n'est trouvé (si la table est vide), on démarre à 1
        if last_id is None:
            new_id=1
        else:
            new_id=last_id+1
        cursor.execute(query,(new_id,link))
        
    except sqlite3.IntegrityError as error:
        print(f"An integrity error occurred while insert the agent: {error}")
        return False
    except sqlite3.Error as error:
        print(f"A database error occurred while inserting the agent: {error}")
        return False
    return True

def get_sources(cursor):
    try:
        query = "SELECT * FROM Source"
        cursor.execute(query, [])
    except sqlite3.IntegrityError as error:
        print(f"An integrity error occurred while fetching the sources: {error}")
        return None
    except sqlite3.Error as error:
        print(f"A database error occurred while fetching the sources: {error}")
        return None
    return cursor.fetchall()
    
