import config_checker_and_tester

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

if __name__ == "__main__":
    print(config_checker_and_tester.CheckWordBetter(word="aab",new_automata=nfa))