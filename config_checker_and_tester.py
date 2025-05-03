# START q0 -
# q0 q1 a
# q0 q2 b
# q0 q3 c
# q1 q2 b
# q2 q3 a
# q1 q4 c
# q2 q4 b
# q3 q4 a
# q4 q5 a
# q5 q4 a

def citesteSigma(lines):
    # parsam lines pana la end
    sigma = set()
    for line in lines:
        line = line.strip()
        if len(line) == 0 or line.startswith('#'):
            continue
        elif line == "End":
            break
        elif line != "Sigma:":
            sigma.add(line)
    return sigma

def citesteStates(lines):
    states = []
    startState = None
    finalStates = []
    for line in lines:
        line = line.strip()
        if len(line) == 0 or line.startswith('#'):
            continue
        elif line == "End":
            break
        elif line != "States:" and len(line) > 0:
            lineParse = line.split()
            states.append(lineParse[0].strip(',').strip())
            for token in lineParse: # verificam daca este start sau finish, pentru flag-uri respectiva
                token = token.strip(',')
                token = token.strip()
                if token == "S" and startState is not None:
                    print("Prea multe start States! (max allowed = 1)")
                    return -1
                if token == "S" and startState is None:
                    startState = lineParse[0].strip(',').strip()
                if(token == "F"):
                    finalStates.append(lineParse[0].strip(',').strip())
    if(startState == None):
        print("Automatul nu contine niciun startState! (min allowed = 1, max allowed = 1)")
        return -1
    return states, startState, finalStates

def citesteTransitions(lines):
    transitions = {}
    for line in lines:
        line = line.strip()
        if len(line) == 0 or line.startswith('#'):
            continue
        if line == "End":
            break
        if line != "Transitions:":
            left, middle, right = line.split(",")
            left = left.strip()
            middle = middle.strip()
            right = right.strip()
            if transitions.get(left, None) == None:
                transitions[left] = [(middle, right)]
            else:
                transitions[left].append((middle, right))
    return transitions


def citire(filename):
    sigma = []
    states = {}
    startState = ""
    finalStates = []
    # pentru fiecare nod
    # vedem ce muchii are, de forma transitions[nod_curent] = lista de tupluri de forma (cuvant_acceptat, nod_urmator)
    transitions = {}
    sigmaIndex, statesIndex, trasitionsIndex = -1, -1, -1
    with open(filename) as f:
        linii = f.readlines()
        lineIndex = -1
        for line in linii:
            line = line.strip()
            lineIndex += 1
            if len(line) != 0 and not line.startswith("#"):
                if line == "Sigma:":
                    sigmaIndex = lineIndex
                elif line == "States:":
                    statesIndex = lineIndex
                elif line == "Transitions:":
                    transitionsIndex = lineIndex
            else:
                continue
        # acum avem indecsii la linii
        # verificam daca ii avem pe toti, daca nu aruncam o eroare
        if sigmaIndex == -1 or statesIndex == -1 or transitionsIndex == -1: # clar una din ele nu este, aruncam o eroare
            print("Date introduse gresit, lipsesc field-urile Sigma/States/Transitions!")
            return -1
        sigma = citesteSigma(linii[sigmaIndex:]) # aici nu avem erori daca mi-a fost transmis ca datele sunt corecte
        verif = citesteStates(linii[statesIndex:])
        if verif == -1:
            print("Intrare fisier stari invalida!")
            return -1
        else:
            states, startState, finalStates = verif
        transitions = citesteTransitions(linii[transitionsIndex:])
    if finalStates == []:
        print("Automatul nu contine nici o stare finala!")
        return -1
    return sigma, states, startState, finalStates, transitions

# verificam daca limbajul este corect definit
def verificare(sigma, states, startState, finalStates, transitions):
    for transition in transitions:
        if transition not in states:
            print(f"Automatul nu contine starea {transition}")
            return -1
        v = []
        for muchie, nod_nou in transitions[transition]:
            if muchie not in sigma:
                print(f"Automatul nu admite in limbaj cuvantul {muchie}")
                return -1
            if nod_nou not in states:
                print(f"Automatul nu contine starea {nod_nou}!")
                return -1
            v.append(muchie)
        if (len(v) != len(set(v))):
            print("Automatul este NFA!")
            return 2
    return 1

