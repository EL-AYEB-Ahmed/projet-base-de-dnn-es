import utils
import sqlite3
import traceback

def insert_incident(name,date,description,type,isConfirmed,source_links,attacker_affiliation,target_name,response_type,cursor):
    try:
        cursor.execute("SELECT MAX(ID_attacks) FROM Attacks")
        id_attacks = cursor.fetchone()[0]
        if id_attacks is None:
            id_attacks=1
        else:
            id_attacks=id_attacks+1
        
        cursor.execute("SELECT MAX(ID_attackers) FROM Attackers")
        id_attackers = cursor.fetchone()[0]
        if id_attackers is None:
            id_attackers=1
        else:
            id_attackers=id_attackers+1
        
        cursor.execute("SELECT MAX(ID_response) FROM Response")
        id_response = cursor.fetchone()[0]
        if id_response is None:
            id_response=1
        else:
            id_response=id_response+1

        cursor.execute("SELECT MAX(ID_info) FROM Source")
        id_source = cursor.fetchone()[0]
        if id_source is None:
            id_source=1
        else:
            id_source=id_source+1

        cursor.execute("SELECT MAX(ID_victim) FROM Victim")
        id_victim = cursor.fetchone()[0]
        if id_victim is None:
            id_victim=1
        else:
            id_victim=id_victim+1

        query1="""INSERT OR IGNORE INTO Attacks (ID_attacks,date,title,description,type,confirmation,ID_attackers) VALUES (?,?,?,?,?,?,?)"""
        query11=(id_attacks,date,name,description,type,isConfirmed,id_attackers)
        query2="""INSERT OR IGNORE INTO Source (ID_info,type_source,source,ID_attacks,ID_response) VALUES (?,?,?,?,?)"""
        query22=(id_source,response_type,source_links,id_attacks,id_response)
        query3="""INSERT OR IGNORE INTO Response VALUES (?,?,?,?)"""
        query33=(id_response,response_type,source_links,id_attacks)
        query4="""INSERT OR IGNORE INTO Attackers VALUES (?,?)"""
        query44=(id_attackers,attacker_affiliation)
        query5="""INSERT OR IGNORE INTO Victim(ID_victim,nameV) VALUES (?,?)"""
        query55=(id_victim,target_name)
        query7="""INSERT OR IGNORE INTO Attackers_Victim VALUES (?,?)"""
        query77=(id_attackers,id_victim)
        query8="""INSERT OR IGNORE INTO Attacks_Victim VALUES (?,?)"""
        query88=(id_attacks,id_victim)
        query9="""INSERT OR IGNORE INTO Affiliation(affiliation_name) VALUES (?)"""
        query99=([attacker_affiliation])
        
        cursor.execute(query1,query11)
        cursor.execute(query2,query22)
        cursor.execute(query3,query33)
        cursor.execute(query4,query44)
        cursor.execute(query5,query55)
        cursor.execute(query7,query77)
        cursor.execute(query8,query88)
        cursor.execute(query9,query99)
    except sqlite3.IntegrityError as error:
        print(f"An integrity error occurred while insert the target: {error}")
        traceback.print_exc()
        return False
    except sqlite3.Error as error:
        print(f"A database error occurred while inserting the target: {error}")
        traceback.print_exc()
        return False
    return True

def get_incident(incident_name,cursor):
    try:
        query_get_incident = "SELECT * FROM Attacks WHERE title = ?"
        cursor.execute(query_get_incident, [incident_name])
        incident = cursor.fetchall()
    except sqlite3.IntegrityError as error:
        print(f"An integrity error occurred while fetching the incident: {error}")
        return None
    except sqlite3.Error as error:
        print(f"A database error occurred while fetching the incident ent: {error}")
        return None
    return incident

def update_incident_attacker(incident_name, new_attacker_affiliation,cursor):
    cursor.execute('SELECT ID_attackers FROM Attackers WHERE affiliation_name = ?', [new_attacker_affiliation])
    result = cursor.fetchone()

    if result is None:
        cursor.execute("SELECT MAX(ID_attackers) FROM Attackers")
        last_id = cursor.fetchone()[0]
        # Si aucun ID n'est trouvé (si la table est vide), on démarre à 1
        if last_id is None:
            new_id=1
        else:
            new_id=last_id+1
        cursor.execute("INSERT INTO Attackers VALUES (?,?)",(new_id,new_attacker_affiliation,))
        cursor.execute("INSERT INTO Affiliation(affiliation_name) VALUES (?)",(new_attacker_affiliation,))
        cursor.execute('''UPDATE Attacks SET ID_attackers = ? WHERE title = ?''', (new_id, incident_name))  
        return True
    new_attacker_id = result[0]

    cursor.execute('''UPDATE Attacks SET ID_attackers = ? WHERE title = ?''', (new_attacker_id, incident_name))    
    # Vérification des lignes affectées (pour savoir si l'agent existe)
    if cursor.rowcount > 0:
        print(f"Le nom de l'attaquant de l'attaque '{incident_name}' a été mis à jour.")
        return True
    else:
        print(f"Aucune attaque trouvé ou aucun attaquant correspondant.")
        return False

