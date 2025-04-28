import json
import config_checker_and_tester as config

def precedence(op):
    # closure and repetition operators
    if op in ['*', '+', '?']:
        return 3
    # explicit concatenation
    if op == '.':
        return 2
    # alternation
    if op == '|':
        return 1
    return 0

# Insert explicit concatenation operator '.'
def add_concat(regex):
    result = []
    prev = None
    for character in regex:
        if prev is not None:
            if (prev not in ['|', '('] and character not in ['|', ')', '*', '+', '?']):
                result.append('.')
        result.append(character)
        prev = character
    return ''.join(result)

# conversion of infix to postfix (Shunting-Yard)
def infix_to_postfix(regex):
    st = []
    output = []
    for c in regex:
        if c.isalnum():  # operand
            output.append(c)
        elif c == '(':
            st.append(c)
        elif c == ')':
            while st and st[-1] != '(':
                output.append(st.pop())
            st.pop()  # remove '('
        else:
            # operator
            while st and precedence(c) <= precedence(st[-1]):
                output.append(st.pop())
            st.append(c)
    while st:
        output.append(st.pop())
    return ''.join(output)

# conversion of infix to prefix (Polish)
def infix_to_prefix(regex):
    exp = add_concat(regex)
    # reverse string and swap parentheses
    rev = []
    for c in exp[::-1]:
        if c == '(':
            rev.append(')')
        elif c == ')':
            rev.append('(')
        else:
            rev.append(c)
    rev_str = ''.join(rev)
    postfix = infix_to_postfix(rev_str)
    return postfix[::-1] # reverse the list

class Node:
    def __init__(self, value, left=None, right=None):
        self.value = value
        self.left = left
        self.right = right

# Build syntax tree from prefix expression
# Unary ops (*, +, ?) take one child (left), binary (., |) take two
def build_tree(prefix):
    tokens = list(prefix)
    def helper():
        if not tokens:
            raise ValueError("Invalid prefix expression")
        tok = tokens.pop(0)
        if tok in ['*', '+', '?']:
            child = helper()
            return Node(tok, left=child)
        if tok in ['.', '|']:
            left = helper()
            right = helper()
            return Node(tok, left, right)
        return Node(tok)
    return helper()

# Generate fully parenthesized infix string from tree
def to_infix(node):
    if node.value in ['*', '+', '?']:
        # unary: child then operator
        return f"({to_infix(node.left)}{node.value})"
    if node.value in ['.', '|']:
        # binary: left, operator, right
        return f"({to_infix(node.left)}{node.value}{to_infix(node.right)})"
    return node.value

# Nicely print the syntax tree using ASCII branches
def print_tree(node, prefix="", is_last=True):
    # Print current node
    branch = "└── " if is_last else "├── "
    print(f"{prefix}{branch}{node.value}")
    # Gather children
    children = []
    if node.left:
        children.append(node.left)
    if node.right:
        children.append(node.right)
    # Recurse on children
    for i, child in enumerate(children):
        last = (i == len(children) - 1)
        new_prefix = prefix + ("    " if is_last else "│   ")
        print_tree(child, new_prefix, last)

def create_dfa(regex):
    prefix = infix_to_prefix(regex)
    print(prefix)
    nfa = {
        "states": {"Start", "End"},
        "alphabet": {"Start", "End", "Lambda"}, # no other sigma should be more than 1 character in length, so these 3 are special
        "transitions":
            {
                "Start" :
                {"Lambda" : {"End"}}
            },
        "start": "Start",
        "accept": {"End"}
    }
    dfa = config.convert_nfa_to_dfa(nfa)
    return dfa


def tester():
    with open("LFA-Assignment2_Regex_DFA_v2.json") as f:
        data = json.load(f)
        for testcase in data:
            name = testcase.get("name")
            regex = testcase.get("regex")
            print(regex)
            test_strings = testcase.get("test_strings")
            dfa = create_dfa(regex)
            # print(dfa)

if __name__ == '__main__':
    tester()
