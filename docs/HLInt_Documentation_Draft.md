<!--
How to use this draft: each "###" heading below is one row of the CSS125
Project Template, in the same order and with the same label. Paste the text
under each heading into the "Details" cell of that row, then export to PDF.
-->

# Mapúa University

## School of Information Technology

### CSS125L Project Documentation: HLInt.py

## Groupings

### Group Name

[GROUP NAME]

### Group Members (including section of each student)

| Full name | Section |
| :--- | :--- |
| [FULL NAME 1] | [SECTION] |
| [FULL NAME 2] | [SECTION] |
| [FULL NAME 3] | [SECTION] |

## I. Introduction

### a. Description of the Program

HLInt.py is a simple interpreter for the hypothetical language HL, written in Python. To run it, open a terminal in the folder that contains `HLInt.py` and give the name of an HL source file:

```text
py HLInt.py PROG1.HL
```

HLInt writes its output files to the folder it runs from. For each source file, it does four things in order:

1. It removes all spaces from the source and writes the result to `NOSPACES.TXT`. It keeps line breaks and the spaces inside string literals.
2. It writes the reserved words and symbols found in the program to `RES_SYM.TXT`. It lists each one once, in the order it first appears.
3. It checks the program for errors. At the first error, it prints `ERROR`, then the line number and the reason, and it stops.
4. If there are no errors, it prints `NO ERROR(S) FOUND`, then the program's output.

HLInt reads the program in one pass. A tokenizer splits the text into words, numbers, strings, and symbols. A recursive-descent parser then checks each statement and runs it. HLInt prints the program output only when the whole program has no errors.

HL has these reserved words and symbols:

| Reserved words | Symbols |
| :--- | :--- |
| `integer`, `double`, `output`, `if` | `:` `:=` `=` `;` `<<` `+` `-` `>` `<` `==` `!=` `(` `)` `"` |

## II. Constructs Supported

### a. Data types

| Type | Meaning | Example values |
| :--- | :--- | :--- |
| `integer` | Whole numbers | `5`, `12` |
| `double` | Numbers with up to 2 decimal places | `2.35`, `1.25` |

A double with more than 2 decimal places, such as `1.234`, is an error.

### b. Variable declarations

```text
x: integer;
y: double;
```

Every variable must be declared before it is used. Declaring the same variable twice is an error. Keywords and variable names are not case-sensitive, so `X` and `x` are the same variable.

### c. Expressions and operations

Assignment uses `:=`. A plain `=` also works, because the math example in the project specifications uses it:

```text
x:= 5;
y:= 2.35;
x = 3 + 2;
y = 4 + 2.56;
```

- Addition (`+`) and subtraction (`-`) can be chained, as in `a + b - c`. HLInt evaluates them from left to right.
- If any value in an expression is a double, the result is a double rounded to 2 decimal places.
- A double cannot be assigned to an integer variable.

The one-way `if` uses the relational operators `>`, `<`, `==`, and `!=`:

```text
if(x<5)
 output<<x;
```

The statement after `if(...)` runs only when the condition is true. HLInt checks it for errors even when the condition is false.

HLInt detects these errors:

| Error | Example | Message |
| :--- | :--- | :--- |
| Missing semicolon | `x:= 5` | `line 3: expected ';'` |
| Undeclared variable | `y:= 5;` | `line 2: 'y' is not declared` |
| Variable declared twice | `x: double;` | `line 2: 'x' is already declared` |
| Double assigned to integer | `x:= 2.5;` | `line 2: cannot assign a double to integer 'x'` |
| Too many decimal places | `y:= 1.234;` | `line 2: '1.234' has more than 2 decimal places` |
| Missing parenthesis | `if(x<5` | `line 4: expected ')'` |
| Invalid relational operator | `if(x<<5)` | `line 3: expected '<', '>', '==' or '!='` |

### d. Input/Output statements

```text
output<<"hello";
output<<x;
output<<x+y;
```

`output<<` prints a string or the value of an expression. Doubles print with 2 decimal places. HL has no input statement. The interpreter's input is the source file named on the command line.

## Code and References

### III. Screenshots of Sample Runs

[INSERT SCREENSHOTS HERE]

<!--
Take one screenshot per run below. Each screenshot shows the command, the
screen output, and the contents of NOSPACES.TXT and RES_SYM.TXT. Run each
command in the folder that contains HLInt.py.

