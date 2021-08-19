# VEEOS_Scripting
VEEOS Scripting allows users of VEE Pro to execute scripts from supported languages, such as Python and R, directly from VEE Pro to execute powerful mathethical computations. 


# Contents
 * [Supported Languages](#supported-languages)
 * [Installation](#installation)
 * [Configuration](#configuration)
 * [Supported Data Types](#data-conversions)
 * [Development](#development)

 # Supported Languages
  
 * Python
 * R
 * Fiji (using Jython)
 * Octave
 # Installation
 

 1. Download the VEEOS library from [here](https://veeos.org/)
 2. Extract the zip file and copy its contents into the VEE Pro install directory (Usually it is C:\Program Files\Keysight\VEE Pro)

# Configuration


For Fiji, ensure that Run single instance listener is turned off by going to Edit -> Options -> Misc... and checking the Run single instance listener is unchecked for best results.

For Octave, the default backend for plotting is gnuplot. If you like to change the backend, go to src/bridgescripts.py and then CTRL/CMD F and search for "gnuplot" and replace it with the backend of your choice.

# Data Conversions
### From VEE Pro to Python/Fiji
```
Boolean -> bool
Text -> str
UInt8 -> int
UInt16 -> int
Int16 -> int
Int32 -> int
Int64 -> int
Real32 -> float
Real64 -> float
Complex -> complex
PComplex -> complex
Boolean Array-> List
Text Array -> List
UInt8 Array -> List
UInt16 Array -> List
Int16 Array -> List
Int32 Array -> List
Int64 Array -> List
Real32 Array -> List
Real64 Array -> List
Complex Array -> List
PComplex Array -> List
```
### From VEE Pro to R
```
Boolean Array-> Logical Array
Text Array -> Character Array
UInt8 Array -> Integer Array
UInt16 Array -> Integer Array
Int16 Array -> Integer Array
Int32 Array -> Integer Array
Int64 Array -> Integer Array
Real32 Array -> Numeric Array
Real64 Array -> Numeric Array
Complex Array -> Complex Array
PComplex Array -> Complex Array
```
### Python/Fiji to VEE Pro
```
bool -> Boolean
str -> Text
int -> Int32
int -> Real64 if integer value is over 32 bits
float -> Real64
complex -> complex
bool List-> Boolean Array
int List -> Int32 Array
int List -> Real64 Array if one value in List is over 32 bits
str list -> Text Array
float List -> Real64 Array
complex List -> Complex Array 
```

# Development

If you would like to help contribute this project, clone this repo, create a virutal enviroment using Python 3 and install dependencies.

```
pip install 
```

Run the Python server using the following command

```
python3 src/server.py
```
