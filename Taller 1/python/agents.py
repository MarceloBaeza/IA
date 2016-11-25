"""Implement Agents and Environments (Chapters 1-2).

The class hierarchies are as follows:

Object ## A physical object that can exist in an environment
    Agent
        Wumpus
        RandomAgent
        ReflexVacuumAgent
        ...
    Dirt
    Wall
    ...

Environment ## An environment holds objects, runs simulations
    XYEnvironment
        VacuumEnvironment
        WumpusEnvironment

EnvFrame ## A graphical representation of the Environment

"""

from utils import *
import random, copy

#______________________________________________________________________________

class Object:
    """This represents any physical object that can appear in an Environment.
    You subclass Object to get the objects you want.  Each object can have a
    .__name__  slot (used for output only)."""
    def __repr__(self):
        return '<%s>' % getattr(self, '__name__', self.__class__.__name__)

    def is_alive(self):
        """Objects that are 'alive' should return true."""
        return hasattr(self, 'alive') and self.alive

    def display(self, canvas, x, y):
        """Display an image of this Object on the canvas."""
        self.canvas.create_image()
        pass

class Agent(Object):
    """An Agent is a subclass of Object with one required slot,
    .program, which should hold a function that takes one argument, the
    percept, and returns an action. (What counts as a percept or action
    will depend on the specific environment in which the agent exists.)
    Note that 'program' is a slot, not a method.  If it were a method,
    then the program could 'cheat' and look at aspects of the agent.
    It's not supposed to do that: the program can only look at the
    percepts.  An agent program that needs a model of the world (and of
    the agent itself) will have to build and maintain its own model.
    There is an optional slots, .performance, which is a number giving
    the performance measure of the agent in its environment."""

    def __init__(self):
        def program(percept):
            return raw_input('Percept=%s; action? ' % percept)
        self.program = program
        self.alive = True

def TraceAgent(agent):
    """Wrap the agent's program to print its input and output. This will let
    you see what the agent is doing in the environment."""
    old_program = agent.program
    def new_program(percept):
        action = old_program(percept)
        print '%s perceives %s and does %s' % (agent, percept, action)
        return action
    agent.program = new_program
    return agent

#______________________________________________________________________________

class TableDrivenAgent(Agent):
    """This agent selects an action based on the percept sequence.
    It is practical only for tiny domains.
    To customize it you provide a table to the constructor. [Fig. 2.7]"""

    def __init__(self, table):
        "Supply as table a dictionary of all {percept_sequence:action} pairs."
        ## The agent program could in principle be a function, but because
        ## it needs to store state, we make it a callable instance of a class.
        Agent.__init__(self)
        percepts = []
        def program(percept):
            percepts.append(percept)
            action = table.get(tuple(percepts))
            return action
        self.program = program


class RandomAgent(Agent):
    "An agent that chooses an action at random, ignoring all percepts."
    def __init__(self, actions):
        Agent.__init__(self)
        self.program = lambda percept: random.choice(actions)


#______________________________________________________________________________

loc_A, loc_B = (0, 0), (1, 0) # The two locations for the Vacuum world

class ReflexVacuumAgent(Agent):
    "A reflex agent for the two-state vacuum environment. [Fig. 2.8]"

    def __init__(self):
        Agent.__init__(self)
        def program((location, status)):
            if status == 'Dirty': return 'Suck'
            elif location == loc_A: return 'Right'
            elif location == loc_B: return 'Left'
        self.program = program


def RandomVacuumAgent():
    "Randomly choose one of the actions from the vaccum environment."
    return RandomAgent(['Right', 'Left', 'Suck', 'NoOp'])


def TableDrivenVacuumAgent():
    "[Fig. 2.3]"
    table = {((loc_A, 'Clean'),): 'Right',
             ((loc_A, 'Dirty'),): 'Suck',
             ((loc_B, 'Clean'),): 'Left',
             ((loc_B, 'Dirty'),): 'Suck',
             ((loc_A, 'Clean'), (loc_A, 'Clean')): 'Right',
             ((loc_A, 'Clean'), (loc_A, 'Dirty')): 'Suck',
             # ...
             ((loc_A, 'Clean'), (loc_A, 'Clean'), (loc_A, 'Clean')): 'Right',
             ((loc_A, 'Clean'), (loc_A, 'Clean'), (loc_A, 'Dirty')): 'Suck',
             # ...
             }
    return TableDrivenAgent(table)


