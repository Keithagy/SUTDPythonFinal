from org.transcrypt.stubs.browser import *
import random
# from app.serverlibrary import *
    
class BoardUI:
    def __init__(self, GameState):
        self.gameState = GameState
        self.render(self.gameState.board)
        
    def render(self, board):
        gameContainer = document.getElementById('gameContainer')
        gameContainer.innerHTML = ''
        
        table = document.createElement('table')
        
        for row in range(board.boardHeight):
            tblrow = document.createElement('tr')
            for square in range(board.boardWidth):
                cell = document.createElement('td')
                cellText = document.createTextNode(str(board[row, square]))
                cell.appendChild(cellText)
                cell.addEventListener('click', lambda evt: self.handleLeftClick(row, square))
                cell.addEventListener('contextmenu', lambda evt: (evt.preventDefault(), self.handleRightClick(row, square)))
                tblrow.appendChild(cell)
            table.appendChild(tblrow)

        gameContainer.appendChild(table)
      
    def handleLeftClick(self, rowNo, colNo):
        console.log('Left click on ('+str(rowNo)+','+str(colNo)+')')
        square = self.gameState.board[rowNo,colNo]

        # Left click disabled for flagged squares
        if square.status == 2:
            console.log('Square ('+str(rowNo)+','+str(colNo)+') is flagged, cannot be left-clicked!')
            return
        
        # Left click disabled for flagged squares
        if square.status == 1:
            console.log('Square ('+str(rowNo)+','+str(colNo)+') is already open!')
            return

        cleanup = self.gameState.signals[square.uncover()]
        cleanup(rowNo, colNo)
        console.log('Cleanup function '+ cleanup.__name__ + ' was called on ('+str(rowNo)+','+str(colNo)+'). Re-rendering...')
        self.render(self.gameState.board)

    def handleRightClick(self, rowNo, colNo):
        console.log('Right click on ('+str(rowNo)+','+str(colNo)+')')
        square = self.gameState.board[rowNo,colNo]
        # Right click disabled for uncovered squares
        if square.status == 1:
            console.log('Square ('+str(rowNo)+','+str(colNo)+') is uncovered, cannot be right-clicked!')
            return
        
        cleanup = None        
        if square.status == 0:
            cleanup = self.gameState.signals[square.flag()]
        else:
            cleanup = self.gameState.signals[square.unflag()]
        
        cleanup(rowNo, colNo)
        console.log('Cleanup function '+ cleanup.__name__ + ' was called on ('+str(rowNo)+','+str(colNo)+'). Re-rendering...')
        self.render(self.gameState.board)

class GameState:

    def __init__(self, boardWidth, boardHeight, minePercentage):
        totalMines = min(int(round(( boardWidth * boardHeight ) * minePercentage)), 1)
        console.log("Total number of mines: ", totalMines)
        self.board = Board(boardWidth, boardHeight, totalMines)
        self.gameStarted = False

        # Keys are board coordinates (tuple), values are bool for whether they are flagged
        self.mineTracker = {}

        # Keys are signals (returned by gameSquare methods), values are cleanup functions
        self.signals = {
            'mineFlagged': self.mineFlagged,
            'mineUnflagged': self.mineUnflagged,
            'mineUncovered': self.mineUncovered,
            'numberFlagged': self.numberFlagged,
            'numberUnflagged': self.numberUnflagged,
            'numberUncovered': self.numberUncovered,
            }

        # Set of all flag coordinatees (tuples)
        self.flagTracker = set()
        
    def mineFlagged(self, rowNo, colNo):
        self.mineTracker[(rowNo,colNo)] = True
        self.flagTracker.add((rowNo,colNo))

    def mineUnflagged(self, rowNo, colNo):
        self.mineTracker[(rowNo, colNo)] = False
        self.flagTracker.remove((rowNo, colNo))

    def mineUncovered(self, rowNo, colNo):
        self.gameLost(rowNo, colNo)
        self.resetBoard()

    def numberFlagged(self, rowNo, colNo):
        self.flagTracker.add((rowNo, colNo))

    def numberUnflagged(self, rowNo, colNo):
        self.flagTracker.remove((rowNo, colNo))
    
    def numberUncovered(self,rowNo, colNo):
        self.board.uncoverSquaresFrom(rowNo, colNo)
    
    def gameLost(self, rowNo, colNo):
        print('Game lost!', rowNo, colNo)

    def resetBoard(self):
        print('Resetting board...')

    def __str__(self):
        boardStr = []
        for row in self.board:
            boardRowStr = []
            for square in row:
                boardRowStr.append(str(square))
            boardStr.append(','.join(boardRowStr))
        boardStr = '\n'.join(boardStr)
        return f"[{boardStr}]"
    
    def __iter__(self):
        return iter(self.board)
    
    def __len__(self):
        return len(self.board)
    
    def __getitem__(self, coordinates):
        return self.board[coordinates]

