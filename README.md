LR(0) LOOK AHEAD OPTIMIZATION 

Overview
This project implements the construction of an LR(0) automaton, detects shift-reduce conflicts, and refines parsing decisions using a partition-based approach. The goal is to improve LR(0) parsing without using full LR(1) lookahead.


---

Components

1. Symbols
Symbols represent grammar elements.



Terminals: +, *, id, (, )

Non-terminals: E, T, F


Helper functions:

T(x): creates a terminal

N(x): creates a non-terminal



---

2. Productions
Productions represent grammar rules such as:



E → E + T

Each production has a head and a body.


---

3. LR(0) Items
An item is a production with a dot indicating parsing progress.



Example:
E → E . + T

Functions:

next(): returns the symbol after the dot

advance(): moves the dot forward

complete(): checks if the dot is at the end



---

LR(0) Automaton

1. Closure
Closure expands a set of items when a non-terminal appears after the dot by adding all its productions.



Example:
E → .T
T → .T * F
T → .F

Closure ensures all possible derivations are considered.


---

2. GOTO
Goto moves the dot over a symbol and generates a new state.



Example:
E → E . + T becomes E → E + . T


---

3. Build Process



Add augmented start production: S' → E $

Compute closure of the start item

Use goto to generate transitions

Repeat until all states are created



---

Conflict Detection

A shift-reduce conflict occurs when a state allows both shifting and reducing at the same time.

Example:
E → E + T .
T → T . * F

The parser cannot decide whether to shift or reduce.


---

Partition Refinement

Instead of using full LR(1) lookahead, terminals are grouped based on parser behavior.

Example:
{+, *} may result in shift
{id, (} may result in reduce

This grouping approximates lookahead.


---

Backward Propagation

If a state's partition changes, predecessor states must also be updated.

Reason: parsing decisions propagate backward through transitions.


---

Forward Merging

Tokens that result in the same parser action are merged into the same group to simplify partitions.


---

Action Function

Determines the parser action for a given token in a state:

S: Shift

R: Reduce

C: Conflict

N: No action



---

Example Grammar

E → E + T | T
T → T * F | F
F → (E) | id

This grammar is not LR(0), so conflicts occur.


---

Output

For each state, the program prints partitions of terminals showing how tokens are grouped based on behavior.

Example format:
State X: [{tokens...}, {tokens...}]


---

Key Concepts

Closure expands all possible derivations.
Goto moves the parser forward.
LR(0) lacks lookahead, leading to conflicts.


---

Why Partitioning

LR(0) has no lookahead.
LR(1) uses full lookahead.
This approach uses grouped tokens to approximate lookahead.


---

Comparison

LR(0): no lookahead, low precision
SLR: uses FOLLOW sets, medium precision
LR(1): exact lookahead, high precision
This approach: partition-based approximation, medium to high precision


---

Limitations

Not as precise as LR(1)

May merge tokens incorrectly

Some conflicts may remain unresolved



---

Summary

The program builds an LR(0) automaton, detects conflicts, and refines parsing decisions using partition refinement. This provides an approximation of LR(1) behavior without explicitly computing lookahead sets.
