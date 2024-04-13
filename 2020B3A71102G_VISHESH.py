#!/usr/bin/env python3
from FourConnect import * # See the FourConnect.py file
import csv
import datetime

class GameTreePlayer:
    
    def __init__(self):
        # order or moves played last is P1, second last P2  
        self.movesPlayedBoth = []
        # order of moves if followed by p1,p2 starts from move of p2
        # then keep following
        self.moveOrdering = []
        # order or states used to find p1 move to add to moves played by both
        self.stateOrder=[]
        # index till which  moveOrdering is followed
        self.followedTill=0
        # number of times evaluation function called (i.e. didn't follow heuristic order)
        self.usedEvaluation=0
        pass

    #get usedEvaluation to print somewhere
    def getUsedEval(self):
        return self.usedEvaluation
    
    #check and remove order if now followed
    def removeUnfollowedOrders(self):
        if len(self.movesPlayedBoth)<2:
            return
        followers = []
        lastP2 = self.movesPlayedBoth[len(self.movesPlayedBoth)-2]
        lastP1 = self.movesPlayedBoth[len(self.movesPlayedBoth)-1]
        if len(self.moveOrdering)>self.followedTill+1:
            if self.moveOrdering[self.followedTill]==lastP2 and self.moveOrdering[self.followedTill+1]==lastP1:
                followers=(self.moveOrdering.copy())
        self.followedTill+=2
        self.moveOrdering=followers

    #if following get next in Order
    def getNextInOrder(self):
        if len(self.moveOrdering)>0:
            bestOrder = self.moveOrdering
            if len(bestOrder)>self.followedTill:
                self.followedTill+=1
                return bestOrder[self.followedTill-1]
        #if not following then set followed till to 0
        # and return -1
        self.followedTill=0
        return -1
    
    #make P2 move in arg state and store it in stateOrder
    def makeP2MoveInStateAndStore(self,state,action):
        dummy = state.copy()
        for i in range(6):
            if dummy[i][action]!=0:
                dummy[i][action]=2
                break
        self.stateOrder.append(dummy)

    #just checks winner
    def checkWinner(self,game):
        if game.winner == 1 :
            return 1
        elif game.winner == 2 :
            return 2
        else:
            return 0

    #func to get min number in array and its indexes
    def minOfArrIndx(self,arr):
        minim = min(arr,default=10)
        res = []
        for i in range(len(arr)):
            if arr[i]==minim:
                res.append(i)
        return res,minim
    
    # To find which move Myopic P1 plays
    def CheckP1Col(self,state1,state2):
        for i in range(6):
            for j in range(7):
                if state1[i][j]!=state2[i][j]:
                    return j
                
    def EvaluateMoves(self,rewards,winNow,p1WinCols,winDepth):
        minDepthArr = []

        # winIndex - actions where rewards are win
        # lossIndex - actions where rewards are loss
        # dkIndex - actions where rewards are draw/no winner yet
        winIndex=[]
        lossIndex=[]
        dkIndex=[]
        #filling winIndex,lossIndex,dkIndex
        for idx in range(7):
            if rewards[idx]==1:
                winIndex.append(idx)
            elif rewards[idx]==-1:
                lossIndex.append(idx)
            elif rewards[idx]==0:
                dkIndex.append(idx)
        
        minDepthArr,minim = self.minOfArrIndx(winDepth)

        rewardBest=0
        bestMove=-1

        #priority1 - win if possible now
        if len(winNow)>0:
            rewardBest=1
            bestMove=random.choice(winNow)
        #priority2 - block p1 if he wins now 
        elif len(p1WinCols)>0:
            bestMove=random.choice(p1WinCols)
            rewardBest=rewards[bestMove]
        #priority3 - p2 wins later based on on min win Depth 
        elif len(minDepthArr)>0 and minim<5:
            bestMove=random.choice(minDepthArr)
            rewardBest=1
        #priority4 - win if possible in next moves
        elif len(winIndex)>0:
            rewardBest=1
            bestMove=random.choice(winIndex)
        #priority5 - draw/no winner yet moves
        elif len(dkIndex)>0:
            rewardBest=0
            bestMove=random.choice(dkIndex)
        #priority6 - no choice and we lose in next moves/now
        elif len(lossIndex)>0:
            rewardBest=-1
            bestMove=random.choice(lossIndex)
        #no moves possible
        else:
            rewardBest=-2
            bestMove=0
        return bestMove,rewardBest


    def MoveFinder(self,currentState,depth):

        #relative depth of winning on action
        winDepth=[10,10,10,10,10,10,10]

        if depth==0:
            return -1,0,winDepth,[]
        
        bestMove = -1
        rewardBest = 0
        '''
        # Rewards keeps track of rewards 
        on each action at each max node
            win = 1
            draw/no winner yet = 0
            lose = -1
            invalid action = -2
        '''
        rewards=[]
    
        # moves which can result win in this level (now not after some moves)
        winNow = []
        # moves which can lead to p1 win if not played by P2 now
        p1WinCols=[]

        moveOrder=[]
        

        for action in range(7):
            #creating game from current state
            fourConnectDummy = FourConnect()
            fourConnectDummy.SetCurrentState(currentState)
            gameWinner=0

            #move order saved here of this action
            moveOrder_inner = []

            #checking action validity
            if currentState[0][action]==0:
                #p2 playing action
                fourConnectDummy.GameTreePlayerAction(action)
                gameWinner = self.checkWinner(fourConnectDummy)
                
                #checking is p2 wins
                if gameWinner!=2:
                    #now p1 plays 
                    #try block as if total moves exhausted p1 cant move and assert will throw error
                    try:
                        #getting state before p1 play
                        state1 = fourConnectDummy.GetCurrentState()
                        #p1 plays myopic
                        fourConnectDummy.MyopicPlayerAction()
                        gameWinner = self.checkWinner(fourConnectDummy)

                        #getting state after p1 play
                        state2 = fourConnectDummy.GetCurrentState()
                        #finding p1 winning move
                        p1Move = self.CheckP1Col(state1,state2)

                        #checking is p1 wins
                        if gameWinner!=1:
                            stateNow = fourConnectDummy.GetCurrentState()
                            bestMove1,rewardBest1,winDepth1,moveOrder1 = self.MoveFinder(stateNow,depth-1)
                            minDepthArr1,minim1 = self.minOfArrIndx(winDepth1)
                            winDepth[action]=minim1+1
                            rewards.append(rewardBest1)
                            
                            #append to move order
                            #append move of this action
                            moveOrder_inner.append(action)
                            #append move of P1 myopic
                            moveOrder_inner.append(p1Move)
                            #append moves of the tree branch
                            for mo1 in moveOrder1:
                                moveOrder_inner.append(mo1)
                        else:
                            #p2 wins so we try to block
                            p1WinCols.append(p1Move)
                            rewards.append(-1)
                    #moves exhausted so throws and hence draw  
                    except AssertionError as e:
                        rewards.append(0)
                else:
                    #p2 wins so reward add 1 and winNow add action
                    winDepth[action]=0
                    winNow.append(action)
                    rewards.append(1)
                    #append the winning move to order
                    moveOrder_inner.append(action)
            else:
                #not valid action
                rewards.append(-2)
            #append each actions moveOrder_inner
            moveOrder.append(moveOrder_inner)

        bestMove,rewardBest = self.EvaluateMoves(rewards,winNow,p1WinCols,winDepth)

        #we know we only choosing best move for P2 , so return only that new move order
        return bestMove,rewardBest,winDepth,moveOrder[bestMove].copy()
    
    def FindBestAction(self,currentState):
        """
        Modify this function to search the GameTree instead of getting input from the keyboard.
        The currentState of the game is passed to the function.
        currentState[0][0] refers to the top-left corner position.
        currentState[5][6] refers to the bottom-right corner position.
        Action refers to the column in which you decide to put your coin. The actions (and columns) are numbered from left to right.
        Action 0 is refers to the left-most column and action 6 refers to the right-most column.
        """
        #save state before p2 turn
        self.stateOrder.append(currentState.copy())
        if len(self.stateOrder)>=2:
            #find p1 move played before the P2 gameTree func call and append it to movesPlayedBoth
            p1Move = self.CheckP1Col(self.stateOrder[len(self.stateOrder)-2],self.stateOrder[len(self.stateOrder)-1])
            self.movesPlayedBoth.append(p1Move)

        #depth
        depth = 5
        
        #purge unfollowed ordering
        self.removeUnfollowedOrders()
        #if follows order get next move
        heuristicAction  = self.getNextInOrder()
        bestMove = -1
        #doesn't follow heuristic move order
        if heuristicAction == -1:
            self.usedEvaluation+=1
            bestMove,rewardBest,winDepth,moveOrder = self.MoveFinder(currentState,depth)
            self.moveOrdering=moveOrder.copy()
        #follows heuristic move order
        else:
            bestMove=heuristicAction
        
        #P2 move is not played yet so we make out function make state of played and save it
        self.makeP2MoveInStateAndStore(currentState,bestMove)
        self.movesPlayedBoth.append(bestMove)

        bestAction = bestMove
        return bestAction