# Note: value 0 being passed into all numberSquares below is placeholder. numberSquare values should be calculated only after mines are seeded, and mines should only be seeded upon opening of first square (first square is never a mine).
class Board:
    def __init__(self, boardWidth, boardHeight, totalMines):
            if isinstance(boardWidth, int) and isinstance(boardHeight, int) and isinstance(totalMines, int) and boardWidth > 0 and boardHeight > 0 and totalMines > 0:
                self._board = [[NumberSquare(0) for _ in range(boardWidth)] for _ in range(boardHeight)]
                self.boardWidth = boardWidth
                self.boardHeight = boardHeight

    # returns an iterator for board's rows
    def __iter__(self):
        return iter(self._board)

    # Invoke using Board[x,y]
    def __getitem__(self, coordinates):
        rowNo, colNo = coordinates
        return self._board[rowNo][colNo]

    # Invoke using Board[x,y] = gameSquare(). 
    # Only implementations of the gameSquare abstract class should be assigned!
    # Should only be called to assign mineSquares at start of game
    def __setitem__(self, coordinates, square):
        rowNo, colNo = coordinates
        self._board[rowNo][colNo] = square
        
    def uncoverSquaresFrom(self,rowNo,colNo):
        self.uncoverSquaresFromRec(rowNo, self.left(colNo))
        self.uncoverSquaresFromRec(self.up(rowNo), self.left(colNo))
        self.uncoverSquaresFromRec(self.up(rowNo), colNo)
        self.uncoverSquaresFromRec(self.up(rowNo), self.right(colNo))
        self.uncoverSquaresFromRec(rowNo, self.right(colNo))
        self.uncoverSquaresFromRec(self.down(rowNo), self.right(colNo))
        self.uncoverSquaresFromRec(self.down(rowNo), colNo)
        self.uncoverSquaresFromRec(self.down(rowNo), self.left(colNo))
        
    def uncoverSquaresFromRec(self, rowNo, colNo):
        # If function is called on out-of-board coordinates, return early
        if rowNo is None or colNo is None:
            return 
        square = self._board[rowNo][colNo]
        # Terminate recursion for already-uncovered or flagged squares
        if square.status != 0:
            return
        # Uncover if NumberSquare and not flagged
        if isinstance(square,NumberSquare):
            square.uncover()
        # recursively call function on surrounding squares until square.value is non-zero, i.e border of the 'island'
        if square.value == 0:
            self.uncoverSquaresFromRec(rowNo, self.left(colNo))
            self.uncoverSquaresFromRec(self.up(rowNo), self.left(colNo))
            self.uncoverSquaresFromRec(self.up(rowNo), colNo)
            self.uncoverSquaresFromRec(self.up(rowNo), self.right(colNo))
            self.uncoverSquaresFromRec(rowNo, self.right(colNo))
            self.uncoverSquaresFromRec(self.down(rowNo), self.right(colNo))
            self.uncoverSquaresFromRec(self.down(rowNo), colNo)
            self.uncoverSquaresFromRec(self.down(rowNo), self.left(colNo))

    # Board navigation methods
    def left(self, colNo):
        if colNo <= 0:
            return None
        return colNo - 1

    def right(self, colNo):
        if colNo >= self.boardWidth - 1:
            return None
        return colNo + 1
    
    def up(self, rowNo):
        if rowNo <= 0:
            return None
        return rowNo - 1
    
    def down(self, rowNo):
        if rowNo >= self.boardHeight - 1:
            return None
        return rowNo + 1    
    
    def __len__(self):
        return self.boardHeight
        
# Abstract class, inherited by mineSquare and numberSquare
class GameSquare:
    state = {
        0: 'covered',
        1: 'uncovered',
        2: 'flagged',
    }

    def __init__(self):
        self.status = 0

    def __str__(self):
        raise Exception('Please specify conditional rendering for square type')

    def flag(self):
        raise Exception('Child classes of gameSquare must implement the method flag, which includes assignment of self.status to 2 and (if needed) returns a signal for a cleanup function')

    def unflag(self):
        raise Exception('Child classes of gameSquare must implement the method unflag, which includes assignment of self.status to 0 and (if needed) returns a signal for a cleanup function')

    def uncover(self):
        raise Exception('Child classes of gameSquare must implement the method uncover, which includes assignment of self.status to 1 and (if needed) returns a signal for a cleanup function')

    @property
    def status(self):
        return self._status

    @status.setter
    def status(self, num):
        if isinstance(num, int):
            if num in self.state:
                self._status = num

class MineSquare(GameSquare):
    def __init__(self):
        super().__init__()

    def flag(self):
        self.status = 2
        return 'mineFlagged'

    def unflag(self):
        self.status = 0
        return 'mineUnflagged'

    def uncover(self):
        if self.status != 2:
            self.status = 1
            return 'mineUncovered'
        
    def __str__(self):
        if self.status == 0:
            return '□'
        elif self.status == 1:
            return '■'
        else:
            return '▣'

    # @property
    # def signals(self):
    #     return self._signals

    # @signals.setter
    # def signals(self, signals):
    #     if ('mineFlagged' not in signals) or ('mineUnflagged' not in signals) or ('mineUncovered' not in signals):
    #         raise Exception('mineSquare requires mineFlagged, mineUnflagged and mineUncovered signals')
    #     self._signals = signals 

class NumberSquare(GameSquare):
    def __init__(self, value):
        super().__init__()
        self.value = value

    def flag(self):
        self.status = 2
        return 'numberFlagged'

    def unflag(self):
        self.status = 0
        return 'numberUnflagged'

    def uncover(self):
        if self.status != 2:
            self.status = 1
            return 'numberUncovered'
        
    def __str__(self):
        if self.status == 0:
            return '□'
        elif self.status == 1:
            return str(self.value) if self.value != 0 else '▦'
        else:
            return '▣'


    # @property
    # def signals(self):
    #     return self._signals

    # @signals.setter
    # def signals(self, signals):
    #     if ('numberFlagged' not in signals) or ('numberUnflagged' not in signals) or ('numberUncovered' not in signals):
    #         raise Exception('numberSquare requires numberFlagged, numberUnflagged and numberUncovered signals')
    #     self._signals = signals 
    
