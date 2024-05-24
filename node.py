# node.py
from flask import Flask, request, jsonify
import os
import uuid
import argparse

app = Flask(__name__)

@app.route('/upload_chunk', methods=['POST'])
def upload_chunk():
    chunk_data = request.data
    chunk_id = str(uuid.uuid4())  # Generate a unique chunk ID
    chunk_path = os.path.join(storage_dir(), chunk_id)  # Use storage_dir() function to get storage directory
    with open(chunk_path, 'wb') as chunk_file:
        chunk_file.write(chunk_data)
    return jsonify({'chunk_id': chunk_id}), 200

@app.route('/associate_chunk', methods=['POST'])
def associate_chunk():
    data = request.json
    filename = data['filename']
    chunk_id = data['chunk_id']
    # Store the association between filename and chunk ID (you can use a dictionary)
    return 'Association created successfully', 200

def storage_dir():
    port = int(os.environ.get("PORT", 5000))  # Get port from environment variable, default to 5000
    return f'storage_{port}'  # Directory name based on port number

if __name__ == '__main__':
    print("************Node.py***************")
    parser = argparse.ArgumentParser(description='Run the node server.')
    parser.add_argument('--port', type=int, default=5000, help='Port to run the server on')
    args = parser.parse_args()
    os.environ["PORT"] = str(args.port)  # Set environment variable for port
    storage_path = storage_dir()
    if not os.path.exists(storage_path):
        os.makedirs(storage_path)
    app.run(port=args.port)
