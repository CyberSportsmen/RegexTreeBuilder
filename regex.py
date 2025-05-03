import json
import os

import config_checker_and_tester as config
from graphviz import Digraph

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


def parse_lambda_nfa_to_graph(lambda_nfa):
    dot = Digraph(format='png')
    dot.attr(rankdir='LR')
    dot.node('', shape='none', label='')
    dot.edge('', lambda_nfa['start'], label='')
    for state in lambda_nfa['states']:
        shape = 'doublecircle' if state in lambda_nfa['accept'] else 'circle'
        dot.node(state, shape=shape)
    for src, paths in lambda_nfa['transitions'].items():
        for symbol, dests in paths.items():
            label = 'λ' if symbol == 'Lambda' else symbol
            for dest in dests:
                dot.edge(src, dest, label=label)
    return dot

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
    new_start = f"Start{timesCalled}_{nfa1.get('start')}+{nfa2.get('start')}"
    new_end = f"End{timesCalled}_{nfa1.get('start')}+{nfa2.get('start')}"
    added_transitions = {new_start: {"Lambda": {nfa1.get("start"), nfa2.get("start")}}}
    for accepted_state in nfa1.get("accept") | nfa2.get("accept"):
        added_transitions.setdefault(accepted_state, {}).setdefault("Lambda", set()).add(new_end)

    new_transitions = {**nfa1.get("transitions"), **nfa2.get("transitions"), **added_transitions}

    new_nfa = {
        "states": nfa1.get("states") | nfa2.get("states") | {new_start} | {new_end},  # union of states
        "alphabet": nfa1.get("alphabet") | nfa2.get("alphabet") | {"Lambda"},  # union of alphabets plus "Lambda"
        "transitions": new_transitions,
        "start": new_start,
        "accept": {new_end},
    }
    return new_nfa

# fixed bug of return lambda not being added. REMINDME: I hate dictionaries
def nfa_kleene(nfa):
    """Return the zero-or-more (kleene star) of nfa."""
    global timesCalled
    timesCalled += 1

    old_start   = nfa["start"]
    old_accepts = set(nfa["accept"])
    trans       = nfa.setdefault("transitions", {})
    new_start  = f"Start*{timesCalled}"
    new_accept = f"End*{timesCalled}"

    states = set(nfa["states"]) | {new_start, new_accept}
    trans.setdefault(new_start, {})
    trans[new_start].setdefault("Lambda", set()).update({old_start, new_accept})

    for fs in old_accepts:
        trans.setdefault(fs, {})
        trans[fs].setdefault("Lambda", set()).update({old_start, new_accept})
    alphabet = set(nfa["alphabet"]) | {"Lambda"}
    nfa = {
        "states":      states,
        "alphabet":    alphabet,
        "transitions": trans,
        "start":       new_start,
        "accept":      {new_accept},
    }
    return nfa

#copy paste practic de la kleene, evident
def nfa_plus(nfa):
    """Return the one-or-more (plus) of nfa, using fresh start/end like Thompson."""
    global timesCalled
    timesCalled += 1

    old_start   = nfa["start"]
    old_accepts = set(nfa["accept"])
    trans       = nfa.setdefault("transitions", {})
    new_start  = f"Start+{timesCalled}"
    new_accept = f"End+{timesCalled}"

    states = set(nfa["states"]) | {new_start, new_accept}
    trans.setdefault(new_start, {})
    trans[new_start].setdefault("Lambda", set()).add(old_start)

    for fs in old_accepts:
        trans.setdefault(fs, {})
        trans[fs].setdefault("Lambda", set()).update({old_start, new_accept})
    alphabet = set(nfa["alphabet"]) | {"Lambda"}
    nfa = {
        "states":      states,
        "alphabet":    alphabet,
        "transitions": trans,
        "start":       new_start,
        "accept":      {new_accept},
    }
    return nfa

# asta inca merge, doamne ajuta
def nfa_optional(nfa):
    """Return the zero-or-one (optional) of nfa."""
    final_states = nfa.get("accept")
    transitions = nfa.get("transitions")
    # adds a bypass from start to end (for 0 occurances acceptance)
    transitions[nfa["start"]].setdefault("Lambda", set()).update(nfa["accept"])
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
    print(prefix)
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
        directory = os.getcwd()
        directory = os.path.join(directory, "graphs")
        os.makedirs(directory, exist_ok=True)
        for testcase in data:
            name = testcase.get("name")
            print("Testing " + name)
            regex = testcase.get("regex")
            # test_strings = testcase.get("test_strings")
            global timesCalled
            timesCalled = 0
            lambda_nfa = create_lambda_nfa(regex)
            graph = parse_lambda_nfa_to_graph(lambda_nfa)
            graph.render(f'lambda_nfa_graph{name}', directory=directory, cleanup=True)
            pretty_print_nfa(lambda_nfa)

if __name__ == '__main__':
    tester()