import re
from collections import OrderedDict
import numpy as np
import cmath
# Types in VEE pro that convert into python datatypes
VEE_TO_PYTHON_TYPES = {
    "Boolean": bool,
    "Text": str,
    "UInt8" : int,
    "UInt16" : int,
    "Int16": int,
    "Int32": int,
    "Int64" : int,
    "Real32" : float,
    "Real64" : float,
    "Complex" : complex,
    "PComplex" : cmath.rect
}

PYTHON_TO_VEE_TYPES = {
    "bool" : "Boolean",
    "int" : "Int32",
    "str": "Text",
    "float": "Real64",
    "complex": "Complex",
    "list": "Array",
    "tuple": "Array",
    "set" : "Array"
}
R_TO_PYTHON_TYPES = {
    "character" : str,
    "logical" : bool,
    "numeric" : float,
    "double" : float,
    "integer" : int,
    "complex" : complex
}

# Reads the string given by VEE pro and returns a value that python that use
# Returns a dictionary with the form
# {
#   "fieldName" : [type, data, numDims, size]   
# }
# if the the String given by VEE was a Record
# else it returns the corresponding data with the type listed in types
def read_string(message):
    TypePattern = "\((\w+)"
    DataPattern = "\(data  ([^ ]+)\)"
    # Check if first six characters is a record
    if("Record" in message[:9]):
        return read_record(message)
    message = message[:-2]
    typeResult = re.search(TypePattern, message).group(1)
    dataResult = re.search(DataPattern, message).group(1)
    if(VEE_TO_PYTHON_TYPES[typeResult] == str):
        dataResult = dataResult[1:-1]
        return dataResult
    if(VEE_TO_PYTHON_TYPES[typeResult] == bool):
        return bool(dataResult.capitalize())
    if(VEE_TO_PYTHON_TYPES[typeResult] == int):
        return int(dataResult)
    if(VEE_TO_PYTHON_TYPES[typeResult] == float):
        return float(dataResult)

def send_string(data):
    VEEType = None
    if(type(data) == str):
        VEEType = "Text"
        data = data.replace(r'"', r'\"').replace(r"'", r"\'")
        return (
            f'({VEEType}\n'
            f' (data  "{data}")\n'
            f')\n'
        )
    if((type(data) == int) or (type(data) == float) or (type(data) == bool)):
        if(type(data) == int):
            VEEType = "Int64"
        if(type(data) == float):
            VEEType = "Real64"
        if(type(data) == bool):
            VEEType = "Boolean"
        return (
            f'({VEEType}\n'
            f' (data  {data})\n'
            f')\n'
        )
        