def LoadTestcaseStateFromCSVfile():
    testcaseState=list()

    with open('testcase.csv', 'r') as read_obj: 
       	csvReader = csv.reader(read_obj)
        for csvRow in csvReader:
            row = [int(r) for r in csvRow]
            testcaseState.append(row)
        return testcaseState


def PlayGame():
    startTime = datetime.datetime.now()
    
    fourConnect = FourConnect()
    fourConnect.PrintGameState()
    gameTree = GameTreePlayer()
    
    move=0
    while move<42: #At most 42 moves are possible
        if move%2 == 0: #Myopic player always moves first
            fourConnect.MyopicPlayerAction()
        else:
            currentState = fourConnect.GetCurrentState()
            gameTreeAction = gameTree.FindBestAction(currentState)
            fourConnect.GameTreePlayerAction(gameTreeAction)
        fourConnect.PrintGameState()
        move += 1
        if fourConnect.winner!=None:
            break
    
    """
    You can add your code here to count the number of wins average number of moves etc.
    You can modify the PlayGame() function to play multiple games if required.
    """
    if fourConnect.winner==None:
        print("Game is drawn.")
    else:
        print("Winner : Player {0}\n".format(fourConnect.winner))
    print("Moves : {0}".format(move))

    endTime = datetime.datetime.now()
    timeDiff = endTime-startTime
    timeInMiliSecs = int(timeDiff.total_seconds() * 1000)
    return fourConnect.winner,move,timeInMiliSecs

