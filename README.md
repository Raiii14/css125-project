# HLInt: an interpreter for the HL language

HLInt is the CSS125L project. It reads a program written in HL, the small language defined in the [project specifications](instructions/CSS125_Project_Specifications.md). It checks the program for errors and runs it.

For each HL file, HLInt writes the program without spaces to `NOSPACES.TXT` and writes the reserved words and symbols to `RES_SYM.TXT`. Then it prints `NO ERROR(S) FOUND` and the program output, or it prints `ERROR` and the line and reason for the first error.

To learn how the code works and why HLInt behaves the way it does, read [How HLInt works](docs/how-hlint-works.md). For the HL statements, types, and error messages, see section II of the [documentation draft](docs/HLInt_Documentation_Draft.md).

## Run HLInt

You need Python 3.9 or newer. HLInt uses no other packages. To check your version, run `py --version` on Windows or `python3 --version` on Mac or Linux.

1. Open a terminal and go to the `hlint` folder:

   ```text
   cd hlint
   ```

2. Run HLInt with the name of an HL file. On Mac or Linux, type `python3` instead of `py`.

   ```text
   py HLInt.py PROG1.HL
   ```

3. Check the screen output:

   ```text
   NO ERROR(S) FOUND
   5
   ```

HLInt writes `NOSPACES.TXT` and `RES_SYM.TXT` in the folder you run it from. Each run replaces both files.

The other sample programs give this output:

| Command | Screen output |
| :--- | :--- |
| `py HLInt.py PROG2.HL` | `NO ERROR(S) FOUND`, then `4.25` |
| `py HLInt.py PROG3.HL` | `NO ERROR(S) FOUND`, then `3` |
| `py HLInt.py tests/ERR_MISSING_SEMICOLON.HL` | `ERROR`, then `line 3: expected ';'` |

## Run the tests

From the `hlint` folder, run:

```text
py -m unittest -v test_hlint
```

All tests must pass. The tests run PROG1 to PROG3 and every file in `tests/`, and they check the output or error message of each one. Two more tests run HLInt as a command and check the files it writes.

## Add an error test

1. In `hlint/tests/`, write a small HL file that contains the error, for example `ERR_SOMETHING.HL`.
2. In `hlint/test_hlint.py`, add a line to the `CASES` list with the file path, `[]` for the output, and the error message you expect.
3. Run the tests.

## Find files in the repo

| Folder | Contents |
| :--- | :--- |
| `hlint/` | The program, the sample programs, and the tests. We zip and submit this folder. |
| `hlint/tests/` | HL programs with errors on purpose, for the tests and the screenshots. |
| `docs/` | The documentation draft, the group member list, and [How HLInt works](docs/how-hlint-works.md). |
| `instructions/` | The course handouts. Keep these files as the course gave them. |

## Submit the project

The full rules are in [Project_Demo.md](instructions/Project_Demo.md) and [Project_Documentation.md](instructions/Project_Documentation.md).

- [ ] Fill in the group name, full names, and sections in `docs/GROUP_MEMBERS.txt` and `docs/HLInt_Documentation_Draft.md`.
- [ ] Take screenshots of the sample runs and add them to section III of the documentation draft.
- [ ] Export the documentation draft to PDF.
- [ ] Delete `NOSPACES.TXT`, `RES_SYM.TXT`, and `__pycache__` from `hlint/`, then zip the `hlint/` folder.
- [ ] Zip the screenshots.
- [ ] Record the demo video with everyone's full name in the first frame.
- [ ] Upload everything to Google Drive and submit the link.
