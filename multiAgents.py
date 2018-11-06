# multiAgents.py
# --------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from util import manhattanDistance
from game import Directions
import random, util

from game import Agent

class ReflexAgent(Agent):
        """
            A reflex agent chooses an action at each choice point by examining
            its alternatives via a state evaluation function.

            The code below is provided as a guide.  You are welcome to change
            it in any way you see fit, so long as you don't touch our method
            headers.
        """


        def getAction(self, gameState):
                """
                You do not need to change this method, but you're welcome to.

                getAction chooses among the best options according to the evaluation function.

                Just like in the previous project, getAction takes a GameState and returns
                some Directions.X for some X in the set {North, South, West, East, Stop}
                """
                # Collect legal moves and successor states
                legalMoves = gameState.getLegalActions()

                # Choose one of the best actions
                scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
                bestScore = max(scores)
                bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
                chosenIndex = random.choice(bestIndices) # Pick randomly among the best

                "Add more of your code here if you want to"

                return legalMoves[chosenIndex]

        def evaluationFunction(self, currentGameState, action):
                """
                Design a better evaluation function here.

                The evaluation function takes in the current and proposed successor
                GameStates (pacman.py) and returns a number, where higher numbers are better.

                The code below extracts some useful information from the state, like the
                remaining food (newFood) and Pacman position after moving (newPos).
                newScaredTimes holds the number of moves that each ghost will remain
                scared because of Pacman having eaten a power pellet.

                Print out these variables to see what you're getting, then combine them
                to create a masterful evaluation function.
                """
                # Useful information you can extract from a GameState (pacman.py)
                successorGameState = currentGameState.generatePacmanSuccessor(action)
                oldFoodNum = currentGameState.getNumFood()
                newPos = successorGameState.getPacmanPosition()
                newFood = successorGameState.getFood()
                newFoodNum = successorGameState.getNumFood()
                newGhostStates = successorGameState.getGhostStates()
                newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]

                # 1. find food distances
                foodList = newFood.asList()
                allFoodDistances = []
                for food in foodList:
                    allFoodDistances.append(manhattanDistance(food, newPos))

                # 2. find capsule distances
                capsuleList = successorGameState.getCapsules()
                allCapsuleDistances = []
                for capsule in capsuleList:
                    allCapsuleDistances.append(manhattanDistance(capsule, newPos))

                # 3. find ghost distances
                ghostPositionList = successorGameState.getGhostPositions()
                allGhostDistances = []
                for ghost in ghostPositionList:
                    allGhostDistances.append(manhattanDistance(ghost, newPos))

                evalScore = 0
                scaredGhosts = False

    	        for scared in newScaredTimes:
                    if scared > 10:
                        scaredGhosts = True

                for ghost in allGhostDistances:
                    if scaredGhosts:
                        if ghost < 2.5:
                            evalScore += 25
                        elif ghost < 6.0:
                            evalScore += 5
                    else:
                        if ghost < 2.5:
                            evalScore -= 15
                        elif ghost < 5.0:
                            evalScore -= 5

                if oldFoodNum > newFoodNum:
                    evalScore += 5

                if any(food < 4.0 for food in allFoodDistances):
                    evalScore += 1
                elif any(food < 2.0 for food in allFoodDistances):
                    evalScore += 3

                return evalScore

def scoreEvaluationFunction(currentGameState):
        """
            This default evaluation function just returns the score of the state.
            The score is the same one displayed in the Pacman GUI.

            This evaluation function is meant for use with adversarial search agents
            (not reflex agents).
        """
        return currentGameState.getScore()

class MultiAgentSearchAgent(Agent):
        """
            This class provides some common elements to all of your
            multi-agent searchers.  Any methods defined here will be available
            to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

            You *do not* need to make any changes here, but you can if you want to
            add functionality to all your adversarial search agents.  Please do not
            remove anything, however.

            Note: this is an abstract class: one that should not be instantiated.  It's
            only partially specified, and designed to be extended.  Agent (game.py)
            is another abstract class.
        """

        def __init__(self, evalFn = 'scoreEvaluationFunction', depth = '2'):
                self.index = 0 # Pacman is always agent index 0
                self.evaluationFunction = util.lookup(evalFn, globals())
                self.depth = int(depth)


