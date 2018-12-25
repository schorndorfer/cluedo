from ortools.sat.python import cp_model
from collections import defaultdict
from enum import Enum


class Suspect(Enum):
    """
    The set of murder suspects.
    """
    MISS_SCARLET = 'MISS_SCARLET'
    PROF_PLUM = 'PROF_PLUM'
    MRS_PEACOCK = 'MRS_PEACOCK'
    MR_GREEN = 'MR_GREEN'
    COL_MUSTARD = 'COL_MUSTARD'
    MRS_WHITE = 'MRS_WHITE'


class Weapon(Enum):
    """
    The set of possible murder weapons.
    """
    CANDLESTICK = 'CANDLESTICK'
    DAGGER = 'DAGGER'
    LEAD_PIPE = 'LEAD_PIPE'
    REVOLVER = 'REVOLVER'
    ROPE = 'ROPE'
    WRENCH = 'WRENCH'


class Room(Enum):
    """
    The set of locations where the murder may have occurred.
    """
    KITCHEN = 'KITCHEN'
    BALLROOM = 'BALLROOM'
    CONSERVATORY = 'CONSERVATORY'
    DINING_ROOM = 'DINING_ROOM'
    BILLIARD_ROOM = 'BILLIARD_ROOM'
    LIBRARY = 'LIBRARY'
    LOUNGE = 'LOUNGE'
    HALL = 'HALL'
    STUDY = 'STUDY'