class ModelBasedVacuumAgent(Agent):
    "An agent that keeps track of what locations are clean or dirty."
    def __init__(self):
        Agent.__init__(self)
        model = {loc_A: None, loc_B: None}
        def program((location, status)):
            "Same as ReflexVacuumAgent, except if everything is clean, do NoOp"
            model[location] = status ## Update the model here
            if model[loc_A] == model[loc_B] == 'Clean': return 'NoOp'
            elif status == 'Dirty': return 'Suck'
            elif location == loc_A: return 'Right'
            elif location == loc_B: return 'Left'
        self.program = program

#______________________________________________________________________________

class Environment:
    """Abstract class representing an Environment.  'Real' Environment classes
    inherit from this. Your Environment will typically need to implement:
        percept:           Define the percept that an agent sees.
        execute_action:    Define the effects of executing an action.
                           Also update the agent.performance slot.
    The environment keeps a list of .objects and .agents (which is a subset
    of .objects). Each agent has a .performance slot, initialized to 0.
    Each object has a .location slot, even though some environments may not
    need this."""

    def __init__(self,):
        self.objects = []; self.agents = []

    object_classes = [] ## List of classes that can go into environment

    def percept(self, agent):
        "Return the percept that the agent sees at this point. Override this."
        abstract

    def execute_action(self, agent, action):
        "Change the world to reflect this action. Override this."
        abstract

    def default_location(self, object):
        "Default location to place a new object with unspecified location."
        return None

    def exogenous_change(self):
    	"If there is spontaneous change in the world, override this."
    	pass

    def is_done(self):
        "By default, we're done when we can't find a live agent."
        for agent in self.agents:
            if agent.is_alive(): return False
        return True

    def step(self):
    	"""Run the environment for one time step. If the
    	actions and exogenous changes are independent, this method will
    	do.  If there are interactions between them, you'll need to
    	override this method."""
    	if not self.is_done():
                actions = [agent.program(self.percept(agent))for agent in self.agents]
                for (agent, action) in zip(self.agents, actions):
    		              self.execute_action(agent, action)
                self.exogenous_change()

    def run(self, steps=1000):
	"""Run the Environment for given number of time steps."""
    	for step in range(steps):
                if self.is_done():
                    return self.step()

    def add_object(self, object, location=None):
    	"""Add an object to the environment, setting its location. Also keep
    	track of objects that are agents.  Shouldn't need to override this."""
    	object.location = location or self.default_location(object)
    	self.objects.append(object)
    	if isinstance(object, Agent):
                object.performance = 0
                self.agents.append(object)
    	return self


class XYEnvironment(Environment):
    """This class is for environments on a 2D plane, with locations
    labelled by (x, y) points, either discrete or continuous.  Agents
    perceive objects within a radius.  Each agent in the environment
    has a .location slot which should be a location such as (0, 1),
    and a .holding slot, which should be a list of objects that are
    held """

    def __init__(self, width=10, height=10):
        update(self, objects=[], agents=[], width=width, height=height)

    def objects_at(self, location):
        "Return all objects exactly at a given location."
        return [obj for obj in self.objects if obj.location == location]

    def objects_near(self, location, radius):
        "Return all objects within radius of location."
        radius2 = radius * radius
        return [obj for obj in self.objects
                if distance2(location, obj.location) <= radius2]

    def percept(self, agent):
        "By default, agent perceives objects within radius r."
        return [self.object_percept(obj, agent)
                for obj in self.objects_near(agent)]

    def execute_action(self, agent, action):
        if action == 'TurnRight':
            agent.heading = turn_heading(agent.heading, -1)
        elif action == 'TurnLeft':
            agent.heading = turn_heading(agent.heading, +1)
        elif action == 'Forward':
            self.move_to(agent, vector_add(agent.heading, agent.location))
        elif action == 'Grab':
            objs = [obj for obj in self.objects_at(agent.location)
                    if obj.is_grabable(agent)]
            if objs:
                agent.holding.append(objs[0])
        elif action == 'Release':
            if agent.holding:
                agent.holding.pop()
        agent.bump = False

    def object_percept(self, obj, agent): #??? Should go to object?
        "Return the percept for this object."
        return obj.__class__.__name__

    def default_location(self, object):
        return (random.choice(self.width), random.choice(self.height))

    def move_to(object, destination):
        "Move an object to a new location."

    def add_object(self, object, location=(1, 1)):
        Environment.add_object(self, object, location)
        object.holding = []
        object.held = None
        self.objects.append(object)

    def add_walls(self):
        "Put walls around the entire perimeter of the grid."
        for x in range(self.width):
            self.add_object(Wall(), (x, 0))
            self.add_object(Wall(), (x, self.height-1))
        for y in range(self.height):
            self.add_object(Wall(), (0, y))
            self.add_object(Wall(), (self.width-1, y))

