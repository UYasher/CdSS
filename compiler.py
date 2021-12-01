from lark import Lark
import ortools
from ortools.sat.python import cp_model

"""
TODOS:
- Make the parser support css and introduction/constraint on the same line as css
- Make expressions inside constraints, not just variable == variable
- Run the model
- Use the output of the model to replace the variables
"""

DEFAULT_MAX = 999999
DEFAULT_MIN = -DEFAULT_MAX


def run_instruction(instruction, model, state):
    if instruction.data == "instruction":
        new_model = model
        for child in instruction.children:
            new_model = run_instruction(child, new_model, state)
        return new_model

    if instruction.data == "introduction":
        name = instruction.children[0].children[0]
        state[name] = model.NewIntVar(DEFAULT_MIN, DEFAULT_MAX, name)
        model.Add(name)
        return model

    if instruction.data == "constraint":
        name1 = instruction.children[0].children[1]
        name2 = instruction.children[1].children[0]


grammar = """
start: instruction+
instruction: introduction  | variable | constraint | css
introduction: "$" string
variable: "v(" string ")"
constraint:  "c(" string "==" string ")"
string: char+
char: ("a".."z")|("0".."9")
css: /.+/
%import common.WS
%ignore WS
"""

text = """
$v1
$v2

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
"""

parser = Lark(grammar)

parse_tree = parser.parse(text)
model = cp_model.CpModel()
state = {}

for instruction in parse_tree.children:
    run_instruction(instruction, model, {})