def verificareNoDebug(sigma, states, startState, finalStates, transitions):
    for transition in transitions:
        if transition not in states:
            return -1
        v = []
        for muchie, nod_nou in transitions[transition]:
            if muchie not in sigma:
                return -1
            if nod_nou not in states:
                return -1
            v.append(muchie)
        if (len(v) != len(set(v))):
            return 2
    return 1


def DFS(actual_state, finalStates, transitions, visited):
    visited[actual_state] = True
    if actual_state in finalStates:
        return 1
    for symbol, next_state in transitions.get(actual_state, []):
        if next_state not in visited:
            if DFS(next_state, finalStates, transitions, visited) == 1:
                return 1
    return 0


def verificareAcceptance(startState, finalStates, transitions, isNfa):
    viz = {}
    result = DFS(startState, finalStates, transitions, viz)
    if result == 1:
        if isNfa == 1:
            return 2
        return 1
    else:
        if isNfa == 0:
            return -1
        else:
            return -2

def printAutomata(sigma, states, startState, finalStates, transitions):
    print("Sigma: ", sigma)
    print("States: ", states)
    print("startState: ", startState)
    print("finalStates: ", finalStates)
    print("transitions: ", transitions)

def cuvantParse(input, Sigma, states, currentNodes, finalStates, transitions):
    with open("wordParse.log", "a") as f:
        f.write("Cuvantul partial de parsat: " + input + "\n")
        f.write("Sigma: " + repr(Sigma) + "\n")
        f.write("States: " + repr(states) + "\n")
        f.write("currentNodes: " + repr(currentNodes) + "\n")
        f.write("finalStates: " + repr(finalStates) + "\n")
        f.write("transitions: " + repr(transitions) + "\n\n")
    currentWord = ""
    for acceptedWord in Sigma:
        if input.startswith(acceptedWord):
            input = input.removeprefix(acceptedWord)
            currentWord = acceptedWord
            break
    if currentWord == "":
        if input == "":
            for finalState in finalStates:
                if finalState in currentNodes:
                    return 1  # cuvant acceptat
        if input != "":
            return -1
        return 0
    if currentNodes == []:
        return -1
    #print(currentNodes)
    nextNodes = []
    for currentNode in currentNodes[:]: # trebuie o copie ca sa nu se strice cand stergem
        # tehnic e redundant daca fac cu 2 doar ca nu imi doresc erori de memorie deloc
        # currentNodes.remove(currentNode) # il scoatem pentru ca obligatoriu va merge in starea urmatoare
        if currentNode in transitions.keys():
            for cuvant, nodUrmator in transitions[currentNode]:
                if cuvant == currentWord:
                    nextNodes.append(nodUrmator) # tinand cont ca i-am facut o copie ar trebui
    return cuvantParse(input, Sigma, states, nextNodes, finalStates, transitions)

def old_to_new(transitions_old):
    """
    Convert transitions from my
    old format
      { state: [(symbol, next_state), …], … }
    to the “new” format which my laborant uses
      { state: { symbol: { next_state, … }, … }, … }.
    """
    transitions_new = {}
    for state, edges in transitions_old.items():
        sym_map = {}
        for symbol, dest in edges:
            sym_map.setdefault(symbol, set()).add(dest)
        transitions_new[state] = sym_map
    return transitions_new


def new_to_old(transitions_new):
    """
    Convert transitions from the new format
      { state: { symbol: { next_state, … }, … }, … }
    back to the “old” format
      { state: [(symbol, next_state), …], … }.
    """
    transitions_old = {}
    for state, sym_map in transitions_new.items():
        lst = []
        for symbol, dests in sym_map.items():
            for dest in dests:
                lst.append((symbol, dest))
        transitions_old[state] = lst
    return transitions_old


def convert_to_new_automata_format(sigma, states, start, accept, transitions_old):
    return {
        "states": set(states),
        "alphabet": set(sigma),
        "transitions": old_to_new(transitions_old),
        "start": start,
        "accept": set(accept),
    }

def convert_to_old_automata_format(config):
    sigma = set(config.get("alphabet", []))
    states = set(config.get("states", []))
    start = config.get("start")
    accept = set(config.get("accept", []))
    transitions_new = config.get("transitions", {})
    transitions_old = new_to_old(transitions_new)
    return sigma, states, start, accept, transitions_old

