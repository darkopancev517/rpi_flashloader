# VCSCRIPT (Vertexcom Scripting Language)

A small scripting language created by **Darko Pancev**

## Overview

**vcscript** is a small scripting language that is use to simplify hardware automation
and auto-testing process. It supports various fundamental programming concepts
such as variable-declaration, function-declaration, function calling,
conditional statements, loops, proper order of operations and recursion.
The language syntax is meant to be very readable and intuitive. **vcscript** is
build on top of the Python programming language. Below are some examples of
programs that vcscript can run.

## Packages

```
    vcscript [folder]
       |----- interperter.py [file] (interpreter implementation)
       '----- native.py      [file] (native functions implementation)
    your_script.py [file]

```

**your_script.py**

```python
from vcscript.interpreter import vcscript

vcscript.input("""

    # put your vcscript code here! #

""")

```

## Examples of Basic Programs

### Basic Comment

Syntax:

**comment::=** '#' comment messages '#'

Example:

```python
from vcscript.interpreter import vcscript

vcscript.input("""

    # This is a comment and will not be executed #

    #

    This is how to comment multiple line of messages and
    anything in between this will be ignored by the interpreter and could
    be use as a note for programmer.

    #

""")
```

### Basic Variable Declaration

Syntax:

**variable-declaration::=** variable-keyword variable-name assignment-operator variable-body  
**variable-keyword::=** 'num' number | 'str' string | 'arr' array | 'bool' boolean | 'conf' configuration-parameters  
**variable-name::=** identifier  
**assigment-operator::** '='  
**variable-body::=** value or parameters  

Example:

```python
from vcscript.interpreter import vcscript

vcscript.input("""

    num one = 7
    str hello = "hello"
    arr array = [1, 2, 3, 4, 5, 6, 7]
    bool boolean = True
    conf config = {param1: "test", param2: 123, param3: True}

""")
```

### Basic Function Declaration

Syntax:

**function-declaration::=** function-keyword function-name assignment-operator ( parameters 'optional' ) : function-body :  
**function-keyword::=** 'func'  
**function-name::=** identifier  
**assigment-operator::** '='  
**function-body::=** program  
**function-return-keyword::=** 'return'  

Example:

```python
from vcscript.interpreter import vcscript

vcscript.input("""

    func getHello = () :
        return "Hello"
    :

    func add = (num a, num b) :
        return a + b
    :

""")
```

### Basic Conditional Statements

Syntax:

**conditional::=** 'if' condition : program : 'elif' condition : program : 'else' : program :

Example:

```python
from vcscript.interpreter import vcscript

vcscript.input("""

    if 3 == 3 :
        print("First Condition!")
    : elif 3 != 2 :
        print("Second Condition!")
    : else :
        print("Third Condition!")
    :    

""")
```

### Basic 'from' Loops

Syntax:

**from-loop::=** 'from' start 'to' end 'with' variable : program :

Example:

```python
from vcscript.interpreter import vcscript

vcscript.input("""

    from 1 to 3 with i :
        print(i)
    :

    # Nested 'from' loops example #

    from 1 to 3 with i :
        from 1 to 3 with j :
            print(i, j)
        :
    :

""")
```

### Basic 'foreach' Loops

Syntax:

**foreach-loop::=** 'foreach' variable 'in' array (iterable variable) : program :

Example:

```python
from vcscript.interpreter import vcscript

vcscript.input("""

    arr array = [1, 2, 3, 4, 5, 6, 7]

    foreach value in array :
        print(value)
    :

""")
```

### Basic Recursion

Example:

```python
from vcscript.interpreter import vcscript

vcscript.input("""

    # Create a fibonacci number #

    func fib = (num n) :
        if n == 1 :
            return 0
        : elif n == 2 :
            return 1
        : else :
            return fib(n - 1) + fib(n - 2)
        :
    :

    from 1 to 15 with i :
        print(i, fib(i))
    :

""")
```

### Basic Array Operations

Example:

