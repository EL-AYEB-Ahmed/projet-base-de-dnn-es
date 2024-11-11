import utils
import sqlite3


def insert_agent(agent,cursor):
    """Inserts an agent into to the database.

    Parameters
    ----------
    agent: a dictionnary
        Agent personal data: agent["username"] and agent["password"].
    cursor:
        The object used to query the database.

    Returns
    -------
    bool
        True if no error occurs, False otherwise.
    """

    try:
        # The agent is described by two attributes: username and password.
        # The values of these attributes are available in the dictionary agent, one of the parameters of this function.
        # So, we need to write our insert query in such a way that the values are obtained from the dictionary agent.
        # Our insert query contains two question marks (?) that indicate that the values will be specified later.
        #
        #  IMPORTANT:
        #
        # * The query assumes that you called Agent the table with the agent personal data. If you gave it another name, CHANGE the query accordingly.
        #
        # * The query assumes that in your table Agent the columns are defined in this order:
        # username, password.
        # IF THE ORDER in which you created the columns IS DIFFERENT, CHANGE this variable accordingly.

        hashed_password=utils.hash_password(agent["password"]) #modif issue de la fin du TP
        query_insert_agent = "INSERT OR IGNORE INTO Agent (username, password) VALUES (?, ?)"
        cursor.execute(query_insert_agent,
                       (agent["username"], hashed_password)) #on ajoute l'agent et son mdp crypté
    except sqlite3.IntegrityError as error:
        print(f"An integrity error occurred while insert the agent: {error}")
        return False
    except sqlite3.Error as error:
        print(f"A database error occurred while inserting the agent: {error}")
        return False
    return True

def get_agent(username,cursor):
    """Get an agent from the database based on its username and a list of
    the incidents assigned to the agent.

    Parameters
    ----------
    username: string
        Agent username.
    cursor:
        The object used to query the database.

    Returns
    -------
    dict
        The agent username, password and incidents if no error occurs, None otherwise.
    """

    try:
        query_get_agent = "SELECT * FROM Agent WHERE username =(?)"
        cursor.execute(query_get_agent, [username]) #on cherche un agent à partir de son nom

        agent = cursor.fetchone()

        query_get_incidents = "SELECT ID_attacks FROM Attacks WHERE username = ?"
        cursor.execute(query_get_incidents, [username])

        incidents = cursor.fetchall()
    except sqlite3.IntegrityError as error:
        print(f"An integrity error occurred while fetching the agent: {error}")
        return None
    except sqlite3.Error as error:
        print(f"A database error occurred while fetching the agent: {error}")
        return None
    return {"username": agent["username"],"incidents": incidents,"password": agent["password"]}

def get_agents(cursor):
    """Get all agents from the database.

    Parameters
    ----------
    cursor:
        The object used to query the database.

    Returns
    -------
    list
        The list of all the agent information if no error occurs, None otherwise.
    """
    try:
        query_get_agents = "SELECT username FROM Agent"
        cursor.execute(query_get_agents, [])

    except sqlite3.IntegrityError as error:
        print(
            f"An integrity error occurred while fetching the agents: {error}")
        return None
    except sqlite3.Error as error:
        print(f"A database error occurred while fetching the agents: {error}")
        return None
    return cursor.fetchall()

def update_password(username, password, cursor):
    """Update the password of an agent.

    Parameters
    ----------
    username: string
        Agent username.
    password: bytes
        New password
    cursor:
        The object used to query the database.

    Returns
    -------
    bool
        True if no error occurs, False otherwise.
    """
     
    # requête SQL pour mettre à jour le mot de passe
    hashed_password=utils.hash_password(password)
    cursor.execute('''UPDATE Agent SET password= ? WHERE username = ?''', (hashed_password,username))
    
    # Vérification des lignes affectées (pour savoir si l'agent existe)
    if cursor.rowcount > 0: #rowcount permet de savoir combien de lignes ont été modifiés
        print(f"Le mot de passe de l'agent '{username}' a été mis à jour.")
        return 1
    else:
        print(f"Aucun agent trouvé avec le nom d'utilisateur '{username}'.")
        return 2
