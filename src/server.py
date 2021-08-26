from VEEParser import read_string, send_record
from VEEParser import send_string, PYTHON_TO_VEE_TYPES, read_script, R_TO_PYTHON_TYPES
import socket
import argparse
import subprocess
import threading
import os
import uuid
from bridgescripts import BRIDGE_SCRIPTS
import tempfile
from client import Client
PROTOCOLS = set(("DATA","SCRIPT", "SERVERSHUTDOWNTIMEOUT", "GETRESULT", "HALT", "EXECUTE", "BRIDGE", "STATUS", "QUIT"))
client_list = dict()
TIMEOUT = 120
TIMEOUTENABLE = True
HEADER_SIZE = 22
DEBUG = 1
PYTHON_PATH = '.\\python.exe'
def handle_new_client(conn,s, HOST, PORT):
    global PROTOCOLS, PYTHON_TO_VEE_TYPES, HEADER_SIZE, DEBUG, PYTHON_PATH
    client = Client(str(uuid.uuid4()))
    client_list[client.id] = client
    while conn:
        try:
            recieved_message = conn.recv(HEADER_SIZE) # String given by VEEPro, print this for debugging
        except:
            conn.close()
            break
        if(DEBUG):
            print(repr(recieved_message))
        recieved_message = recieved_message.decode().strip()
        if(not recieved_message):
            break
        if(recieved_message in PROTOCOLS): # Check if the recieved Message is a protocol
            client.protocol = recieved_message
        else:
            conn.send(send_string("Incorrect Protocol").encode("utf-8"))
            continue
        if(client.protocol == "DATA"):
            conn.send(send_string("SEND").encode())
            recievedSize = conn.recv(11).decode("utf-8")
            size = int(recievedSize)
            conn.send(send_string("SIZE").encode())
            recievedContainer = conn.recv(size + 100)
            recievedContainer = recievedContainer.decode()
            if(DEBUG):
                print(repr(recievedContainer))
            lines = recievedContainer.split("\n")
            for line in lines:
                if(line != ''):
                    client.search_string += line + '\n'
            try:
                client.input_data = read_string(client.search_string)
            except TypeError as err:
                client.error[0] = True
                client.error[1] = err.args[0]
            client.search_string = ''
            client.protocol = ''
            conn.send(send_string("OK").encode())

        elif(client.protocol == "SCRIPT"):
            conn.send(send_string("SIZE").encode())
            recievedSize = conn.recv(11).decode("utf-8")
            size = int(recievedSize)
            conn.send(send_string("SEND").encode())
            recievedContainer = conn.recv(size + 100).decode("utf-8")
            lines = recievedContainer.split("\n")
            for line in lines:
                if('[' in line):
                    client.script_string = read_script(line)
                    if("#!" in client.script_string[:4]):
                        client.commands = client.script_string.partition('\n')[0][2:].strip().split(" ",1)
                        client.commands[0] = client.commands[0].lower()
                        client.script_string = client.script_string.partition('\n')[2] # remove first line of script
                    else:
                        client.commands = tuple(["python"])
            conn.send(send_string("OK").encode())

        elif(client.protocol == "EXECUTE"):
            if(not client.script_string or not client.input_data):
                sendString = send_string(client.error[1])
                conn.send(sendString.encode("utf-8"))
                continue
            else:
                if("python" in client.commands[0]):
                    if(len(client.commands) > 1):
                        if(os.path.basename(client.commands[1]) != "python.exe"):
                            conn.send(send_string("Incorrect filepath").encode("utf-8"))
                            continue
                        if(os.path.exists(client.commands[1])):
                            client.running = subprocess.Popen([client.commands[1], f'{tempfile.gettempdir()}\\bridge_python.py', 
                            client.id, f'--host={HOST}', f'--port={PORT}'])
                        else:
                            conn.send(send_string("Invalid Path").encode("utf-8"))
                            continue
                    else:
                        client.running = subprocess.Popen([PYTHON_PATH, f'{tempfile.gettempdir()}\\bridge_python.py', 
                        client.id, f'--host={HOST}', f'--port={PORT}'])
                if("fiji" in client.commands[0]):
                    if((os.path.basename(client.commands[1]) != "ImageJ-win64.exe") and (os.path.basename(client.commands[1]) != "ImageJ-win32.exe")):
                        conn.send(send_string("Invalid Path").encode("utf-8"))
                        continue
                    filePath = client.commands[1]
                    command = f'{filePath} --ij2 --run "{tempfile.gettempdir()}\\bridge_jython.py" "id=\'{client.id}\', host=\'{HOST}\', port={PORT}"'
                    client.running = subprocess.Popen(command)
                if("r" in client.commands[0]):
                    invalid = False
                    for item in client.input_data:
                        if(not client.input_data[item][2]):
                            conn.send(send_string(f"{item} not an array").encode())
                            invalid = True
                    if(invalid):
                        continue
                    if(os.path.basename(client.commands[1]) != "R.exe"):
                        conn.send(send_string("Incorrect filepath").encode("utf-8"))
                        continue
                    file_path = client.commands[1]
                    cmd = f"{file_path} --ess --vanilla --args {client.id} {HOST} {PORT}" 
                    client.running = subprocess.Popen(cmd, stdin=subprocess.PIPE,stdout=subprocess.PIPE)
                    r_thread = threading.Thread(target=client.summon_r, daemon=True)
                    r_thread.start()
                if("octave" in client.commands[0]):
                    if(os.path.basename(client.commands[1]) != "octave-gui.exe"):
                        conn.send(send_string("Incorrect filepath").encode("utf-8"))
                        continue
                    client.running = subprocess.Popen([PYTHON_PATH, f'{tempfile.gettempdir()}\\bridge_octave.py', 
                    client.id, f'--host={HOST}', f'--port={PORT}'])
                if("maxima" in client.commands[0]):
                    if(os.path.basename(client.commands[1]) != "maxima.bat"):
                        conn.send(send_string("Incorrect filepath").encode("utf-8"))
                        continue
                    client.running = subprocess.Popen([PYTHON_PATH, f'{tempfile.gettempdir()}\\bridge_maxima.py', 
                    client.id, f'--host={HOST}', f'--port={PORT}'])
                sendString = send_string("OK")
                conn.send(sendString.encode("utf-8"))

        elif(client.protocol == "STATUS"):
            if(client.error[0]):
                sendString = send_string(client.error[1])
                conn.send(sendString.encode("utf-8"))
            else:
                if(client.running):
                    if(client.running.poll() is None):
                        conn.send(send_string("BUSY").encode("utf-8"))
                    else:
                        conn.send(send_string("OK").encode("utf-8"))
                else:
                    conn.send(send_string("OK").encode("utf-8"))

        elif(client.protocol == "GETRESULT"):
            if(client.error[0]):
                sendString = send_string(client.error[1])
                conn.send(sendString.encode("utf-8"))
            else:
                if(DEBUG):
                    print(repr(client.output_data))
                sendString = send_record(client.output_data)
                sendBuffSize = str(len(sendString)) + "\n"
                sendToVEE = sendBuffSize + sendString
                conn.send(sendToVEE.encode())
                if(DEBUG):
                    print(repr(sendToVEE))

        elif(recieved_message == "BRIDGE"): # Bridge protocol (Reserved for Bridgescripts)
            del client_list[client.id] # deletes client from client_list as EXECUTE is a not a "real" new client
            del client
            conn.send(b'OK') # Send OK back
            recievedID = conn.recv(36).decode('utf-8') # Get real Client ID
            currentClient = client_list[recievedID]
            python_bridges = ["python", "embed", "fiji", "maxima"]
            if(currentClient.commands[0] in python_bridges):
                currentClient.python_bridge(conn)
            if(currentClient.commands[0] == "r"):
                currentClient.r_bridge(conn)
            if(currentClient.commands[0] == "octave"):
                currentClient.octave_bridge(conn)
            conn.close()
            break

        elif(recieved_message == "SERVERSHUTDOWNTIMEOUT"):
            conn.send(send_string("OK").encode("utf-8"))
            recievedSize = int(conn.recv(11).decode("utf-8"))
            s.settimeout(recievedSize)
            conn.send(send_string("OK").encode("utf-8"))

        elif(client.protocol == "QUIT"):
            cleanup()
            conn.send(send_string("OK").encode("utf-8"))
            print("Shutting down server...")
            conn.close()
            s.close()
            break
        
        elif(client.protocol == "HALT"):
            conn.send(send_string("OK").encode("utf-8"))
            print("Closing Connection...")
            del client_list[client.id]
            del client
            conn.close()
            break

