"""
Tic Tac Toe Player
"""

import math
import copy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    # always starts with x
    # if count of X is more than O next turn is O

    countX = 0
    countO = 0

    for i in range(len(board)):
        for j in range(len(board[i])):
            if board[i][j] == X:
                countX += 1
            if board[i][j] == O:
                countO += 1

    if countX > countO:
        return O
    else:
        return X


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    actions = set()
    # find any cell that is empty
    # should return set of tuples
    for i in range(len(board)):
        for j in range(len(board[i])):
            if board[i][j] == EMPTY:
                action = (i, j)
                actions.add(action)
    return actions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    # If action is not a valid action for the board, your program should raise an exception.
    valid_actions = actions(board)
    if action not in valid_actions:
        raise Exception('This is not a valid move.')
    # The returned board state should be the board that would result from taking the original input board, and letting the player whose turn it is make their move at the cell indicated by the input action.
    i, j = action
    board_copy = copy.deepcopy(board)
    board_copy[i][j] = player(board)
    return board_copy


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    raise NotImplementedError


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    raise NotImplementedError


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    raise NotImplementedError


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    raise NotImplementedError
