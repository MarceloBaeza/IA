from constraint import *
"""problem = Problem()
problem.addVariable("a", [1,2,3])
problem.addVariable("b", [4,5,6])
problem.addConstraint(lambda a, b: a*2 == b,("a", "b"))
print problem.getSolutions()
print "\n"
problem.getSolutions()
problem = Problem()
problem.addVariables(["a", "b"], [1, 2, 3])
problem.addConstraint(AllDifferentConstraint())
print problem.getSolutions()"""
problem = Problem()
numpieces = 8
cols = range(numpieces)
rows = range(numpieces)
problem.addVariables(cols, rows)
for col1 in cols:
    for col2 in cols:
        if col1 < col2:
            problem.addConstraint(lambda row1, row2: row1 != row2,
                                  (col1, col2))
solutions = problem.getSolutions()
print solutions
