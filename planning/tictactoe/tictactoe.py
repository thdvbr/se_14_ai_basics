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
    # winner in same row: 3 times same player on same row, not empty
    for i in range(len(board)):
        if board[i][0] == board[i][1] == board[i][2] != EMPTY:
            if board[i][0] == X:
                return X
            else:
                return O

    # winner in same column
    for j in range(len(board)):
        if board[0][j] == board[1][j] == board[2][j] != EMPTY:
            if board[0][j] == X:
                return X
            else:
                return O

    # winner in diagonal: 2 cases (0,0) (1,1) (2,2) or (0,2), (1,1), (2,0)
    if board[0][0] == board[1][1] == board[2][2] != EMPTY:
        if board[0][0] == X:
            return X
        else:
            return O
    elif board[0][2] == board[1][1] == board[2][0] != EMPTY:
        if board[0][2] == X:
            return X
        else:
            return O

    # no winner / draw
    else:
        return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    # if there is a winner
    if winner(board) != None:
        return True
    # if all cells have been filled (no more moves possible, empty actions)
    elif len(actions(board)) == 0:
        return True
    else:
        return False


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if winner(board) == X:
        return 1
    elif winner(board) == O:
        return -1
    else:
        return 0


def max_value(board, count):
    v = -math.inf
    # 1. first check if game is over
    if terminal(board):
        return utility(board), count+1
    # 2. compare v with maximum value of minValue
    for action in actions(board):
        best_val, count = min_value(result(board, action), count)
        v = max(v, best_val)
    return v, count+1


def min_value(board, count):
    # initial value of the state
    v = math.inf
    if terminal(board):
        return utility(board), count+1
    # loop over all of the possible actions
    for action in actions(board):
        # take the min of max players decision vs current value v
        best_val, count = max_value(result(board, action), count)
        v = min(v, best_val)
    return v, count+1


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    # The move returned should be the optimal action (i, j) that is one of the allowable actions on the board.
    # If multiple moves are equally optimal, any of those moves is acceptable.

    # If the board is a terminal board, the minimax function should return None.
    if terminal(board):
        return None

    best_move = None
    # X wants to maximize score: get the action that returns the biggest minimum value
    if player(board) == X:
        for action in actions(board):
            v = -math.inf
            best_val, count = min_value(result(board, action), 0)
            if v < best_val:
                v = best_val
                best_move = action

    # O wants to minimize score: get the action that returns the smallest maximum value
    else:
        for action in actions(board):
            v = math.inf
            best_val, count = max_value(result(board, action), 0)
            if v > best_val:
                v = best_val
                best_move = action

    print(f"Number of explored states: {count}")
    return best_move
