from flask import Blueprint, request, jsonify

data_bp = Blueprint("data", __name__)
import sqlite3
import utils
import csv
from utils import token_required

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

@data_bp.route("/sources")
@token_required
def get_sources():
    """Get all sources in the database.

    Returns
    -------
    data
        all sources in the database
        an error message "Error: while fetching sources" if an error occured
            while fetching the sources.
    status_code
        200 if the sources are correctly fetched
        500 if an error occured while fetching the sources
    """
    conn = get_db_connexion()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM Source WHERE source <> ''")
        sources =cursor.fetchall()

        if not sources:
            return jsonify({"message": "No sources found"}), 404
        conn.close()
        return jsonify({"sources": [dict(source)["source"] for source in sources]}), 200
    except Exception as e:
        conn.close()
        return jsonify({"message": "Error: while fetching sources", "error": str(e)}), 500
    
@data_bp.route("/targets")
@token_required
def get_targets():
    """Get all targets in the database.

    Returns
    -------
    data
        all targets in the database
        an error message "Error: while fetching targets" if an error occured
            while fetching the targets.
    status_code
        200 if the targets are correctly fetched
        500 if an error occured while fetching the targets
    """
    conn = get_db_connexion()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM Victim")
        targets = cursor.fetchall()

        if not targets:
            return jsonify({"message": "No targets found"}), 404
        conn.close()
        return jsonify({"targets": [dict(target)["nameV"] for target in targets]}), 200
        
    except Exception as e:
        conn.close()
        return jsonify({"message": "Error: while fetching targets", "error": str(e)}), 500

@data_bp.route("/attackers")
@token_required
def get_attackers():
    """Get all attackers in the database.

    Returns
    -------
    data
        all attackers in the database
        an error message "Error: while fetching attackers" if an error occured
            while fetching the attackers.
    status_code
        200 if the attackers are correctly fetched
        500 if an error occured while fetching the attackers
    """
    conn = get_db_connexion()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM Attackers")
        attackers = cursor.fetchall()

        if not attackers:
            return jsonify({"message": "No attackers found"}), 404
        conn.close()
        return jsonify({"attackers": [dict(attacker)["affiliation_name"] for attacker in attackers]}), 200

    except Exception as e:
        conn.close()
        return jsonify({"message": "Error: while fetching attackers", "error": str(e)}), 500

@data_bp.route("/responses")
def get_responses():
    """Get all responses in the database.

    Returns
    -------
    data
        all responses in the database
        an error message "Error: while fetching responses" if an error occured
            while fetching the responses.
    status_code
        200 if the responses are correctly fetched
        500 if an error occured while fetching the responses
    """
    conn = get_db_connexion()
    cursor = conn.cursor()

    try:
        cursor.execute("SELECT * FROM Response WHERE source_of_response <> ''")
        responses = cursor.fetchall()

        if not responses:
            return jsonify({"message": "No responses found"}), 404
        conn.close()
        return jsonify({"responses": [dict(response)["source_of_response"] for response in responses]}), 200

    except Exception as e:
        conn.close()
        return jsonify({"message": "Error: while fetching responses", "error": str(e)}), 500
