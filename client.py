import requests

def upload_file(file_path, coordinator_url):
    with open(file_path, 'rb') as file:
        files = {'file': file}
        response = requests.post(f'{coordinator_url}/upload', files=files)
    return response.text

def download_file(filename, coordinator_url, save_path):
    response = requests.get(f'{coordinator_url}/download/{filename}')
    if response.status_code == 200:
        with open(save_path, 'wb') as file:
            file.write(response.content)
        return 'File downloaded successfully'
    else:
        return 'File not found'

if __name__ == '__main__':
    print("************Client.py***************")
    coordinator_url = 'http://localhost:5005'
    print(upload_file('example.txt', coordinator_url))
    print(download_file('example.txt', coordinator_url, 'downloaded_example.txt'))