class Cluedo(object):
    """
    Cluedo! (https://en.wikipedia.org/wiki/Cluedo)
    """

    class Player(object):
        """
        A Cluedo player. Each player holds a certain number of cards, each of which indicates
        a murder suspect, weapon, or room. There is a special "player" called the "Murderer".
        The Murderer holds three cards, one of which is a suspect, one of which is a weapon, and
        one of which is a room. These are taken to be the actual details of the crime,
        and it is the job of the actual players to figure out what cards the Murderer holds.
        """

        # reserved name for the true murderer "player"
        Murderer = 'Murderer'

        def __init__(self, name, num_cards, model):
            self.__name = name
            self.__num_cards = num_cards
            self.__model = model
            self.__variable_map = {}

            # add suspect variables
            suspect_vars = {}
            for s in list(Suspect):
                var_name = "{}${}".format(name, s.value)
                suspect_vars[var_name] = self.model.NewBoolVar(var_name)

            # add weapon variables
            weapon_vars = {}
            for w in list(Weapon):
                var_name = "{}${}".format(name, w.value)
                weapon_vars[var_name] = self.model.NewBoolVar(var_name)

            # add room variables
            room_vars = {}
            for r in list(Room):
                var_name = "{}${}".format(name, r.value)
                room_vars[var_name] = self.model.NewBoolVar(var_name)

            # aggregate into a single collection
            self.__variable_map.update(suspect_vars)
            self.__variable_map.update(weapon_vars)
            self.__variable_map.update(room_vars)

            # add a constraint that there can only by <num_cards> true values for a given player
            self.model.AddSumConstraint(self.__variable_map.values(), num_cards, num_cards)

            # if this is the "murderer", then add another constraint that
            # there must be one and only one of each suspect, weapon, and room
            if self.name == Cluedo.Player.Murderer:
                assert num_cards == 3
                self.model.Add(sum(suspect_vars.values()) == 1)
                self.model.Add(sum(weapon_vars.values()) == 1)
                self.model.Add(sum(room_vars.values()) == 1)

        @property
        def name(self):
            return self.__name

        @property
        def num_cards(self):
            return self.__num_cards

        @property
        def model(self):
            return self.__model

        @property
        def variable_map(self):
            return self.__variable_map

    class SolutionCollector(cp_model.CpSolverSolutionCallback):
        """
        A callback class that stores intermediate solutions to the SAT solver.
        Instances of this class can also be used to store "packed" representations
        of solutions, where a packed representation is a variable mapped to the set of
        possible values it can contain, after running the constraint solver.

        Each variable indicates whether it is known that a given player holds a given suspect,
        weapon, or room card. For example, if it is known that 'Will' holds the 'Kitchen' card,
        then variable 'Will$KITCHEN' will be set to True.

        """

        def __init__(self, variables):
            cp_model.CpSolverSolutionCallback.__init__(self)
            self.__variables = variables
            self.__solutions = []

        def Solutions(self):
            return self.__solutions.copy()

        def SolutionCount(self):
            return len(self.__solutions)

        def OnSolutionCallback(self):
            pass

        def NewSolution(self):
            solution = {}
            for key, value in self.__variables.items():
                solution[key] = self.Value(value)
            self.__solutions.append(solution)

        def PackedSolutions(self, player_name):
            ret_val = {}
            ret_val[Suspect] = defaultdict(set)
            ret_val[Weapon] = defaultdict(set)
            ret_val[Room] = defaultdict(set)

            suspects = list(Suspect).copy()
            weapons = list(Weapon).copy()
            rooms = list(Room).copy()

            for sol in self.Solutions():
                for key, value in sol.items():
                    for s in suspects:
                        if key == f"{player_name}${s.value}":
                            ret_val[Suspect][s.value].add(value)
                    for w in weapons:
                        if key == f"{player_name}${w.value}":
                            ret_val[Weapon][w.value].add(value)
                    for r in rooms:
                        if key == f"{player_name}${r.value}":
                            ret_val[Room][r.value].add(value)
                remove_suspects = [s for s in suspects if len(ret_val[Suspect][s.value]) > 1]
                suspects = [s for s in suspects if s not in remove_suspects]
                remove_weapons = [w for w in weapons if len(ret_val[Weapon][w.value]) > 1]
                weapons = [w for w in weapons if w not in remove_weapons]
                remove_rooms = [r for r in rooms if len(ret_val[Room][r.value]) > 1]
                rooms = [r for r in rooms if not r in remove_rooms]
                if not (suspects) and not (weapons) and not (rooms):
                    break

            return ret_val

    def __init__(self, players_spec):
        """
        Initialize the Cluedo game instance.
        @param: players_spec A specification of each player name along with the number of cards she holds.
        """
        self.__players_spec = players_spec
        self.__model = cp_model.CpModel()
        self.__solver = None
        self.__solution_collector = None
        self.__players = {}  # dictionary from name -> Player instance

        # initialize the Murderer Player
        self.__players[Cluedo.Player.Murderer] = Cluedo.Player(Cluedo.Player.Murderer, 3, self.model)

        # initialize the other Players
        for name, card_count in self.__players_spec:
            self.__players[name] = Cluedo.Player(name, card_count, self.model)

        # put all the variables into a single collection
        self.__variable_map = {}
        self.__variable_map.update(self.__players[Cluedo.Player.Murderer].variable_map)
        for name, player in self.__players.items():
            self.__variable_map.update(player.variable_map)

        # Add constraint that at most one player can have a particular card
        pvar_maps = [p.variable_map for p in list(self.__players.values())]
        pvars = [list(vm.values()) for vm in pvar_maps]
        for v in zip(*pvars):
            self.__model.AddBoolXOr(v)

    def add_constraint(self, player_name, item, value=True):
        self.model.Add(self.variable_map[f"{player_name}${item.value}"] == value)

    def add_or_constraint(self, player_name, items):
        constraint_vars = []
        for item in items:
            constraint_vars.append(self.variable_map[f"{player_name}${item.value}"])
        self.model.AddBoolOr(constraint_vars)

    def solve(self, time_limit=None):
        # create the solver and solve the problem
        self.__solver = cp_model.CpSolver()
        if time_limit:
            # Sets a time limit of 10 seconds",
            self.__solver.parameters.max_time_in_seconds = time_limit

        self.__solution_collector = Cluedo.SolutionCollector(self.variable_map)
        status = self.__solver.SearchForAllSolutions(self.__model, self.__solution_collector)
        return self.__solution_collector.SolutionCount()

    def player(self, player_name=Player.Murderer):
        return self.solution_collector.PackedSolutions(player_name)

    @property
    def players(self):
        player_names = [name for name, _ in self.__players.items()]
        player_assignments = {}
        for player_name in player_names:
            player_assignments[player_name] = self.player(player_name)
        return player_assignments

    @property
    def player_names(self):
        return [name for name, _ in self.__players.items()]

    @property
    def model(self):
        return self.__model

    @property
    def variable_map(self):
        return self.__variable_map

    @property
    def solver(self):
        return self.__solver

    @property
    def solution_collector(self):
        return self.__solution_collector




