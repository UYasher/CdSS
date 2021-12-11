from lark import Lark
import ortools
from ortools.sat.python import cp_model
import random, string

DEFAULT_MAX = 1000000
DEFAULT_MIN = -1000000


reif_names = {}

def rand_name():
    while True:
        s = "__" + "".join(random.choice(string.ascii_lowercase) for i in range(6))
        if s not in reif_names:
            reif_names[s] = True
            return s


def atom_insn(insn, model, state):
    if insn.data == "number":
        return model.NewConstant(int(insn.children[0]))
    
    if insn.data == "neg":
        s = model.NewIntVar(DEFAULT_MIN, DEFAULT_MAX, f"NEG_{rand_name()}")
        model.Add(s == -atom_insn(insn.children[0], model, state))
        return s

    if insn.data == "var":
        name = str(insn.children[0].children[0])
        if name not in state:
            state[name] = model.NewIntVar(DEFAULT_MIN, DEFAULT_MAX, name)
        return state[name]

    if insn.data == "asum":
        return sum_insn(insn.children[0], model, state)

def prod_insn(insn, model, state):
    if insn.data == "punit":
        return atom_insn(insn.children[0], model, state)

    if insn.data == "mul":
        lhs = prod_insn(insn.children[0], model, state)
        rhs = atom_insn(insn.children[1], model, state)
        print(type(lhs), type(rhs))
        s = model.NewIntVar(DEFAULT_MIN, DEFAULT_MAX, f"MUL_{rand_name()}")
        model.AddMultiplicationEquality(s, [lhs, rhs])
#        model.Add((lhs * rhs) == s)
        return s

    if insn.data == "div":
        lhs = prod_insn(insn.children[0], model, state)
        rhs = atom_insn(insn.children[1], model, state)
        s = model.NewIntVar(DEFAULT_MIN, DEFAULT_MAX, f"DIV_{rand_name()}")
        model.Add(s == (lhs // rhs))
        return s



def sum_insn(insn, model, state):
    if insn.data == "unit":
        return prod_insn(insn.children[0], model, state)

    if insn.data == "add":
        lhs = sum_insn(insn.children[0], model, state)
        rhs = prod_insn(insn.children[1], model, state)
        s = model.NewIntVar(DEFAULT_MIN, DEFAULT_MAX, f"ADD_{rand_name()}")
        model.Add(s == (lhs + rhs))
        return s

    if insn.data == "sub":
        lhs = sum_insn(insn.children[0], model, state)
        rhs = prod_insn(insn.children[1], model, state)
        s = model.NewIntVar(DEFAULT_MIN, DEFAULT_MAX, f"SUB_{rand_name()}")
        model.Add(s == (lhs - rhs))
        return s

def run_instruction(instruction, model, state):
    if instruction.data == "instruction":
        for child in instruction.children:
            run_instruction(child, model, state)


    if instruction.data == "constraint":
        lhs = sum_insn(instruction.children[0].children[0], model, state)
        rhs = sum_insn(instruction.children[0].children[1], model, state)

        model.Add({
            "eq": lhs == rhs,
            "leq": lhs <= rhs,
            "geq": lhs >= rhs,
            "neq": lhs != rhs,
            "lt" : lhs < rhs,
            "gt" : lhs > rhs
        }[instruction.children[0].data])


def solve_model(state):
    solver = cp_model.CpSolver()
    if solver.Solve(model) == cp_model.OPTIMAL:
        values = {}
        for name in state:
            print(name)
            values[name] = solver.Value(state[name])
        return values

    return None


# TODO: Make the parser support css and constraint on the same line as css
grammar = """
start: instruction+
instruction: code | css
code:
    | "v(" string ")" -> variable
    | "c(" cmp ")" -> constraint

cmp:  sum "==" sum -> eq
    | sum "<=" sum -> leq
    | sum ">=" sum -> geq
    | sum "!=" sum -> neq
    | sum "<"  sum -> lt
    | sum ">" sum -> gt

sum:  product -> unit
    | sum "+" product -> add
    | sum "-" product -> sub

product:  atom -> punit
        | product "*" atom -> mul
        | product "//" atom -> div

atom:  NUMBER    -> number
     | "-" atom  -> neg
     | string    -> var
     | "(" sum ")" -> asum

string: /[a-zA-Z0-9_]+/
NUMBER: /[0-9]+/
css.-100: /.+/
%import common.WS
%ignore WS
"""

text = """
#square1 {
    height: 
    v(x),
    width: 
    v(x)
}

#square2{
    height: 
    v(y)
    width: 
    v(y),
    v(z),
    v(w)
}
c(0 <= x)c(0 <= y)
c(0 <= z)
c(x <= 10)
c(y <= 10)
c(z <= 10)

c(4*x+2*y+z >= 24)
c((x-y)*(x-y) <= 4)
c(w <= x)
c(w <= y)
c((w-y)*(w-x) == 0)
c(w == z*z)
"""
#c(x1 == x2)

parser = Lark(grammar)

parse_tree = parser.parse(text)
model = cp_model.CpModel()
state = {}

for instruction in parse_tree.children:
    run_instruction(instruction, model, state)

values = solve_model(state)
if values:
    new_text = text
    for key, val in values.items():
        new_text = new_text.replace(f"v({key})", str(val))
        new_text = new_text.replace(f"${key}\n", "")

    #TODO: eliminate constraint expressions from output CSS
    
else:
    raise Exception("Unsolvable constraints")
