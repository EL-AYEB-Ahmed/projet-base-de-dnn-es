from flask import Blueprint, request, jsonify
import utils 
from db import agents
from db import get_db_connexion
from db import close_db_connexion
auth_bp = Blueprint("login", __name__)

@auth_bp.route("/login", methods=["POST"])
def login():
    """Login an agent and provide a token for future requests to the API

    Returns
    -------
    data
        a token to authenticate future request to the API.
        an error message "No username or password provided" if the
            username or password is not provided
        an error message "Error: while authenticating agent" if an error
            occured while authenticating the agent.
    status_code
        200 if the token is correctly provided
        400 if the username or password is not provided
        500 if an error occured while authenticating the agent
    """
    try:
        conn = get_db_connexion()
        cursor = conn.cursor()
        # Get the username and password from the request data
        data = request.get_json()
        username = data.get("username")
        password = data.get("password")

        # Check if both username and password are provided
        if not username or not password:
            return jsonify({"message": "No username or password provided"}), 400

        # Fetch the agent from the database
        agent = agents.get_agent(username,cursor)

        # Check if the agent exists
        if agent is None:
            return jsonify({"message": "Agent not found"}), 404

        # Check the password against the stored hash
        if not utils.check_password(password, agent["password"]):
            return jsonify({"message": "Invalid username or password"}), 401

        # Generate a token for the agent
        token = utils.generate_token(username)

        return jsonify({"token": token}), 200

    except Exception as e:
        return jsonify({"message": f"Error: while authenticating agent: {str(e)}"}), 500