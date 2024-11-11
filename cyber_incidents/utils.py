import bcrypt
import jwt
import datetime
from functools import wraps
from flask import request, jsonify
import csv
import utils
import sqlite3

CONFIG_FILE = "./config/config"

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

def load_config():
    """Loads the application configuration from the configuration file
    into a dictionary.

    Returns
    -------
    A dictionary.
        The application configuration.
    """
    config = {}         # The dictionary to return.
    with open(CONFIG_FILE,mode='r',newline='',encoding='utf-8') as config_file:
        lecteur_csv=csv.reader(config_file)
        for ligne in lecteur_csv:
            #on crée les différentes clés du dictionnaire
            config[str(ligne[0])] = str(ligne[1])
    return config

def hash_password(plain_password):
    """Hash a password

    Parameters
    ----------
    plain_password
        plain password to hash

    Returns
    -------
    hashed_password
        A password hash
    """
     # Convertir le mot de passe en bytes
    password_bytes = str(plain_password).encode('utf-8')

    # Générer un salt pour hacher le mot de passe
    salt = bcrypt.gensalt()

    # Hacher le mot de passe avec bcrypt
    hashed_password = bcrypt.hashpw(password_bytes, salt)

    return hashed_password

def check_password(plain_password,hashed_password):
    """Check the plain password against its hashed value

    Parameters
    ----------
    plain_password
        the plain password to check
    hashed_password
        a password hash to check if it is the hash of the plain password

    Returns
    -------
    bool
        True if hashed_password is the hash of plain_password, False otherwise
    """
    # Convertir le mot de passe en texte clair en bytes
    plain_password = str(plain_password).encode('utf-8')

    # Utiliser bcrypt pour comparer le mot de passe en clair et son hachage
    return bcrypt.checkpw(plain_password,hashed_password)
    
def check_agent(username, plain_password):
    """Authenticate an agent based on its username and a plain password.

    Parameters
    ----------
    username
        the agent username
    plain_password
        the plain password to check

    Returns
    -------
    bool
        True if the password is associated to the agent, False otherwise
    """
    # Connexion à la base de données
    conn = get_db_connexion()  # Remplacez par le chemin de votre base de données
    cursor = conn.cursor()

    # Récupérer le mot de passe haché de l'agent à partir de la base de données
    cursor.execute("SELECT password FROM Agent WHERE username = ?", (username,))
    result = cursor.fetchone()
    # Vérifier si l'agent existe
    if result is None:
        return False  # L'agent n'existe pas
    # Obtenir le mot de passe haché
    hashed_password = result[0]
    # Vérifier le mot de passe fourni
    return check_password(int(plain_password),hashed_password)

def generate_token(username):
    """Generate a token with a username and an expiracy date of 1h.

    Parameters
    ----------
    username
        the agent username

    Returns
    -------
    token
        the generated token based on the username and an expiracy date of 1h.
    """
    try:
        # Définir la date d'expiration
        expiration_time = datetime.datetime.utcnow() + datetime.timedelta(hours=1)

        # Créer le payload du token
        payload = {
            'username': username,
            'exp': expiration_time
        }

        # Charger la clé secrète depuis la configuration
        secret_key = load_config().get('SECRET_KEY')
        
        if not secret_key:
            raise ValueError("Clé secrète manquante dans la configuration")

        # Générer le token en utilisant la clé secrète
        token = jwt.encode(payload, key=secret_key, algorithm="HS256")

        # Si la version de PyJWT retourne un objet bytes, on le décode en string
        if isinstance(token, bytes):
            token = token.decode('utf-8')

        return token

    except Exception as e:
        print(f"Erreur lors de la génération du token: {str(e)}")
        return None

def check_token(token):
    """Check the validity of a token.

    Parameters
    ----------
    token
        the token to check

    Returns
    -------
    payload
        The payload associated with the token if the token is correctly decoded.
        An error if the token is expired or invalid
    """
    try:
        # Load the secret key from the config
        secret_key = load_config()['SECRET_KEY'] 
        # Decode the token using the secret key and specifying the algorithm
        payload = jwt.decode(token, key=secret_key, algorithms=["HS256"])
        return payload
    except jwt.ExpiredSignatureError:
        # Token has expired
        return {"message": "Token has expired"}, 401
    except jwt.InvalidTokenError:
        # Token is invalid (signature failure or token is malformed)
        return {"message": "Invalid token"}, 401

def token_required(f):
    """A decorator to specify which routes need a token validation."""

    @wraps(f)
    def decorated(*args, **kwargs):
        """Define the behaviour of a route when a token validation is required.
        """
        token = None

        if "Authorization" in request.headers:
            token = request.headers["Authorization"].split(" ")[0]

        if not token:
            return jsonify({"message": "Missing token"}), 401

        try:
            payload = check_token(token)
            if not "username" in payload or not "exp" in payload:
                return jsonify({"error": "Invalid token"}), 401

        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401
        return f(*args, **kwargs)

    return decorated
