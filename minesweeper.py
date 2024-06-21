import itertools
import random


class Minesweeper():
    """
    Minesweeper game representation
    """

    def __init__(self, height=8, width=8, mines=8):

        # Set initial width, height, and number of mines
        self.height = height
        self.width = width
        self.mines = set()

        # Initialize an empty field with no mines
        self.board = []
        for i in range(self.height):
            row = []
            for j in range(self.width):
                row.append(False)
            self.board.append(row)

        # Add mines randomly
        while len(self.mines) != mines:
            i = random.randrange(height)
            j = random.randrange(width)
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        # At first, player has found no mines
        self.mines_found = set()

    def print(self):
        """
        Prints a text-based representation
        of where mines are located.
        """
        for i in range(self.height):
            print("--" * self.width + "-")
            for j in range(self.width):
                if self.board[i][j]:
                    print("|X", end="")
                else:
                    print("| ", end="")
            print("|")
        print("--" * self.width + "-")

    def is_mine(self, cell):
        i, j = cell
        return self.board[i][j]

    def nearby_mines(self, cell):
        """
        Returns the number of mines that are
        within one row and column of a given cell,
        not including the cell itself.
        """

        # Keep count of nearby mines
        count = 0

        # Loop over all cells within one row and column
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):

                # Ignore the cell itself
                if (i, j) == cell:
                    continue

                # Update count if cell in bounds and is mine
                if 0 <= i < self.height and 0 <= j < self.width:
                    if self.board[i][j]:
                        count += 1

        return count

    def won(self):
        """
        Checks if all mines have been flagged.
        """
        return self.mines_found == self.mines


class Sentence():
    """
    Logical statement about a Minesweeper game
    A sentence consists of a set of board cells,
    and a count of the number of those cells which are mines.
    """

    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        """
        Returns the set of all cells in self.cells known to be mines.
        """
        mines = set()
        # If the number of mines in a set is the same as length of set,
        # all cells in set must be mines...
        if len(self.cells) == self.count and self.count != 0:
            for cell in self.cells:
                mines.add(cell)
        
        return mines # Return set of mines found

    def known_safes(self):
        """
        Returns the set of all cells in self.cells known to be safe.
        """
        safes = set()
        if self.count == 0:
            for cell in self.cells:
                safes.add(cell)
        
        return safes # Return set of safe squares found

    def mark_mine(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be a mine.
        """
        # Check if cell included in sentence
        if cell in self.cells:
            self.cells.remove(cell) # Remove cell from sentence
            self.count -= 1 # This cell was a mine, hence one less in set.

    def mark_safe(self, cell):
        """
        Updates internal knowledge representation given the fact that
        a cell is known to be safe.
        """
        # Check if cell included in sentence
        if cell in self.cells:
            self.cells.remove(cell) # Remove cell from sentence
            # count unchanged.



class MinesweeperAI():
    """
    Minesweeper game player
    """

    def __init__(self, height=8, width=8):

        # Set initial height and width
        self.height = height
        self.width = width

        # Keep track of which cells have been clicked on
        self.moves_made = set()

        # Keep track of cells known to be safe or mines
        self.mines = set()
        self.safes = set()

        # List of sentences about the game known to be true
        self.knowledge = []

    def mark_mine(self, cell):
        """
        Marks a cell as a mine, and updates all knowledge
        to mark that cell as a mine as well.
        """
        self.mines.add(cell)
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        """
        Marks a cell as safe, and updates all knowledge
        to mark that cell as safe as well.
        """
        self.safes.add(cell)
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        """
        Called when the Minesweeper board tells us, for a given
        safe cell, how many neighboring cells have mines in them.

        This function should:
            1) mark the cell as a move that has been made
            2) mark the cell as safe
            3) add a new sentence to the AI's knowledge base
               based on the value of `cell` and `count`
            4) mark any additional cells as safe or as mines
               if it can be concluded based on the AI's knowledge base
            5) add any new sentences to the AI's knowledge base
               if they can be inferred from existing knowledge
        """

        self.moves_made.add(cell) # Mark the cell as a move that's been made

        self.mark_safe(cell) # Mark the cell as safe

        """
        3) The function should add a new sentence to the AI’s knowledge base,
        based on the value of cell and count, to indicate that count of the cell’s neighbors are mines.
        Be sure to only include cells whose state is still undetermined in the sentence.
        """
        unexplored_neighbours = set()
        mine_count = 0
        # Loop over all cells within one row and column of cell
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):
                if (i, j) in self.mines:
                    mine_count += 1
                # Confirm neighbouring cell is still undetermined
                if ((0 <= i < self.height) and (0 <= j < self.width)):
                    if (i,j) not in self.safes and (i,j) not in self.mines:
                        unexplored_neighbours.add((i,j))

        # Add sentence to knowledge base.
        new_sentence = Sentence(unexplored_neighbours, count - mine_count)
        self.knowledge.append(new_sentence)
        """
        4) If, based on any of the sentences in self.knowledge, 
        new cells can be marked as safe or as mines, then the function should do so.
        """
        
        while True:
            new_safes = set()
            new_mines = set()

            for sentence in self.knowledge:
                new_safes.update(sentence.known_safes())
                new_mines.update(sentence.known_mines())

            if not new_safes and not new_mines:
                break

            for safe in new_safes:
                self.mark_safe(safe)
            for mine in new_mines:
                self.mark_mine(mine)

            """
            5) If, based on any of the sentences in self.knowledge, 
            new sentences can be inferred (using the subset method described in the Background), 
            then those sentences should be added to the knowledge base as well.
            """
            new_knowledge = []
            for sentence1 in self.knowledge:
                for sentence2 in self.knowledge:
                    if sentence1 != sentence2 and sentence2.cells.issubset(sentence1.cells):
                        inferred_sentence = Sentence((sentence1.cells - sentence2.cells), (sentence1.count - sentence2.count))
                        if inferred_sentence not in self.knowledge:
                            new_knowledge.append(inferred_sentence)
            
            for item in new_knowledge:
                self.knowledge.append(item)

    def make_safe_move(self):   
        """
        Returns a safe cell to choose on the Minesweeper board.
        The move must be known to be safe, and not already a move
        that has been made.

        This function may use the knowledge in self.mines, self.safes
        and self.moves_made, but should not modify any of those values.
        """
        for cell in self.safes:
            # Confirm move not yet made
            if cell in self.moves_made:
                continue
            else:
                return cell
            
        # If all known safe moves have been made, return None
        return None

    def make_random_move(self):
        """
        Returns a move to make on the Minesweeper board.
        Should choose randomly among cells that:
            1) have not already been chosen, and
            2) are not known to be mines
        """
        # Initialise array for potential moves
        possibleMoves = []
        for i in range(self.height):
            for j in range(self.width):
                if (i,j) not in self.mines and (i,j) not in self.moves_made:
                    possibleMoves.append((i,j))
            
        # If no possible moves, return None
        if len(possibleMoves) == 0:
            return None
        else:
            return random.choice(possibleMoves)
    