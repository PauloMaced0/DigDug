from abc import ABC, abstractmethod
import asyncio
#
class SearchDomain(ABC):

    # construtor
    @abstractmethod
    def __init__(self):
        pass

    # lista de accoes possiveis num estado
    @abstractmethod
    def actions(self, state):
        pass

    # resultado de uma accao num estado, ou seja, o estado seguinte
    @abstractmethod
    def result(self, state, action):
        pass

    # custo de uma accao num estado
    @abstractmethod
    def cost(self, state, action):
        pass 

    # custo estimado de chegar de um estado a outro
    @abstractmethod
    def heuristic(self, state, goal):
        pass

    # test if the given "goal" is satisfied in "state"
    @abstractmethod
    def satisfies(self, state, goal):
        pass

# Problemas concretos a resolver
# dentro de um determinado dominio
class SearchProblem:
    def __init__(self, domain, initial, goal):
        self.domain = domain
        self.initial = initial
        self.goal = goal

    def goal_test(self, state, goal):
        return self.domain.satisfies(state, goal)

# Nos de uma arvore de pesquisa
class SearchNode:
    def __init__(self, state, parent, depth, cost, heuristic, action):
        self.state = state
        self.parent = parent
        self.cost = cost 
        self.depth = depth 
        self.heuristic = heuristic 
        self.action = action

    def __str__(self):
        return "no(" + str(self.state) + "," + str(self.parent) + ")"

    def __repr__(self):
        return str(self)

# Arvores de pesquisa
class SearchTree:

    # construtor
    def __init__(self, problem): 
        self.problem = problem
        root = SearchNode(problem.initial, None, 0, 0, 0, ()) 
        self.open_nodes = [root]

    # obter o caminho (sequencia de estados) da raiz ate um no
    def get_path(self, node):
        if node.parent is None:
            return [node.state]
        path = self.get_path(node.parent)
        path += [node.state]
        return path 

    # procurar a solucao
    def search(self):
        while self.open_nodes != []:
            node = self.open_nodes.pop(0)

            if self.problem.goal_test(node.state, self.problem.goal):
                path = self.get_path(node)
                return path[1]['key_action']
                # return calculate_key(path[1]['digdug'],path[0]['digdug'])

            lnewnodes = []
            for a in self.problem.domain.actions(node.state): 
                newstate = self.problem.domain.result(node.state, a)
                if newstate not in self.get_path(node):
                    newnode = SearchNode(newstate, node, node.depth + 1, 
                                         node.cost + self.problem.domain.cost(node.state, newstate), 
                                         self.problem.domain.heuristic(newstate),
                                         a)
                    lnewnodes.append(newnode)

            self.open_nodes = sorted(self.open_nodes + lnewnodes, 
                                     key=lambda node: 
                                     node.heuristic + node.cost)
        return None 
