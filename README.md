# Regex Builder in Python

**Minimal .NET regex and Automata graph visualiser**

A tiny library to parse .NET-style regular expressions into an abstract syntax tree (AST) for inspection or transformation.

## Dependencies

- graphviz for python
- python 3.11

## Installation

https://graphviz.org/download/ (make sure to add graphviz to PATH)

# How to run

### Place your input strings and regexes in a .json file with following format example:
```json
[
  {
    "name": "R1",
    "regex": "(a|b|c)",
    "test_strings": [
      { "input": "", "expected": true },
      { "input": "a", "expected": true }
    ]
  },
  {
    "name": "R2",
    "regex": "(a?b?)?",
    "test_strings": [
      { "input": "a", "expected": true },
      { "input": "ab", "expected": true },
      { "input": "acb", "expected": true }
    ]
  }
]
```
### Open cmd on the filepath of the project and run:
```powershell
python3 regex.py <your_json_file_path>
```