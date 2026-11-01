"""Week 5: forward and backward chaining over one rule list (the classic animal identifier).

Forward chaining starts from what you observed and fires rules until nothing new follows.
Backward chaining starts from a guess ("is it a tiger?") and asks only the questions that
guess depends on. Both print the rules they used, so every answer comes with its reason.

Run:  python3 chaining.py          the test animals below, output also saved to outputs/run.txt
      python3 chaining.py --ask    think of an animal and answer the questions yourself
"""

import sys                  # sys.argv: the words typed after "python3 chaining.py"
from pathlib import Path    # Path: an easy way to build file paths and write files

# ---------------------------------------------------------------------------
# THE RULES (the knowledge). This is data, not code: the engine below never
# mentions any animal by name, so you could swap in rules about cars or classes
# and the same functions would still work.
#
# Each rule is a pair (tuple):  ( [list of conditions], conclusion )
# Read it as:  IF every condition is true  THEN the conclusion is true.
#
# Why a list of pairs and not a dict like {"mammal": ["has hair"]}?
# A dict key can only appear once, but "mammal" has TWO rules (hair OR milk).
# Two rules with the same conclusion = OR.  Several conditions in one rule = AND.
# ---------------------------------------------------------------------------
RULES = [
    (["has hair"], "mammal"),                                  # has hair -> mammal
    (["gives milk"], "mammal"),                                # OR gives milk -> mammal
    (["has feathers"], "bird"),
    (["flies", "lays eggs"], "bird"),                          # flies AND lays eggs -> bird
    (["mammal", "eats meat"], "carnivore"),                    # uses another rule's result: a chain
    (["mammal", "has pointed teeth", "has claws"], "carnivore"),
    (["mammal", "has hooves"], "ungulate"),                    # ungulate = hoofed animal
    (["carnivore", "tawny", "dark spots"], "cheetah"),         # tawny = sandy yellow-brown
    (["carnivore", "tawny", "black stripes"], "tiger"),
    (["ungulate", "long neck", "long legs", "dark spots"], "giraffe"),
    (["ungulate", "white", "black stripes"], "zebra"),
    (["bird", "can't fly", "long neck", "long legs"], "ostrich"),
    (["bird", "can't fly", "swims", "black and white"], "penguin"),
    (["bird", "flies well"], "albatross"),
]

# The final answers we are trying to reach. "mammal" or "carnivore" are steps
# along the way, not answers, so they are not in this list.
ANIMALS = ["cheetah", "tiger", "giraffe", "zebra", "ostrich", "penguin", "albatross"]

# Every word that appears on the RIGHT side of some rule can be worked out by the
# system ("mammal", "carnivore", "cheetah", ...). Anything else ("has hair",
# "tawny", ...) can never be worked out; it has to be observed, or asked.
# This line is a set comprehension: loop over every rule, ignore the conditions
# (the "_" means "don't care"), and keep each conclusion. A set drops duplicates,
# so "mammal" appears once even though two rules conclude it.
DERIVED = {conclusion for _, conclusion in RULES}

# Test cases: what a person would see when looking at each animal.
# The house cat is a trick case: no rule ends in "house cat", so the right answer
# is "I don't know". A good system should say that instead of guessing.
TESTS = {
    "cheetah": {"has hair", "eats meat", "tawny", "dark spots"},
    "zebra": {"gives milk", "has hooves", "white", "black stripes"},
    "penguin": {"has feathers", "can't fly", "swims", "black and white", "lays eggs"},
    "house cat (not in the rules)": {"has hair", "has pointed teeth", "has claws", "eats meat"},
}


# ---------------------------------------------------------------------------
# FORWARD CHAINING: facts -> conclusions.
# Start with what you observed. Go through the rules; whenever ALL of a rule's
# conditions are already known facts, add its conclusion as a new fact. New facts
# can unlock more rules, so repeat until a whole pass adds nothing new.
# ---------------------------------------------------------------------------
def forward(observed, log):
    facts = set(observed)          # copy, so we don't change the caller's set
    changed = True                 # "did the last pass add anything?" True to start the loop
    while changed:                 # keep making passes over the rules...
        changed = False            # ...until one pass adds nothing (then we stop)
        for conditions, conclusion in RULES:      # unpack each pair into its two parts
            # Fire the rule if: we don't already know the conclusion, AND
            # every one of its conditions is already a fact.
            # all(...) is True only if the check is True for every condition.
            if conclusion not in facts and all(c in facts for c in conditions):
                facts.add(conclusion)              # the new fact
                log(f"  {' + '.join(conditions)}  ->  {conclusion}")   # record WHY
                changed = True                     # something new, so do another pass
    # The answer: whichever animals ended up in the facts (usually 0 or 1).
    return [a for a in ANIMALS if a in facts]


