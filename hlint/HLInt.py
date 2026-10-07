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
