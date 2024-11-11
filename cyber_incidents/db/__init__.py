import sqlite3
import utils
import csv


def get_db_connexion():
    # Loads the app config into the dictionary app_config.
    app_config = utils.load_config()
    if not app_config:
        print("Error: while loading the app configuration")
        return None

    # From the configuration, gets the path to the database file.
    db_file = app_config["db"]

    # Open a connection to the database.
    conn = sqlite3.connect(db_file)
    conn.row_factory = sqlite3.Row

    return conn

def close_db_connexion(cursor, conn):
    """Close a database connexion and the cursor.

    Parameters
    ----------
    cursor
        The object used to query the database.
    conn
        The object used to manage the database connection.
    """
    cursor.close()
    conn.close()

def transform_csv(old_csv_file_name, new_csv_file_name):
    """Write a new CSV file based on the input CSV file by adding
    new columns to obtain a CSV file that is easier to read.

    Parameters
    ----------
    
    """
    with open(old_csv_file_name,mode='r',newline='',encoding='utf-8') as old_csv, open(new_csv_file_name, mode='w', newline='') as new_file:
        lecteur_csv=csv.DictReader(old_csv)


        liste_colone_titre=[]   #on crée une liste où on va mettre les titre des colonnes
        for colone_titre in lecteur_csv.fieldnames:
            if colone_titre!= "Response":
                liste_colone_titre.append(colone_titre) #On met tout les titres de colonnes sauf response
        liste_colone_titre.append('Type of response')   #On met les deux nouveaux titres de colonnes
        liste_colone_titre.append('Source of response')

        liste_colone_titre.append('Confirmation') #Q3


        ecrivain_csv = csv.DictWriter(new_file,fieldnames=liste_colone_titre)
        ecrivain_csv.writeheader()                              
        for ligne in lecteur_csv:       #om implémente les lignes pour les modifier une à une
            ligne_complete_à_modifier = ligne.pop('Response')
            try:

                L = ligne_complete_à_modifier.split(sep='   ')
                ligne['Type of response'] = L[0]    
                ligne['Source of response'] = L[1]     #on sépare la colonne en deux parties dans L
            except:
                print('E')
            
            if ligne['Affiliations']=='':            #Q3
                ligne['Confirmation']='No'           #Q3
            else:                                    #Q3
                ligne['Confirmation']='Yes'          #Q3

            ecrivain_csv.writerow(ligne)
    return 