class MinimaxAgent(MultiAgentSearchAgent):
        """
            Your minimax agent (question 2)
        """
        def isLastAgent(self, gameState, agent):
            return agent == gameState.getNumAgents()

        def minimax(self, gameState, agent, currentDepth):
            # not reached last agent
            if not self.isLastAgent(gameState, agent):
                nextMoves = gameState.getLegalActions(agent)
                # no moves possible
                if len(nextMoves) == 0:
                    return self.evaluationFunction(gameState)

                # check if agent is pacman
                if agent == 0:
                    # select the max value of all succeeding nodes and pass it up
                    succeeding = []
                    for move in nextMoves:
                        succeeding.append(self.minimax(gameState.generateSuccessor(agent, move), agent + 1, currentDepth))
                    return max(succeeding)

                # for ghosts return the min value
                else:
                    succeeding = []
                    for move in nextMoves:
                        succeeding.append(self.minimax(gameState.generateSuccessor(agent, move), agent + 1, currentDepth))
                    return min(succeeding)

            # last agent reached
            else:
                # start new max with pacman (0) or evaluate 
                if currentDepth != self.depth:
                    return self.minimax(gameState, 0, currentDepth + 1)
                else:
                    return self.evaluationFunction(gameState)

        def getAction(self, gameState):
                # select the action with the greatest minimax value
                # starting with pacman who has the index 0
                resultVal = -float("inf")
                result = ""

                # start with the actions of pacman
                for action in gameState.getLegalActions(0):
                    # pass the action, first min ghost, and next layer into minimax
                    temp = self.minimax(gameState.generateSuccessor(0, action), 1, 1)
                    if temp > resultVal:
                        resultVal = temp
                        # get the winning action of pacman
                        result = action

                return result

class AlphaBetaAgent(MultiAgentSearchAgent):
        """
            Your minimax agent with alpha-beta pruning (question 3)
        """
        # could have been merged into one method like in expectimax
        def maxValue(self, gameState, agent, currentDepth, a, b):
                if currentDepth > self.depth:
                    return self.evaluationFunction(gameState)
                v = -float("inf")
                if len(gameState.getLegalActions(agent)) == 0:
                    return self.evaluationFunction(gameState)
                for action in gameState.getLegalActions(agent):
                    successor = self.minValue(gameState.generateSuccessor(agent, action), agent + 1, currentDepth, a, b)
                    v = max(v, successor)
                    if v > b:
                        return v
                    a = max(a, v)
                return v

        def minValue(self, gameState, agent, currentDepth, a, b):
                if agent == gameState.getNumAgents():
                    return self.maxValue(gameState, 0, currentDepth + 1, a, b)
                v = float("inf")
                if len(gameState.getLegalActions(agent)) == 0:
                    return self.evaluationFunction(gameState)
                for action in gameState.getLegalActions(agent):
                    successor = self.minValue(gameState.generateSuccessor(agent, action), agent + 1, currentDepth, a, b)
                    v = min(v, successor)
                    if v < a:
                        return v
                    b = min(b, v)
                return v

        def getAction(self, gameState):
                resultVal = -float("inf")
                result = ""
                a = -float("inf")
                b = float("inf")

                for action in gameState.getLegalActions(0):
                    # init pacman with depth 1 and starting values for a and b
                    value = max(resultVal, self.minValue(gameState.generateSuccessor(0, action), 1, 1, a, b))
                    if value > a:
                        result = action
                    a = max(value, a)
                return result