1. py HLInt.py PROG1.HL                        -> NO ERROR(S) FOUND, then 5
2. py HLInt.py PROG2.HL                        -> NO ERROR(S) FOUND, then 4.25
3. py HLInt.py PROG3.HL                        -> NO ERROR(S) FOUND, then 3
4. py HLInt.py tests/ERR_MISSING_SEMICOLON.HL  -> ERROR, then line 3: expected ';'
5. py HLInt.py tests/ERR_UNDECLARED.HL         -> ERROR, then line 2: 'y' is not declared
-->

### IV. Source Code

HLInt.py:

```python
"""HLInt: a simple interpreter for the hypothetical language HL.

Usage: py HLInt.py PROG1.HL

Writes the source without spaces to NOSPACES.TXT, the reserved words and
symbols found to RES_SYM.TXT, then prints "NO ERROR(S) FOUND" followed by
the program's output, or "ERROR" followed by the line and reason.
"""

import re
import sys
from dataclasses import dataclass, field

RESERVED = ["integer", "double", "output", "if"]
# Longest symbols first so ":=" is not read as ":" followed by "=".
SYMBOLS = [":=", "<<", "==", "!=", "=", ":", ";", "+", "-", ">", "<", "(", ")"]
RELATIONAL = ["<", ">", "==", "!="]
TYPES = ["integer", "double"]

TOKEN_RE = re.compile(
    r'(?P<str>"[^"\n]*")'
    r"|(?P<num>\d+(?:\.\d+)?)"
    r"|(?P<word>[A-Za-z_]\w*)"
    r"|(?P<sym>" + "|".join(re.escape(s) for s in SYMBOLS) + ")"
    r"|(?P<newline>\n)"
    r"|(?P<bad>.)"
)


class HLError(Exception):
    pass


@dataclass
class Token:
    kind: str  # "str", "num", "word", "sym" or "bad"
    text: str
    line: int


@dataclass
class Result:
    nospaces: str
    reserved: list
    symbols: list
    error: str = None
    output: list = field(default_factory=list)


def remove_spaces(source):
    """Remove spaces and tabs, except inside string literals. Keeps newlines."""
    kept = []
    in_string = False
    for ch in source:
        if ch == '"':
            in_string = not in_string
        elif ch == "\n":
            in_string = False
        elif ch in " \t\r" and not in_string:
            continue
        kept.append(ch)
    return "".join(kept)


def tokenize(text):
    tokens = []
    line = 1
    for match in TOKEN_RE.finditer(text):
        kind = match.lastgroup
        if kind == "newline":
            line += 1
            continue
        value = match.group()
        if kind == "word":
            value = value.lower()  # HL is case-insensitive
        tokens.append(Token(kind, value, line))
    return tokens


def reserved_and_symbols(tokens):
    """Each reserved word and symbol once, in order of first appearance."""
    reserved, symbols = [], []
    for tok in tokens:
        if tok.kind == "word" and tok.text in RESERVED and tok.text not in reserved:
            reserved.append(tok.text)
        found = '"' if tok.kind == "str" else tok.text if tok.kind == "sym" else None
        if found and found not in symbols:
            symbols.append(found)
    return reserved, symbols


def format_value(var_type, value):
    return f"{value:.2f}" if var_type == "double" else str(value)


class Parser:
    """Checks the program and runs it in one pass."""

    def __init__(self, tokens):
        self.tokens = tokens
        self.pos = 0
        self.types = {}  # variable name -> "integer" or "double"
        self.values = {}  # variable name -> current value
        self.output = []

    def peek(self):
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def fail(self, message):
        tok = self.peek() or (self.tokens[-1] if self.tokens else Token("", "", 1))
        raise HLError(f"line {tok.line}: {message}")

    def take(self, text):
        tok = self.peek()
        if tok is None or tok.text != text or tok.kind not in ("sym", "word"):
            self.fail(f"expected '{text}'")
        self.pos += 1
        return tok

    def program(self):
        while self.peek():
            self.statement(run=True)

    def statement(self, run):
        """Checks one statement, and runs it only if run is True."""
        tok = self.peek()
        if tok is None:
            self.fail("expected a statement")
        if tok.kind == "word" and tok.text == "if":
            self.if_stmt(run)
        elif tok.kind == "word" and tok.text == "output":
            self.output_stmt(run)
        elif tok.kind == "word" and tok.text not in RESERVED:
            self.pos += 1
            nxt = self.peek()
            if nxt and nxt.text == ":":
                self.declaration(tok.text)
            elif nxt and nxt.text in (":=", "="):  # the spec's math example uses "="
                self.assignment(tok.text, run)
            else:
                self.fail("expected ':', ':=' or '='")
        else:
            self.fail(f"unexpected '{tok.text}'")

    def declaration(self, name):
        self.take(":")
        tok = self.peek()
        if tok is None or tok.kind != "word" or tok.text not in TYPES:
            self.fail("expected 'integer' or 'double'")
        self.pos += 1
        if name in self.types:
            self.fail(f"'{name}' is already declared")
        self.types[name] = tok.text
        self.values[name] = 0
        self.take(";")

    def assignment(self, name, run):
        self.pos += 1  # ":=" or "=", already checked by statement()
        if name not in self.types:
            self.fail(f"'{name}' is not declared")
        expr_type, value = self.expression()
        if self.types[name] == "integer" and expr_type == "double":
            self.fail(f"cannot assign a double to integer '{name}'")
        self.take(";")
        if run:
            self.values[name] = value

    def if_stmt(self, run):
        self.take("if")
        self.take("(")
        _, left = self.expression()
        tok = self.peek()
        if tok is None or tok.kind != "sym" or tok.text not in RELATIONAL:
            self.fail("expected '<', '>', '==' or '!='")
        self.pos += 1
        _, right = self.expression()
        self.take(")")
        holds = {"<": left < right, ">": left > right, "==": left == right, "!=": left != right}[tok.text]
        self.statement(run and holds)

    def output_stmt(self, run):
        self.take("output")
        self.take("<<")
        tok = self.peek()
        if tok and tok.kind == "str":
            self.pos += 1
            text = tok.text[1:-1]
        else:
            text = format_value(*self.expression())
        self.take(";")
        if run:
            self.output.append(text)

    def expression(self):
        """Terms joined by + or -, left to right. Returns (type, value)."""
        expr_type, value = self.term()
        while self.peek() and self.peek().text in ("+", "-"):
            op = self.peek().text
            self.pos += 1
            term_type, term_value = self.term()
            value = value + term_value if op == "+" else value - term_value
            if "double" in (expr_type, term_type):
                expr_type, value = "double", round(value, 2)
        return expr_type, value

    def term(self):
        """A number or a declared variable. Returns (type, value)."""
        tok = self.peek()
        if tok and tok.kind == "num":
            if "." not in tok.text:
                self.pos += 1
                return "integer", int(tok.text)
            if len(tok.text.split(".")[1]) > 2:
                self.fail(f"'{tok.text}' has more than 2 decimal places")
            self.pos += 1
            return "double", float(tok.text)
        if tok and tok.kind == "word" and tok.text not in RESERVED:
            if tok.text not in self.types:
                self.fail(f"'{tok.text}' is not declared")
            self.pos += 1
            return self.types[tok.text], self.values[tok.text]
        self.fail("expected a number or variable")


def interpret(source):
    nospaces = remove_spaces(source)
    tokens = tokenize(nospaces)
    reserved, symbols = reserved_and_symbols(tokens)
    parser = Parser(tokens)
    try:
        parser.program()
    except HLError as err:
        return Result(nospaces, reserved, symbols, error=str(err))
    return Result(nospaces, reserved, symbols, output=parser.output)


def main(argv):
    if len(argv) != 2:
        print("Usage: py HLInt.py <source file>")
        return 1
    try:
        with open(argv[1], encoding="utf-8") as f:
            source = f.read()
    except OSError as err:
        print(f"Cannot open {argv[1]}: {err.strerror}")
        return 1

    result = interpret(source)
    with open("NOSPACES.TXT", "w", encoding="utf-8") as f:
        f.write(result.nospaces)
    with open("RES_SYM.TXT", "w", encoding="utf-8") as f:
        f.write("Reserved words:\n")
        f.writelines(word + "\n" for word in result.reserved)
        f.write("\nSymbols:\n")
        f.writelines(sym + "\n" for sym in result.symbols)

    if result.error:
        print("ERROR")
        print(result.error)
    else:
        print("NO ERROR(S) FOUND")
        for line in result.output:
            print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
```

### V. References

1. CSS125L Project Specifications (course handout).
2. Python Software Foundation. *Python 3 documentation: re (regular expression operations)*. https://docs.python.org/3/library/re.html
3. Python Software Foundation. *Python 3 documentation: unittest*. https://docs.python.org/3/library/unittest.html
4. [ADD ANY OTHER REFERENCES YOUR GROUP USED]
