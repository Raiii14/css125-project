# How HLInt works

This page explains how `hlint/HLInt.py` turns an HL file into output. It also explains why HLInt behaves the way it does where the spec leaves room for choice. Read it before you change the code or answer questions in the demo.

## HLInt reads a program in four steps

`interpret(source)` runs four steps in order. Each step is one function or class in `HLInt.py`.

1. `remove_spaces` removes the spaces. `main` writes the result to `NOSPACES.TXT`.
2. `tokenize` splits the text into tokens.
3. `reserved_and_symbols` lists the reserved words and symbols. `main` writes the lists to `RES_SYM.TXT`.
4. `Parser` checks each statement and runs it.

`interpret` returns a `Result` that holds everything HLInt produces. It does not read or write files, so the tests call it directly with a string of HL code.

`main` is the only part that touches files. It reads the HL file, calls `interpret`, writes the two output files, and prints the result.

## Spaces go, line breaks stay

`remove_spaces` removes spaces and tabs. It keeps line breaks, so the error messages give the same line numbers as the original file. It also keeps the spaces inside quotes, so `output<<"hello world";` prints `hello world`.

## The tokenizer cuts the text into tokens

A token is the smallest piece of a program that has a meaning. HL has four kinds of token: a word such as `output` or `x`, a number such as `2.35`, a string such as `"hello"`, and a symbol such as `:=`.

`tokenize` uses one regular expression, `TOKEN_RE`, to cut the text into tokens. It records the line number of each token for the error messages. It also changes every word to lowercase, so HL treats `If`, `IF`, and `if` as the same word.

Python builds `TOKEN_RE` from the `SYMBOLS` list at the top of the file. To support a new symbol, add it to that list. Put a longer symbol before a shorter one that starts the same way. If `:` came before `:=`, the tokenizer would read `:=` as `:` and then `=`.

A character that fits no token becomes a `bad` token. The parser reports it as an error.

## The parser checks and runs the program in one pass

The parser reads the tokens from left to right. It has one method for each part of the language:

| Method | Reads |
| :--- | :--- |
| `statement` | The first token of a statement, then calls the method below that fits. |
| `declaration` | `x: integer;` |
| `assignment` | `x:= 5;` and `x = 5;` |
| `output_stmt` | `output<<x;` and `output<<"text";` |
| `if_stmt` | `if(x<5)` and the statement after it. |
| `expression` | `a + b - c`. It returns the type and the value. |
| `term` | One number or one variable. |

The parser keeps two dictionaries. `types` maps each variable to `integer` or `double`. `values` maps each variable to its current value.

Each statement method takes a `run` flag. When an `if` condition is false, the parser still reads the next statement and checks it for errors. It passes `run=False`, so the statement does not change a variable or print anything. This is why `if(x>5) output<<z;` reports that `z` is not declared, even when `x` is 1.

When the parser finds an error, it raises `HLError` with the line and the reason, and it stops. `main` prints the program output only when the whole file has no errors. A broken program never prints part of its output.

## Why HLInt behaves this way

The spec leaves some behavior open. These are our choices and the reasons for them:

| Choice | Reason |
| :--- | :--- |
| `NOSPACES.TXT` keeps the spaces inside quotes. | Removing them would change what `output<<"hello world";` prints. |
| Both `:=` and `=` assign a value. | Every example in the spec uses `:=`, except the math example in section 3, which writes `x = 3 + 2;`. We accept both so that every example in the spec runs. |
| HLInt runs the program and prints its output. | The spec title says the interpreter "performs operations". |
| The error message gives the line and the reason. | The required word `ERROR` stays the same, and the reason shows where to fix the program. |
| An undeclared variable, a variable declared twice, a double assigned to an `integer`, and a number with more than 2 decimal places are errors. | The spec defines the two types and their precision. A program that breaks those rules is wrong. |
| Integers with more than one digit are allowed. | The spec says "single digit integers" for math, but a rule against `12` would reject normal programs. |
| Upper and lower case are the same. | The spec's own `if` example writes `If`, `Output`, and `X`. |
