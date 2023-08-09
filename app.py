from dotenv import load_dotenv

load_dotenv()

from flask import Flask, jsonify, request
from flask_cors import CORS
from proxy.datebase_proxy import database_proxy

app = Flask(__name__)
CORS(app)

@app.route('/data/get-chat-message', methods=['POST'])
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