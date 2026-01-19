"""
Tic Tac Toe Player
"""

import math

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
    x = 0
    o = 0
    for row in board:
        for cell in row:
            if cell == X:
                x += 1

            elif cell == O:
                o += 1

    if x > o:
        return O
    elif x < o:
        return X
    else:
        return X


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    actions = set()

    for i, row in enumerate(board):
        for j, col in enumerate(row):
            if col == None:
                actions.add((i, j))

    return actions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    import copy

    copied_board = copy.deepcopy(board)

    turn = player(board)
    # cs50 ai taught me this below
    i, j = action

    if i < 0 or i > 2 or j < 0 or j > 2:
        raise ValueError("out-of-bounds move")

    if board[i][j] == EMPTY:
        copied_board[i][j] = turn
    else:
        raise ValueError("error")

    return copied_board


def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    for row in board:
        # winner X horizontally
        if row[0] == X and row[1] == X and row[2] == X:
            return X
        # winner O horizontally
        elif row[0] == O and row[1] == O and row[2] == O:
            return O

    # winner X vertically
    if board[0][0] == X and board[1][0] == X and board[2][0] == X:
        return X
    elif board[0][1] == X and board[1][1] == X and board[2][1] == X:
        return X
    elif board[0][2] == X and board[1][2] == X and board[2][2] == X:
        return X

    # winner O vertically
    if board[0][0] == O and board[1][0] == O and board[2][0] == O:
        return O
    elif board[0][1] == O and board[1][1] == O and board[2][1] == O:
        return O
    elif board[0][2] == O and board[1][2] == O and board[2][2] == O:
        return O

    # winner X diagonally
    if board[0][0] == X and board[1][1] == X and board[2][2] == X:
        return X
    elif board[0][2] == X and board[1][1] == X and board[2][0] == X:
        return X

    # winner O diagonally
    if board[0][0] == O and board[1][1] == O and board[2][2] == O:
        return O
    elif board[0][2] == O and board[1][1] == O and board[2][0] == O:
        return O

    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    win = winner(board)
    if win == X or win == O:
        return True
    else:
        for row in board:
            for cell in row:
                if cell == EMPTY:
                    return False
        else:
            return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    win = winner(board)
    if win == X:
        return 1
    elif win == O:
        return -1
    else:
        return 0


def minimax(board, is_top_level=True):
    """
    Returns the optimal action for the current player on the board.
    """
    best_value = float('-inf')
    best_action = None
    turn = player(board)
    util = utility(board)

    if turn == O:
        best_value = float('inf')

    # cs50 ai helped me with the if statement and elif
    if terminal(board) and is_top_level == True:
        return None
    elif terminal(board):
        return util
    else:
        # cs50 ai helped me with this line below
        for i in actions(board):
            new_board = result(board, i)
            # cs50 ai helped me with with this one
            value = minimax(new_board, False)
            if turn == X:
                # cs50 ai helped me with this 3 lines below
                if value > best_value:
                    best_value = value
                    best_action = i
            elif turn == O:
                if value < best_value:
                    best_value = value
                    best_action = i

    if is_top_level == False:
        return best_value
    else:
        return best_action