def turn_heading(self, heading, inc,
                 headings=[(1, 0), (0, 1), (-1, 0), (0, -1)]):
    "Return the heading to the left (inc=+1) or right (inc=-1) in headings."
    return headings[(headings.index(heading) + inc) % len(headings)]

#______________________________________________________________________________
## Vacuum environment

class TrivialVacuumEnvironment(Environment):
    """This environment has two locations, A and B. Each can be Dirty or Clean.
    The agent perceives its location and the location's status. This serves as
    an example of how to implement a simple Environment."""

    def __init__(self):
        Environment.__init__(self)
        self.status = {loc_A:random.choice(['Clean', 'Dirty']),
                       loc_B:random.choice(['Clean', 'Dirty'])}

    def percept(self, agent):
        "Returns the agent's location, and the location status (Dirty/Clean)."
        return (agent.location, self.status[agent.location])

    def execute_action(self, agent, action):
        """Change agent's location and/or location's status; track performance.
        Score 10 for each dirt cleaned; -1 for each move."""
        if action == 'Right':
            agent.location = loc_B
            agent.performance -= 1
        elif action == 'Left':
            agent.location = loc_A
            agent.performance -= 1
        elif action == 'Suck':
            if self.status[agent.location] == 'Dirty':
                agent.performance += 10
            self.status[agent.location] = 'Clean'

    def default_location(self, object):
        "Agents start in either location at random."
        return random.choice([loc_A, loc_B])

class Dirt(Object): pass
class Wall(Object): pass

class VacuumEnvironment(XYEnvironment):
    """The environment of [Ex. 2.12]. Agent perceives dirty or clean,
    and bump (into obstacle) or not; 2D discrete world of unknown size;
    performance measure is 100 for each dirt cleaned, and -1 for
    each turn taken."""
    def __init__(self, width=10, height=10):
        XYEnvironment.__init__(self, width, height)
        self.add_walls()

    object_classes = [Wall, Dirt, ReflexVacuumAgent, RandomVacuumAgent,
                      TableDrivenVacuumAgent, ModelBasedVacuumAgent]

    def percept(self, agent):
        """The percept is a tuple of ('Dirty' or 'Clean', 'Bump' or 'None').
        Unlike the TrivialVacuumEnvironment, location is NOT perceived."""
        status =  if_(self.find_at(Dirt, agent.location), 'Dirty', 'Clean')
        bump = if_(agent.bump, 'Bump', 'None')
        return (status, bump)

    def execute_action(self, agent, action):
        if action == 'Suck':
            if self.find_at(Dirt, agent.location):
                agent.performance += 100
        agent.performance -= 1
        XYEnvironment.execute_action(self, agent, action)

#______________________________________________________________________________

class SimpleReflexAgent(Agent):
    """This agent takes action based solely on the percept. [Fig. 2.13]"""

    def __init__(self, rules, interpret_input):
        Agent.__init__(self)
        def program(percept):
            state = interpret_input(percept)
            rule = rule_match(state, rules)
            action = rule.action
            return action
        self.program = program

