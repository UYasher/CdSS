from lark import Lark
import ortools
from ortools.sat.python import cp_model
import random, string

DEFAULT_MAX = 1000
DEFAULT_MIN = -DEFAULT_MAX


reif_names = {}

def rand_name(): # TODO: replace this with a more sensible naming scheme
    while True:
        s = "__" + "".join(random.choice(string.ascii_lowercase) for i in range(6))
        if s not in reif_names:
            reif_names[s] = True
            return s


def atom_insn(insn, model, state):
    if insn.data == "number":
        s = model.NewIntVar(DEFAULT_MIN, DEFAULT_MAX, f"NUM_{rand_name()}")
        model.Add(s == int(insn.children[0]))
        print(f"set {str(s)} to {int(insn.children[0])}")
        return s
    
    if insn.data == "neg":
        s = model.NewIntVar(DEFAULT_MIN, DEFAULT_MAX, f"NEG_{rand_name()}")
        model.Add(s == -atom_insn(insn.children[0], model, state))
        return s

    if insn.data == "var":
        name = str(insn.children[0].children[0])
        return state[name]

    if insn.data == "asum":
        return sum_insn(insn.children[0], model, state)

def prod_insn(insn, model, state):
    if insn.data == "punit":
        return atom_insn(insn.children[0], model, state)

    if insn.data == "mul":
        lhs = prod_insn(insn.children[0], model, state)
        rhs = atom_insn(insn.children[1], model, state)
        s = model.NewIntVar(DEFAULT_MIN, DEFAULT_MAX, f"MUL_{rand_name()}")
        model.Add(s == (lhs * rhs))
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

    if instruction.data == "introduction":
        name = str(instruction.children[0].children[0])
        state[name] = model.NewIntVar(DEFAULT_MIN, DEFAULT_MAX, name)

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


# TODO: Make the parser support css and introduction/constraint on the same line as css
grammar = """
start: instruction+
instruction: code | css
code:
    | "$" string -> introduction
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
$x1
$x2

#square1 {
    height: 
    v(x1),
    width: 
    v(x1)
}

#square2{
    height: 
    v(x2)
    width: 
    v(x2),
}

c(x1 == x2)
c(x1+ x1 * 5 <= (--x2))
"""

parser = Lark(grammar)

parse_tree = parser.parse(text)
model = cp_model.CpModel()
state = {}

for instruction in parse_tree.children:
    run_instruction(instruction, model, state)

values = solve_model(state)
values = False
if values:
    new_text = text
    for key, val in values.items():
        new_text = new_text.replace(f"v({key})", str(val))
        new_text = new_text.replace(f"${key}\n", "")

    #TODO: eliminate constraint expressions from output CSS
    
else:
    raise Exception("Unsolvable constraints")