def read_record(message):
    # if VEE gives a record, then this function will dissect the record and return the following Ordered dictionary
    # Ordered Dictionary of recordData will be in the form
    # {
    #   "fieldName" : [type, data, numDims, size]   
    # }
    # fieldName is the name of the variable VEE record
    # data is the data in python format of the variable from VEE record 
    # numsDims if it exists, is the number of dimesions of the data array
    # size if it exists, is the number of elements in each dimension, contained in a List
    recordData = OrderedDict()
    schemaRegex = '\(fieldName "(\w+)"\n   \(type ([\w\d]+)\)(\n   \((numDims (\d+)\)))?(\n   \((size (.+)\)))?'
    schema = re.findall(schemaRegex, message) # match all fieldNames, type, numdims and total elements
    dataRegex = '\(data' # regex to find all data
    data = re.search(dataRegex, message)
    numFieldsRegex = '\(numFields (\d+)\)' # regex to find numFields in Record
    numFields = int(re.search(numFieldsRegex, message).group(1))
    for i in range(numFields): # loop through numFields (because there might be a Text or Text array that satsfies the Regex)
        fieldName = schema[i][0] # Assign fieldName, type and numDims according to group number in regex
        type = schema[i][1]
        if(type not in VEE_TO_PYTHON_TYPES):
            raise TypeError("Unsupported Type")
        numDims = schema[i][4]
        if(numDims):
            numDims = int(numDims)
            sizeDimsArray = re.findall('(\d+)', schema[i][6])
            sizeDimsArray = [int(i) for i in sizeDimsArray]
            recordData[fieldName] = [type, 0, numDims, sizeDimsArray]
        else:
            recordData[fieldName] = [type, 0, 0, 0]
    searchData = message[data.start():].split('\n') # spilt data into list by spilting \n
    searchData = [i.strip() for i in searchData] # remove all leading and trailing whitepaces
    currentFieldArray = []
    currentFieldName = [] # currentFieldName = [fieldName, type]
    for line in searchData[2:-1]: # loop through array of data point of the String 
        line = line.strip()
        searchDataRegex = '\( "(.+)" (.+)\)'
        search_array_variable = '\( "(.+)"'
        if(re.fullmatch(searchDataRegex, line)): # checks if field name is scalar
            if(currentFieldName):
                size = recordData[currentFieldName[0]][3]
                numpyDataArray = np.array(currentFieldArray).reshape(size).tolist()
                recordData[currentFieldName[0]][1] = numpyDataArray
                currentFieldArray = []
            currentFieldName = [] # reset currentFieldName
            fieldName = re.fullmatch(searchDataRegex, line).group(1) # fieldName
            data = re.fullmatch(searchDataRegex, line).group(2) # data
            Type = recordData[fieldName][0]
            if(Type == "Text"):
                data = data[1:-1]
                data = data.replace(r'\"', '"').replace(r'\'', "'").replace('\\\\', '\\')
            VEETypetoPythonType = VEE_TO_PYTHON_TYPES[Type] # function that converts from VEE Type to Python Type
            if(Type == "Complex"):
                complexMatches = re.fullmatch(r'\((-?\d+(\.\d+)?), (-?\d+(\.\d+)?)\)', data)
                realNumber = complexMatches.group(1)
                realNumber = float(realNumber)
                imaginaryNumber = complexMatches.group(3)
                imaginaryNumber = float(imaginaryNumber)
                recordData[fieldName][1] = complex(realNumber, imaginaryNumber)
            elif(Type == "PComplex"):
                complex_matches = re.fullmatch(r'\((-?\d+(\.\d+)?), @(-?\d+(\.\d+)?)\)', data)
                real_number = complex_matches.group(1)
                imaginary_number = complex_matches.group(3)
                recordData[fieldName][1] = cmath.rect(float(real_number), float(imaginary_number))
            else:
                recordData[fieldName][1] = VEETypetoPythonType(data) # append data to array in dictionary
        elif((line == ')') or (line == ']') or (line == '[')): # Skip through array that has only ')' ']' or '['
            continue
        elif(re.fullmatch(search_array_variable, line)): # checks if field name is array
            if(currentFieldArray):
                size = recordData[currentFieldName[0]][3]
                numpyDataArray = np.array(currentFieldArray).reshape(size).tolist()
                recordData[currentFieldName[0]][1] = numpyDataArray
                currentFieldArray = []
            fieldName = re.fullmatch(search_array_variable, line).group(1)
            currentFieldName = [fieldName, recordData[fieldName][0]]
        elif(currentFieldName): # check if you are reading an Array
            dataArray = []
            if(currentFieldName[1] == "Text"):
                textArrayElements = line[3:-3].split('" "')
                for element in textArrayElements:
                    element = element.replace(r'\"', '"').replace(r'\'', "'").replace('\\\\', '\\')
                    dataArray.append(str(element))
            elif(currentFieldName[1] == "Boolean"):
                boolArrayElements = re.findall(r'(false|true)', line)
                for element in boolArrayElements:
                    if(element == "false"):
                        dataArray.append(bool(0))
                    else:
                        dataArray.append(bool(1))
            elif(currentFieldName[1] == "Complex"):
                complexArrayElements = re.findall(r'\((-?\d+(\.\d+)?), (-?\d+(\.\d+)?)\)', line)
                for element in complexArrayElements:
                    dataArray.append(complex(float(element[0]), float(element[2])))
            elif(currentFieldName[1] == "PComplex"):
                complexArrayElements = re.findall(r'\((-?\d+(\.\d+)?), @(-?\d+(\.\d+)?)\)', line)
                for element in complexArrayElements:
                    dataArray.append(cmath.rect(float(element[0]), float(element[2])))
            else:
                searchArrayRegex = ' (-?\d+(\.\d+)?)'
                textArrayElements = re.findall(searchArrayRegex, line)
                for element in textArrayElements:
                    PythonType = VEE_TO_PYTHON_TYPES[currentFieldName[1]]
                    dataArray.append(PythonType(element[0]))
            currentFieldArray += dataArray
    if(currentFieldName):
        size = recordData[currentFieldName[0]][3]
        numpyDataArray = np.array(currentFieldArray).reshape(size).tolist()
        recordData[currentFieldName[0]][1] = numpyDataArray
    return recordData

def send_record(data):
    returnString = (f'(Record\n' +
        f'(schema\n' +
        f'(numFields {len(data)})\n'
    )
    for fieldName in data:
        returnString += (f'(fieldName "{fieldName}"\n' +
                         f'(type {data[fieldName][0]})\n')
        if(data[fieldName][2]):
            sizeString = [str(i) for i in data[fieldName][3]]
            sizeString = " ".join(sizeString)
            returnString += (f'(numDims {data[fieldName][2]})\n' +
                             f'(size {sizeString})\n') 
        returnString += '  )\n'
    returnString += (f')\n' +
                     f'(data\n' +
                     f'(record\n')
    for fieldName in data:
        if(data[fieldName][2]): # if it has numDims then it is an array
            data[fieldName][1] = np.array(data[fieldName][1]).flatten().tolist()
            returnString += f'( "{fieldName}"\n'
            if(data[fieldName][0] == "Text"):
                data[fieldName][1] = [element.replace('\\', '\\\\').replace(r'"', r'\"').replace(r"'",r"\'")
                                     for element in data[fieldName][1]]
                returnString += '[ "' + '" "'.join(data[fieldName][1]) + '" ]\n)\n'
            elif(data[fieldName][0] == "Boolean"):
                arrayComprehension = [str(value).lower() for value in data[fieldName][1]]
                returnString += '[ ' + ' '.join(arrayComprehension) + ' ]\n)\n'
            elif(data[fieldName][0] == "Complex"):
                arrayComprehension = [f'({value.real}, {value.imag})' for value in data[fieldName][1]]
                returnString += '[ ' + ' '.join(arrayComprehension) + ' ]\n)\n' 
            else:
                arrayComprehension = [str(value) for value in data[fieldName][1]]
                returnString += '[ ' + ' '.join(arrayComprehension) + ' ]\n)\n'
        else:
            if(data[fieldName][0] == "Text"):
                data[fieldName][1] = data[fieldName][1].replace('\\', '\\\\').replace(r'"', r'\"').replace(r"'",r"\'")
                returnString += f'( "{fieldName}" "{data[fieldName][1]}")\n'
            elif(data[fieldName][0] == "Boolean"):
                returnString += f'( "{fieldName}" {str(data[fieldName][1]).lower()})\n'
            elif(data[fieldName][0] == "Complex"):
                returnString += f'( "{fieldName}" ({data[fieldName][1].real}, {data[fieldName][1].imag}))\n'
            else:
                returnString += f'( "{fieldName}" {data[fieldName][1]})\n'
    returnString += (
        f')\n' +
        f')\n' +
        f')'
    )
    returnString = str(returnString)
    return returnString

