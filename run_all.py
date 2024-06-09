import subprocess
import time

def start_node(port):
    return subprocess.Popen(['python', 'node.py', '--port', str(port)])

def start_coordinator():
    return subprocess.Popen(['python', 'coordinator.py'])

if __name__ == '__main__':
    print("************Run_all.py***************")
    node_ports = [5001, 5002, 5003, 5004]
    node_processes = [start_node(port) for port in node_ports]
    time.sleep(1)  # Give nodes some time to start
    coordinator_process = start_coordinator()
    coordinator_process.wait()  # Wait for coordinator to finish
    for process in node_processes:
        process.terminate()  # Terminate node processes
    coordinator_process.terminate()  # Terminate coordinator process
