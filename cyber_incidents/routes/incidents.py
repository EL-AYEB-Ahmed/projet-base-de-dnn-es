from flask import Blueprint, jsonify,request

incidents_bp = Blueprint("incidents", __name__)
import sqlite3
import utils
from db import get_db_connexion
from db import close_db_connexion
from utils import token_required


@incidents_bp.route("/<int:incident_id>")
def get_incident(incident_id):
    """Get an incident in the database based on its incident id.

    Parameters
    ----------
    incident_id
        id of the incident to get

    Returns
    -------
    data
        all data about the incident if correctly fetched
        a message "Incident does not exist" if the incident is not found in
            the database.
        an error message "Error: while fetching the incident" if an error
            occured while fetching the incident.
    status_code
        200 if the incident is correctly fetched
        404 if the incident does not exist in the database
        500 if an error occured while fetching the incident
    """
    try:
        # Connect to the database
        conn = get_db_connexion()
        cur = conn.cursor()

        # Fetch the incident from the database
        cur.execute("SELECT * FROM Attacks WHERE ID_attacks = ?", (incident_id,))
        incident = cur.fetchone()

        if not incident:
            return jsonify({"message": "Incident does not exist"}), 404

        # Extracting details from the fetched incident
        incident_data = {
            "ID_attacks": incident[0],
            "date": incident[1],
            "title": incident[2],
            "description": incident[3],
            "type": incident[4],
            "confirmation": incident[5],
            "ID_attackers": incident[6],
            "username": incident[7]
        }
        conn.close()
        return jsonify(incident_data), 200

    except Exception as e:
        conn.close()
        return jsonify({"message": f"Error: while fetching the incident. {str(e)}"}), 500

@incidents_bp.route("/<int:incident_id>/assign", methods=["POST"])
@token_required
def assign_incident(incident_id):
    """Assign an incident to an agent.

    Parameters
    ----------
    incident_id
        id of the incident to get

    Returns
    -------
    data
        a message "Done" if the agent is assigned correctly to the incident.
        a message "No agent username provided for assignment" if no the field
            username is not found in the request data
        a message "Incident does not exist" if the incident is not found in
            the database.
        a message "Agent does not exist" if the agent is not found in the
            database
        an error message "Error: while fetching the incident" if an error
            occured while fetching the incident.
    status_code
        200 if the agent is assigned correctly to the incident.
        400 if no the field username is not found in the request data
        404 if the incident does not exist in the database
        404 if the agent does not exist in the database
        500 if an error occured while fetching the incident
    """
    conn = get_db_connexion()
    cur = conn.cursor()
    try:
        # Get the username from the request data
        data = request.get_json()
        agent_username = data.get('username')

        if not agent_username:
            return jsonify({"message": "No agent username provided for assignment"}), 400

        # Check if the incident exists
        cur.execute("SELECT * FROM Attacks WHERE ID_attacks = ?", (incident_id,))
        incident = cur.fetchone()

        if not incident:
            return jsonify({"message": "Incident does not exist"}), 404

        # Check if the agent exists
        cur.execute("SELECT * FROM Agent WHERE username = ?", (agent_username,))
        agent = cur.fetchone()

        if not agent:
            return jsonify({"message": "Agent does not exist"}), 404

        # Assign the agent to the incident
        cur.execute("""
            UPDATE Attacks
            SET username = ?
            WHERE ID_attacks = ?
        """, (agent_username, incident_id))

        # Commit the changes to the database
        conn.commit()
        conn.close()
        return jsonify({"message": "Done"}), 200

    except Exception as e:
        conn.close()
        return jsonify({"message": f"Error: while fetching the incident. {str(e)}"}), 500

@incidents_bp.route("/<int:incident_id>", methods=["PATCH"])
@token_required
def update_incident(incident_id):
    """Update an incident in the database based on its incident id.
    The fields to update must be passed in the data of the PATCH request among
    the following (pass any of them):
        - agent_username
        - description
        - type
        - date
        - name
        - isConfirmed
        - response_type

    Parameters
    ----------
    incident_id
        id of the incident to update

    Returns
    -------
    data
        a message "Done" if the incident is updated correctly.
        a message "No field provided for update" if no field is found in the
            data passed in the request
        a message "Incident does not exist" if the incident is not found in
            the database.
        an error message "Error: while updating the incident" if an error
            occured while updating the incident.
    status_code
        200 if the incident is updated correctly
        400 if no field is found in the data passed in the request
        404 if the incident does not exist in the database
        500 if an error occured while updating the incident
    """
     # Connexion à la base de données
    conn = get_db_connexion()
    cur = conn.cursor()
    try:
        # Récupérer les champs de mise à jour à partir de la requête PATCH
        data = request.get_json()
        update_fields = []

        # Gestion des champs disponibles pour la mise à jour
        if "username" in data:
            update_fields.append("username = ?")
        if "description" in data:
            update_fields.append("description = ?")
        if "type" in data:
            update_fields.append("type = ?")
        if "date" in data:
            update_fields.append("date = ?")
        if "title" in data:
            update_fields.append("title = ?")
        if "confirmation" in data:
            update_fields.append("confirmation = ?")
        if "type_response" in data:
            update_fields.append("type_response = ?")

        # Si aucun champ n'est passé pour la mise à jour
        if not update_fields:
            return jsonify({"message": "No field provided for update"}), 400

        # Vérification si l'incident existe
        cur.execute("SELECT * FROM Attacks WHERE ID_attacks = ?", (incident_id,))
        incident = cur.fetchone()

        if not incident:
            return jsonify({"message": "Incident does not exist"}), 404

        # Générer la requête SQL de mise à jour
        update_query = f"UPDATE Attacks SET {', '.join(update_fields)} WHERE ID_attacks = ?"

        # Exécution de la requête avec les valeurs correspondantes
        cur.execute(update_query, (*data.values(), incident_id))
        conn.commit()
        conn.close()
        return jsonify({"message": "Done"}), 200

    except Exception as e:
        conn.close()
        return jsonify({"message": f"Error: while updating the incident. {str(e)}"}), 500