# ---------------------------------------------------------------------------
# BACKWARD CHAINING: goal -> what would prove it.
# Start from a guess, e.g. "cheetah". Find a rule whose conclusion is "cheetah".
# To use it, each of its conditions must be true, so prove each condition the
# SAME way (this function calls itself: recursion). Eventually you reach a base
# fact like "has hair" that no rule concludes, and you just ask.
#
#   goal    the thing we're trying to prove right now, e.g. "carnivore"
#   ask     a function: ask("has hair") returns True/False (a test case or a person)
#   known   a dict of everything already decided, {"has hair": True, ...},
#           shared across all the calls so we never ask the same question twice
#   log     a function that prints/saves a line of the explanation
#   depth   how deep in the recursion we are; only used to indent the printout
# ---------------------------------------------------------------------------
def backward(goal, ask, known, log, depth=0):
    pad = "  " * (depth + 1)               # 2 spaces per level, so the output looks like a tree

    # 1. Already decided earlier? Reuse the answer (True or False).
    if goal in known:
        return known[goal]

    # 2. A base fact (no rule concludes it): nothing to reason about, so ask.
    if goal not in DERIVED:
        known[goal] = ask(goal)
        log(f"{pad}{goal}? {'yes' if known[goal] else 'no'}")
        return known[goal]

    # 3. Otherwise try every rule that concludes this goal (there may be several,
    #    e.g. two rules for "mammal"). If ANY one works, the goal is proven.
    for conditions, conclusion in RULES:
        if conclusion != goal:
            continue                       # not a rule for this goal, skip it
        log(f"{pad}{goal}: try IF {' + '.join(conditions)}")
        # Prove every condition, each by calling backward() on it (recursion).
        # all() stops at the first False, so once one condition fails we stop
        # asking about the rest of this rule: no wasted questions.
        if all(backward(c, ask, known, log, depth + 1) for c in conditions):
            log(f"{pad}{goal}: proven")
            known[goal] = True             # remember it, e.g. "mammal" is now known
            return True

    # 4. No rule worked, so the goal is false.
    log(f"{pad}{goal}: not proven")
    known[goal] = False
    return False


# Backward chaining needs a goal, so to identify an unknown animal, guess each
# animal in turn and try to prove it. The first one proven is the answer.
# "known" is shared across all the guesses, so if the cheetah guess already asked
# "has hair?", the tiger guess reuses that answer instead of asking again.
def identify_backward(ask, log):
    known = {}
    for animal in ANIMALS:
        log(f" goal: {animal}?")
        if backward(animal, ask, known, log):
            return animal, known
    return None, known                     # every guess failed: "I don't know"


# ---------------------------------------------------------------------------
# THE EXPERIMENT: run every test animal through both methods and compare.
# ---------------------------------------------------------------------------
def run_tests(log):
    # Every condition word that is not DERIVED is something you could be asked.
    # "-" on sets means "remove these"; sorted() turns the set into a sorted list.
    base_facts = sorted({c for conditions, _ in RULES for c in conditions} - DERIVED)
    log(f"{len(RULES)} rules, {len(base_facts)} observable features, {len(ANIMALS)} animals\n")

    for name, observed in TESTS.items():
        log(f"=== {name} ===")
        log(f"observed: {', '.join(sorted(observed))}")

        log("\nforward chaining:")
        found = forward(observed, log)
        log(f"  result: {', '.join(found) or 'unknown (no animal rule fired)'}")

        log("\nbackward chaining:")
        # The "ask" here is a stand-in for a person: a tiny function (a lambda)
        # that answers yes if the feature is in this test animal's observed set.
        animal, known = identify_backward(lambda f: f in observed, log)
        # The questions asked = base facts that ended up in "known".
        asked = [f for f in known if f not in DERIVED]
        log(f"  result: {animal or 'unknown (every animal goal failed)'}")
        log(f"  asked {len(asked)} of {len(base_facts)} possible questions\n")


def main():
    # Interactive mode: a real person answers the questions.
    if "--ask" in sys.argv:
        # input() shows the question and waits for typing; anything starting
        # with "y" counts as yes.
        ask = lambda f: input(f"  {f}? (y/n) ").strip().lower().startswith("y")
        animal, _ = identify_backward(ask, lambda s: None)    # a log that prints nothing
        print(f"It's a {animal}." if animal else "I can't identify that animal with these rules.")
        return

    # Test mode: run the experiment, print it, and save the same text to a file.
    out = Path(__file__).parent / "outputs" / "run.txt"     # week-5/outputs/run.txt
    out.parent.mkdir(exist_ok=True)                          # make outputs/ if missing
    lines = []
    def log(s):                # every line goes to the screen AND into the list
        print(s)
        lines.append(s)
    run_tests(log)
    out.write_text("\n".join(lines) + "\n")
    print(f"saved to {out}")


# This runs main() only when you run the file directly (not when another file imports it).
if __name__ == "__main__":
    main()