def cleanup():
    for key in BRIDGE_SCRIPTS:
        if(os.path.exists(f'{tempfile.gettempdir()}\\bridge_{key}.{BRIDGE_SCRIPTS[key][1]}')):
            os.remove(f'{tempfile.gettempdir()}\\bridge_{key}.{BRIDGE_SCRIPTS[key][1]}')

def main(host, port):
    global PROTOCOLS, BRIDGE_SCRIPTS, TIMEOUT, TIMEOUTENABLE
    for key in BRIDGE_SCRIPTS:
        bridgeFile = open(f'{tempfile.gettempdir()}\\bridge_{key}.{BRIDGE_SCRIPTS[key][1]}','w')
        bridgeFile.write(BRIDGE_SCRIPTS[key][0])
        bridgeFile.close()
    isConnected = True
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            if(TIMEOUTENABLE):
                s.settimeout(TIMEOUT)
            s.bind((host, port))
            print(f'Binded on host = {host} and port = {port}')
            print("Listening...")
            s.listen()
        except Exception as msg:
            print('An error occurred:\n' + str(msg))
            send_string('An error occurred: ' + str(msg))
            isConnected = False
        # This while loop means the server is continuously running
        while (isConnected):
            try:
                conn, addr = s.accept() # Waiting for a connection from VEEPro (async)
                t1 = threading.Thread(target=handle_new_client, args=(conn,s,host,port,))
                t1.daemon = True
                t1.start()
            except socket.timeout:
                print("TIMED OUT")
                cleanup()
                s.close()
                break
            except OSError:
                cleanup()
                s.close()
                break

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Initate the VEE to Python server connection')
    parser.add_argument('--host', default='127.0.0.1', help="Connect to a specific host. Default is 127.0.0.1 (localhost).")
    parser.add_argument('--port', default=65433, type=int, help="Port to connect to server. Default is 65433.")
    
    args = parser.parse_args()
    main(args.host, args.port)

