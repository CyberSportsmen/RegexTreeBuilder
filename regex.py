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

def print_tree(node, prefix="", is_last=True):
    """prints the syntax tree using ASCII branches"""
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

def pretty_print_nfa(nfa):
    for key in ('states', 'alphabet', 'start', 'accept'):
        if key in nfa:
            print(f"{key}: {nfa[key]}")
    transitions = nfa.get('transitions', {})
    print('transitions:')
    for state, trans in transitions.items():
        print(f"    {state}: {{", end='')
        parts = []
        for symbol, targets in trans.items():
            parts.append(f"'{symbol}': {targets}")
        print(', '.join(parts) + ' }')


timesCalled = 0

def create_symbol_nfa(symbol):
    """Return an NFA that recognizes a single symbol."""
    global timesCalled
    timesCalled += 1
    nfa = {
        "states": {f"Start{timesCalled}{symbol}", f"End{timesCalled}{symbol}"},
        "alphabet": {symbol},
        "transitions": {
            f"Start{timesCalled}{symbol}" : {
                symbol : {f"End{timesCalled}{symbol}"}
            }
        },
        "start": f"Start{timesCalled}{symbol}",
        "accept": {f"End{timesCalled}{symbol}"},
    }
    #print(nfa)
    return nfa

def nfa_concatenate(nfa1, nfa2):
    """Return the concatenation of nfa1 and nfa2."""
    # Add lambda transitions from nfa1's accept states to nfa2's start
    lambda_transitions = {}
    nfa1_accept_states = nfa1.get("accept")
    nfa2_start = nfa2.get("start")

    for accept_state in nfa1_accept_states:
        lambda_transitions.setdefault(accept_state, {}).setdefault("Lambda", set()).add(nfa2_start)

    new_nfa = {
        "states": nfa1.get("states") | nfa2.get("states"),  # union of states
        "alphabet": nfa1.get("alphabet") | nfa2.get("alphabet") | {"Lambda"},  # union of alphabets plus "Lambda"
        "transitions": {**nfa1.get("transitions"), **nfa2.get("transitions"), **lambda_transitions},
        "start": nfa1.get("start"),
        "accept": nfa2.get("accept"),
    }
    #print(new_nfa)
    return new_nfa


def nfa_alternate(nfa1, nfa2):
    """Return the alternation (union) of nfa1 and nfa2."""
    global timesCalled
    timesCalled += 1
    raise NotImplementedError

def nfa_kleene(nfa):
    """Return the Kleene star of nfa."""
    final_states = nfa.get("accept")
    transitions = nfa.get("transitions")
    # adds a bypass from start to end (for 0 occurances acceptance)
    transitions[nfa.get("start")] = {**transitions[nfa.get("start")], "Lambda": nfa.get("accept")}
    # adds a bypass from end to start (for 1+ occurance acceptance)
    for final_state in final_states:
         if final_state not in transitions.keys():
             transitions[final_state] = {"Lambda": {nfa.get("start")}}
         else:
             transitions[final_state] = ({**transitions[final_state], "Lambda": {nfa.get("start")}})
    new_nfa = {
        "states": nfa.get("states"),
        "alphabet": nfa.get("alphabet"),
        "transitions": transitions,
        "start": nfa.get("start"),
        "accept": nfa.get("accept"),
    }
    return new_nfa

def nfa_plus(nfa):
    """Return the one-or-more (plus) of nfa."""
    final_states = nfa.get("accept")
    transitions = nfa.get("transitions")
    # adds a bypass from end to start (for 1+ occurance acceptance)
    for final_state in final_states:
        if final_state not in transitions.keys():
            transitions[final_state] = {"Lambda": {nfa.get("start")}}
        else:
            transitions[final_state] = ({**transitions[final_state], "Lambda": {nfa.get("start")}})
    new_nfa = {
        "states": nfa.get("states"),
        "alphabet": nfa.get("alphabet"),
        "transitions": transitions,
        "start": nfa.get("start"),
        "accept": nfa.get("accept"),
    }
    return new_nfa

def nfa_optional(nfa):
    """Return the zero-or-one (optional) of nfa."""
    final_states = nfa.get("accept")
    transitions = nfa.get("transitions")
    # adds a bypass from start to end (for 0 occurances acceptance)
    transitions[nfa.get("start")] = {**transitions[nfa.get("start")], "Lambda": nfa.get("accept")}
    new_nfa = {
        "states": nfa.get("states"),
        "alphabet": nfa.get("alphabet"),
        "transitions": transitions,
        "start": nfa.get("start"),
        "accept": nfa.get("accept"),
    }
    return new_nfa

# Create epsilon-NFA from regex by traversing syntax tree
def create_lambda_nfa(regex):
    prefix = infix_to_prefix(regex)
    tree = build_tree(prefix)
    global timesCalled
    timesCalled = 0
    def traverse(node):
        # Leaf: single symbol
        if node.value not in ['.', '|', '*', '+', '?']:
            return create_symbol_nfa(node.value)

        # Unary operators
        if node.value == '*':
            child_nfa = traverse(node.left)
            return nfa_kleene(child_nfa)
        if node.value == '+':
            child_nfa = traverse(node.left)
            return nfa_plus(child_nfa)
        if node.value == '?':
            child_nfa = traverse(node.left)
            return nfa_optional(child_nfa)

        # Binary operators
        left_nfa = traverse(node.left)
        right_nfa = traverse(node.right)
        if node.value == '.':
            return nfa_concatenate(left_nfa, right_nfa)
        if node.value == '|':
            return nfa_alternate(left_nfa, right_nfa)

        raise ValueError(f"Unknown operator: {node.value}")

    # Build the NFA
    lambda_nfa = traverse(tree)
    # Optionally convert to DFA:
    # dfa = config.convert_nfa_to_dfa(lambda_nfa)
    return lambda_nfa


def tester():
    with open("tests_clone.json") as f:
        data = json.load(f)
        for testcase in data:
            name = testcase.get("name")
            regex = testcase.get("regex")
            test_strings = testcase.get("test_strings")
            # lambda_nfa = create_lambda_nfa(regex)
            # print(lambda_nfa)
            global timesCalled
            timesCalled = 0
            nfa = create_lambda_nfa(regex)
            pretty_print_nfa(nfa)

if __name__ == '__main__':
    tester()
# class A, Class B, Class C, Class D
# class B : A
# Class C : A
# class D : B, C