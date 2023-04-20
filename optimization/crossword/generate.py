import sys


from crossword import *
from collections import deque


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {   # a dictionary that maps variables to a set of possible words the variable might take on as a value.
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        # unary constraint: same number of letters as variable length
        # for every variable, each value in its domain is consistent with the variables unary constraints
        # check if every value in variables domain has the same num of letters as variable length
        # if not then remove word from the domain of variable v

        # if variable length != domains variable length (word candidates)

        for var in self.domains:
            # self.domains[var] is a set
            for word in list(self.domains[var]):
                # self.crosswords.word:
                if len(word) != var.length:
                    self.domains[var].remove(word)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        overlap = self.crossword.overlaps[x, y]
        (i, j) = overlap
        revised = False
        if overlap:
            for val_x in list(self.domains[x]):
                conflict = True
                for val_y in self.domains[y]:
                    if val_x[i] == val_y[j]:
                        conflict = False
                if conflict:
                    self.domains[x].remove(val_x)
                    revised = True
        return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """

        # if arcs is none, initial list with all arcs
        if arcs is None:
            arcs = deque()
            for var1 in self.crossword.variables:
                for var2 in self.crossword.neighbors(var1):
                    arcs.appendleft((var1, var2))
        # if arcs is not None, use arcs as the initial list of arcs
        else:
            arcs = deque(arcs)

        while arcs:
            x, y = arcs.pop()

            if self.revise(x, y):
                # nothing left in domainX impossible to solve problem
                if len(self.domains[x]) == 0:
                    return False
                # else add new arcs (x's neighbors excluding y and x) to the queue arc
                for z in self.crossword.neighbors(x) - {y}:
                    arcs.appendleft((z, x))
        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for var in self.crossword.variables:
            if var not in assignment.keys():
                return False

        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # verify if all words have correct length
        for var_1, word_1 in assignment.items():
            if var_1.length != len(word_1):
                return False

            # verify if all words different
            for var_2, word_2 in assignment.items():
                if word_2 == word_1:
                    return False

                # verify if there are no conflicting characters
                overlap = self.crossword.overlaps[var_1, var_2]
                if overlap:
                    (i, j) = overlap  # overlap indices
                    if word_1[i] != word_2[j]:
                        return False
        # assignment is consistent
        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        # least constraining values heuristics
        # variable x has words ['Egg', 'Tree', 'Sea']
        # find neighbors of x w self.crossword.neighbors(x)
        # then we get a variable y which has words ['Salt', 'Sun', 'Eel', 'Apple']
        # now get the overlaps self.crossword.overlaps[x,y] = (0, 0)
        # then check the character on index 0
        # Egg has one, Tree has none, Sea has two
        # return ['Sea', 'Egg', 'Tree']

        # IF any variable present in assignment already has a value, and therefore shouldn’t be counted
        # when computing the number of values ruled out for neighboring unassigned variables.

        # if a var is already in assignment remove it from neighbors
        neighbors = self.crossword.neighbors(var)
        for var in assignment:
            if var in neighbors:
                neighbors.remove(var)

        ruleout_count = {val: 0 for val in self.domains[var]}

        # ordered_domains = []
        for val_1 in self.domains[var]:
            # iterate thru neighboring variables and values
            for neighbor_var in neighbors:
                for val_2 in self.domains[neighbor_var]:
                    overlap = self.crossword.overlaps[var, neighbor_var]
                    # if val_1 rules out val_2 then increment ruleout_count
                    if overlap:
                        (i, j) = overlap
                        if val_1[i] != val_2[j]:
                            ruleout_count[val_1] += 1

        return sorted([x for x in ruleout_count],
                      key=lambda x: ruleout_count[x])
        # return in any order
        # return [x for x in self.domains[var]]

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        # returns a Variable object, that has fewest number of remaining values in its domain
        # minimum remaining value heuristic & degree heuristic

        # find unassigned variables and put it in a set
        unassigned = set(self.domains.keys()) - set(assignment.keys())

        # check number of remaining values in its domain and add to result
        result = {var: 0 for var in unassigned}
        for var in unassigned:
            result[var] = len(self.domains[var])

        return sorted([x for x in result],
                      key=lambda x: result[x], reverse=False)[0]
        # todo check highest degree

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        # if assignment complete return assignment
        if self.assignment_complete(assignment):
            return assignment
        # select a variable from list of unassigned var
        var = self.select_unassigned_variable(assignment)
        # loop thru the list of domain values
        for val in self.order_domain_values(var, assignment):
            assignment[var] = val
            # check if assignment is still consistent
            if self.consistent(assignment):
                # recursive backtracking search
                result = self.backtrack(assignment)
                #
                if result:
                    return result
            # remove the variable from assignment because it was fail
            assignment.pop(var)
        # return failure
        return None


def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()
