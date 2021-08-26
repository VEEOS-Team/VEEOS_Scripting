# VEEOS_Scripting
VEEOS Scripting allows users of VEE Pro to execute scripts from supported languages, such as Python and R, directly from VEE Pro to execute powerful mathematical computations. 

Additional Documentiaton for VEE Users can be found [here](https://www.veeos.org/library/R2/scriptLib.htm)


# Contents
 * [Supported Languages](#supported-languages)
 * [Installation](#installation)
 * [Configuration](#configuration)
 * [Supported Data Types](#data-conversions)
 * [Development](#development)

 # Supported Languages
  
 * [Python](https://www.python.org/)
 * [R](https://www.r-project.org/)
 * [Fiji (using Jython)](https://imagej.net/software/fiji/)
 * [Octave](https://www.gnu.org/software/octave/)
 * [Maxima](https://maxima.sourceforge.io/)
 # Installation
 

 1. Download the VEEOS library from [here](https://veeos.org/)
 2. Extract the zip file and copy its contents into the VEE Pro install directory (Usually it is C:\Program Files\Keysight\VEE Pro)

 To upgrade from a previous version, follow these steps
 1. Download all files in the src folder of this repo 
 2. Copy the files into VEE Install directory/veeos/python

# Configuration

For Fiji, ensure that Run single instance listener is turned off by going to Edit -> Options -> Misc... and checking the Run single instance listener is unchecked for best results.


# Supported Data Conversions

## VEE Pro to \<language>

<details>
<summary> From VEE Pro to Python/Fiji </summary>
<pre>
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
</pre>
</details>
<p>
<details>
<summary> From VEE Pro to R </summary>
<pre>
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
</pre>
</details>
<p>

<details>
<summary> From VEE Pro to Octave </summary>
<pre>
Boolean -> logical
Text -> dq_string
UInt8 -> int64
UInt16 -> int64
Int16 -> int64
Int32 -> int64
Int64 -> int64
Real32 -> double
Real64 -> double
Complex -> double complex scalar
PComplex -> double complex scalar
Boolean Array-> bool matrix
Text Array -> Cell array of strings
UInt8 Array -> int64 matrix
UInt16 Array -> int64 matrix
Int16 Array -> int64 matrix
Int32 Array -> int64 matrix
Int64 Array -> int64 matrix
Real32 Array -> double matrix
Real64 Array -> double matrix
Complex Array -> complex matrix
PComplex Array -> complex matrix
</pre>
</details>
<p>
<details>
<summary> From VEE Pro to Maxima </summary>
<pre>
Boolean -> number
Text -> string
UInt8 -> number
UInt16 -> number
Int16 -> number
Int32 -> number
Int64 -> number
Real32 -> number
Real64 -> number
Complex -> complex scalar number
PComplex -> complex scalar number
Boolean Array-> bool array
Text Array -> string array
UInt8 Array -> number array
UInt16 Array -> number array
Int16 Array -> number array
Int32 Array -> number array
Int64 Array -> number array
Real32 Array -> number array
Real64 Array -> number array
Complex Array -> complex array
PComplex Array -> complex array
</pre>
</details>
<p>

## \<language> to VEE Pro

<details>
<summary> Python/Fiji to VEE Pro </summary>
<pre>
bool -> Boolean
str -> Text
int -> Int32
int -> Real64 if integer value is over 32 bits
float -> Real64
complex -> Complex
bool List-> Boolean Array
int List -> Int32 Array
int List -> Real64 Array if one value in List is over 32 bits
str list -> Text Array
float List -> Real64 Array
complex List -> Complex Array 
</pre>
</details>
<p>

<details>
<summary> R to VEE Pro </summary>
<pre>
bool Array-> Boolean Array
int Array -> Int32 Array
int Array -> Real64 Array if one value in List is over 32 bits
str Array -> Text Array
float Array -> Real64 Array
complex Array -> Complex Array 
</pre>
</details>

<p>
<details>
<summary> Octave to VEE Pro </summary>
<pre>
logical -> Boolean
dq_string/sq_string -> Text
(u)int(8/16/32/64) -> Int32
(u)int(8/16/32/64) -> Real64 if value is over 32 bits
double -> Real64
single -> Real64
(int or double/single) complex -> Complex
bool matrix-> Boolean Array
int matrix -> Int32 Array
int matrix -> Real64 Array if one value in List is over 32 bits
dq_string/sq_string Cell Array -> Text Array
double matrix -> Real64 Array
single matrix -> Real64 Array
(int or double/single) complex matrix -> Complex Array 
</pre>
</details>
<p>
<details>
<summary> Maxima to VEE Pro </summary>
<pre>
returns a variable called returnToVEE, which is a text array of the output of all commands in Maxima. 
</pre>
</details>
<p>
Note : To comply with VEE Pro requirements, all Arrays must be non jagged (dimensions of every array must be consistent with thier length)

# Development

1. If you would like to help contribute this project, clone this repo, create a virutal enviroment using Python 3 and install dependencies.

```
pip install -r requirements.txt
```

2. Change PYTHON_PATH in src/server.py to "python3" if Python is installed in your PATH or the Path of your python.exe file


3. Run the Python server using the following command

```
python3 src/server.py
```
