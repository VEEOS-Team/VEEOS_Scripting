# Bridge scripts are designed to communicate with specified engine installed in the user's computer
# They written into the computer's Temp folder and then they are deleted once the server exits
BRIDGE_SCRIPTS = {
        "python" :[ """from collections import OrderedDict
import socket
import json
import re
import argparse
import sys
import traceback
import ast
import struct
def checkforVEE(script):
    returnToVEE = []
    checkRegex = r'returnToVEE( +)(((.+)(,)?)+)'
    returnScript = ''
    for line in script.split("\\n"):
        if(re.match(checkRegex, line)):
            matched = re.match(checkRegex, line)
            args = matched.group(2).split(",")
            for item in args:
                item = item.strip()
                if(item == ""):
                    continue
                else:
                    returnToVEE.append(item)
        else:
            returnScript += line + "\\n"
    return returnScript, returnToVEE
def execute_script(_input, _script):
    _outputData = {}
    eval_globals = dict() # create new environment for exec script
    for item in globals():
        eval_globals[item] = globals()[item]
    del eval_globals["checkforVEE"] # delete global namespaces
    del eval_globals["main"]
    del eval_globals["execute_script"]
    del eval_globals["args"]
    for key in _input.keys(): # loop through the keys in dictionary (which are the fieldNames in the Record)
        if(_input[key][0] != "str"):
            _value = ast.literal_eval(_input[key][1])
        else:
            _value = _input[key][1]
        eval_globals[key] = _value
    _script, returnToVEE = checkforVEE(_script)
    try:
        exec(_script, eval_globals)
    except Exception as err:
        lineRegex = r'File "<string>", line (\d+)'
        lineNumber = re.search(lineRegex, traceback.format_exc()).group(1)
        errorMessage = err.__class__.__name__ + ": " + err.args[0] + " at line number " + lineNumber
        _outputData["VEESTATUS"] = ["int", "1", 0, 0]
        _outputData["ERRORMESSAGE"] = ["str", errorMessage, 0, 0]
        return _outputData
    if(returnToVEE):
        try:
            for key in returnToVEE: # loop through the keys in dictionary (which are the fieldNames in the Record)
                _outputData[key] = [0, eval_globals[key], 0, 0]
                _outputData[key][0] = type(_outputData[key][1]).__name__
                _outputData[key][1] = str(_outputData[key][1])
        except Exception as err:
            errorMessage = err.__class__.__name__ + ": " + err.args[0]
            _outputData["VEESTATUS"] = ["int", "1", 0, 0]
            _outputData["ERRORMESSAGE"] = ["str", errorMessage, 0, 0]
            return _outputData
    _outputData["VEESTATUS"] = ["int", "0", 0, 0]
    return _outputData
def main(id, host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    s.send(b'BRIDGE')
    s.recv(2)
    s.send(id.encode('utf-8'))
    recievedBufferSize = int(s.recv(10).decode('utf-8'))
    recievedDict = s.recv(recievedBufferSize)
    recievedDict = json.loads(recievedDict.decode('utf-8'))
    outputDict = execute_script(recievedDict[0], recievedDict[1])
    sendoutputDictSize = str(len(json.dumps(outputDict))).zfill(10)
    s.send(sendoutputDictSize.encode('utf-8'))
    s.send(json.dumps(outputDict).encode('utf-8'))
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('id')
    parser.add_argument('--host', default='127.0.0.1', help="Connect to a specific host. Default is 127.0.0.1 (localhost).")
    parser.add_argument('--port', default=65433, type=int, help="Port to connect to server. Default is 65433.")
    args = parser.parse_args()
    main(args.id, args.host, args.port)""","py"],




    "jython": ["""#@ String id
#@ String host
#@ int port 
from collections import OrderedDict
import socket
import json
import re
import argparse
import traceback
import ast
def checkforVEE(script):
    returnToVEE = []
    checkRegex = r'returnToVEE( +)(((.+)(,)?)+)'
    returnScript = ''
    for line in script.split("\\n"):
        if(re.match(checkRegex, line)):
            matched = re.match(checkRegex, line)
            args = matched.group(2).split(",")
            for item in args:
                item = item.strip()
                if(item == ""):
                    continue
                else:
                    returnToVEE.append(item)
        else:
            returnScript += line + "\\n"
    return returnScript, returnToVEE
def execute_script(_input, _script):
    _outputData = {}
    eval_globals = dict() # create new environment for exec script
    for item in globals():
        eval_globals[item] = globals()[item]
    del eval_globals["checkforVEE"] # delete global namespaces
    del eval_globals["main"]
    del eval_globals["execute_script"]
    for key in _input.keys(): # loop through the keys in dictionary (which are the fieldNames in the Record)
        if(_input[key][0] != "str"):
            _value = ast.literal_eval(_input[key][1])
        else:
            _value = _input[key][1]
        eval_globals[key] = _value
    _script, returnToVEE = checkforVEE(_script)
    try:
        exec(_script, eval_globals)
    except Exception as err:
        lineRegex = r'File "<string>", line (\d+)'
        lineNumber = re.search(lineRegex, traceback.format_exc()).group(1)
        errorMessage = err.__class__.__name__ + ": " + err.args[0] + " at line number " + lineNumber
        _outputData["VEESTATUS"] = ["int", "1", 0, 0]
        _outputData["ERRORMESSAGE"] = ["str", errorMessage, 0, 0]
        return _outputData
    if(returnToVEE):
        try:
            for key in returnToVEE: # loop through the keys in dictionary (which are the fieldNames in the Record)
                _outputData[key] = [0, eval_globals[key], 0, 0]
                _outputData[key][0] = type(_outputData[key][1]).__name__
                _outputData[key][1] = str(_outputData[key][1])
        except Exception as err:
            errorMessage = err.__class__.__name__ + ": " + err.args[0]
            _outputData["VEESTATUS"] = ["int", "1", 0, 0]
            _outputData["ERRORMESSAGE"] = ["str", errorMessage, 0, 0]
            return _outputData
    _outputData["VEESTATUS"] = ["int", "0", 0, 0]
    return _outputData
def main(id, host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    s.send(b'BRIDGE')
    s.recv(2)
    s.send(id.encode('utf-8'))
    recievedBufferSize = int(s.recv(10).decode('utf-8'))
    recievedDict = s.recv(recievedBufferSize)
    recievedDict = json.loads(recievedDict.decode('utf-8'))
    outputDict = execute_script(recievedDict[0], recievedDict[1])
    sendoutputDictSize = str(len(json.dumps(outputDict))).zfill(10)
    s.send(sendoutputDictSize.encode('utf-8'))
    s.send(json.dumps(outputDict).encode('utf-8'))
if __name__ == '__main__':
    main(id, host, port)""", "py"],




    "R" : ["""
returnToVEE <- vector()
    r_to_python <- function(values) {
        return_value <- "{"
        counter = 1
        for (current_value in values) {
        if (!is.null(dim(current_value))) { # check if it is an array or matrix
                size <- dim(current_value)
                dims <- length(size)
                size <- paste(size, collapse = ",")
                size <- paste("[", size, "]", sep="")
            }
        else{
                size <- paste("[", length(current_value), "]", sep="")
                dims <- 1
            }
            one_dimension_array <- c(current_value)
            one_dimension_array <- paste(one_dimension_array,collapse = "\\\",\\\"")
            one_dimension_array <- paste("[\\\"", one_dimension_array, "\\\"]",sep="")
            type = paste("\\\"", typeof(current_value), "\\\"", sep="")
            send_list <- paste(type, one_dimension_array, dims, 
                                   size, sep = ",")
            send_list <- paste("[", send_list, "]",sep="")
            complete_fieldname = paste("\\\"", names(values)[counter], "\\\":", 
                                           send_list ,",", sep="")
            return_value <- paste(return_value, complete_fieldname, sep="")
        counter <- counter + 1
        }
        return_value <- substr(return_value, 1, nchar(return_value)-1)
        return_value <- paste(return_value, "}", sep="")
        return(return_value)
    }
    check_for_return_to_VEE <- function(script){
        lines <- unlist(strsplit(script, "\\n"))
        return_script = ""
        pattern = "^returnToVEE( +)(((.+)(,)?)+)$"
        for(line in lines){
            if(grepl(pattern, line)){
                found <- regmatches(line, regexec(pattern, line))[[1]][3]
                args <- strsplit(found, ",")[[1]]
                for(arg in args){
                    arg <- trimws(arg)
                    returnToVEE <<- c(returnToVEE,arg)
                }
            }
            else{
                return_script <- paste(return_script, line, "\\n", sep = "")
            }
        }
        return(return_script)
    }
args <- commandArgs(trailingOnly = TRUE)
HOST <- args[2]
PORT <- strtoi(args[3])
con <- make.socket(host = HOST, port = PORT, server = FALSE)
send_protocol <- "BRIDGE"
write.socket(con, send_protocol)
read.socket(con)
write.socket(con, args[1])
data_size <- read.socket(con, maxlen = 10L)
data_size <- strtoi(data_size)
write.socket(con, "OK")
windows()
env <- new.env()
script <- read.socket(con, maxlen = data_size)
script <- check_for_return_to_VEE(script)
send_values <- tryCatch({
    eval(parse(text = script), envir = env)
    vee_vals <- list()
    vee_vals[["VEESTATUS"]] <- 0L
    if (length(returnToVEE) != 0) {
        for (value in returnToVEE) {
            vee_vals[[value]] <- get(value, envir = env)
            }
    }
    send_values <- r_to_python(vee_vals)
}, error = function(cond) {
    vee_vals <- list()
    vee_vals[["VEESTATUS"]] <- 1L
    vee_vals[["ERRORMESSAGE"]] <- paste(cond)
    send_values <- r_to_python(vee_vals)
    return(send_values)
}, finally = function() {
    return(send_values)
})
len_send_values <- toString(nchar(send_values))
write.socket(con, len_send_values)
read.socket(con)
write.socket(con, send_values)
close.socket(con)
    """, "r"],





    "octave" : ["""from subprocess import PIPE, Popen
import json
import re
import socket
import argparse
def checkforVEE(script):
    returnToVEE = []
    checkRegex = r'returnToVEE( +)(((.+)(,)?)+)'
    returnScript = ''
    for line in script.split("\\n"):
        if(re.match(checkRegex, line)):
            matched = re.match(checkRegex, line)
            args = matched.group(2).split(",")
            for item in args:
                item = item.strip()
                if(item == ""):
                    continue
                else:
                    returnToVEE.append(item)
        else:
            returnScript += line + "\\n"
    return returnScript, returnToVEE
def execute_script(send_expressions, script, path, bridge_script):
    script, return_args = checkforVEE(script)
    script = script.strip().replace("\\\\",r'\\\\').replace(r'"', r'\\"')
    send_scripts = []
    for line in script.split("\\n"):
        send_scripts.append(f'eval("{line}","error(lasterr())");')
    send_scripts = '\\n'.join(send_scripts)
    return_args_string = [f'"{i}", eval("{{{i}}}","error(lasterr())")' for i in return_args]
    return_args_string = "s = struct(" + ','.join(return_args_string) + ");"
    send_string = send_expressions + send_scripts + return_args_string + bridge_script
    # print(send_string)
    x = Popen([path, "--eval", send_string], stdout=PIPE, stderr=PIPE)
    output, error = x.communicate()
    if(x.returncode != 0):
        error_message = error.decode().split("\\n")
        return_dict = {
            "VEESTATUS": ["scalar", "int64", "1", 0, 0],
            "ERRORMESSAGE": ["cell", "char", error_message, 1, [len(error_message)]]
        }
    else:
        last_line =  output.decode().split("\\n")[-2]
        pattern = r'return_to_python = ({.+})'
        matches = re.search(pattern, last_line)
        return_dict = json.loads(matches.group(1))
        return_dict["VEESTATUS"] = ["scalar", "int64", "0", 0, 0]
    return return_dict
def main(id, host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    s.send(b'BRIDGE')
    s.recv(2)
    s.send(id.encode('utf-8'))
    recievedBufferSize = int(s.recv(10).decode('utf-8'))
    recievedDict = s.recv(recievedBufferSize)
    recievedDict = json.loads(recievedDict.decode('utf-8'))
    outputDict = execute_script(recievedDict[0], recievedDict[1],recievedDict[2], recievedDict[3])
    sendoutputDictSize = str(len(json.dumps(outputDict))).zfill(10)
    s.send(sendoutputDictSize.encode('utf-8'))
    s.send(json.dumps(outputDict).encode('utf-8'))
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('id')
    parser.add_argument('--host', default='127.0.0.1', help="Connect to a specific host. Default is 127.0.0.1 (localhost).")
    parser.add_argument('--port', default=65433, type=int, help="Port to connect to server. Default is 65433.")
    args = parser.parse_args()
    main(args.id, args.host, args.port)
    """, "py"],



    

    "maxima" : ["""import subprocess
import socket
import numpy as np
import json
import argparse
import re
import ast
def checkforVEE(script):
    returnToVEE = []
    checkRegex = r'returnToVEE( +)(((.+)(,)?)+)'
    returnScript = ''
    for line in script.split("\\n"):
        if(re.match(checkRegex, line)):
            matched = re.match(checkRegex, line)
            args = matched.group(2).split(",")
            for item in args:
                item = item.strip()
                if(item == ""):
                    continue
                else:
                    returnToVEE.append(item)
        else:
            returnScript += line + "\\n"
    return returnScript, returnToVEE
def convert_to_maxima(value):
    if(type(value) == bool):
        if(value):
            return "true"
        else:
            return "false"
    if(type(value) == str):
        return f'\\\\"{value}\\\\"'
    if(type(value) == complex):
        complex_i = "%i"
        imag_number = '{:+}'.format(value.imag)
        return f'{value.real} {imag_number}*{complex_i}'
    return value
def execute_script(input_data, script, path):
    script, returnToVEE = checkforVEE(script)
    for field_name in input_data:
        if(input_data[field_name][0] != "str"):
            input_data[field_name][1] = ast.literal_eval(input_data[field_name][1])
    send_expressions = []
    for item in input_data:
        if(input_data[item][2]):
            array = np.array(input_data[item][1])
            it = np.nditer(array, flags=['multi_index'])
            size_as_string = ','.join([str(i-1) for i in input_data[item][3]])
            send_expr = f'array({item}, {size_as_string});'
            send_expressions.append(send_expr)
            for i in it:
                index = ','.join([str(i) for i in it.multi_index])
                i = i.item()
                send_expr = f"{item}[{index}] : {convert_to_maxima(i)};"
                send_expressions.append(send_expr)
        else:
            value = convert_to_maxima(input_data[item][1])
            send_expr = f'{item}:{value};'
            send_expressions.append(send_expr)
    send_string = ''.join(send_expressions)
    send_string += script.replace("\\n", "")
    send_string += "quit();"
    x = subprocess.check_output(f"{path} --run-string=\\"{send_string}\\"").decode()
    return_value = str(x.split("\\n"))
    output_data = {"returnToVEE" : ["list", return_value, 0, 0], "VEESTATUS": ["int", "0", 0, 0]}
    return output_data
def main(id, host, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((host, port))
    s.send(b'BRIDGE')
    s.recv(2)
    s.send(id.encode('utf-8'))
    recievedBufferSize = int(s.recv(10).decode('utf-8'))
    recievedDict = s.recv(recievedBufferSize)
    recievedDict = json.loads(recievedDict.decode('utf-8'))
    outputDict = execute_script(recievedDict[0], recievedDict[1],recievedDict[2])
    sendoutputDictSize = str(len(json.dumps(outputDict))).zfill(10)
    s.send(sendoutputDictSize.encode('utf-8'))
    s.send(json.dumps(outputDict).encode('utf-8'))
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('id')
    parser.add_argument('--host', default='127.0.0.1', help="Connect to a specific host. Default is 127.0.0.1 (localhost).")
    parser.add_argument('--port', default=65433, type=int, help="Port to connect to server. Default is 65433.")
    args = parser.parse_args()
    main(args.id, args.host, args.port)
    """, "py"]
}
