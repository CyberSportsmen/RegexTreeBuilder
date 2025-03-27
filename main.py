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
    sigma = []
    for line in lines:
        line = line.strip()
        if line.startswith('#'):
            continue
        elif line == "End":
            break
        elif line != "Sigma:":
            sigma.append(line)
    return sigma

def citesteStates(lines):
    states = []
    startState = None
    finalStates = []
    for line in lines:
        line = line.strip()
        if line.startswith('#'):
            continue
        elif line == "End":
            break
        elif line != "States:":
            lineParse = line.split()
            states.append(lineParse[0].strip(',').strip())
            for token in lineParse: # verificam daca este start sau finish, pentru flag-uri respectiva
                token = token.strip(',')
                token = token.strip()
                if(token == "S" and startState != None):
                    print("Prea multe start States! (max allowed = 1)")
                    return -1
                if(token == "S" and startState == None):
                    startState = lineParse[0].strip(',').strip()
                if(token == "F"):
                    finalStates.append(lineParse[0].strip(',').strip())
    return states, startState, finalStates

def citesteTransitions(lines):
    transitions = []



def citire(filename):
    sigma = []
    states = {}
    startState = ""
    finalStates = []
    # pentru fiecare nod
    # vedem ce muchii are, de forma transitions[nod_curent] = lista de tupluri de forma (cuvant_acceptat, nod_urmator)
    transitions = []
    sigmaIndex, statesIndex, trasitionsIndex = -1, -1, -1
    with open(filename) as f:
        linii = f.readlines()
        lineIndex = -1
        for line in linii:
            line = line.strip()
            lineIndex += 1
            if line[0] == "#":
                continue
            else:
                if line == "Sigma:":
                    sigmaIndex = lineIndex
                elif line == "States:":
                    statesIndex = lineIndex
                elif line == "Transitions:":
                    transitionsIndex = lineIndex
        # acum avem indecsii la linii
        # verificam daca ii avem pe toti, daca nu aruncam o eroare
        if sigmaIndex == -1 or statesIndex == -1 or transitionsIndex == -1: # clar una din ele nu este, aruncam o eroare
            print("Date introduse gresit, lipsesc field-urile Sigma/States/Transitions!")
            return -1
        # else
        sigma = citesteSigma(linii[sigmaIndex:]) # aici nu avem erori daca mi-a fost transmis ca datele sunt corecte
        verif = citesteStates(linii[statesIndex:])
        if verif == -1:
            return -1
        else:
            states, startState, finalStates = verif

    return sigma, states, startState, finalStates, transitions

def main():
    result = citire("dfa_config_file.txt")
    if result == -1:
        print("Automatul contine erori! Verificati mesajul anterior!")
        return
    sigma, states, startState, finalStates, transitions = result
    print("Sigma:", sigma)
    print("States: ", states)
    print("startState: ", startState)
    print("finalStates: ", finalStates)
    print("transitions: ", transitions)

if __name__ == '__main__':
    main()