from lark import Lark

"""
TODOS:
- Make the parser support css and introduction/constraint on the same line as css
- Make expressions inside constraints, not just varialbe == variable
- Make a function which takes a bunch of instruction and updates the model
- Run the model
- Use the output of the model to replace the 
"""

grammar = """
start: instruction+
instruction: introduction | constraint | css
introduction: "v(" string ")"
constraint:  "c(" string "==" string ")"
string: char+
char: ("a".."z")|("0".."9")
css: /.+/
%import common.WS
%ignore WS
"""

text = """
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

print(parser.parse(text).pretty())