class ExpectimaxAgent(MultiAgentSearchAgent):
        """
            Your expectimax agent (question 4)
        """
        # too much redundancy in this one --> merge into one
        ''' def maxValue(self, gameState, agent, currentDepth):
            v = -float("inf")
            nextMoves = gameState.getLegalActions(agent)
            if len(nextMoves) == 0:
                return self.evaluationFunction(gameState)
            for action in nextMoves:
                successor = self.expValue(gameState.generateSuccessor(agent, action), agent + 1, currentDepth)
                v = max(v, successor)
            return v

        def expValue(self, gameState, agent, currentDepth):
            if agent == gameState.getNumAgents():
                if currentDepth == self.depth:
                    return self.evaluationFunction(gameState)
                else:
                    return self.maxValue(gameState, 0, currentDepth + 1)
            v = 0.0
            nextMoves = gameState.getLegalActions(agent)
            if len(nextMoves) == 0:
                return self.evaluationFunction(gameState)
            for action in nextMoves:
                probability = 1.0/len(nextMoves)
                successor = self.maxValue(gameState.generateSuccessor(agent, action), agent + 1, currentDepth)
                v += probability * successor
            return v '''

        def expectimax(self, gameState, agent, currentDepth):
            if agent == gameState.getNumAgents():
                if currentDepth == self.depth:
                    return self.evaluationFunction(gameState)
                else:
                    return self.expectimax(gameState, 0, currentDepth + 1)
            else:
                nextMoves = gameState.getLegalActions(agent)
                if len(nextMoves) == 0:
                    return self.evaluationFunction(gameState)
                if agent == 0:
                    v = -float("inf")
                    for action in nextMoves:
                        successor = self.expectimax(gameState.generateSuccessor(agent, action), agent + 1, currentDepth)
                        v = max(v, successor)
                    return v
                else:
                    v = 0.0
                    for action in nextMoves:
                        probability = 1.0/len(nextMoves)
                        successor = self.expectimax(gameState.generateSuccessor(agent, action), agent + 1, currentDepth)
                        v += probability * successor
                    return v
            
        def getAction(self, gameState):
                """
                    Returns the expectimax action using self.depth and self.evaluationFunction

                    All ghosts should be modeled as choosing uniformly at random from their
                    legal moves.
                """
                result = ""
                resultVal = -float("inf")
                for action in gameState.getLegalActions(0):
                    temp = self.expectimax(gameState.generateSuccessor(0, action), 1, 1)
                    if temp > resultVal:
                        resultVal = temp
                        # get the winning action of pacman
                        result = action
                return result
                
def betterEvaluationFunction(currentGameState):
        """
            Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
            evaluation function (question 5).

            DESCRIPTION: just a linear combination of the most effective factors which seem to be like amountOfFood (minimize), minGhostDistance (minimize) and amoungOfCapsule (minimize)
        """
        "*** YOUR CODE HERE ***"
        # get features to include into calculation
        # taking reciprocal values of the distances to increase the effect of low distances on the game state value
        currentPos = currentGameState.getPacmanPosition()
        ghostPos = currentGameState.getGhostPositions()
        ghostStates = currentGameState.getGhostStates()
        scaredTimes = [ghostState.scaredTimer for ghostState in ghostStates]
        scared = True
        scaredScore = 0
        
        foodPos = currentGameState.getFood()
        capsulePos = currentGameState.getCapsules()

        minGhostDistance = float("inf")
        for ghost in ghostPos:
            ghostDist = manhattanDistance(currentPos, ghost)
            if ghostDist < minGhostDistance:
                minGhostDistance = 1.0/(ghostDist+0.01)
        
        minFoodDistance = float("inf")
        # states with less food are better
        amountOfFood = currentGameState.getNumFood()
        for food in foodPos:
            foodDist = manhattanDistance(currentPos, food)
            if foodPos < minFoodDistance:
                minFoodDistance = 1.0/foodDist
        
        minCapsuleDist = float("inf")
        amountOfCapsules = len(capsulePos)
        for capsule in capsulePos:
            capsuleDist = manhattanDistance(currentPos, capsule)
            if capsuleDist < minCapsuleDist:
                minCapsuleDist = 1.0/capsuleDist

        # for low remaining scared times and ghosts in distance we don't try to chase them
        for scared in scaredTimes:
            if scared < 8 and minGhostDistance > 4:
                scared = False
                scaredScore = 100
        
        #wins always
        #return - 3 * amountOfFood - 10 * minGhostDistance + 10 * scaredScore
        return - 5 * amountOfFood - 10 * minGhostDistance - 4 * amountOfCapsules

# Abbreviation
better = betterEvaluationFunction