```python
from vcscript.interpreter import vcscript

vcscript.input("""

    arr array = [1, 2, 3, 4, 5, 6, 7]

    # get element from specific index on the array #

    num value = index(array, 0)

    print(value) # this will print '1' #

    # push new element to the last of the array #

    push(array, 8)

    print(array) # this will print [1, 2, 3, 4, 5, 6, 7, 8] #

""")
```

### Order of Operations

Example:

```python
from vcscript.interpreter import vcscript

vcscript.input("""

    num one = 1
    num three = 3

    func add = (num a, num b) :
        return a + b
    :

    func echo = (num a) :
        return a
    :

    func fib = (num n) :
        if n == 1 :
            return 0
        : elif n == 2 :
            return 1
        : else :
            return fib(n - 1) + fib(n - 2)
        :
    :

    # this function is testing the order of the operation and will return 2 as a result #

    func alwaysTwo = (num n) :
        return ((((n + 47 % (19 * add(-3, 5))) * echo(three - one) - 4) / fib(4) - n + fib(echo(10)) - 29) * 3 - 9) / 3 - (((n + 109 % 10) * 2 - 4) / 2 - n)
    :

    # the result should be 2, otherwise the order operation is incorrect #

    print(alwaysTwo(4751))

""")
```

## Hardware Scripting

### Basic Serial Communication

```python
from vcscript.interpreter import vcscript

vcscript.input("""

    conf serial1 = { port: "dev/ttyUSB1", baudrate: 115200 }
    conf serial2 = { port: "dev/ttyUSB2", baudrate: 115200 }

    # Example 1 -------------------------------------------------------- #

    str result1 = sendcmd(serial1, "ver")
    str result2 = sendcmd(serial2, "ver")

    expect "software v1.2" in result1
    expect "software v1.2" in result2

    print("Software version is up-to-dated")

    # Example 2 -------------------------------------------------------- #

    arr serials = [serial1, serial2]

    foreach serial in serials :
        str result = sendcmd(serial, "ver")
        expect "software v1.2" in result
    :

    print("Software version is up-to-dated")

""")
```

## Remote Testing

**vcscript** is capable to use as remote testing because vcscript language is
a strings with logic information that passed into **vcscript.input()** function as an
argument. Therefore we can defined our script in RF packet.

### Configurations

```
 __________ ______________________________________________
|          |  RF packet {"""                              |
|          |      foreach serial in serials :             |
|  NODE    |          str result = sendcmd(serial, "ver") |
|  Device  |          expect "v1.2" in result             |
|          |      :                                       |
|          |  """}                                        |
'----------'----------------------------------------------'
     .
     .                              ___________________________________________________________________ 
     . RF     __________           |   |  vcscript.input("""                                           |
     .       |          |          |   |      conf serial1 = { port: "dev/ttyUSB1", baudrate: 115200 } |
     .       |  ROOT    |   UART   | S |      conf serial2 = { port: "dev/ttyUSB2", baudrate: 115200 } |
     . . . ..|  Device  |==========| E |      conf serial2 = { port: "dev/ttyUSB3", baudrate: 115200 } |
             |          |          | R |      arr serials = [serial1, serial2, serial3]                |
             '__________'          | V |  """)                                                         |
                                   | E |  while True:                                                  |
                                   | R |    if scriptIsAvailable():                                    |
                                   |   |        vcscript.input(getScript())                            |
                                   '___'_______________________________________________________________'
                                   |                           RASPBERRY PI                            |
                                   '-------------------------------------------------------------------'
                                                                   |  |  |  UART
                                                     .-------------'  |  '-------------.  
                                                     | dev/ttyUSB1    | dev/ttyUSB2    | dev/ttyUSB3
                                                 ____o____        ____o____        ____o____
                                                |         |      |         |      |         |
                                                |  DUT 1  |      |  DUT 2  |      |  DUT 3  |
                                                |         |      |         |      |         |
                                                '_________'      '_________'      '_________'    
```