@incidents_bp.route("/<int:incident_id>/add", methods=["POST"])
@token_required
def add_element_to_incident(incident_id):
    """Add an element to an incident in the database based on its incident id.
    The data to update must be passed in the data of the POST request among
    the following:
        - target
        - source

    Parameters
    ----------
    incident_id
        id of the incident to update

    Returns
    -------
    data
        a message "Done" if the incident is updated correctly.
        a message "No field provided for addition" if no field is found in the
            data passed in the request
        a message "Incident does not exist" if the incident is not found in
            the database.
        an error message "Error: while updating the incident" if an error
            occured while updating the incident.
    status_code
        200 if the incident is updated correctly
        400 if no field is found in the data passed in the request
        404 if the incident does not exist in the database
        500 if an error occured while updating the incident
    """
     # Connexion à la base de données
    conn = get_db_connexion()
    cur = conn.cursor()
    try:
        # Récupérer les données de la requête
        data = request.get_json()
        # Vérifier qu'au moins un champ (target ou source) est fourni
        if not data or not ("nameV" in data or "source" in data):
            return jsonify({"message": "No field provided for addition"}), 400
        # Vérifier si l'incident existe
        cur.execute("SELECT * FROM Attacks WHERE ID_attacks = ?", (incident_id,))
        incident = cur.fetchone()        
        if not incident:
            return jsonify({"message": "Incident does not exist"}), 404

        # Ajouter un élément 'target' à l'incident
        if "nameV" in data:
            cur.execute("SELECT ID_victim FROM Victim WHERE nameV = ?", (data["nameV"],))
            result = cur.fetchone()
            target_id = result[0]
            cur.execute("INSERT INTO Attacks_Victim (ID_attacks, ID_victim) VALUES (?, ?)",(incident_id, target_id))
        # Ajouter un élément 'source' à l'incident
        if "source" in data:
            source_info = data["source"]
            cur.execute("SELECT MAX(ID_info) FROM Source")
            id_source = cur.fetchone()[0]
            # Si aucun ID n'est trouvé (si la table est vide), on démarre à 1
            if id_source is None:
                id_source=1
            else:
                id_source=id_source+1
            cur.execute("INSERT INTO Source (ID_info,source,ID_attacks) VALUES (?,?,?)",(id_source,source_info, incident_id,))
        # Valider les changements
        conn.commit()
        conn.close()
        return jsonify({"message": "Done"}), 200

    except Exception as e:
        conn.close()
        return jsonify({"message": f"Error: while updating the incident. {str(e)}"}), 500

@incidents_bp.route("/<int:incident_id>/remove", methods=["POST"])
@token_required
def remove_element_from_incident(incident_id):
    """Remove an element from an incident in the database.
    The data to update must be passed in the data of the POST request among
    the following:
        - target
        - source

    Parameters
    ----------
    incident_id
        id of the incident to update

    Returns
    -------
    data
        a message "Done" if the incident is updated correctly.
        a message "No field provided to be removed" if no field is found in the
            data passed in the request
        a message "Incident does not exist" if the incident is not found in
            the database.
        an error message "Error: while updating the incident" if an error
            occured while updating the incident.
    status_code
        200 if the incident is updated correctly
        400 if no field is found in the data passed in the request
        404 if the incident does not exist in the database
        500 if an error occured while updating the incident
    """
    # Connecter à la base de données
    conn = get_db_connexion()
    cur = conn.cursor()

    try:
 
        # Récupérer les données de la requête
        data = request.get_json()

        # Vérifier qu'au moins un champ (target ou source) est fourni
        if not data or not ("nameV" in data or "source" in data):
            return jsonify({"message": "No field provided to be removed"}), 400

        # Vérifier si l'incident existe
        cur.execute("SELECT * FROM Attacks WHERE ID_attacks = ?", (incident_id,))
        incident = cur.fetchone()

        if not incident:
            return jsonify({"message": "Incident does not exist"}), 404

        # Supprimer un élément 'target' de l'incident
        if "nameV" in data:
            target_id =cur.execute("SELECT ID_victim FROM Victim WHERE nameV=?",[data["nameV"]])
            result = cur.fetchone()
    
            # Vérifier si une victime a été trouvée
            if result:
                target_id=result[0]
            cur.execute(
                "DELETE FROM Attacks_Victim WHERE ID_attacks = ? AND ID_victim = ?",
                (incident_id, target_id)
            )

        # Supprimer un élément 'source' de l'incident
        if "source" in data:
            source_info = data["source"]
            cur.execute(
                "DELETE FROM Source WHERE ID_attacks = ? AND source = ?",
                (incident_id, source_info)
            )

        # Valider les changements
        conn.commit()
        conn.close()
        return jsonify({"message": "Done"}), 200

    except Exception as e:
        conn.close()
        return jsonify({"message": f"Error: while updating the incident. {str(e)}"}), 500
