# CdSS: Constrained Style Sheets

## Quick Start
To compile a cdss file `input` to css, run the following command:
```bash
python compiler.py <input>
```
The output is written to `stdout`, so to write the output of a compiler to a file,
redirect the output, as so:
```bash
python compiler.py <input> > <output>
```
You can find an EBNF definition of the language's syntax in `grammar.lark`.
## Introduction
Constraint programming is a programming paradigm where the programmer
describes the parameters and solution to a problem, then the machine
computes an answer without being told the explicit steps to do so.
Prolog and miniKanren are examples of such languages.

Constraint programming can also be done in other langauges using
libraries. For example, Google's [OR-Tools.](https://developers.google.com/optimization)
enables constraint programming in Python, C++, C#, and Java. Indeed,
leveraging SAT solving, the solver used by OR-Tools is more efficient
than the solvers used in Prolog or miniKanren.

This project uses OR-Tools to bring some of the power of constraint programming to
front-end development -- in particular, CSS. By using constraint
programming in CSS, we can tell the computer what we would like
our designs to look like rather than specifying how to make them
look that way. You can think of this project (CdSS) as an
assembly language to use constraint programming in CSS. It
enables the creation of more powerful abstractions that bring
constraint programming to front-end development.
## The CdSS Spec
You can see a full spec for the grammar of CdSS in `grammar.lark`.
Briefly, there are three constructs:
1. **Variables.** These are variables whose values are injected into CSS code.
These are specified like so: `v(<variable name>)`. For example: `v(x)`.
2. **Constraints.** These tell the compiler what a solution (i.e. a good design) would look like.
Constraints are equalities or inequalities expressing the relationships between variables. For example: `c(x <= y + 4*z + y*z)`.
More generally, they are specified as `c(<LHS> <comparator> <RHS>)`
3. **CSS.** Just regular old CSS into which we inject values!

You can see example cdss files in `tests/cdss_examples`.

## The Compiler
Once you write a CdSS file, you can compile it using `python compiler.py <input>`. 
This gives you a CSS file where the constraints have been removed, and the variables
have been replaced with values specified by the constraints.

These constraints are solved by OR-Tools. First, we parse the CdSS using `lark`. Then,
the parse tree is converted into a model which can be used by OR-Tools. (`utilities.py`
provides utility functions which are helpful in this process.) Using Or-Tools,
we solve the model. Finally, we replace the nodes in the parse tree which used to be
variables with the values from the OR-Tools solution and make the tree into css.

## Tests
To help ensure the compiler works correctly, you can run `python test.py`. This file
uses `tests/parser_tests` to check that the parser correctly generates parse trees
by checking them against hand-generated parse trees. in `tests/parser_tests`, the
CdSS is provided in a file `<name>.txt` and the hand-generated tree is in the file 
`<name>_expected.txt`. Then, the compiler is tested using a simple constraint problem
with a known solution. Several variants of this problem are provided as `.cdss` files
in `tests/cdss_examples`.  

You can also see an example of how CdSS can be used to generate more interesting
abstractions. [Neumorphism](https://uxdesign.cc/neumorphism-in-user-interfaces-b47cef3bf3a6) is a style used in web design to make beautiful and subtle
websites. It makes heavy use of shadows and lighting, and how objects on the page interact
with shadows and light will depend on the size of the object. We can make styles for objects
of different sizes easily by specifying how the shadows should vary with the size of the
object. You can see an example of this by running:
`python generate.py > tests/neumorphism_example/neumorphic.css`

Now that you've seen CdSS in action, try it out in your projects, and use it to build
interesting abstractions!
