# CSS125L project specifications

## A simple "interpreter"

Your simple interpreter called "HLInt.XXX" reads a source code written in our hypothetical language "HL." Then, it performs operations based on the source code.

Our hypothetical language has the following:

### 1) Variable declaration

```text
x:integer;
y:double;
```

`integer`, `double`, data types

### 2) Assignment statements

```text
x:= 5;
y:= 2.35;
```

### 3) Mathematical operations

Addition and subtraction of single digit integers and double values with precision of 2

```text
x = 3 + 2;
y = 4 + 2.56;
```

### 4) Sending output to screen

```text
output<<" <string>";
output<<value;

output<<"hello";
output<<x;
```

### 5) Conditional statement

One-way if

```text
If(<condition>)
 <statement>
```

Relational operators: `>`, `<`, `==`, `!=`

Example:

```text
x:= 6;
If(x<5)
 Output<<X;
```

---

## Program listing

### PROG1.HL

```text
x: integer;
x:= 5;
output<<x;
```

### PROG2.HL

```text
x: integer;
y: double;
x:= 3;
y:= 1.25;
output<<x+y;
```

### PROG3.HL

```text
x: integer;
y: double;
x:= 3;
if(x<5)
 output<<x;
```

---

## The process

When HLInt.XXX runs, it opens a source code [PROG1.HL or PROG2.HL or PROG3.HL], then it removes all spaces in the program and sends the contents "without spaces" to an output file named "NOSPACES.TXT". Then, it sends reserved words and symbols found in the program to "RES_SYM.TXT". Finally, it prints on the screen "ERROR" if it finds any syntax error in the program or "NO ERROR(S) FOUND" if there are no errors.
