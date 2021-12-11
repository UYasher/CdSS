import lark
from lark import Lark
from ortools.sat.python import cp_model
import random, string

DEFAULT_MAX = 1000000
DEFAULT_MIN = -1000000


def static_vars(**kwargs):
    def decorate(func):
        for k in kwargs:
            setattr(func, k, kwargs[k])
        return func
    return decorate


@static_vars(existing_names={})
def rand_name():
    while True:
        s = "__" + "".join(random.choice(string.ascii_lowercase) for i in range(6))
        if s not in rand_name.existing_names:
            rand_name.existing_names[s] = True
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
        s = model.NewIntVar(DEFAULT_MIN, DEFAULT_MAX, f"MUL_{rand_name()}")
        model.AddMultiplicationEquality(s, [lhs, rhs])
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
            "lt": lhs < rhs,
            "gt": lhs > rhs
        }[instruction.children[0].data])


def solve_model(model, state):
    solver = cp_model.CpSolver()
    if solver.Solve(model) == cp_model.OPTIMAL:
        values = {}
        for name in state:
            values[name] = solver.Value(state[name])
        return values

    return None


def make_tree(node, values):
    if type(node) == lark.lexer.Token:
        return str(node)
    if node.data == "variable":
        return str(values[str(node.children[0].children[0])])
    if node.data == "constraint":
        return ""
    return "".join(make_tree(c, values) for c in node.children)


text = """
#square1 {
    height: v(x),
    width: v(x)
}

#square2 {
    height: v(y),
    width: v(y),
    v(z),
    v(w)
} c(0 <= x)c(0 <= y)
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


def compile_to_css(cdss):
    with open('grammar.lark', 'r') as grammar:
        parser = Lark(grammar.read())

        parse_tree = parser.parse(cdss)
        model = cp_model.CpModel()
        state = {}

        for instruction in parse_tree.children:
            run_instruction(instruction, model, state)

        values = solve_model(model, state)
        if values:
            return make_tree(parse_tree, values)
        else:
            raise Exception("Unsolvable constraints")


print(compile_to_css(text))
