from flask import Blueprint, request, jsonify

import sqlite3
import utils
import db.agents
from db import get_db_connexion
from db import close_db_connexion
from utils import token_required


agents_bp = Blueprint("agents", __name__)

@agents_bp.route("/", methods=["GET"])
@token_required
def get_all_agents():
    """Fetch all agents from the database.

    Returns
    -------
    status_code
        200 by default if no error occured
        500 if an error occured while fetching the agents
    data
        agents as a json if no error occurs (can be empty if no agents)
        an error message if an error occured while fetching the agents.
    """
    conn = get_db_connexion()
    cursor = conn.cursor()

    all_agents = db.agents.get_agents(cursor)
    if all_agents == None:
        conn.rollback()
        conn.close()
        return "Error: while fetching agents", 500
    conn.close()
    return jsonify({"agents": [dict(agent)["username"] for agent in all_agents]})

@agents_bp.route("/<agent_username>", methods=["GET"])
@token_required
def get_agent(agent_username):
    """Fetch a single agent from the database based on its username.

    Parameters
    ----------
    agent_username
        username of the agent (as defined in the database)

    Returns
    -------
    data
        agent as a json if the agent is in the database
        an error message "This agent does not exists" if the agent requested
            is not in the database
        an error message "Error: while fetching agent" if an error occured
            while fetching the agent.
    status_code
        200 if the agent is correctly fetched
        404 if the query to the database was a success but the agent
                is not in the database
        500 if an error occured while fetching the agent
    """
    import base64

    conn = get_db_connexion()  # Connect to the database
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT * FROM Agent WHERE username = ?", (agent_username,))
        row = cursor.fetchone()
        if row is None:
            close_db_connexion(cursor, conn)  # Close connection
            return jsonify({"message": "This agent does not exist"}), 404
        # Convert the sqlite3.Row object to a dictionary
        agent = dict(row)  # Convert row to a dictionary
        if agent:
            agent_dict = dict(agent)

            # Si le champ 'password' est un type bytes, on l'encode en Base64
            if isinstance(agent_dict.get('password'), bytes):
                agent_dict['password'] = base64.b64encode(agent_dict['password']).decode('utf-8')

        conn.close()
        # Commit the transaction and close the connection
        return jsonify(agent_dict), 200

    except Exception as e:
        conn.close()
        return jsonify({"message": "Error: while fetching agent", "error": str(e)}), 500

@agents_bp.route("/<agent_username>", methods=["PATCH"])
@token_required
def patch_password(agent_username):
    """Patch the password of an agent.
    The password must be passed in the data of the POST request.

     Parameters
     ----------
     agent_username
         username of the agent (as defined in the database)

     Returns
     -------
     data
         agent as a json if the agent is in the database
         a message "Password not provided" if the password is not in
             the request
         an error message "Error: while updating password" if an error
             occured while updating the password.
     status_code
         200 if the password is correctly modified
         404 if no password is provided in the request
         500 if an error occured while updating the password
    """
    
    # Get the request data (POST request body)
    agent_data = request.get_json()

    # Extract the new password from the request data
    new_password = agent_data.get("password")

    # Check if the new password is provided
    if not new_password:
        return jsonify({"message": "Password not provided"}), 404

    # Establish a database connection
    conn = get_db_connexion()
    cursor = conn.cursor()
    try:
        # Update the password of the agent
        pw=db.agents.update_password(agent_username,new_password,cursor)
        if pw==2:
            close_db_connexion(cursor, conn)
            return jsonify({"message": "Agent not found"}), 404
        elif pw==1:
            conn.commit()
            close_db_connexion(cursor, conn)
            return jsonify({"message": "Password successfully updated"}), 200
    except Exception as e:
        # Rollback the transaction in case of an error
        conn.rollback()
        close_db_connexion(cursor, conn)
        return jsonify({"message": "Error: while updating password", "error": str(e)}), 500

@agents_bp.route("/", methods=["POST"])
@token_required
def add_agent():
    """Add an agent to the database.
    The username and password must be passed in the data of the POST request.

    Returns
    -------
    data
        a message "Done" if the agent is correctly added
        a message "Username or password not provided" if the password or
            username is not in the data of the POST request
        an error message "Error: while adding a new agent" if an error occured
            while updating the password
    status_code
        200 if the agent was added to the database
        404 if no username and password are provided in the request
        500 if an error occured while updating the password
    """
    # Get the request data (POST request body)
    agent_data = request.get_json()

    # Extract username and password from the request data
    agent_username = agent_data.get("username")
    agent_password = agent_data.get("password")

    # Check if both username and password are provided
    if not agent_username or not agent_password:
        return jsonify({"message": "Username or password not provided"}), 404

    agent={"username":agent_username,"password":agent_password}
    # Establish database connection
    conn = get_db_connexion()
    cursor = conn.cursor()

    try:
        agent=db.agents.insert_agent(agent,cursor)
        if agent==True:
            conn.commit()
            close_db_connexion(cursor, conn)
            return jsonify({"message": "Done"}), 200
    except Exception as e:
        # Rollback the transaction in case of an error
        conn.rollback()
        close_db_connexion(cursor, conn)
        return jsonify({"message": "Error: while adding a new agent", "error": str(e)}), 500
    