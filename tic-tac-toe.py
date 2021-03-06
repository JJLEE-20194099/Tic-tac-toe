import numpy as np
import pickle

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
        new_state.data[i, j] = symbol
        return new_state
        
    def print_state(self):
        for i in range(BOARD_ROWS):
            print('-------------')
            out = '|'
            for j in range(BOARD_COLS):
                if (self.data[i, j] == 1):
                    tocken = '*'
                elif self.data[i, j] == -1:
                    tocken = 'X'
                
                else:
                    tocken = '0'
                out += tocken + ' | '
            print(out)
        print('-------------')

def get_all_states_impl(current_state, current_symbol, all_states):
    for i in range(BOARD_ROWS):
        for j in range(BOARD_COLS):
            if current_state.data[i, j] == 0:
                new_state = current_state.next_state(i, j, current_symbol)
                new_hash = new_state.hash()
                if new_hash not in all_states:
                    is_end = new_state.is_end()
                    all_states[new_hash] = (new_state, is_end)
                
                    if not is_end:
                        get_all_states_impl(new_state, -current_symbol, all_states)


def get_all_states():
    current_symbol = 1
    current_state = State()
    all_states = dict()
    all_states[current_state.hash()] = (current_state, current_state.is_end())
    get_all_states_impl(current_state, current_symbol, all_states)
    return all_states

all_states = get_all_states()

class Judger:
    def __init__(self, player1, player2):
        self.p1 = player1
        self.p2 = player2
        self.current_player = None
        self.p1_symbol = 1
        self.p2_symbol = -1
        self.p1.set_symbol(self.p1_symbol)
        self.p2.set_symbol(self.p2_symbol)
        self.current_state = State()

    def reset(self):
        self.p1.reset()
        self.p2.reset()
    
    def alternate(self):
        while True:
            yield self.p1
            yield self.p2
    
    def play(self, print_state = False):
        alternator = self.alternate()
        self.reset()
        current_state = State()
        self.p1.set_state(current_state)
        self.p2.set_state(current_state)

        if print_state:
            current_state.print_state()
        while(True):
            player = next(alternator)
            i, j, symbol = player.act()
            next_state_hash = current_state.next_state(i, j, symbol).hash()
            current_state, is_end = all_states[next_state_hash]
            self.p1.set_state(current_state)
            self.p2.set_state(current_state)
            if print_state:
                current_state.print_state()
            
            if is_end:
                return current_state.winner

class Player:
    def __init__(self, step_size, epsilon = 0.1):
        self.estimators = dict()
        self.step_size = step_size
        self.epsilon = epsilon
        self.states = []
        self.greedy = []
        self.symbol = 0

    

    def reset(self):
        self.states = []
        self.greedy = []
    
    def set_state(self, state):
        self.states.append(state)
        self.greedy.append(True)

    def set_symbol(self, symbol):
        self.symbol = symbol

        for hash_val in all_states:
            state, is_end = all_states[hash_val]
            if is_end:
                if state.winner == self.symbol:
                    self.estimators[hash_val] = 1.0
                elif state.winner == 0:
                    self.estimators[hash_val] = 0.5
                else:
                    self.estimators[hash_val] = 0
            else:
                self.estimators[hash_val] = 0.5
    
    def backup(self):
        states = [state.hash() for state in self.states]

        for i in reversed(range(len(states) - 1)):
            state = states[i]
            td_error = self.greedy[i] * (self.estimators[states[i + 1]] - self.estimators[state])
            self.estimators[state] += self.step_size * td_error

    def act(self):
        state = self.states[-1]
        next_states = []
        next_positions = []

        for i in range(BOARD_ROWS):
            for j in range(BOARD_COLS):
                if (state.data[i, j] == 0):
                    next_positions.append([i, j])
                    next_states.append(state.next_state(i, j, self.symbol).hash())
        
        if np.random.rand() < self.epsilon:
            action = next_positions[np.randonm.randint(len(next_positions))]
            action.append(self.symbol)
            self.greedy[-1] = False
            return action
    
        values = []
        for hash_val, pos in zip(next_states, next_positions):
            values.append((self.estimators[hash_val], pos))
        
        np.random.shuffle(values)

        values.sort(key = lambda x: x[0], reverse = True)
        action = values[0][1]
        action.append(self.symbol)
        return action
    
    def save_policy(self):
        with open('policy_%s.bin' % ('first' if self.symbol == 1 else 'second'), 'wb') as f:
            pickle.dump(self.estimators, f)
    
    def load_policy(self):
        with open('policy_%s.bin' % ('first' if self.symbol == 1 else 'second'), 'rb') as f:
            self.estimators = pickle.load(f)


class HumanPlayer:
    def __init__(self, **kwargs):
        self.symbol = None
        self.keys = ['q', 'w', 'e', 'a', 's', 'd', 'z', 'x', 'c']
        self.state = None
    def reset(self):
        pass

    def set_state(self, state):
        self.state = state
    
    def set_symbol(self, symbol):
        self.symbol = symbol
    
    def act(self):
        self.state.print_state()
        key = input("Input your position")
        data = self.keys.index(key)
        i = data // BOARD_COLS
        j = data % BOARD_COLS

        return i, j, self.symbol

def train(epochs, print_every_n = 500):
    player1 = Player(epsilon=0.01)
    player2 = Player(epsilon=0.01)
    judger = Judger(player1, player2)
    player1_win = 0.0
    player2_win = 0.0

    for i in range(1, epochs + 1):
        winner = judger.play(print_state=False)
        if (winner == 1):
            player1_win += 1
        
        if(winner == -1):
            player2_win += 1
        
        if i % print_every_n == 0:
            print('Epoch %d, player 1 winrate: %.02f, player 2 winrate: %.2f' %(i, player1_win / i, player2_win / i))
        
        player1.backup()
        player2.backup()
        judger.reset()
    
    player1.save_policy()
    player2.save_policy()
            



    


