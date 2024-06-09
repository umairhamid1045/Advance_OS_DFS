# coordinator.py
from flask import Flask, request, jsonify, send_file, render_template
import requests
import time
import os

app = Flask(__name__)
chunk_servers = ['http://localhost:5001', 'http://localhost:5002', 'http://localhost:5003', 'http://localhost:5004']
global_chunk_counter = 1  # Start chunk counter at 1
replication_factor = 3  # Replicate each chunk on 3 different servers

def wait_for_server(url):
    while True:
        try:
            requests.get(url)
            break
        except requests.exceptions.ConnectionError:
            time.sleep(1)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    global global_chunk_counter
    file = request.files['file']
    client_name = request.form['clientName']
    filename = file.filename
    chunk_size = 1024 * 1024  # 1 MB chunk size (adjust as needed)
    chunks = []
    with file.stream:  # Access the underlying file object
        while True:
            chunk = file.stream.read(chunk_size)
            if not chunk:
                break
            chunks.append(chunk)
    for idx, chunk_data in enumerate(chunks):
        chunk_id = f"{client_name}-{filename}-{global_chunk_counter}"  # Use client_name, filename, and global_chunk_counter as the chunk ID
        global_chunk_counter += 1  # Increment global chunk counter for the next chunk
        
        # Distribute the chunk to multiple servers for replication
        for i in range(replication_factor):
            chunk_server_url = chunk_servers[(global_chunk_counter + i) % len(chunk_servers)]
            wait_for_server(chunk_server_url)
            response = requests.post(f'{chunk_server_url}/upload_chunk', data=chunk_data, headers={"Chunk-ID": chunk_id})
            if response.status_code == 200:
                # Associate the chunk ID with the filename
                requests.post(f'{chunk_server_url}/associate_chunk', json={'filename': filename, 'chunk_id': chunk_id})
    return 'File uploaded successfully', 200

@app.route('/download/<client_name>/<filename>', methods=['GET'])
def download_file(client_name, filename):
    # Retrieve chunk IDs associated with the filename
    chunk_ids = set()
    for chunk_server_url in chunk_servers:
        wait_for_server(chunk_server_url)
        response = requests.get(f'{chunk_server_url}/get_chunks/{filename}')
        if response.status_code == 200:
            chunk_ids.update(response.json()['chunk_ids'])

    # Retrieve chunks from chunk servers
    file_chunks = []
    for chunk_id in sorted(chunk_ids):
        if chunk_id.startswith(f"{client_name}-{filename}"):
            chunk_found = False
            for chunk_server_url in chunk_servers:
                wait_for_server(chunk_server_url)
                response = requests.get(f'{chunk_server_url}/download_chunk/{chunk_id}')
                if response.status_code == 200:
                    file_chunks.append(response.content)
                    chunk_found = True
                    break  # Move to the next chunk ID
            if not chunk_found:
                return f"Chunk {chunk_id} not found", 500  # If a chunk is missing, return an error

    # Reassemble file from chunks
    file_data = b''.join(file_chunks)
    save_path = os.path.join('downloads', filename)
    with open(save_path, 'wb') as f:
        f.write(file_data)
    return send_file(save_path, as_attachment=True)

if __name__ == '__main__':
    print("************Coordinator.py***************")
    if not os.path.exists('downloads'):
        os.makedirs('downloads')
    app.run(port=5005)
