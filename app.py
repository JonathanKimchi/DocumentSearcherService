from flask import Flask, jsonify, request
import proxy.datebase_proxy as datebase_proxy

app = Flask(__name__)

@app.route('/data/get-chat-message', methods=['POST'])
def get_data():
    query = request.json.get('query')
    print(query)
    return jsonify(datebase_proxy.get_data(query))

@app.route('/data/update-document', methods=['POST'])
def update_data():
    data = request.json.get('data')
    filename = request.json.get('filename')
    return jsonify(datebase_proxy.update_data(data, filename))

if __name__ == '__main__':
    app.run(debug=True)