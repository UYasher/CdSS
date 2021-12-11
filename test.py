from compiler import parse, compile_to_css


def parser_test(name):
    with open(f'tests/parser_tests/{name}.txt') as example:
        with open(f'tests/parser_tests/{name}_expected.txt') as expected:
            parse_tree = str(parse(example.read()).pretty())
            expected_tree = str(expected.read())
            assert remove_whitespace(parse_tree) == remove_whitespace(expected_tree), f"Failed parser test: {name}"


def compiler_test():
    with open('tests/cdss_examples/hw3.cdss', 'r') as f:
        print(compile_to_css(f.read()))


def remove_whitespace(string):
    return"".join(string.split())


if __name__ == "__main__":
    parser_test_names = [
        "css_only",
        "variables_only",
        "constraints_only",
        "combined"
    ]
    for name in parser_test_names:
        parser_test(name)

    compiler_test()