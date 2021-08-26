import json
from VEEParser import python_to_r, python_to_octave
from VEEParser import PYTHON_TO_VEE_TYPES, Int32OrReal64, R_TO_PYTHON_TYPES
import numpy as np
import tempfile
import ast
class Client:
    def __init__(self, id):
        self.id = id # Unique Client ID
        self.search_string = '' # SearchString for DATA 
        self.script_string = '' # SearchString for SCRIPT
        self.input_data = {} # input_data from VEE(DATA)
        self.output_data = {} # OutputData from Python(GETRESULT)
        self.protocol = '' # Current protocol
        self.commands = () # commands for EXECUTE
        self.running = False # Check if EXECUTE is currently running
        self.error = [False, '']

    def python_bridge(self, conn):
        sendInputData = {}
        for key in self.input_data:
            value = self.input_data[key][1]
            sendInputData[key] = [type(value).__name__, str(value), self.input_data[key][2], self.input_data[key][3]]
        path = ''
        if(len(self.commands) > 1):
            path = self.commands[1]
        send_array = [sendInputData, self.script_string, path] # Send input Data and Script
        send_json = json.dumps(send_array) # Use json library
        send_json_size = str(len(send_json)).zfill(10)
        send_to_bridge = send_json_size + send_json
        conn.send(send_to_bridge.encode())
        recieved_dict_size = int(conn.recv(10).decode()) # recieve length of JSON string
        recieved_dict = conn.recv(recieved_dict_size).decode('utf-8') # Get Data back
        recieved_dict = json.loads(recieved_dict) # Use JSON library to load the dictionary
        for key in recieved_dict: # Loop through each fieldName in the recieved Dictonary
            dataType = recieved_dict[key][0]
            if(dataType not in PYTHON_TO_VEE_TYPES):
                recieved_dict["VEESTATUS"] = ["Int32", 1, 0, 0]
                recieved_dict["ERRORMESSAGE"] = ["Text", f'{key} Python type/object not a supported VEE Type', 0, 0]
                break
            if(recieved_dict[key][0] != "str"):
                recieved_dict[key][1] = ast.literal_eval(recieved_dict[key][1])
            isArray = PYTHON_TO_VEE_TYPES[dataType]
            if(isArray == "Array"): # check if fieldName is an Array
                numDims = len(np.array(recieved_dict[key][1]).shape) # Use numpy to get number of dimensions
                size = np.array(recieved_dict[key][1]).shape # Use numpy to get the size of each dimension
                elements = np.array(recieved_dict[key][1]).size # Use numpy to get the number of elements
                if(elements == 0):
                    recieved_dict[key] = ["Int32", 0, 0, 0] 
                else:
                    if(recieved_dict[key][0] == "int"):
                        recieved_dict[key][1] = Int32OrReal64(recieved_dict[key][1])
                    element = np.array(recieved_dict[key][1]).item(0) # get first item to check the type
                    recieved_dict[key][0] = PYTHON_TO_VEE_TYPES[type(element).__name__]
                    recieved_dict[key][2] = numDims
                    recieved_dict[key][3] = size
            else:
                if(dataType == int):
                    recieved_dict[key][1] = Int32OrReal64(recieved_dict[key][1])
                recieved_dict[key][0] = PYTHON_TO_VEE_TYPES[type(recieved_dict[key][1]).__name__]
        self.output_data = recieved_dict

    def r_bridge(self, conn):
        send_input_data = python_to_r(self.input_data) + "\n" + self.script_string
        send_data_size = str(len(send_input_data))
        conn.send(send_data_size.encode())
        conn.recv(3)
        conn.send(send_input_data.encode())
        recieve_data_size = int(conn.recv(14).decode())
        conn.send(b'OK')
        recieved_dict = conn.recv(recieve_data_size).decode()
        recieved_dict = json.loads(recieved_dict, strict=False) # Use JSON library to load the dictionary
        for key in recieved_dict:
            if(recieved_dict[key][0] not in R_TO_PYTHON_TYPES): # checks if returned R type is valid
                recieved_dict["VEESTATUS"] = ["Int32", 1, 0, 0]
                recieved_dict["ERRORMESSAGE"] = ["Text", f'{key} R type/object not a supported VEE Type', 0, 0]
                break
            elements = np.array(recieved_dict[key][1]).size # Use numpy to get the number of elements
            if(elements == 0):
                recieved_dict[key] = ["Int32", 0, 0, 0] 
                continue
            if(recieved_dict[key][0] == "logical"):
                for i in range(len(recieved_dict[key][1])):
                    if(recieved_dict[key][1][i] == "FALSE"):
                        recieved_dict[key][1][i] = bool(0)
                    else:
                        recieved_dict[key][1][i] = bool(1)
            elif(recieved_dict[key][0] == "integer"):
                for i in range(len(recieved_dict[key][1])):
                    recieved_dict[key][1][i] = int(recieved_dict[key][1][i])
                recieved_dict[key][1] = Int32OrReal64(recieved_dict[key][1])
            elif(recieved_dict[key][0] == "complex"):
                for i in range(len(recieved_dict[key][1])):
                    recieved_dict[key][1][i] = recieved_dict[key][1][i].replace("i", "j")
                    recieved_dict[key][1][i] = complex(recieved_dict[key][1][i])
            else:
                for i in range(len(recieved_dict[key][1])):
                    python_type = R_TO_PYTHON_TYPES[recieved_dict[key][0]]
                    recieved_dict[key][1][i] = python_type(recieved_dict[key][1][i])
            element = np.array(recieved_dict[key][1]).item(0) # get first item to check the type
            recieved_dict[key][0] = PYTHON_TO_VEE_TYPES[type(element).__name__]
            size = recieved_dict[key][3]
            recieved_dict[key][1] = np.array(recieved_dict[key][1]).reshape(size, order="F").flatten().tolist()
        self.output_data = recieved_dict

    def summon_r(self):
        path = f'{tempfile.gettempdir()}\\bridge_R.r'.replace("\\", "/")
        self.running.communicate(input=f"source(\"{path}\")\nq()".encode())[0]

    def octave_bridge(self, conn):
        bridge = """
return_to_python = "{";
for [key, value] = s
    return_to_python = [return_to_python '"' value '":["'];
    if (ischar(key) && isvector(key))
        if(is_dq_string(key))
            return_to_python = [return_to_python typeinfo(key) '", "' class(key) '","' undo_string_escapes(key) '", 0, 0 ],'];
        else
            return_to_python = [return_to_python typeinfo(key) '", "' class(key) '","' key '", 0, 0 ],'];
        endif
    elseif (iscellstr(key))
        if(isvector(key))
            size_array = ["[" num2str(length(key)) "]"];
            dims = "1";
        else
            size_dims = size(key);
            size_array = "[";
            dims = num2str(ndims(key));
            for i = 1:length(size_dims)
                size_array = [size_array num2str(size_dims(i)) ","];
            endfor
            size_array = substr(size_array, 1, length(size_array) - 1);
            size_array = [size_array "]"];
        endif
        array = key(:)';
        array_string = "[";
        for i = 1:length(array)
            if(is_dq_string(array{i}))
                array_string = [array_string '"' undo_string_escapes(array{i}) '"' ","];
            else
                array_string = [array_string '"' array{i} '"' ","];
            endif
        endfor
        array_string = substr(array_string, 1, length(array_string) - 1);
        array_string = [array_string "]"];
        return_to_python = [return_to_python typeinfo(key) '", "' class(key) '",' array_string ',' dims "," size_array "],"];
    elseif (isscalar(key))
        return_to_python = [return_to_python typeinfo(key) '", "' class(key) '","' num2str(key) '", 0, 0 ],'];
    elseif (strfind(typeinfo(key), "matrix"))
        if(isvector(key))
            size_array = ["[" num2str(length(key)) "]"];
            dims = "1";
        else
            size_dims = size(key);
            size_array = "[";
            dims = num2str(ndims(key));
            for i = 1:length(size_dims)
                size_array = [size_array num2str(size_dims(i)) ","];
            endfor
            size_array = substr(size_array, 1, length(size_array) - 1);
            size_array = [size_array "]"];
        endif
        array = key(:)';
        array_string = "[";
        for i = 1:length(array)
            array_string = [array_string '"' num2str(array(i)) '"' ","];
        endfor
        array_string = substr(array_string, 1, length(array_string) - 1);
        array_string = [array_string "]"];
        return_to_python = [return_to_python typeinfo(key) '", "' class(key) '",' array_string ',' dims "," size_array "],"];
    else
        error = "Unsupported Octave Type";
        return_to_python = [return_to_python typeinfo(error) '", "' class(error) '","' undo_string_escapes(error) '", 0, 0 ],'];
    endif
endfor
return_to_python = substr(return_to_python, 1, length(return_to_python) - 1);
return_to_python = [return_to_python "}"]
"""
        OCTAVE_TO_PYTHON = {
            "char": str,
            "single": float,
            "double": float,
        }
        path = self.commands[1]
        send_script = self.script_string.strip()
        send_data = [python_to_octave(self.input_data) + "\n", send_script, path, bridge]
        send_json = json.dumps(send_data) # Use json library
        send_json_size = str(len(send_json)).zfill(10)
        send_to_bridge = send_json_size + send_json
        conn.send(send_to_bridge.encode())
        recieved_dict_size = int(conn.recv(10).decode()) # recieve length of JSON string
        recieved_dict = conn.recv(recieved_dict_size).decode('utf-8') # Get Data back
        recieved_dict = json.loads(recieved_dict) # Use JSON library to load the dictionary
        for key in recieved_dict:
            if("string" in recieved_dict[key][0]):
                recieved_dict[key] = ["Text", recieved_dict[key][2], 0, 0]
            elif("matrix" in recieved_dict[key][0]):
                if("logical" in recieved_dict[key][1]):
                    array = recieved_dict[key][2]
                    for i in range(len(array)):
                        array[i] = bool(int(array[i]))
                elif("int" in recieved_dict[key][1]):
                    array = recieved_dict[key][2]
                    for i in range(len(array)):
                        array[i] = int(array[i])
                    array = Int32OrReal64(array)
                elif("complex" in recieved_dict[key][0]):
                    array = recieved_dict[key][2]
                    for i in range(len(array)):
                        array[i] = complex(array[i].replace("i", "j"))
                else:
                    python_type = OCTAVE_TO_PYTHON[recieved_dict[key][1]]
                    array = recieved_dict[key][2]
                    for i in range(len(array)):
                        array[i] = python_type(array[i])
                if(len(array) == 0):
                    recieved_dict[key] = ["Int32", 0, 0, 0]
                    continue
                else:
                    element = array[0] # get first item to check the type
                    VEE_Type = PYTHON_TO_VEE_TYPES[type(element).__name__]
                    size = recieved_dict[key][4]
                    dims = recieved_dict[key][3]
                    array = np.array(array).reshape(size, order="F").flatten().tolist()
                    recieved_dict[key] = [VEE_Type, array, dims, size]
            elif(("scalar" in recieved_dict[key][0]) or ("bool" in recieved_dict[key][0])):
                if("logical" in recieved_dict[key][1]):
                    value = bool(int(recieved_dict[key][2]))
                elif("int" in recieved_dict[key][1]):
                    value = int(recieved_dict[key][2])
                    value = Int32OrReal64(value)
                elif("complex" in recieved_dict[key][0]):
                    value = complex(recieved_dict[key][2].replace("i", "j"))
                else:
                    python_type = OCTAVE_TO_PYTHON[recieved_dict[key][1]]
                    value = python_type(recieved_dict[key][2])
                VEE_Type = PYTHON_TO_VEE_TYPES[type(value).__name__]
                recieved_dict[key] = [VEE_Type, value, 0, 0]
            elif("cell" in recieved_dict[key][0]):
                if(len(recieved_dict[key][2]) == 0):
                    recieved_dict[key] = ["Int32", 0, 0, 0]
                    continue
                recieved_dict[key] = ["Text", recieved_dict[key][2], recieved_dict[key][3], recieved_dict[key][4]]
        self.output_data = recieved_dict