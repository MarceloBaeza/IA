from constraint import *
TAM=8
def print_solution(s, size):
		print len(s)
		for i in range(1, size-1):
			for j in range(1, size-1):
				print s[i*size+j],
			print

p1 = Problem()
print "Agregando variable"
for i in range(0,TAM):
	for j in range(0, TAM):
		p1.addVariable(i*TAM+j, [0,1])
p1.addConstraint(lambda var, val=0: var == val, (3*8+3,))

#add row sum constraint
row_constraint = [0, 4, 0, 2, 1, 2, 1, 0]

for row in range(0,TAM):
	p1.addConstraint(ExactSumConstraint(row_constraint[row]), [row*TAM+col for col in range(0,TAM)])

#add column constraint
#1st puzzle
col_constraint = [0, 1, 0, 4, 0, 3, 2, 0]

for col in range(0,TAM):
	p1.addConstraint(ExactSumConstraint(col_constraint[col]), [col+row*TAM for row in range(0,TAM)])

for i in range (0, TAM):
	for j in range (0, TAM):
		print 0,
	print row_constraint[i]
	print
for i in range (0, TAM):
	print col_constraint[i],
print

def attack_function(cell, up_left, up_right, down_left, down_right):
	if up_left==0 and up_left==0 and up_right==0 and down_left==0 and down_right==0:
		if cell == 1 or cell== 0:
			return 1
	else:
		if cell == 1:
			return 0
		else:
			return 1

for i in range(1,7):
	for j in range(1, 7):
		p1.addConstraint(attack_function, [i*8+j, (i-1)*8+(j-1), (i-1)*8+(j+1), (i+1)*8+(j-1), (i+1)*8+(j+1)])


def relation_fun(a,b):
	if b==0:
		if a=='W':
			return 1
		else:
			return 0
	else:
		if a=='W':
			return 0
		else:
			return 1

sol = p1.getSolution()

if not sol:
	print "no solution"
	exit()

#middle segment constraint
def middle_segment_constraint(cell, left, up, down, right):
	if((up=='U' and down=='D') or (right=='R' and left=='L')):
		if cell == 'M':
			return 1
		else:
			return 0
	else:
		if cell == 'M':
			return 0
		else:
			return 1

#left segment constraint
def left_segment_constraint(cell, left, up, down, right):
	if(left=='W' and up=='W' and down=='W' and (right=='M' or right=='R')):
		if cell == 'L':
			return 1
		else:
			return 0
	else:
		if cell == 'L':
			return 0
		else:
			return 1

#up segment constraint
def up_segment_constraint(cell, left, up, down, right):
	if(left=='W' and up=='W'and (down=='M' or down=='D') and right=='W'):
		if cell == 'U':
			return 1
		else:
			return 0
	else:
		if cell == 'U':
			return 0
		else:
			return 1

#down segment constraint
def down_segment_constraint(cell, left, up, down, right):
	if(left=='W' and (up=='M' or up=='U') and down=='W' and right=='W'):
		if cell == 'D':
			return 1
		else:
			return 0
	else:
		if cell == 'D':
			return 0
		else:
			return 1

#right segment constraint
def right_segment_constraint(cell, left, up, down, right):
	if((left=='M' or left=='L') and up=='W'and down=='W' and right=='W'):
		if cell == 'R':
			return 1
		else:
			return 0
	else:
		if cell == 'R':
			return 0
		else:
			return 1


#single segment constraint
def single_segment_constraint(cell, left, up, down, right):
	if(left=='W' and up=='W' and down=='W' and right=='W'):
		if cell=='S' or cell=='W':
			return 1
		else:
			return 0
	else:
		if cell == 'S':
			return 0
		else:
			return 1

p2 = Problem()

for i in range(0, 8):
	for j in range(0, 8):
		value = sol[i*8+j]
		if sol[i*8+j] == 0:
			p2.addVariable(i*8+j, ['W'])
		else:
			p2.addVariable(i*8+j, ['S', 'L', 'U', 'D', 'M', 'R'])
			if(i>=1 and i<=7 and j>=1 and j<=7):
				p2.addConstraint(single_segment_constraint, [i*8+j, (i)*8+(j-1), (i-1)*8+(j), (i+1)*8+(j), (i)*8+(j+1)])
				p2.addConstraint(left_segment_constraint, [i*8+j, (i)*8+(j-1), (i-1)*8+(j), (i+1)*8+(j), (i)*8+(j+1)])
				p2.addConstraint(up_segment_constraint, [i*8+j, (i)*8+(j-1), (i-1)*8+(j), (i+1)*8+(j), (i)*8+(j+1)])
				p2.addConstraint(down_segment_constraint, [i*8+j, (i)*8+(j-1), (i-1)*8+(j), (i+1)*8+(j), (i)*8+(j+1)])
				p2.addConstraint(right_segment_constraint, [i*8+j, (i)*8+(j-1), (i-1)*8+(j), (i+1)*8+(j), (i)*8+(j+1)])
				p2.addConstraint(middle_segment_constraint, [i*8+j, (i)*8+(j-1), (i-1)*8+(j), (i+1)*8+(j), (i)*8+(j+1)])

sol2 = p2.getSolution()


if sol2:
	print "S: Submarine, L: Left part, U: Upper part"
	print "D: Down Part, R: Right Part, M: Middle Part"
	print "W: Water"
	print_solution(sol2, 8)
else:
	print "no solution"