def RunTestCase():
    """
    This procedure reads the state in testcase.csv file and start the game.
    Player 2 moves first. Player 2 must win in 5 moves to pass the testcase; Otherwise, the program fails to pass the testcase.
    """
    
    fourConnect = FourConnect()
    gameTree = GameTreePlayer()
    testcaseState = LoadTestcaseStateFromCSVfile()
    fourConnect.SetCurrentState(testcaseState)
    fourConnect.PrintGameState()

    move=0
    while move<5: #Player 2 must win in 5 moves
        if move%2 == 1: 
            fourConnect.MyopicPlayerAction()
        else:
            currentState = fourConnect.GetCurrentState()
            gameTreeAction = gameTree.FindBestAction(currentState)
            fourConnect.GameTreePlayerAction(gameTreeAction)
        fourConnect.PrintGameState()
        move += 1
        if fourConnect.winner!=None:
            break
    
    print("Roll no : 2020B3A71102G") #Put your roll number here
    
    if fourConnect.winner==2:
        print("Player 2 has won. Testcase passed.")
    else:
        print("Player 2 could not win in 5 moves. Testcase failed.")
    print("Moves : {0}".format(move))
    return fourConnect.winner,move

def main():
    
    # wins = 0
    # loss = 0
    # draw = 0
    # totalMovesInWin = 0
    # totalMovesInLoss = 0
    # totalMovesInDraw = 0

    # totalTimeInWin = 0
    # totalTimeInLoss = 0
    # totalTimeInDraw = 0

    # for times in range(50):
    #     gameWinner,move,timeInMiliSecs = PlayGame()
    #     # gameWinner,move = RunTestCase()

    #     if gameWinner==2:
    #         wins+=1
    #         totalMovesInWin+=move
    #         totalTimeInWin+=timeInMiliSecs
    #     elif gameWinner==1:
    #         loss+=1
    #         totalMovesInLoss+=move
    #         totalTimeInLoss+=timeInMiliSecs
    #     else:
    #         draw+=1
    #         totalMovesInDraw+=move
    #         totalTimeInDraw+=timeInMiliSecs

    # print("Roll no : 2020B3A71102G\n") #Put your roll number here
    # print('-----50 Games-----\n')
    # print('#PlayGame:\n')
    # if wins>0:
    #     avgMoveWin = totalMovesInWin/wins
    #     avgTimeWin = totalTimeInWin/(wins*1000)
    #     print('Wins: ',wins,', Avg Moves: ',avgMoveWin,', Avg Time: ',avgTimeWin,'sec\n')

    # if loss>0:
    #     avgMoveLoss = totalMovesInLoss/loss
    #     avgTimeLoss = totalTimeInLoss/(loss*1000)
    #     print('Losses: ',loss,', Avg Moves: ',avgMoveLoss,', Avg Time: ',avgTimeLoss,'sec\n')

    # if draw>0 : 
    #     avgMoveDraw = totalMovesInDraw/draw
    #     avgTimeDraw = totalTimeInDraw/(draw*1000)
    #     print('Draws: ',draw,', Avg Moves: ',avgMoveDraw,', Avg Time: ',avgTimeDraw,'sec\n')


    # PlayGame()
    """
    You can modify PlayGame function for writing the report
    Modify the FindBestAction in GameTreePlayer class to implement Game tree search.
    You can add functions to GameTreePlayer class as required.
    """

    """
        The above code (PlayGame()) must be COMMENTED while submitting this program.
        The below code (RunTestCase()) must be UNCOMMENTED while submitting this program.
        Output should be your rollnumber and the bestAction.
        See the code for RunTestCase() to understand what is expected.
    """
    
    RunTestCase()


if __name__=='__main__':
    main()
