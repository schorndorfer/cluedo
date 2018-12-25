from enum import Enum


class Suspect(Enum):
    """
    The set of murder suspects.
    """
    COL_MUSTARD = 'COL_MUSTARD'
    MISS_SCARLET = 'MISS_SCARLET'
    MR_GREEN = 'MR_GREEN'
    MRS_PEACOCK = 'MRS_PEACOCK'
    MRS_WHITE = 'MRS_WHITE'
    PROF_PLUM = 'PROF_PLUM'


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
    BALLROOM = 'BALLROOM'
    BILLIARD_ROOM = 'BILLIARD_ROOM'
    CONSERVATORY = 'CONSERVATORY'
    DINING_ROOM = 'DINING_ROOM'
    HALL = 'HALL'
    KITCHEN = 'KITCHEN'
    LIBRARY = 'LIBRARY'
    LOUNGE = 'LOUNGE'
    STUDY = 'STUDY'


class Player(object):
    """
    A Cluedo player
    """
    def __init__(self, name, num_cards):
        self.__name = name
        self.__num_cards = num_cards

    @property
    def name(self):
        return self.__name

    @property
    def num_cards(self):
        return self.__num_cards


class Cluedo(object):
    """
    Cluedo! (https://en.wikipedia.org/wiki/Cluedo)
    """
    def __init__(self, players):
        self.__players = players

    @property
    def players(self):
        return self.__players

    @property
    def player_names(self):
        return [player.name for player in self.__players]
