from flask import Flask, request, jsonify
import os
import argparse
import json

app = Flask(__name__)

# Dictionary to store associations between filenames and chunk IDs
file_chunks = {}

@app.route('/upload_chunk', methods=['POST'])
def upload_chunk():
    chunk_data = request.data
    chunk_id = request.headers.get('Chunk-ID')  # Get chunk ID from the request headers
    chunk_path = os.path.join(storage_dir(), chunk_id)  # Use chunk ID as the filename
    with open(chunk_path, 'wb') as chunk_file:
        chunk_file.write(chunk_data)
    return jsonify({'chunk_id': chunk_id}), 200

@app.route('/associate_chunk', methods=['POST'])
def associate_chunk():
    data = request.json
    filename = data['filename']
    chunk_id = data['chunk_id']
    if filename not in file_chunks:
        file_chunks[filename] = []
    file_chunks[filename].append(chunk_id)
    return 'Association created successfully', 200

@app.route('/get_chunks/<filename>', methods=['GET'])
def get_chunks(filename):
    chunks = file_chunks.get(filename, [])
    return jsonify({'chunk_ids': chunks}), 200

@app.route('/download_chunk/<chunk_id>', methods=['GET'])
def download_chunk(chunk_id):
    chunk_path = os.path.join(storage_dir(), chunk_id)
    if os.path.exists(chunk_path):
        with open(chunk_path, 'rb') as chunk_file:
            chunk_data = chunk_file.read()
        return chunk_data, 200
    else:
        return 'Chunk not found', 404

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
