from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, auth
from functools import wraps
from flask import Flask, jsonify, request
from flask_cors import CORS
from proxy.SpeakeasyBackendProxy import speakeasy_backend_proxy
from proxy.datebase_proxy import database_proxy
import os
import json
import base64

from base64 import b64encode

load_dotenv()

# Initialize Firebase Admin SDK

cred = None

if os.environ['ENV_STAGE'] != 'production':
    cred = credentials.Certificate('speakeasy-dev-c15db-firebase-adminsdk-fjtqq-c513c0b82a.json')
else:
    encoded_cert = os.environ['ENCODED_FIREBASE_CREDENTIALS']
    # Decode base64 encoded string to bytes
    decoded_bytes = base64.b64decode(encoded_cert)
    # Decode bytes to string
    decoded_str = decoded_bytes.decode('utf-8')
    # Load string into a JSON object
    cert_json = json.loads(decoded_str)
    # Initialize Firebase credentials using the decoded JSON object
    cred = credentials.Certificate(cert_json)

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
            request.user_encoded = token.split(" ")[1]
        except Exception as e:
            print(e)
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
    if database_proxy.get_client_id() != client_id:
        database_proxy.set_client_id(client_id)
        database_proxy.load_database()
    return jsonify(database_proxy.get_data(query))

@app.route('/data/update-document', methods=['POST'])
@authenticate
def update_data():
    file = request.files.get('file')
    filename = request.form.get('filename')
    request_info_json = request.form.get('requestInfo')
    request_info = json.loads(request_info_json) if request_info_json else {}
    client_id = request_info.get('clientId')
    if database_proxy.get_client_id() != client_id:
        database_proxy.set_client_id(client_id)
    database_proxy.update_data(file, filename)  # Assumes this method now accepts bytes
    return jsonify({"message": "Document updated successfully"}), 200


@app.route('/data/delete-document', methods=['POST'])
@authenticate
def delete_data():
    filename = request.json.get('filename')
    request_info = request.json.get('requestInfo')
    client_id = request_info.get('clientId')
    if database_proxy.get_client_id() != client_id:
        database_proxy.set_client_id(client_id)
    success = database_proxy.delete_data(filename)
    if success:
        return jsonify({"message": "Document deleted successfully"}), 200
    else:
        return jsonify({"message": "Failed to delete document"}), 500
    
@app.route('/data/list-documents', methods=['POST'])
@authenticate
def list_documents():
    request_info = request.json.get('requestInfo')
    client_id = request_info.get('clientId')
    if database_proxy.get_client_id() != client_id:
        database_proxy.set_client_id(client_id)
    files = database_proxy.list_data()
    return jsonify(files)

@app.route('/data/download-document', methods=['POST'])
@authenticate
def download_document():
    filename = request.json.get('filename')
    request_info = request.json.get('requestInfo')
    client_id = request_info.get('clientId')
    if database_proxy.get_client_id() != client_id:
        database_proxy.set_client_id(client_id)
    
    data = database_proxy.download_data(filename)
    if data is not None:
        encoded_data = b64encode(data).decode()  # Convert bytes to base64 encoded string
        return jsonify({"data": encoded_data})
    else:
        return jsonify({"error": "File not found"}), 404
    
@app.route('/data/upload-slack-messages-to-s3', methods=['POST'])
@authenticate
def upload_slack_messages_to_s3():
    print("starting upload_slack_messages_to_s3")
    request_info = request.json.get('requestInfo')
    print(request_info)
    client_id = request_info.get('clientId')
    if database_proxy.get_client_id() != client_id:
        database_proxy.set_client_id(client_id)
    print("getting slack access token")
    slack_access_token = speakeasy_backend_proxy.get_slack_access_token_for_chatbot(client_id, request.user_encoded)
    print("saving slack conversations to s3")
    database_proxy.save_slack_conversations_to_s3(slack_access_token)
    notion_access_token = speakeasy_backend_proxy.get_notion_access_token_for_chatbot(client_id, request.user_encoded)
    database_proxy.save_notion_data_to_s3(notion_access_token)
    linear_access_token = speakeasy_backend_proxy.get_linear_access_token_for_chatbot(client_id, request.user_encoded)
    database_proxy.save_linear_data_to_s3(linear_access_token)
    database_proxy.load_database()
    return jsonify({"message": "Slack messages uploaded successfully"}), 200
    
if __name__ == '__main__':
    app.run(debug=True, port=3000)
