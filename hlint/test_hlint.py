import os
import subprocess
import sys
import tempfile
import unittest

from HLInt import interpret

HERE = os.path.dirname(os.path.abspath(__file__))

# (file, expected program output, expected error text or None)
CASES = [
    ("PROG1.HL", ["5"], None),
    ("PROG2.HL", ["4.25"], None),
    ("PROG3.HL", ["3"], None),
    ("tests/ERR_MISSING_PAREN.HL", [], "line 4: expected ')'"),
    ("tests/ERR_BAD_RELATIONAL.HL", [], "line 3: expected '<', '>', '==' or '!='"),
    ("tests/ERR_DOUBLE_TO_INTEGER.HL", [], "line 2: cannot assign a double to integer 'x'"),
    ("tests/ERR_TOO_MANY_DECIMALS.HL", [], "line 2: '1.234' has more than 2 decimal places"),
    ("tests/ERR_MISSING_SEMICOLON.HL", [], "line 3: expected ';'"),
    ("tests/ERR_UNDECLARED.HL", [], "line 2: 'y' is not declared"),
    ("tests/ERR_REDECLARED.HL", [], "line 2: 'x' is already declared"),
]


def read(path):
    with open(os.path.join(HERE, path), encoding="utf-8") as f:
        return f.read()


class ProgramTests(unittest.TestCase):
    def test_programs(self):
        for path, output, error in CASES:
            with self.subTest(path=path):
                result = interpret(read(path))
                self.assertEqual(result.error, error)
                self.assertEqual(result.output, output)

    def test_removes_spaces_but_keeps_lines_and_strings(self):
        result = interpret('x: integer;\noutput << "hello world";\n')
        self.assertEqual(result.nospaces, 'x:integer;\noutput<<"hello world";\n')
        self.assertEqual(result.output, ["hello world"])

    def test_lists_reserved_words_and_symbols_once(self):
        result = interpret(read("PROG1.HL"))
        self.assertEqual(result.reserved, ["integer", "output"])
        self.assertEqual(result.symbols, [":", ";", ":=", "<<"])

    def test_keywords_and_names_ignore_case(self):
        result = interpret("X: INTEGER;\nx:= 2;\nOutput<<X;\n")
        self.assertIsNone(result.error)
        self.assertEqual(result.output, ["2"])

    def test_chained_arithmetic_with_doubles(self):
        source = "x: integer;\ny: double;\nx:= 3 + 2;\ny:= 4 + 2.56 - x;\noutput<<x;\noutput<<y;\noutput<<0.1+0.2;\n"
        self.assertEqual(interpret(source).output, ["5", "1.56", "0.30"])

    def test_integer_value_in_double_variable_prints_as_double(self):
        self.assertEqual(interpret("y: double;\ny:= 2;\noutput<<y;\n").output, ["2.00"])

    def test_spec_example_with_false_condition_prints_nothing(self):
        result = interpret("x: integer;\nx:= 6;\nIf(x<5)\n Output<<X;\n")
        self.assertIsNone(result.error)
        self.assertEqual(result.output, [])

    def test_spec_math_example_with_plain_equals(self):
        result = interpret("x: integer;\ny: double;\nx = 3 + 2;\ny = 4 + 2.56;\noutput<<x;\noutput<<y;\n")
        self.assertIsNone(result.error)
        self.assertEqual(result.output, ["5", "6.56"])

    def test_relational_operators(self):
        source = "x: integer;\nx:= 3;\nif(x>2) output<<1;\nif(x==3) output<<2;\nif(x!=3) output<<3;\nif(x+0.5<3.6) output<<4;\n"
        self.assertEqual(interpret(source).output, ["1", "2", "4"])

    def test_skipped_if_body_does_not_assign(self):
        source = "x: integer;\nx:= 1;\nif(x>5)\n x:= 9;\noutput<<x;\n"
        self.assertEqual(interpret(source).output, ["1"])

    def test_skipped_if_body_is_still_checked(self):
        source = "x: integer;\nx:= 1;\nif(x>5)\n output<<z;\n"
        self.assertEqual(interpret(source).error, "line 4: 'z' is not declared")

    def test_nested_if(self):
        source = "x: integer;\nx:= 1;\nif(x<5)\n if(x>0)\n  output<<\"both\";\n"
        self.assertEqual(interpret(source).output, ["both"])

    def test_if_without_body_is_an_error(self):
        self.assertEqual(interpret("x: integer;\nif(x<5)\n").error, "line 2: expected a statement")

    def test_unknown_character_is_an_error(self):
        self.assertEqual(interpret("x: integer;\nx:= 5 $\n").error, "line 2: expected ';'")


class CommandLineTests(unittest.TestCase):
    def run_hlint(self, source):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "PROG.HL")
            with open(path, "w", encoding="utf-8") as f:
                f.write(source)
            proc = subprocess.run(
                [sys.executable, os.path.join(HERE, "HLInt.py"), path],
                cwd=tmp, capture_output=True, text=True,
            )
            files = {name: read(os.path.join(tmp, name)) for name in ("NOSPACES.TXT", "RES_SYM.TXT")}
            return proc.stdout, files

    def test_valid_program_writes_both_files(self):
        stdout, files = self.run_hlint(read("PROG1.HL"))
        self.assertEqual(stdout, "NO ERROR(S) FOUND\n5\n")
        self.assertEqual(files["NOSPACES.TXT"], "x:integer;\nx:=5;\noutput<<x;\n")
        self.assertEqual(files["RES_SYM.TXT"], "Reserved words:\ninteger\noutput\n\nSymbols:\n:\n;\n:=\n<<\n")

    def test_invalid_program_prints_error_and_no_output(self):
        stdout, files = self.run_hlint(read("tests/ERR_MISSING_SEMICOLON.HL"))
        self.assertEqual(stdout, "ERROR\nline 3: expected ';'\n")
        self.assertIn("x:=5\n", files["NOSPACES.TXT"])


if __name__ == "__main__":
    unittest.main()
