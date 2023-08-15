from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, auth
from functools import wraps
from flask import Flask, jsonify, request
from flask_cors import CORS
from proxy.datebase_proxy import database_proxy
import os
import json

load_dotenv()

# Initialize Firebase Admin SDK

cred = None

if os.environ['ENV_STAGE'] != 'production':
    credentials.Certificate('speakeasy-dev-c15db-firebase-adminsdk-fjtqq-c513c0b82a.json')
else:
    cert = os.environ['ENCODED_FIREBASE_CREDENTIALS']
    # translate base64 encoded string to bytes
    cert = cert.encode('utf-8')
    # decode string into json
    cert = json.loads(cert)
    cred = credentials.Certificate(cert)

firebase_admin.initialize_app(cred)


app = Flask(__name__)
CORS(app, resources={r"/data/*": {"origins": "*", "methods": "GET,HEAD,POST,OPTIONS,PUT,DELETE", "allow_headers": "*"}})

# Authentication middleware
def authenticate(f):
    @wraps(f)
    def wrapped(*args, **kwargs):
        token = request.headers.get('Authorization')
        if token is None:
            return jsonify({"message": "No token provided"}), 401
        
        try:
            # Remove "Bearer " from the token
            decoded_token = auth.verify_id_token(token.split(" ")[1])
            request.user = decoded_token
        except Exception as e:
            return jsonify({"message": "Invalid token"}), 401
        
        return f(*args, **kwargs)
    return wrapped

@app.route('/data/get-chat-message', methods=['POST'])
@authenticate
def get_data():
    print("starting get_data")
    query = request.json.get('query')
    request_info = request.json.get('requestInfo')
    client_id = request_info.get('clientId')
    print('clientId', client_id)
    print(query)
    if database_proxy.get_database_name() != client_id:
        database_proxy.set_database_name(client_id)
        database_proxy.load_database()
    return jsonify(database_proxy.get_data(query))

@app.route('/data/update-document', methods=['POST'])
@authenticate
def update_data():
    data = request.json.get('data')
    filename = request.json.get('filename')
    request_info = request.json.get('requestInfo')
    client_id = request_info.get('clientId')
    if database_proxy.get_database_name() != client_id:
        database_proxy.set_database_name(client_id)
    return jsonify(database_proxy.update_data(data, filename))

if __name__ == '__main__':
    app.run(debug=True)