def read_script(message):
    returnScript = ''
    textArrayElements = message[6:-3].split('" "')
    textArrayElements = [element.replace(r'\"', r'"').replace(r'\'', r"'").replace("\\\\", "\\") 
                        for element in textArrayElements]
    for element in textArrayElements:
        returnScript += element + '\n'
    return returnScript

def Int32OrReal64(int_values):
    if(hasattr(int_values, "__len__")):
        is_float = False
        for value in int_values:
            if(value > 2147483647):
                is_float = True
            elif(value < -2147483648):
                is_float = True
        if(is_float):
            for i in range(len(int_values)):
                int_values[i] = float(int_values[i])
        return int_values
    if(int_values > 2147483647):
        return float(int_values)
    elif(int_values < -2147483648):
        return float(int_values)
    else:
        return int_values

def python_to_r(data):
    send_values = []
    for field_name in data:
        flatten_array = np.array(data[field_name][1]).flatten(order="F").tolist()
        if("Text" in data[field_name][0]):
            r_array = "c(\"{0}\")".format("\",\"".join(flatten_array))
        elif("Boolean" in data[field_name][0]):
            r_array = f'c({",".join([str(x) for x in flatten_array])})'.replace("True", "TRUE").replace("False", "FALSE")
        elif("Complex" in data[field_name][0]):
            r_array = f'c({",".join([str(x) for x in flatten_array])})'.replace("j", "i")
        elif("Int" in data[field_name][0]):
            r_array = f'c({"L,".join([str(x) for x in flatten_array])}L)'
        elif("Real" in data[field_name][0]):
            r_array = f'c({",".join([str(x) for x in flatten_array])})'
        dim_argument = f'c({",".join([str(x) for x in data[field_name][3]])})'
        send_expression = f'{field_name} <- array({r_array}, dim = {dim_argument})'
        send_values.append(send_expression)
    return "\n".join(send_values)
def python_to_octave(data):
    send_values = []
    for field_name in data:
        if(data[field_name][2]): # check if field_name is an array
            flatten_array = np.array(data[field_name][1]).flatten(order="F").tolist()
            if("Text" in data[field_name][0]):
                flatten_array = [x.replace(r'"', r'\"') for x in flatten_array]
                array = " ".join([f'\"{x}\"' for x in flatten_array])
                array_expression = f'global {field_name} = {{{array}}};'
                dim_expression = f'reshape({field_name},{",".join([str(x) for x in data[field_name][3]])});'
                send_values.append(array_expression)
                send_values.append(dim_expression)
                continue
            elif("Boolean" in data[field_name][0]):
                array = " ".join([str(x) for x in flatten_array]).replace("True", "true").replace("False", "false")
            elif("Complex" in data[field_name][0]):
                array = " ".join([str(x) for x in flatten_array]).replace("j", "i")
            elif("Int" in data[field_name][0]):
                array = " ".join([f'int64({x})' for x in flatten_array])
            elif("Real" in data[field_name][0]):
                array = " ".join([str(x) for x in flatten_array])
            else:
                continue
            array_expression = f'{field_name} = [{array}];'
            dim_expression = f'reshape({field_name},{",".join([str(x) for x in data[field_name][3]])});'
            send_values.append(array_expression)
            send_values.append(dim_expression)
        else:
            if("Text" in data[field_name][0]):
                string_value = data[field_name][1].replace(r'"', r'\"')
                send_value = f'\"{string_value}\"'
            elif("Complex" in data[field_name][0]):
                send_value = f'{data[field_name][1]}'.replace("j", "i")
            elif("Int" in data[field_name][0]):
                send_value = f'int64({data[field_name][1]})'
            elif("Real" in data[field_name][0]):
                send_value = f'{data[field_name][1]}'
            send_expression = f'{field_name} = {send_value};' 
            send_values.append(send_expression)
    return "\n".join(send_values)    
            


            

