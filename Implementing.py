from dataclasses import dataclass
from collections import defaultdict

# -----------------------------
# SYMBOLS
# -----------------------------
@dataclass(frozen=True)
class Symbol:
    name: str
    is_terminal: bool

    def __repr__(self):
        return self.name


def T(x): return Symbol(x, True)
def N(x): return Symbol(x, False)

EOF = T("$")

# -----------------------------
# PRODUCTIONS & ITEMS
# -----------------------------
@dataclass(frozen=True)
class Production:
    head: Symbol
    body: tuple

@dataclass(frozen=True)
class Item:
    prod: Production
    dot: int = 0

    def next(self):
        return self.prod.body[self.dot] if self.dot < len(self.prod.body) else None

    def complete(self):
        return self.dot >= len(self.prod.body)

    def advance(self):
        return Item(self.prod, self.dot + 1)


# -----------------------------
# LR(0) AUTOMATON
# -----------------------------
class LR0:
    def __init__(self, prods, start):
        self.prods = prods
        self.start = start
        self.states = []
        self.trans = {}
        self.build()

    def closure(self, items):
        res = set(items)
        changed = True
        while changed:
            changed = False
            for it in list(res):
                nxt = it.next()
                if nxt and not nxt.is_terminal:
                    for p in self.prods:
                        if p.head == nxt:
                            new = Item(p, 0)
                            if new not in res:
                                res.add(new)
                                changed = True
        return frozenset(res)

    def goto(self, state, sym):
        return self.closure({it.advance() for it in state if it.next() == sym})

    def build(self):
        start_prod = Production(N("S'"), (self.start, EOF))
        start_state = self.closure({Item(start_prod, 0)})

        self.states = [start_state]
        mp = {start_state: 0}
        q = [start_state]

        while q:
            s = q.pop()
            sid = mp[s]
            symbols = {it.next() for it in s if it.next()}

            for sym in symbols:
                nxt = self.goto(s, sym)
                if not nxt: continue
                if nxt not in mp:
                    mp[nxt] = len(self.states)
                    self.states.append(nxt)
                    q.append(nxt)
                self.trans[(sid, sym)] = mp[nxt]


# -----------------------------
# CONFLICT DETECTION
# -----------------------------
def detect_conflicts(lr):
    conflicts = {}

    for i, st in enumerate(lr.states):
        shift = {it.next() for it in st if it.next() and it.next().is_terminal}
        reduce = [it for it in st if it.complete()]

        if shift and reduce:
            conflicts[i] = shift

    return conflicts


# -----------------------------
# PARTITION
# -----------------------------
class Partition:
    def __init__(self, blocks):
        self.blocks = blocks

    def split(self, tokens):
        new = []
        changed = False
        for b in self.blocks:
            i = b & tokens
            o = b - tokens
            if i and o:
                new += [i, o]
                changed = True
            else:
                new.append(b)
        return Partition(new), changed


# -----------------------------
# BACKWARD
# -----------------------------
def backward(lr, parts):
    preds = defaultdict(list)
    for (s, sym), d in lr.trans.items():
        preds[d].append(s)

    changed = True
    while changed:
        changed = False
        for d in range(len(lr.states)):
            for s in preds[d]:
                for b in parts[d].blocks:
                    new, ch = parts[s].split(b)
                    if ch:
                        parts[s] = new
                        changed = True
    return parts


# -----------------------------
# ACTION
# -----------------------------
def action(state, token):
    shift = any(it.next() == token for it in state if it.next())
    reduce = any(it.complete() for it in state)

    if shift and reduce: return "C"
    if shift: return "S"
    if reduce: return "R"
    return "N"


# -----------------------------
# FORWARD
# -----------------------------
def forward(lr, parts):
    new_parts = {}

    for sid, p in parts.items():
        st = lr.states[sid]
        merged = []

        for b in p.blocks:
            done = False
            for i, ex in enumerate(merged):
                if all(action(st, x) == action(st, y) for x in b for y in ex):
                    merged[i] |= b
                    done = True
                    break
            if not done:
                merged.append(set(b))

        new_parts[sid] = Partition(merged)

    return new_parts


# -----------------------------
# DEMO
# -----------------------------
def demo():
    E = N("E"); T_ = N("T"); F = N("F")
    plus = T("+"); mul = T("*")
    lp = T("("); rp = T(")")
    id_ = T("id")

    terms = {plus, mul, lp, rp, id_, EOF}

    prods = [
        Production(E, (E, plus, T_)),
        Production(E, (T_,)),
        Production(T_, (T_, mul, F)),
        Production(T_, (F,)),
        Production(F, (lp, E, rp)),
        Production(F, (id_,))
    ]

    lr = LR0(prods, E)

    conflicts = detect_conflicts(lr)

    parts = {i: Partition([set(terms)]) for i in range(len(lr.states))}

    # seed
    for sid, toks in conflicts.items():
        parts[sid], _ = parts[sid].split(toks)

    # backward refine
    parts = backward(lr, parts)

    # forward merge
    parts = forward(lr, parts)

    # print
    print("\nFINAL PARTITIONS\n")
    for sid, p in parts.items():
        print(f"State {sid}: {p.blocks}")


if __name__ == "__main__":
    demo()
