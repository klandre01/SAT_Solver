"""
6.1010 Spring '23 Lab 8: SAT Solver
"""

#!/usr/bin/env python3

import sys
import typing
import doctest

sys.setrecursionlimit(10_000)
# NO ADDITIONAL IMPORTS


def new_formula(f0, var, value):
    """
    helper function to create a new formula applying assignemnts to f0
    """
    f1 = []
    for clause in f0:
        new_clause = clause[:]
        satisfied = False
        for literal in clause:
            if literal == (var, value):
                satisfied = True
                break
            if literal == (var, not value):
                new_clause.remove((var, not value))
        if not satisfied:
            f1.append(new_clause)
    return f1

def merge_dicts(dict1, dict2):
    """
    merges two dictionaries but adds the values if two matching keys
    """
    dict3 = dict(dict1.items())
    for key in dict2:
        if key in dict3:
            dict3[key] += dict2[key]
        else:
            dict3[key] = dict2[key]
    return dict3

def handle_unit_clause(formula, assignments={}):
    """helper function that handles unit clauses"""
    if len(formula) == 0:
        return [], assignments
    if assignments is None:
        return formula, None
    # goes through every clause to find unit clauses
    found_unit = True
    while found_unit:
        found_unit = False
        for clause in formula:
            if len(clause) == 1:
                found_unit = True
                literal = clause[0]
                var = literal[0]
                value = literal[1]
                if var in assignments and assignments[var] != value:
                    return formula, None
                else:
                    assignments[var] = value
                formula = new_formula(formula, var, value)
                break

    return formula, assignments

def satisfying_assignment(formula):
    """
    Find a satisfying assignment for a given CNF formula.
    Returns that assignment if one exists, or None otherwise.

    >>> satisfying_assignment([])
    {}
    >>> x = satisfying_assignment([[('a', True), ('b', False), ('c', True)]])
    >>> x.get('a', None) is True or x.get('b', None) is False or x.get('c', None) is True
    True
    >>> satisfying_assignment([[('a', True)], [('a', False)]])
    """
    # variable --> string
    # literal --> tuple (variable, Bool)
    # clause --> list of literals
    # formula --> list of clauses

    # base cases
    if len(formula) == 0:
        return {}
    assignments = {}

    # handle unit clauses
    formula, assignments = handle_unit_clause(formula, assignments)
    if assignments is None:
        return None
    
    for clause in formula:
        if clause == []:
            return None

    if len(formula) == 0:
        return assignments

    # first clause --> first literal --> first variable
    x = formula[0][0][0]

    # setting first to true
    assignments_true = {x: True} | assignments
    formula_true = new_formula(formula, x, True)
    result_true = satisfying_assignment(formula_true)
    if result_true is not None:
        return assignments_true | result_true

    # setting first to false
    assignments_false = {x: False} | assignments
    formula_false = new_formula(formula, x, False)
    result_false = satisfying_assignment(formula_false)
    if result_false is not None:
        return assignments_false | result_false

    return None


# SUDOKU


def values_in_row(board, r):
    """sudoku helper that returns all values in a given row"""
    return [i for i in board[r] if i != 0]


def values_in_column(board, c):
    """sudoku helper that returns all values in a given column"""
    return [row[c] for row in board if row[c] != 0]


def values_in_subgrid(board, sr, sc):
    """
    sudoku helper that returns all values in a subgrid
    sr: subgrid row
    sc: subgrid column
    (0,0) --> top left subgrid
    (sqrt(n), sqrt(n)) --> bottom right subgrid
    """
    subgrid_size = int(len(board) ** 0.5)
    keys = list(range(subgrid_size))  # keys are subgrid numbers
    # populate subgrid indices
    subgrid_indices = {}
    for key in keys:
        value_range = list(range(subgrid_size * key, subgrid_size * (key + 1)))
        subgrid_indices[key] = value_range
    # populate subgrid values
    subgrid_values = []
    for i in subgrid_indices[sr]:
        for j in subgrid_indices[sc]:
            if board[i][j] != 0:
                subgrid_values.append(board[i][j])
    return subgrid_values