class ReflexAgentWithState(Agent):
    """This agent takes action based on the percept and state. [Fig. 2.16]"""

    def __init__(self, rules, udpate_state):
        Agent.__init__(self)
        state, action = None, None
        def program(percept):
            state = update_state(state, action, percept)
            rule = rule_match(state, rules)
            action = rule.action
            return action
        self.program = program

#______________________________________________________________________________
## The Wumpus World

class Gold(Object): pass
class Pit(Object): pass
class Arrow(Object): pass
class Wumpus(Agent): pass
class Explorer(Agent): pass
class WumpusEnvironment(XYEnvironment):
    object_classes = [Wall, Gold, Pit, Arrow, Wumpus, Explorer]
    def __init__(self, width=10, height=10):
        XYEnvironment.__init__(self, width, height)
        self.add_walls()
    ## Needs a lot of work ...


#______________________________________________________________________________

def compare_agents(EnvFactory, AgentFactories, n=10, steps=1000):
    """See how well each of several agents do in n instances of an environment.
    Pass in a factory (constructor) for environments, and several for agents.
    Create n instances of the environment, and run each agent in copies of
    each one for steps. Return a list of (agent, average-score) tuples."""
    envs = [EnvFactory() for i in range(n)]
    return [(A, test_agent(A, steps, copy.deepcopy(envs)))
            for A in AgentFactories]

def test_agent(AgentFactory, steps, envs):
    "Return the mean score of running an agent in each of the envs, for steps"
    total = 0
    for env in envs:
        agent = AgentFactory()
        env.add_object(agent)
        env.run(steps)
        total += agent.performance
    return float(total)/len(envs)

#______________________________________________________________________________

#______________________________________________________________________________
# GUI - Graphical User Interface for Environments
# If you do not have Tkinter installed, either get a new installation of Python
# (Tkinter is standard in all new releases), or delete the rest of this file
# and muddle through without a GUI.


import Tkinter as tk
from Tkinter import *
import time
class EnvFrame(tk.Frame):
    def __init__(self, env, title='AIMA GUI', cellwidth=50, n=10):
        update(self, cellwidth = cellwidth, running=False, delay=1.0)
        self.n = n
        self.running = 0
        self.delay = 1.0
        self.env = env
        tk.Frame.__init__(self, None, width=(cellwidth+2)*n, height=(cellwidth+2)*n)
        #self.title(title)
        # Toolbar
        toolbar = tk.Frame(self, relief='raised', bd=2)
        toolbar.pack(side='top', fill='x')
        for txt, cmd in [('Step >', self.env.step), ('Run >>', self.run),
                         ('Stop [ ]', self.stop)]:
            tk.Button(toolbar, text=txt, command=cmd).pack(side='left')
        tk.Label(toolbar, text='Delay').pack(side='left')
        scale = tk.Scale(toolbar, orient='h', from_=0.0, to=10, resolution=0.5,
                         command=lambda d: setattr(self, 'delay', d))
        scale.set(self.delay)
        scale.pack(side='left')
        # Canvas for drawing on
        self.canvas = tk.Canvas(self, width=(cellwidth+1)*n,
                                height=(cellwidth+1)*n, background="white")
        self.canvas.bind('<Button-1>', self.left) ## What should this do?
        self.canvas.bind('<Button-2>', self.edit_objects)
        self.canvas.bind('<Button-3>', self.add_object)
        if cellwidth:
            c = self.canvas
            for i in range(1, n+1):
                c.create_line(0, i*cellwidth, n*cellwidth, i*cellwidth)
                c.create_line(i*cellwidth, 0, i*cellwidth, n*cellwidth)
                c.pack(expand=1, fill='both')
        self.pack()

    def background_run(self):
        if self.running:
            self.env.step()
            ms = int(1000 * max(float(self.delay), 0.5))
            self.after(ms, self.background_run)

    def run(self):
        print 'run'
        self.running = 1
        self.background_run()

    def stop(self):
        print 'stop'
        self.running = 0

    def left(self, event):
        print 'left at ', event.x/50, event.y/50

    def edit_objects(self, event):
        """Choose an object within radius and edit its fields."""
        pass

    def add_object(self, event):
        c = self.canvas
        ## This is supposed to pop up a menu of Object classes; you choose the one
        ## You want to put in this square.  Not working yet.
        menu = tk.Menu(self, title='Edit (%d, %d)' % (event.x/50, event.y/50))
        for (txt, cmd) in [('Wumpus', self.run), ('Pit', self.run)]:
            menu.add_command(label=txt, command=cmd)
        menu.tk_popup(event.x + self.winfo_rootx(),
                      event.y + self.winfo_rooty())

        image=PhotoImage(file="../Imagenes/oie_transparent_converted.pgm")
        self.images = []
        self.images.append(image)
        c.create_image(100,10,anchor=NW,image=image)#posicione x,y

