import compiler

with open('tests/neumorphism_example/neumorphic.cdss', 'r') as f:
    cdss = f.read()
    for i in range(0, 1000, 100):
        for j in range(0, 1000, 100):
            css = compiler.compile_to_css("".join([f"c({k} == {v})" for k, v in {"h": i, "w": j}.items()]) + cdss)
            print(css.replace("&", " "))