def update_incident_response(incident_name,new_response,cursor):
    cursor.execute('SELECT ID_attacks FROM Attacks WHERE title = ?',[incident_name])
    requete=cursor.fetchone()
    if requete is None:
        print(f"Attack '{incident_name}' not found.")
        return

    cursor.execute('''UPDATE Response SET source_of_response=? WHERE ID_attacks = ?''', (new_response,requete[0]))  
    
    cursor.execute('SELECT ID_response FROM response WHERE ID_attacks = ?',(requete[0],))
    result = cursor.fetchone()
    
    cursor.execute("SELECT MAX(ID_info) FROM Source")
    last_id_source = cursor.fetchone()[0]
    # Si aucun ID n'est trouvé (si la table est vide), on démarre à 1
    if last_id_source is None:
        new_id_source=1
    else:
        new_id_source=last_id_source+1
    cursor.execute("INSERT INTO Source(ID_info,source,ID_attacks,ID_response) VALUES (?,?,?,?)",(new_id_source,new_response,requete[0],result[0]))
    
    if cursor.rowcount > 0:
        print(f"la réponse de l'attaque '{incident_name}' a été mis à jour.")
        return True
    else:
        print(f"Aucune attaque trouvé ou aucune réponse correspondante.")
        return False

def add_incident_target(incident_name, target_name_to_add,cursor):
     # Récupérer l'ID de l'attaque à partir du titre
    cursor.execute('SELECT ID_attacks FROM Attacks WHERE title = ?', (incident_name,))
    attack_result = cursor.fetchone()

    if attack_result is None:
        print(f"Attack '{incident_name}' not found.")
        return

    attack_id = attack_result[0]

    # Vérifier si la victime existe, sinon l'ajouter à la table Victim
    cursor.execute('SELECT ID_victim FROM Victim WHERE nameV = ?', (target_name_to_add,))
    victim_result = cursor.fetchone()

    if victim_result is None:
        # Si la victime n'existe pas, on la crée avec un ID > 15000
        cursor.execute("SELECT MAX(ID_attackers) FROM Attackers")
        last_id = cursor.fetchone()[0]
        # Si aucun ID n'est trouvé (si la table est vide), on démarre à 1
        if last_id is None:
            new_id=1
        else:
            new_id=last_id+1

        cursor.execute('''INSERT INTO Victim (ID_victim, nameV) VALUES (?, ?)''', (new_id, target_name_to_add))

        print(f"Victim '{target_name_to_add}' added to the Victim table with ID {new_id}.")
        victim_id = new_id
    else:
        # Si la victime existe déjà, on récupère son ID
        victim_id = victim_result[0]

    #on insère dans la table Attacks_Victim
    try:
        cursor.execute('''INSERT INTO Attacks_Victim (ID_attacks, ID_victim) VALUES (?, ?)''', (attack_id, victim_id))
        print(f"Victim '{target_name_to_add}' associated with attack '{incident_name}'.")
    except sqlite3.IntegrityError:
        print(f"Victim '{target_name_to_add}' is already associated with the attack '{incident_name}'.")
        return True
    return True

def remove_incident_target(incident_name, target_name_to_remove,cursor):
     #Récupérer l'ID de l'attaque à partir du titre
    cursor.execute('SELECT ID_attacks FROM Attacks WHERE title = ?', (incident_name,))
    attack_result = cursor.fetchone()

    if attack_result is None:
        print(f"Attack '{incident_name}' not found.")
        return

    attack_id = attack_result[0]

    #Récupérer l'ID de la victime à partir de son nom
    cursor.execute('SELECT ID_victim FROM Victim WHERE nameV = ?', (target_name_to_remove,))
    victim_result = cursor.fetchone()

    if victim_result is None:
        print(f"Victim '{target_name_to_remove}' not found.")
        return

    victim_id = victim_result[0]

    #Supprimer l'association dans la table Attacks_Victim
    cursor.execute('''
        DELETE FROM Attacks_Victim
        WHERE ID_attacks = ? AND ID_victim = ?
    ''', (attack_id, victim_id))
    
    if cursor.rowcount > 0:
        print(f"Victim '{target_name_to_remove}' removed from attack '{incident_name}'.")
    else:
        print(f"Victim '{target_name_to_remove}' is not associated with the attack '{incident_name}'.")
    return True

def add_incident_source(incident_name, source_link,cursor):
    #on récupère l'ID de l'attaque à partir du titre
    cursor.execute('SELECT ID_attacks FROM Attacks WHERE title = ?', (incident_name,))
    attack_result = cursor.fetchone()

    if attack_result is None:
        print(f"Attack '{incident_name}' not found.")
        return

    attack_id = attack_result[0]

    #on crée un nouvel ID pour la source
    cursor.execute('SELECT MAX(ID_info) FROM Source')
    max_id_info = cursor.fetchone()[0] or 0  # Si aucune source, commence à 0
    new_source_id = max_id_info + 1  # Nouveau ID_info

    #on insère la nouvelle source dans la table Source
    try:
        cursor.execute('''
            INSERT INTO Source (ID_info, source, ID_attacks)
            VALUES (?,?,?)
        ''', (new_source_id, source_link, attack_id))
        print(f"Source '{source_link}' added to attack '{incident_name}' with Source ID {new_source_id}.")
    except sqlite3.IntegrityError as e:
        print(f"Failed to add source '{source_link}' to attack '{incident_name}': {e}")
        return False
    return True

def remove_incident_source(incident_name, source_link,cursor):
    # on recupère l'ID de l'attaque à partir du titre
    cursor.execute('SELECT ID_attacks FROM Attacks WHERE title = ?', (incident_name,))
    attack_result = cursor.fetchone()

    if attack_result is None:
        print(f"Attack '{incident_name}' not found.")
        return

    attack_id = attack_result[0]

    # on supprime la source associée à cette attaque
    cursor.execute('''
        DELETE FROM Source
        WHERE source = ? AND ID_attacks = ?
    ''', (source_link, attack_id))

    # on vérifie si la suppression a eu lieu
    if cursor.rowcount > 0:
        print(f"Source '{source_link}' removed from attack '{incident_name}'.")
        return True
    else:
        print(f"Source '{source_link}' not found for attack '{incident_name}'.")
        return True