class Hereda_fram(EnvFrame,object):
    def __init__(self, env, title='AIMA GUI', cellwidth=50, n=10):
        update(self, cellwidth = cellwidth, running=False, delay=1.0)
        self.n = n
        self.running = 0
        self.delay = 1.0
        self.env = env
        tk.Frame.__init__(self, None, width=(cellwidth+2)*n, height=(cellwidth+2)*n)
        # Toolbar
        toolbar = tk.Frame(self, relief='raised', bd=2)
        toolbar.pack(side='top', fill='x')
        for txt, cmd in [('Step >', self.env.step), ('Run >>', self.run),('Stop [ ]', self.stop)]:
            tk.Button(toolbar, text=txt, command=cmd).pack(side='left')
        tk.Label(toolbar, text='Delay').pack(side='left')
        scale = tk.Scale(toolbar, orient='h', from_=0.0, to=10, resolution=0.5,
                         command=lambda d: setattr(self, 'delay', d))
        scale.set(self.delay)
        scale.pack(side='left')
        # Canvas for drawing on
        self.canvas = tk.Canvas(self, width=(cellwidth+1)*n,height=(cellwidth+1)*n, background="white")
        self.canvas.bind('<Button-1>', self.left) ## What should this do?
        self.canvas.bind('<Button-2>', self.edit_objects)
        self.canvas.bind('<Button-3>', self.add_objecto)
        if cellwidth:
            c = self.canvas
            for i in range(1, n+1):
                c.create_line(0, i*cellwidth, n*cellwidth, i*cellwidth)
                c.create_line(i*cellwidth, 0, i*cellwidth, n*cellwidth)
                c.pack(expand=1, fill='both')

        self.pack()
        self.add_object_panel()
    def background_run(self):
        if self.running:
            self.env.step()
            ms = int(1000 * max(float(self.delay), 0.5))
            self.move_object()
            self.after(ms, self.background_run)
    def run(self):
        print 'run'
        self.running = 1
        self.background_run()
    def stop(self):
        print 'stop'
        self.running = 0
    def left(self, event):
        print 'left at ', event.x/50, event.y/50
    def edit_objects(self, event):
        """Choose an object within radius and edit its fields."""
        pass
    def move_object(self):
        c=self.canvas
        a=0
        for i in self.env.observers:
            difx =  i.location[0] - self.obser[a][0]
            dify = i.location[1] - self.obser[a][1]
            for i1 in range (50):
                c.move(self.img[a], difx,0)
                c.update()
                time.sleep(1/2)
            for i1 in range (50):
                c.move(self.img[a], 0,dify)
                c.update()
                time.sleep(1/2)
            self.obser[a]=(i.location[0],i.location[1])
            #c.update()
            a+=1
    def add_object_panel(self):
        c=self.canvas
        self.img=[]
        self.obser=[]
        image=PhotoImage(file ="../Imagenes/Agent.pgm")
        a=0
        for i in self.env.observers:
            self.obser.append((i.location[0],i.location[1]))
            val=c.create_image(50*i.location[0],50*i.location[1]+10,anchor=NW,image=image)#posicione x,y
            self.img.append(val)
            a+=1
        c.mainloop();
    def add_objecto(self,event):
        menu = tk.Menu(self, title='Edit (%d, %d)' % (event.x/50, event.y/50))
        for (txt, cmd) in [('Wumpus', self.run), ('Pit', self.run)]:
            menu.add_command(label=txt, command=cmd)
        menu.tk_popup(event.x + self.winfo_rootx(),
                      event.y + self.winfo_rooty())

