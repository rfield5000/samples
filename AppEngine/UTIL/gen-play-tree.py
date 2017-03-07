# Generate tic-tac-toe position evaluation tree for
# an automated player.

from optparse import OptionParser

verbose_output = True

class Position:

    def __init__(self, state, value, player, moves):
        self.state = state
        self.value = value
        self.player = player
        self.moves = moves

    def describe(self):
        return ("state: %6d value: [%s] player: [%s] moves: [%s]"
                % (self.state,
                   repr(self.value),
                   repr(self.player),
                   repr(self.moves)))

# turn a state encoded as an integer into a vector
# of moves, with 0 for empty, 1 for the human player,
# 2 for the machine.
#
# The position is encoded base 3 with upper left as units
# and lower right as 3^8.
def explode_state(state):
    exp = []
    for K in range(9):
        exp.append(state % 3)
        state = state / 3
    if verbose_output:
        print "state", state
        print "exp", state, exp
    return exp

# determine if a state is a winner from a list of known
# winning positions
def winner(state, player):
    wins = [[0, 1, 2], [3, 4, 5], [6, 7, 8],
            [0, 3, 6], [1, 4, 7], [2, 5, 8],
            [0, 4, 8], [2, 4, 6]]
    x = explode_state(state)
    for t in wins:
        if (player == x[t[0]]) and (player == x[t[1]]) and (player == x[t[2]]):
            if verbose_output:
                print "WINNER", player, state, t, x
            return True
    if verbose_output:
        print "NOT WINNER", player, state, x
    return False

# player 1 is the human player
def other_player(player):
    return 3 - player

# the values for the human player
def draw_value(player):
    return 0

def win_value(player):
    if player == 1:
        return 1
    else:
        return -1



def moves_possible(state):
    board = explode_state(state)
    possible = [n for n in range(9) if board[n] == 0]
    return possible

# save evaluations of positions here
cached = {}

def evaluate_positions(state, player, positions):
    if verbose_output:
        print "EVALUATE ", state, player
    if cached.has_key(state):
        if verbose_output:
            print "CACHED"
        return cached[state]
    value = draw_value(player)
    moves = moves_possible(state)
    if winner(state, player):
        pos = Position(state, win_value(player), player, [])
        positions.append(pos)
        value = win_value(player)
    elif len(moves) > 0:
        results = []
        for k in moves:
            new_state = state + player*(3**k)
            results.append([k, evaluate_positions(new_state, other_player(player), positions)])
        counts = {}
        for rs in results:
            m = rs[1]
            if verbose_output:
                print "m", m
            if counts.has_key(m):
                counts[m].append(rs[0])
            else:
                counts[m] = [rs[0]]
        w = win_value(player)
        d = draw_value(player)
        l = win_value(other_player(player))
        for k in [w, d, l]:
            if counts.has_key(k):
                pos = Position(state, k, player, counts[k])
                value = k
                positions.append(pos)
                break
    else:
        # no legal moves so the value is that which is
        # the value of the position as is
        pos_value = draw_value(player)
        if winner(state, other_player(player)):
            if verbose_output:
                print "OTHER WINS WITH NO MOVE"
            pos_value = win_value(other_player(player))
        pos = Position(state, pos_value, player, [])
        positions.append(pos)
        value = pos_value
    if verbose_output:
        print "RETURN", value
    cached[state] = value
    return value

def dump_positions(positions):
    outfile = open('moves.txt', 'w')
    for p in (positions):
        if verbose_output:
            print p.describe()
        print >>outfile, p.state, p.player, p.value, p.moves

parser = OptionParser()
parser.add_option("-f", "--file", dest="filename",
                  help="write report to FILE", metavar="FILE")
parser.add_option("-q", "--quiet",
                  action="store_false", dest="verbose", default=True,
                  help="don't print status messages to stdout")

(options, args) = parser.parse_args()

verbose_output = options.verbose

positions = []


# a little bit of demonstration, in lieu of unit tests
if verbose_output:
    print explode_state(0)
    print explode_state(3**8 + 2*(3**7))
    print moves_possible(0)
    print moves_possible(3 + 81 + 2*729)
    print 5450, moves_possible(5450)
    print 5450 + 2*(3**3)
    print 5450 + 2*(3**8)
    print 5450 + 2*(3**8) + (3**3)
    print winner(0, 1)
    print winner(1 + 3 + 9, 1)
    print winner(1 + 6 + 9, 2)
    print winner(2*(27 + 81 + 243), 2)

evaluate_positions(0, 1, positions)

if verbose_output:
    print "DUMP"
    print repr(positions)

dump_positions(positions)

