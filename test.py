from compiler import parse, compile_to_css
import time


def parser_test(name):
    with open(f'tests/parser_tests/{name}.txt') as example:
        with open(f'tests/parser_tests/{name}_expected.txt') as expected:
            start_time = time.time()
            parse_tree = str(parse(example.read()).pretty())
            expected_tree = str(expected.read())
            assert remove_whitespace(parse_tree) == remove_whitespace(expected_tree), f"Failed parser test: {name}"
            print(f"{name} succeeded in {time.time() - start_time} seconds")


def compiler_test():
    with open('tests/cdss_examples/hw3.cdss', 'r') as f:
        css = compile_to_css(f.read())
        print(css)
        with open('tests/cdss_examples/hw3-oneline.cdss', 'r') as f2:
            assert compile_to_css(f2.read()) == css, f"Failed compiler test"


def remove_whitespace(string):
    return"".join(string.split())


if __name__ == "__main__":
    parser_test_names = [
        "css_only",
        "variables_only",
        "constraints_only",
        "combined"
    ]
    print("__ Parser Tests __")
    for name in parser_test_names:
        parser_test(name)

    print("__ Compiler Tests __")
    compiler_test()