class Ambiente_Birds(XYEnvironment,object,tk.Frame):
    def __init__(self):
        super(Ambiente_Birds, self).__init__()
        update(self, observers=[])
        self.flock=[]
    def step(self):
        for obs in self.observers:
            val=True
            for g in self.flock:
                for g1 in g:
                    if g1.name==obs.name:
                        val=False
            if val==True:
                obs.actions(self)
        for obs in self.flock:
            obs[0].actions(self);
    def run(self):
        for i in range (1000):
            self.step()
    def execute_action(self, agent, action,direction):
        if action =='explore':
            val=self.move_to(agent,direction)
            return val
        if action=="movetogroup":
            self.movetogroup(agent,action,direction)
    def movetogroup(self,agent,action,direction):

        if direction=="right":
            """Check size of environment"""
            if(agent.location[1]+1<=self.width-1):
                if self.checkig_bird(direction,agent)==True:
                    agent.location=(agent.location[0],agent.location[1]+1)
        if direction=="left":
            if(agent.location[1]-1>=0):
                if self.checkig_bird(direction,agent)==True:
                    agent.location=(agent.location[0],agent.location[1]-1)
        if direction=="up":
            if(agent.location[0]-1>=0):
                if self.checkig_bird(direction,agent)==True:
                    agent.location=(agent.location[0]-1,agent.location[1])
        if direction=="down":
            if(agent.location[0]+1<=self.height-1):
                if self.checkig_bird(direction,agent)==True:
                    agent.location=(agent.location[0]+1,agent.location[1])
    def checking(self,bird):#checkeando si hay que moverse hacia un grupo o explorar....
        val=" "
        for obs in self.observers:
            if obs.name!=bird.name:
                dist=abs(bird.location[0]-obs.location[0])+abs(bird.location[1]-obs.location[1])
                if dist==2:#indica si esta en el rango, para acercase
                    val="movetogroup"
                    break
                if dist<2:#indica que esta en el rango para unirse o crear un grupo
                    val="joint"
                    break
        if val==" ":
            return "explore"
        else:
            return val
    def checkig_bird(self,direction,bird):#para saber si existe un bird al rededor
        val=True
        if direction=="right":
            for obs in self.observers:
                if bird.name==obs.name: continue
                if bird.location[1]+1==obs.location[1] and bird.location[0]==obs.location[0]:
                    val=False
        if direction=="left":
            for obs in self.observers:
                if bird.name==obs.name: continue
                if bird.location[1]-1==obs.location[1] and bird.location[0]==obs.location[0]:
                    val=False
        if direction=="up":
            for obs in self.observers:
                if bird.name==obs.name: continue
                if bird.location[0]-1==obs.location[0] and bird.location[1]==obs.location[1]:
                    val=False
        if direction=="down":
            for obs in self.observers:
                if bird.name==obs.name: continue
                if bird.location[0]+1==obs.location[0] and bird.location[1]==obs.location[1]:
                    val=False
        return val
    def search_location_flock(self,bird):#recorrer una lista de grupos y recorrer los grupos
        x=-1
        y=-1
        dis_t=999
        for f1 in self.flock:
            for f in f1:
                if bird.name==f.name: continue
                dist=abs(bird.location[0]-f.location[0])+abs(bird.location[1]-f.location[1])
                if dist < dis_t:
                    x=f.location[0]
                    y=f.location[1]
                    dis_t=dist
        return (x,y)
    def move_to(self, thing, direction):
        if direction=="right":
            """Check size of environment"""
            if(thing.location[1]+1<=self.width-1):
                if self.checkig_bird(direction,thing)==True:
                    thing.location=(thing.location[0],thing.location[1]+1)
                    return True
        if direction=="left":
            #print thing.location
            if(thing.location[1]-1>=0):
                #print thing.location
                if self.checkig_bird(direction,thing)==True:
                    thing.location=(thing.location[0],thing.location[1]-1)
                    #print thing.location
                    return True
        if direction=="up":
            #print thing.location
            if(thing.location[0]-1>=0):
                #print thing.location
                if self.checkig_bird(direction,thing)==True:
                    thing.location=(thing.location[0]-1,thing.location[1])
                    #print thing.location
                    return True
        if direction=="down":
            #print thing.location
            if(thing.location[0]+1<=self.height-1):
                #print thing.location
                if self.checkig_bird(direction,thing)==True:
                    thing.location=(thing.location[0]+1,thing.location[1])
                    #print thing.location
                    return True

        return False
    def add_thing(self, thing):
        #return all things in the location
        while True:
            val=False
            location=(random.randint(0,9),random.randint(0,9))
            for obs in self.observers:
                if obs.location==location:
                    val=True
            if val==False:
                break
        Environment.add_object(self, thing, location)
        thing.holding = []
        thing.held = None

        self.observers.append(thing)
    def joinGroup(self,bird):
        dis_t=999
        for f1 in self.flock:
            for f in f1:
                if bird.name==f.name: continue
                dist=abs(bird.location[0]-f.location[0])+abs(bird.location[1]-f.location[1])
                if dist < dis_t:
                    dis_t=dist
                    group=f1
        return group
    def makeGroup(self,thing):
        dis=9999
        obj=thing
        for obs in self.observers:
            if thing.name==obs.name: continue
            dist=abs(thing.location[0]-obs.location[0])+abs(thing.location[1]-obs.location[1])
            if dist < dis:
                obj=obs
        return obj
    def move_group(self,group,direction):
        cambio =True
        if direction=="right":
            for i in group:
                if (i.location[1]+1) > self.width-1:
                    cambio=False
            if cambio==False:
                return cambio
            else:
                for i in group:
                    i.location=(i.location[0],i.location[1]+1)
                """for obs in group:
                    print obs.location"""
                return cambio
        if direction=="left":
            for i in group:
                if (i.location[1]-1) < 0:
                    cambio=False
            if cambio==False:
                return cambio
            else:
                for i in group:
                    i.location=(i.location[0],i.location[1]-1)
                """for obs in group:
                    print obs.location"""
                return cambio
        if direction=="up":
            for i in group:
                if (i.location[0]-1) < 0:
                    cambio=False
            if cambio==False:
                return cambio
            else:
                for i in group:
                    i.location=(i.location[0]-1,i.location[1])
                """for obs in group:
                    print obs.location"""
                return cambio
        if direction=="down":
            for i in group:
                if (i.location[0]+1) > self.height-1:
                    cambio=False
            if cambio==False:
                return cambio
            else:
                for i in group:
                    i.location=(i.location[0]+1,i.location[1])
                """for obs in group:
                    print obs.location"""
                return cambio
