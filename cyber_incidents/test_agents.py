import db.agents
from db import get_db_connexion, close_db_connexion


def print_agents():
    """Print the agents in the database in the console."""
    conn = get_db_connexion()
    cursor = conn.cursor()

    agents = db.agents.get_agents(cursor)
    print("Agents in database:", [dict(agent) for agent in agents])
    close_db_connexion(cursor, conn)

def print_one_agent():
    conn = get_db_connexion()
    cursor = conn.cursor()
    agent=db.agents.get_agent("hubert",cursor)
    print("on affiche l'agent hubert seul avec succès",agent)
    return

def insert_hubert(cursor):
    """Inserts an agent into the database.

    Parameters
    ----------
    cursor:
        The object used to query the database.

    Returns
    -------
    bool
        True if the agent could be inserted, False otherwise.
    """
    # Personal data of agent Hubert
    hubert = {"username": "hubert", "password": "117"}
    
    print("Inserting agent Hubert...")
    if db.agents.insert_agent(hubert, cursor):
        print("Hubert added successfully !")
        return True
    else:
        print("Impossible to add Hubert ...")
        return False

def insert_other_agents(cursor):
    # Personal data of agent Hubert
    charles = {"username": "charles", "password": "1982"}
    François={"username": "François", "password": "1975"}
    Henriette={"username": "henriette", "password": "1979"}

    print("Inserting agents...")
    if db.agents.insert_agent(charles, cursor) and db.agents.insert_agent(François, cursor) and db.agents.insert_agent(Henriette, cursor):
        print("Agents added successfully !")
        return True
    else:
        print("Impossible to add Agents ...")
        return False

########## TEST FUNCTIONS ##########

def test_insert_agent():
    print("## TEST: insert an agent")
    # Open a connexion to the database.
    conn = get_db_connexion()

    # Get the cursor for the connection. This object is used to execute queries
    # in the database.
    cursor = conn.cursor()

    # Insert agent Hubert
    insert_hubert(cursor)
    insert_other_agents(cursor)
    conn.commit()
    # Close connexion
    close_db_connexion(cursor, conn)

def test_update_password_existing_agent():
    print("\n## TEST: update an agent that is in the database")
    conn = get_db_connexion()
    cursor = conn.cursor()

    try:
        # Update agent hubert
        update_ok = db.agents.update_password("hubert", "12", cursor)
        # Print results from update
        print("Update successful:", update_ok)
        print("Number of modified rows in the database:", cursor.rowcount)
    
    except NotImplementedError as error:
        print("update_password() not implemented")
    conn.commit()
    close_db_connexion(cursor, conn)

def test_update_password_non_existing_agent():
    print("\n## TEST: update an agent that does not exist in the database")
    conn = get_db_connexion()
    cursor = conn.cursor()

    # Update agent bond
    try:
        update_ok = db.agents.update_password("bond", "12", cursor)
        # Print results from update
        print("Update successful:", update_ok)
        print("Number of modified rows in the database:", cursor.rowcount)
    except NotImplementedError as error:
        print("update_password() not implemented")

    close_db_connexion(cursor, conn)


if __name__ == "__main__":
    conn = get_db_connexion()

    test_insert_agent()
    print_agents()
    print_one_agent()
    test_update_password_non_existing_agent()

    # test_update_password_non_existing_agent()
