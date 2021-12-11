import lark
from lark import Lark
from ortools.sat.python import cp_model
import random, string
from utilities import static_vars
import argparse
import time

DEFAULT_MAX = 1000000
DEFAULT_MIN = -1000000


def compile_to_css(cdss):
    parse_tree = parse(cdss)
    model = cp_model.CpModel()
    state = {}

    for instruction in parse_tree.children:
        run_instruction(instruction, model, state)

    values = solve_model(model, state)
    if values:
        return make_tree(parse_tree, values)
    else:
        raise Exception("Unsolvable constraints")


def parse(cdss):
    with open('grammar.lark', 'r') as grammar:
        parser = Lark(grammar.read())

        return parser.parse(cdss)


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


@static_vars(existing_names={})
def rand_name():
    while True:
        s = "__" + "".join(random.choice(string.ascii_lowercase) for i in range(6))
        if s not in rand_name.existing_names:
            rand_name.existing_names[s] = True
            return s


if __name__ == "__main__":
    arg_parser = argparse.ArgumentParser(description='Compile cdss files to css files')
    arg_parser.add_argument('input', help='the cdss file to compile')
    arg_parser.add_argument('--time', help='print out the time to parse and compile', action='store_true')
    args = arg_parser.parse_args()

    with open(args.input, 'r') as f:
        start_time = time.time()
        print(compile_to_css(f.read()))
        if args.time:
            print(f"/* {time.time() - start_time} seconds */")