class Bird(Agent,object):
    def __init__(self,id):
        super(Bird,self).__init__()
        self.name="Bird "+str(id)
    def explore (self,env,action,direction):
        val=env.execute_action(self,action ,direction)
        return val
    def move_gruop (self,env,action,direction):
        env.execute_action(self,action,direction)
    def make_group (self,env):#unir un bird cuando no existen grupos...
        group=[]
        obj=env.makeGroup(self)
        group.append(self)
        group.append(obj)
        env.flock.append(group)
    def comprobar_group(self,env): #comprobar si esta en un grupo..
        val=False
        for f in env.flock:
            for f1 in f:
                if f1.name==self.name:
                    val=True
        return val
    def join_group(self,env): #unir al grupo...
        group=[]
        for i in env.flock:
            for i1 in i:
                if self.name==i1.name: continue
                dist=abs(i1.location[0]-self.location[0])+abs(i1.location[1]-self.location[1])
                if dist<2:
                    group=i
        group.append(self)
    def group_pertenencia(self,env):
        for f in env.flock:
            for f1 in f:
                if f1.name==self.name:
                    val=f
        return val
    def group_move(self,group,env,direction):
        return env.move_group(group,direction)
    def actions(self,env):
        if len(env.flock)==0: #si el grupo esta vacio...
            action=env.checking(self)
            if action=="movetogroup":#se mueve en direccion al grupo, que pasa si no hay grupo.....
                direction=env.search_location_flock(self)
                if abs(self.location[0]-direction[0]) < abs(self.location[1]-direction[1]):#verificamos hacia donde es mejor, movimiento horizontal o vertical
                    if self.location[0]-direction[0] < 0: #si hay que subir o bajar
                        self.explore(env,"movetogroup","up")
                    else:
                        self.explore(env,"movetogroup","down")
                else:
                    if self.location[1]-direction[1] < 0: #si hay que ir a la derecha o izquierda.
                        self.explore(env,"movetogroup","left")
                    else:
                        self.explore(env,"movetogroup","right")
                self.join_group(env)
            elif action=="joint":#Crear un grupo...
                self.make_group(env)
            elif action =="explore":#solo explora
                val=random.randint(1,4)
                if val==1:
                    viaje=self.explore(env,"explore","right")#obtener si es posible el movimiento
                    if viaje==False:
                        self.actions(env)
                if val==2:
                    viaje=self.explore(env,"explore","left")
                    if viaje==False:
                        self.actions(env)
                if val==3:
                    viaje=self.explore(env,"explore","up")
                    if viaje==False:
                        self.actions(env)
                if val==4:
                    viaje=self.explore(env,"explore","down")
                    if viaje==False:
                        self.actions(env)
        else:
            if self.comprobar_group(env)==True: #esta en un grupo....
                group=self.group_pertenencia(env)#obtengo el grupo a que pertence
                val=random.randint(1,4)
                print val
                if val==1:
                    viaje=self.group_move(group,env,"right")#obtener si es posible el movimiento
                    if viaje==False:
                        self.actions(env)
                if val==2:
                    viaje=self.group_move(group,env,"left")
                    if viaje==False:
                        self.actions(env)
                if val==3:
                    viaje=self.group_move(group,env,"up")
                    if viaje==False:
                        self.actions(env)
                if val==4:
                    viaje=self.group_move(group,env,"down")
                    if viaje==False:
                        self.actions(env)

            else: #si no esta en grupo
                action=env.checking(self)
                if action=="movetogroup":#se mueve en direccion al grupo, que pasa si no hay grupo.....
                    direction=env.search_location_flock(self)
                    if abs(self.location[0]-direction[0]) < abs(self.location[1]-direction[1]):#verificamos hacia donde es mejor, movimiento horizontal o vertical
                        if self.location[0]-direction[0] < 0: #si hay que subir o bajar
                            self.move_gruop(env,"movetogroup","up")
                        else:
                            self.move_gruop(env,"movetogroup","down")
                    else:
                        if self.location[1]-direction[1] < 0: #si hay que ir a la derecha o izquierda.
                            self.move_gruop(env,"movetogroup","left")
                        else:
                            self.move_gruop(env,"movetogroup","right")
                    #self.join_group(env)
                elif action=="joint":#Unirse a group...
                    self.join_group(env)
                elif action =="explore":#solo explora
                    val=random.randint(1,4)
                    if val==1:
                        viaje=self.explore(env,"explore","right")#obtener si es posible el movimiento
                        if viaje==False:
                            self.actions(env)
                    if val==2:
                        viaje=self.explore(env,"explore","left")
                        if viaje==False:
                            self.actions(env)
                    if val==3:
                        viaje=self.explore(env,"explore","up")
                        if viaje==False:
                            self.actions(env)
                    if val==4:
                        viaje=self.explore(env,"explore","down")
                        if viaje==False:
                            self.actions(env)
def main ():
    birds=[]
    ambiente=Ambiente_Birds()
    for i in range (5):
        birds.append(Bird(i))
        ambiente.add_thing(birds[i])
        print birds[i].name
        print birds[i].location
    w=Hereda_fram(ambiente)
    w.mainloop()
    print len(ambiente.flock)
    for i in range (5):
        print birds[i].location
main ()
