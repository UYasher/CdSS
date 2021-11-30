from lark import Lark
import ortools
from ortools.sat.python import cp_model

"""
TODOS:
- Make the parser support css and introduction/constraint on the same line as css
- Make expressions inside constraints, not just variable == variable
- Make a function which takes a bunch of instruction and updates the model
- Run the model
- Use the output of the model to replace the variables
"""


def run_instruction(instruction, model):
    print(instruction.data)
    if instruction.data == "introduction":
        print(instruction)

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

for instruction in parse_tree.children:
    run_instruction(instruction, model)