# acelasi lucru ca CheckConfig, dar foloseste modelul nou
def CheckConfigFromModel(config):
    sigma, states, start, accept, transitions = convert_to_old_automata_format(config)
    if verificare(sigma, states, start, accept, transitions) < 1:
        return False
    is_nfa = verificare(sigma, states, start, accept, transitions) == 2
    result = verificareAcceptance(start, accept, transitions, is_nfa)
    return result in (1, 2)

# Bool
def CheckConfig(configpath):
    result = citire(configpath)
    if result == -1:
        return False
    sigma, states, startState, finalStates, transitions = result
    finalCheck = verificare(sigma, states, startState, finalStates, transitions)
    if finalCheck == -1:
        return False
    isNfa = (finalCheck == 2)
    acceptance = verificareAcceptance(startState, finalStates, transitions, isNfa)
    if acceptance == 1:
        return True
    elif acceptance == 2:
        return True
    elif acceptance == -1:
        return False
    elif acceptance == -2:
        return False
    else:
        return False # nu ar trebui sa ajunga aici niciodata


def CheckWordValidity(word, sigma, states, start, accept, transitions):
    return cuvantParse(input=word,
                       Sigma=sigma,
                       states=states,
                       currentNodes=[start],
                       finalStates=accept,
                       transitions=transitions) == 1

def lambda_closure(state, transitions):
    """Return the lambda closure of a single state."""
    stack = [state]
    closure = {state}
    while stack:
        s = stack.pop()
        for dest in transitions.get(s, {}).get("Lambda", []):
            if dest not in closure:
                closure.add(dest)
                stack.append(dest)
    return closure

def convert_lambda_nfa_to_nfa(lambda_nfa):
    states = lambda_nfa["states"]
    alphabet = lambda_nfa["alphabet"] - {"Lambda"} # I was today days old when I found out you can just - a dictionary
    raw_trans = lambda_nfa["transitions"]
    start = lambda_nfa["start"]
    orig_accept = set(lambda_nfa["accept"])

    closures = {s: lambda_closure(s, raw_trans) for s in states}

    new_trans = {s: {} for s in states}
    for s in states:
        for a in alphabet:
            dests = set()
            for r in closures[s]:
                for t in raw_trans.get(r, {}).get(a, []):
                    dests |= closures[t]
            if dests:
                new_trans[s].setdefault(a, set()).update(dests)

    #new accept states
    new_accept = {s for s, cl in closures.items() if cl & orig_accept}

    nfa = {
        "states": states,
        "alphabet": alphabet,
        "transitions": new_trans,
        "start": start,
        "accept": new_accept,
    }
    return nfa

def convert_nfa_to_dfa(nfa_config):
    alphabet = nfa_config["alphabet"]
    transitions = nfa_config["transitions"]
    start = nfa_config["start"]
    accept = nfa_config["accept"]

    dfa_start = frozenset([start])

    dfa_states = []
    dfa_transitions = {}
    dfa_accept = set()

    unprocessed = [dfa_start]
    while unprocessed:
        current = unprocessed.pop(0)
        if current not in dfa_states:
            dfa_states.append(current)

        if any(state in accept for state in current):
            dfa_accept.add(current)

        for symbol in alphabet:
            next_state = set()
            # For each NFA state in the current DFA state, get transitions on the symbol.
            for state in current:
                # If the state has a transition on this symbol, add the resulting states.
                if symbol in transitions.get(state, {}):
                    next_state.update(transitions[state][symbol])
            # Convert to frozenset to use as a DFA state.
            next_state = frozenset(next_state)
            if not next_state:
                continue  # No transitions on this symbol.
            # Record the DFA transition.
            dfa_transitions.setdefault(current, {})[symbol] = next_state
            # If the next state hasn't been processed yet, add it to the queue.
            if next_state not in dfa_states and next_state not in unprocessed:
                unprocessed.append(next_state)
    dfa = {
        "states": dfa_states,
        "alphabet": alphabet,
        "transitions": dfa_transitions,
        "start": dfa_start,
        "accept": dfa_accept
    }
    return dfa

global count
global map_frozenset_to_string

