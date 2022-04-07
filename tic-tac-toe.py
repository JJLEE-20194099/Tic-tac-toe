from audioop import reverse
import numpy as np

BOARD_ROWS = 3
BOARD_COLS = 3

BOAED_SIZE = BOARD_ROWS * BOARD_COLS

class State:
    def __init__(self):
        self.data = np.zeros((BOARD_ROWS, BOARD_COLS))
        self.winner = None
        self.hash_val = None
        self.end = None

    
    def hash(self):
        if self.hash_val is None:
            self.hash_val = 0
            for i in np.nditer(self.data):
                self.hash_val = self.hash_val * 3 + i + 1
        
        return self.hash_val
    
    def is_end(self):
        if self.end is not None:
            return self.end
        
        results = []

        for i in range(BOARD_ROWS):
            results.append(np.sum(self.data[i, :]))

        for i in range(BOARD_COLS):
            results.append(np.sum(self.data[:, i]))
        
        trace = 0
        reverse_trace = 0

        for i in range(BOARD_ROWS):
            trace += self.data[i, i]
            reverse_trace += self.data[i, BOARD_ROWS - 1 - i]
        
        results.append(trace)
        results.append(reverse_trace)

        for result in results:
            if result == 3:
                self.winner = 1
                self.end = True
                return self.end

            if (result == -3):
                self.winner = -1
                self.end = True
                return self.end
        
        sum_values = np.sum(np.abs(self.data))
        if sum_values == BOAED_SIZE:
            self.winner = 0
            self.end = True
            return self.end
        self.end = False
        return self.end
    
    def next_state(self, i, j, symbol):
        new_state = State()
        new_state.data = np.copy(self.data)
        new_state.data[i][j] = symbol
        return new_state
        
