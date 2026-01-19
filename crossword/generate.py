import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
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
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
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
        items = self.domains.items()
        for variable, domain in items:
            valid_words = set()
            let = variable.length
            for word in domain:
                if len(word) == let:
                    valid_words.add(word)

            self.domains[variable] = valid_words

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised = False
        to_remove = []
        for variable1 in self.domains[x]:
            for variable2 in self.domains[y]:
                if (x, y) in self.crossword.overlaps:
                    if self.crossword.overlaps[x, y] is None:
                        continue
                    else:
                        i, j = self.crossword.overlaps[x, y]
                        if variable1[i] == variable2[j]:
                            break
            else:
                to_remove.append(variable1)

        for item in to_remove:
            self.domains[x].remove(item)
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
        queue = []
        if arcs is None:
            for variable1 in self.crossword.variables:
                check_neighbor = self.crossword.neighbors(variable1)
                for neighbor in check_neighbor:
                    queue.append((variable1, neighbor))
        else:
            queue = arcs

        while len(queue) > 0:
            arc = queue.pop(0)
            var1, var2 = arc
            rev = self.revise(var1, var2)
            if rev == True:
                check_neighbor1 = self.crossword.neighbors(var1)
                for neighbor in check_neighbor1:
                    if neighbor != var2:
                        if (neighbor, var1) not in queue:
                            queue.append((neighbor, var1))

        for domain in self.domains:
            if len(self.domains[domain]) == 0:
                return False

        return True

    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for variable1 in self.crossword.variables:
            if variable1 not in assignment:
                return False
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        consist = set()
        for variable, word in assignment.items():
            length_w = len(word)

            if word in consist:
                return False
            else:
                consist.add(word)

            if length_w != variable.length:
                return False

            for overlap1, overlap2 in self.crossword.overlaps:
                if overlap1 in assignment and overlap2 in assignment:
                    assign_ov1 = assignment[overlap1]
                    assign_ov2 = assignment[overlap2]
                    if self.crossword.overlaps[overlap1, overlap2] is not None:
                        i, j = self.crossword.overlaps[overlap1, overlap2]
                        if assign_ov1[i] != assign_ov2[j]:
                            return False

        return True

    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        dict = {}
        check_neighbor1 = self.crossword.neighbors(var)
        for domain in self.domains[var]:
            if domain not in dict:
                dict[domain] = 0.
            for neighbor in check_neighbor1:
                i, j = self.crossword.overlaps[var, neighbor]
                if neighbor not in assignment:
                    for value in self.domains[neighbor]:
                        if value[i] != domain[j]:
                            dict[domain] += 1

        sort = sorted(dict, key=lambda x: (dict[x], len(x)) if x in dict else (x, len(x)))

        return sort

    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        best_variable = None
        min_remaining_values = float('inf')
        for variable1 in self.crossword.variables:
            if variable1 not in assignment:
                if len(self.domains[variable1]) < min_remaining_values:
                    best_variable = variable1
                    min_remaining_values = len(self.domains[variable1])
        return best_variable

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        check = True
        if len(assignment) == len(self.crossword.variables):
            return assignment
        for variable1 in self.crossword.variables:
            if variable1 not in assignment:
                for word in self.domains[variable1]:
                    check = True
                    assignment[variable1] = word
                    for overlap1, overlap2 in self.crossword.overlaps:
                        if overlap1 in assignment and overlap2 in assignment:
                            assign_ov1 = assignment[overlap1]
                            assign_ov2 = assignment[overlap2]
                            if self.crossword.overlaps[overlap1, overlap2] is not None:
                                i, j = self.crossword.overlaps[overlap1, overlap2]
                                if assign_ov1[i] != assign_ov2[j]:
                                    check = False
                    if check == True:
                        result = self.backtrack(assignment)
                        if result is not None:
                            return result
                        del assignment[variable1]                 
                                    
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