def create_database(cursor,conn):
    """Creates the incident database

    Parameters
    ----------
    cursor
        The object used to query the database.
    conn
        The object used to manage the database connection.

    Returns
    -------
    bool
        True if the database could be created, False otherwise.
    """

    # We open a transaction.
    # A transaction is a sequence of read/write statements that
    # have a permanent result in the database only if they all succeed.
    #
    # More concretely, in this function we create many tables in the database.
    # The transaction is therefore a sequence of CREATE TABLE statements such as :
    #
    # BEGIN
    # CREATE TABLE XXX
    # CREATE TABLE YYY
    # CREATE TABLE ZZZ
    # ....
    #
    # If no error occurs, all the tables are permanently created in the database.
    # If an error occurs while creating a table (for instance YYY), no table will be created, even those for which
    # the statement CREATE TABLE has already been executed (in this example, XXX).
    #
    # When we start a transaction with the statement BEGIN, we must end it with either COMMIT
    # or ROLLBACK.
    #
    # * COMMIT is called when no error occurs. After calling COMMIT, the result of all the statements in
    # the transaction is permanetly written to the database. In our example, COMMIT results in actually creating all the tables
    # (XXX, YYY, ZZZ, ....)
    #
    # * ROLLBACK is called when any error occurs in the transaction. Calling ROLLBACK means that
    # the database is not modified (in our example, no table is created).
    #
    #
    cursor.execute("BEGIN")

    # Création des tables
    tables = {
        "Agent": """
            CREATE TABLE IF NOT EXISTS Agent(
                username TEXT PRIMARY KEY,
                password BINARY(256)
            );
            """,    #table agents
        "Victim": """
            CREATE TABLE IF NOT EXISTS Victim(
                ID_victim INTEGER PRIMARY KEY AUTOINCREMENT,
                nameV TEXT UNIQUE,
                category TEXT
            );
            """, #table victim
        "Affiliation": """
            CREATE TABLE IF NOT EXISTS Affiliation(
                affiliation_name TEXT PRIMARY KEY,
                country TEXT UNIQUE   
            );
            """,  #table affiliation
        "Attackers": """
            CREATE TABLE IF NOT EXISTS Attackers(
                ID_attackers INTEGER PRIMARY KEY,
                affiliation_name TEXT UNIQUE,
                FOREIGN KEY(affiliation_name) REFERENCES Affiliation(affiliation_name)
            );
            """,#table attackers
        "Attackers_Victim": """
            CREATE TABLE IF NOT EXISTS Attackers_Victim(
                ID_attackers INTEGER,
                ID_victim TEXT,
                PRIMARY KEY(ID_attackers,ID_victim),
                FOREIGN KEY(ID_attackers) REFERENCES Attackers(ID_attackers),
                FOREIGN KEY(ID_victim) REFERENCES Victim(ID_victim)
            );
            """,#table intermédiaire attackers et victim
        "Attacks":"""
            CREATE TABLE IF NOT EXISTS Attacks(
                ID_attacks INTEGER PRIMARY KEY,
                date DATE,
                title TEXT,
                description TEXT,
                type TEXT ,
                confirmation TEXT,
                ID_attackers INTEGER,
                username TEXT,
                FOREIGN KEY(ID_attackers) REFERENCES Attackers(ID_attackers),
                FOREIGN KEY(username) REFERENCES Agent(username)
            );
            """, #table attack
        "Source": """
            CREATE TABLE IF NOT EXISTS Source(
                ID_info INTEGER PRIMARY KEY,
                type_source TEXT,
                source TEXT,
                ID_attacks INTEGER,
                ID_response INTEGER,
                FOREIGN KEY(ID_response) REFERENCES Response(ID_response),
                FOREIGN KEY(ID_attacks) REFERENCES Attacks(ID_attacks)
            );
            """, #table Source
        "Response": """
            CREATE TABLE IF NOT EXISTS Response(
                ID_response INTEGER PRIMARY KEY,
                type_response TEXT,
                source_of_response TEXT,
                ID_attacks INTEGER,
                FOREIGN KEY(ID_attacks) REFERENCES Attacks(ID_attacks)
            );
            """, #table Response
        "Attacks_Victim": """
            CREATE TABLE IF NOT EXISTS Attacks_Victim(
                ID_attacks INTEGER,
                ID_victim TEXT,
                PRIMARY KEY(ID_attacks,ID_victim),
                FOREIGN KEY(ID_attacks) REFERENCES Attacks(ID_attacks),
                FOREIGN KEY(ID_victim) REFERENCES Victim(ID_victim)
            );
            """, #table intermédiaire attacks victim
        
      
        
    }
    try:
        # To create the tables, we call the function cursor.execute() and we pass it the
        # CREATE TABLE statement as a parameter.
        # The function cursor.execute() can raise an exception sqlite3.Error.
        # That's why we write the code for creating the tables in a try...except block.
        for tablename in tables:
            print(f"Creating table {tablename}...", end=" ")
            cursor.execute(tables[tablename])
            print("OK")

    ###################################################################

    # Exception raised when something goes wrong while creating the tables.
    except sqlite3.Error as error:
        print("An error occurred while creating the tables: {}".format(error))
        # IMPORTANT : we rollback the transaction! No table is created in the database.
        conn.rollback()
        # Return False to indicate that something went wrong.
        return False
            
    # If we arrive here, that means that no error occurred.
    # IMPORTANT : we must COMMIT the transaction, so that all tables are actually created in the database.
    conn.commit()
    print("Database created successfully")
    # Returns True to indicate that everything went well!
    return True

