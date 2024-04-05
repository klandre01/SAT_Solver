## Satisfiability Solver
_Assignment for 6.1010 Fundamentals of Programming (MIT, Spring 2023)_

SAT_Writeup.pdf in the root directory contains the instructions for this assignment. Within the sat folder, lab.py contains the code I wrote and submitted.

For this assignment, I was tasked with coding a satisfiability solver. CNF formulas would be fed into the `satisfying_assignment(formula)` function and a dictionary of variable assignments would be returned.

The satisfiability solver was then used to solve a Sudoku board, represented as a 2D array. I was tasked with creating the following helper functions:
* `sudoku_board_to_sat_formula(sudoku_board)`: takes in a sudoku board and generates a CNF formula representation that can be fed into the `satisfying_assignment(formula)` function
* `assignments_to_sudoku_board(assignments, n)`: takes variable assignments and `n` as the size of the sudoku board and returns a 2D array representing a Sudoku board