def find_subgrid(board, r, c):
    """
    sudoku helper that returns (sr, sc) given a row and column
    where sr is the subgrid row and sc is the subgrid column
    """
    n = len(board)
    num_grids = int(n**0.5)
    return (r // num_grids, c // num_grids)


def find_combos(to_match, value):
    """
    helper to create pairwise combinations of values in to_match
    and then map them to the given value to return a literal
    """
    n = len(to_match)
    pairs = []
    for i in range(n):
        var1 = to_match[i]
        for j in range(i + 1, n):
            var2 = to_match[j]
            pair = [(var1, value), (var2, value)]
            pairs.append(pair)
    return pairs


def neighboring_indices(board, current):
    """helper to find indices of column, row, and grid tiles shared"""
    sr, sc = find_subgrid(board, *current)
    indices = (
        row_indices(board, current[0])
        + col_indices(board, current[1])
        + grid_indices(board, sr, sc)
    )
    seen = {current}
    returning = []
    for index in indices:
        if index not in seen:
            returning.append(index)
        seen.add(index)
    return returning


def row_indices(board, row_num):
    """helper to return list of row's indices (tuples)"""
    n_cols = len(board)
    return [(row_num, i) for i in range(n_cols)]


def col_indices(board, col_num):
    """helper to return list of column's indices (tuples)"""
    n_rows = len(board)
    return [(i, col_num) for i in range(n_rows)]


def grid_indices(board, sr, sc):
    """
    helper to return list of subgrid's indices
    sr --> subgrid row
    sc --> subgrid col
    """
    sub_size = int(len(board) ** 0.5)
    indices = []
    for i in range(sub_size * sr, sub_size * (sr + 1)):
        for j in range(sub_size * sc, sub_size * (sc + 1)):
            indices.append((i, j))
    return indices

def create_literals(variables, value):
    """creates and returns a list of literals that all evaluate to value
    using each variable in variables"""
    return [(var, value) for var in variables]

def exactly_once(coordinates, value):
    """creates sat formula for each value to appear only once in a 
    set of coordinates"""
    formula = []
    variables = [coordinate + (value,) for coordinate in coordinates]
    formula.append(create_literals(variables, True))
    formula.extend(find_combos(variables, False))
    return formula

def sudoku_board_to_sat_formula(sudoku_board):
    """
    Generates a SAT formula that, when solved, represents a solution to the
    given sudoku board.  The result should be a formula of the right form to be
    passed to the satisfying_assignment function above.
    """

    # RULES
    # 1. each grid has a value
    # 2. each value appears in a row once (same for column and subgrid)
    # 3. each row has one value in [1, n] (same for column and subgrid)
    # 4. no value appears more than once in a row (same for column and subgrid)

    n = len(sudoku_board)
    n_grids = int(n**0.5)

    formula = []
    for row in range(n):
        for col in range(n):
            value_in_cell = sudoku_board[row][col]  # value of (row, col)
            lit = (row, col, value_in_cell)
            if value_in_cell != 0:
                condition = [(lit, True)]
                formula.append(condition)
                neighbors = neighboring_indices(sudoku_board, (row, col))
                for neighbor in neighbors:
                    neighbor_condition = [(neighbor + (value_in_cell,), False)]
                    formula.append(neighbor_condition)
                continue
            cell_has_value = []
            for i in range(1, n + 1):  # each number entry that appears
                literal1 = (row, col, i)
                cell_has_value.append((literal1, True))  # cell has a value
                for j in range(i + 1, n + 1):
                    clause = [(literal1, False)]
                    literal2 = (row, col, j)
                    clause.append((literal2, False))
                    # clause --> cell has at most one value
                    formula.append(clause)
            formula.append(cell_has_value)

    for i in range(n):
        row_n = row_indices(sudoku_board, i)
        col_n = col_indices(sudoku_board, i)
        for j in range(1, n+1):
            formula += exactly_once(row_n, j) + exactly_once(col_n, j)

    # # value occurs exactly once in the row
    # for row in range(n):
    #     row_n = row_indices(sudoku_board, row)
    #     for i in range(n):  # each value that should be in the grid
    #         variables = [coordinate + (i,) for coordinate in row_n]
    #         formula.append(create_literals(variables, True))  # at least
    #         formula.extend(find_combos(variables, False))  # at most
    # # value occurs exactly once in the col
    # for col in range(n):
    #     col_n = col_indices(sudoku_board, col)
    #     for i in range(n):
    #         variables = [coordinate + (i,) for coordinate in col_n]
    #         formula.append(create_literals(variables, True))  # at least
    #         formula.extend(find_combos(variables, False))  # at most
    # value occurs exactly once in each sub grid
    for sr in range(n_grids):
        for sc in range(n_grids):
            grid_n = grid_indices(sudoku_board, sr, sc)
            for i in range(n):
                formula += exactly_once(grid_n, i)
                # variables = [coordinate + (i,) for coordinate in grid_n]
                # formula.append(create_literals(variables, True))  # at least
                # formula.extend(find_combos(variables, False))  # at most

    return sorted(formula, key=lambda x: len(x))


def assignments_to_sudoku_board(assignments, n):
    """
    Given a variable assignment as given by satisfying_assignment, as well as a
    size n, construct an n-by-n 2-d array (list-of-lists) representing the
    solution given by the provided assignment of variables.

    If the given assignments correspond to an unsolvable board, return None
    instead.
    """
    if assignments is None:
        return None
    # create a board
    board = []
    for i in range(n):
        board.append([0 for _ in range(n)])
    # applying the assignments
    for key, value in assignments.items():
        row, col, val = key
        if value and board[row][col] == 0:
            board[row][col] = val
    # makes sure all cells are filled
    for i in range(n):
        for j in range(n):
            if board[i][j] == 0:
                return None
    return board


if __name__ == "__main__":
    # _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    # doctest.testmod(optionflags=_doctest_flags)

    # sudoku = [
    #     [5, 1, 7, 6, 0, 0, 0, 3, 4],
    #     [2, 8, 9, 0, 0, 4, 0, 0, 0],
    #     [3, 4, 6, 2, 0, 5, 0, 9, 0],
    #     [6, 0, 2, 0, 0, 0, 0, 1, 0],
    #     [0, 3, 8, 0, 0, 6, 0, 4, 7],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0],
    #     [0, 9, 0, 0, 0, 0, 0, 7, 8],
    #     [7, 0, 3, 4, 0, 0, 5, 6, 0],
    #     [0, 0, 0, 0, 0, 0, 0, 0, 0]
    # ]
    # f0 = sudoku_board_to_sat_formula(sudoku)
    # # print(f0)
    # x = assignments_to_sudoku_board(satisfying_assignment(f0), len(sudoku))
    # print(x)

    # true = True
    # false = False
    # b = [
    #     [("b", true), ("a", true)],
    #     [("b", true)],
    #     [("b", false), ("a", false)],
    #     [("c", true), ("d", true)],
    # ]
    # g = [
    #         [("d", true), ("b", true)],
    #         [("c", true), ("d", true)],
    #         [("c", false), ("a", true)],
    #         [("c", false), ("a", false)],
    #         [("b", true), ("a", true)],
    #         [("b", true), ("a", false)],
    #         [("d", true), ("a", true)],
    #         [("d", true), ("a", false)]
    # ]
    # print(new_formula(g, "d", True))

    pass
