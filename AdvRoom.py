# File: AdvRoom.py

"""
This module is responsible for modeling a single room in Adventure.
"""

# Constants

MARKER = "-----"

class AdvRoom:
    def __init__(self, name, shortdesc, longdesc, passages):
        """Creates a new room with the specified attributes."""
        self._name = name
        self._shortdesc = shortdesc
        self._longdesc = longdesc
        self._passages = passages
        self._visited = False
        self._objects = []

    def getName(self):
        """Returns the name of this room."""
        return self._name

    def getShortDescription(self):
        """Returns a one-line short description of this room."""
        return self._shortdesc

    def getLongDescription(self):
        """Returns the list of lines describing this room."""
        return self._longdesc

    #removed getNextRoom method because it was redundant with getPassages and my decomposition within AdvGame

    def getPassages(self):
        return self._passages #returns list of tuples

    def setVisited(self, visited):    #sets a room if visited or not
        self._visited = visited

    def hasBeenVisited(self):       #determines if a room has been visited
        return self._visited

    def addObject(self, obj):       #adds object to room
        self._objects.append(obj)

    def removeObject(self, obj):   #removes object from room
        self._objects.remove(obj)

    def containsObject(self, obj):     #checks if room contains object
        return obj in self._objects

    def getContents(self):
        return self._objects   # returns list of object contents



    @staticmethod
    def readRoom(f):
        """Reads a room from the data file."""
        name = f.readline().rstrip()
        if name == "":
            return None
        shortdesc = f.readline().rstrip()
        longdesc = []
        while True:
            line = f.readline().rstrip()
            if line == MARKER:
                break
            longdesc.append(line)
        passages = []
        while True:
            line = f.readline().rstrip()
            if line == "":
                break
            colon = line.find(":")
            if colon == -1:
                raise ValueError("Missing colon in " + line)
            verb = line[:colon].strip().upper()
            slash = line.find("/")
            next_room = None
            key = None

            if slash == -1:
                next_room = line[colon + 1:].strip()
            else:
                next_room = line[colon + 1: slash].strip()
                key = line[slash + 1:].strip()

            tuple_passages = (verb, next_room, key)
            passages.append(tuple_passages)
        return AdvRoom(name, shortdesc, longdesc, passages)