def populate_database(cursor,conn,csv_file_name):

    """Populate the database with data in a CSV file.
    Parameters
    ----------
    cursor
        The object used to query the database.
    conn
        The object used to manage the database connection.
    csv_file_name
        Name of the CSV file where the data are.
    Returns
    -------
    bool
        True if the database is correctly populated, False otherwise.

    """
    
    with open(csv_file_name,mode='r',newline='') as file:
        csv_reader = csv.DictReader(file, delimiter=',')

        id_attacks=1000
        id_attackers=2000   #on fait débuter les différents ID pour chaque table
        id_response=3000
        id_source1=4000
        id_source2=5000
        id_source3=6000
        for row in csv_reader:
            victims = row['Victims'].split(',')
            category = row.get('Category')
            for victim in victims:
                victim = victim.strip()
                
                cursor.execute("SELECT ID_victim FROM Victim WHERE nameV = ?", (victim,))
                result = cursor.fetchone()

                if result is None:
                    # Si la victime n'existe pas encore, l'insérer dans la table Victim
                    cursor.execute("""
                        INSERT INTO Victim (nameV, category)
                        VALUES (?, ?)
                    """, (victim, category))
                    
                    # Récupérer l'ID de la nouvelle victime
                    id_victim = cursor.lastrowid
                else:
                    # Si la victime existe déjà, récupérer son ID
                    id_victim = result[0]
                # Ajouter chaque victime avec son nom et sa catégorie dans la base de données
                cursor.execute("""INSERT OR IGNORE INTO Victim (nameV, category) VALUES (?,?)""",(victim, category))
                cursor.execute("""INSERT OR IGNORE INTO Attackers_Victim VALUES (?,?)""",(id_attackers,id_victim))
                cursor.execute("""INSERT OR IGNORE INTO Attacks_Victim VALUES (?,?)""",(id_attacks,id_victim))

            query1="""INSERT OR IGNORE INTO Attacks (ID_attacks,date,title,description,type,confirmation,ID_attackers) VALUES (?,?,?,?,?,?,?)"""
            query11=(id_attacks,row["Date"],row["Title"],row["Description"],row["Type"],row["Confirmation"],id_attackers)                
            cursor.execute(query1,query11)

            if row["Sources_1"]==row["Source of response"]:
                query2="""INSERT OR IGNORE INTO Source (ID_info,type_source,source,ID_attacks,ID_response) VALUES (?,?,?,?,?)"""
                query22=(id_source1,row["Type of response"],row["Sources_1"],id_attacks,id_response)
            else:
                query2="""INSERT OR IGNORE INTO Source (ID_info,source,ID_attacks) VALUES (?,?,?)"""
                query22=(id_source1,row["Sources_1"],id_attacks)
            cursor.execute(query2,query22)

            if row["Sources_2"]==row["Source of response"]:
                query9="""INSERT OR IGNORE INTO Source (ID_info,type_source,source,ID_attacks,ID_response) VALUES (?,?,?,?,?)"""
                query99=(id_source2,row["Type of response"],row["Sources_2"],id_attacks,id_response)
            else:
                query9="""INSERT OR IGNORE INTO Source (ID_info,source,ID_attacks) VALUES (?,?,?)"""
                query99=(id_source2,row["Sources_2"],id_attacks)
            cursor.execute(query9,query99)

            if row["Sources_3"]==row["Source of response"]:
                query10="""INSERT OR IGNORE INTO Source (ID_info,type_source,source,ID_attacks,ID_response) VALUES (?,?,?,?,?)"""
                query110=(id_source3,row["Type of response"],row["Sources_3"],id_attacks,id_response)
            else:
                query10="""INSERT OR IGNORE INTO Source (ID_info,source,ID_attacks) VALUES (?,?,?)"""
                query110=(id_source3,row["Sources_3"],id_attacks)
            cursor.execute(query10,query110)

            query3="""INSERT OR IGNORE INTO Response VALUES (?,?,?,?)"""
            query33=(id_response,row["Type of response"],row["Source of response"],id_attacks)
            cursor.execute(query3,query33)

            query4="""INSERT OR IGNORE INTO Attackers VALUES (?,?)"""
            query44=(id_attackers,row["Affiliations"])
            cursor.execute(query4,query44)  

            query5="""INSERT OR IGNORE INTO Victim VALUES (?,?,?)"""
            query55=(id_victim,row["Victims"],row["Category"])
            cursor.execute(query5,query55)

            query6="""INSERT OR IGNORE INTO Affiliation VALUES (?,?)"""
            query66=(row["Affiliations"],row["Sponsor"])
            cursor.execute(query6,query66)

            id_attacks+=1
            id_attackers+=1
            id_response+=1
            id_source1+=1       #on modifie les ID de chaque table pour la prochaine ligne 
            id_source2+=1
            id_source3+=1
            
            # To create the tables, we call the function cursor.execute() and we pass it the
            # CREATE TABLE statement as a parameter.
            # The function cursor.execute() can raise an exception sqlite3.Error.
            # That's why we write the code for creating the tables in a try...except block.
                
            ################################################################### 
            # Exception raised when something goes wrong while creating the tables.
            """except sqlite3.Error as error:
                print("Error: Database cannot be populated:", error)
                # IMPORTANT : we rollback the transaction! No table is created in the database.
                conn.rollback()
                # Return False to indicate that something went wrong."""


    # If we arrive here, that means that no error occurred.
    # IMPORTANT : we must COMMIT the transaction, so that all tables are actually created in the database.   
    conn.commit()
    print("Database populated successfully")

    return True 

def init_database():
    """Initialise the database by creating the database
    and populating it.
    """
    try:
        conn = get_db_connexion()

        # The cursor is used to execute queries to the database.
        cursor = conn.cursor()

        # Creates the database. THIS IS THE FUNCTION THAT YOU'LL NEED TO MODIFY
        create_database(cursor,conn)

        # Populates the database.
        populate_database(cursor,conn,"data/nouveau_BDD.csv")

        # Closes the connection to the database
        close_db_connexion(cursor,conn)
        conn.close()
        print("Database initialized successfully")

    except Exception as e:
        print("Error: Database cannot be initialised:", e)