def convert_frozenset_to_string(fs):
    global count
    count += 1
    global map_frozenset_to_string
    map_frozenset_to_string[fs] = str(count)
    return str(count)

def convert_dfa_to_dfa_dict(dfa_config):
    global count
    global map_frozenset_to_string
    map_frozenset_to_string = {}
    count = 0
    states = {convert_frozenset_to_string(x) for x in dfa_config["states"]}
    alphabet = dfa_config["alphabet"]
    accept = {map_frozenset_to_string[x] for x in dfa_config["accept"]}
    start = map_frozenset_to_string[dfa_config["start"]]
    transitions = {}
    for old_src, symbol_map in dfa_config["transitions"].items():
        src_name = map_frozenset_to_string[old_src]
        transitions[src_name] = {}
        for sym, old_dest in symbol_map.items():
            dest_name = map_frozenset_to_string[old_dest]
            transitions[src_name][sym] = dest_name
    dfa = {
        "states": states,
        "alphabet": alphabet,
        "transitions": transitions,
        "start": start,
        "accept": accept
    }
    return dfa


def CheckWordBetter(word, new_automata):
    sigma, states, start, accept, transitions_old = convert_to_old_automata_format(new_automata)
    # before parsing check if old format automata is valid
    # if verificareNoDebug(sigma, states, start, accept, transitions_old) < 1:
    #     return False
    if cuvantParse(input=word, Sigma=sigma, states=states, currentNodes=[start], finalStates=accept, transitions=transitions_old) == 1:
        return True
    else:
        return False



# -----------code below not to be used in a module-------------
def test():
    nfa = {
        "states": {"q0", "q1", "q2"},
        "alphabet": {"a", "b"},
        "transitions": {
            "q0": {
                "a": {"q0", "q1"},
                "b": {"q0"}
            },
            "q1": {
                "b": {"q2"}
            },
            "q2": {
                "a": {"q2"},
                "b": {"q2"}
            }
        },
        "start": "q0",
        "accept": {"q2"}
    }
    dfa = convert_nfa_to_dfa(nfa)
    print(CheckWordBetter("abb",nfa)) # HELL YEA IT WORKS
    #print(dfa)
    #sigma, states, start, accept, transitions_old = convert_to_old_automata_format(nfa)
    #printAutomata(sigma, states, start, accept, transitions_old)
    #print(convert_to_new_automata_format(sigma, states, start, accept, transitions_old))


# -----------code below not to be used in a module-------------
def main():
    result = citire("dfa_config_file.txt")
    if result == -1:
        print("Automatul contine erori! Verificati mesajul anterior!")
        return
    sigma, states, startState, finalStates, transitions = result
    finalCheck = verificare(sigma, states, startState, finalStates, transitions)
    if finalCheck == -1:
        print("Automatul contine erori! Verificati mesajul anterior!")
        return
    isNfa = (finalCheck == 2)
    acceptance = verificareAcceptance(startState, finalStates, transitions, isNfa)
    if  acceptance == 1:
        print("Dfa Acceptat!")
    elif acceptance == 2:
        print("Nfa Acceptat!")
    elif acceptance == -1:
        print("Dfa Invalid!")
        return -1
    elif acceptance == -2:
        print("Nfa Invalid!")
        return -2
    else:
        print("Eroare!")
        return -3
    #userInput = input("Doriti sa vedeti variabilele stocate? (Y/N)\nUser:")
    #if userInput == "Y":
    #    printAutomata(sigma, states, startState, finalStates, transitions)
    userInput = input("Introduceti un cuvant pentru limbaj!\nUser:")
    with open("wordParse.log", "w") as f:
        f.write("Input initial: " + userInput + "\n")
    raspuns = cuvantParse(input=userInput, Sigma=sigma,states = states, currentNodes = [startState], finalStates=finalStates, transitions=transitions)
    if raspuns == 1:
        if isNfa == 1:
            print("Nfa-ul accepta cuvantul!")
        else:
            print("Dfa-ul accepta cuvantul!")
    elif raspuns == 0:
        if isNfa == 1:
            print("Nfa-ul nu accepta cuvantul!")
        else:
            print("Dfa-ul nu accepta cuvantul!")
    else:
        print("Eroare! Verifica mesajul anterior sau logs!")

# if it is not a module, run the main script to mantain functionality.
if __name__ == '__main__':
    test()