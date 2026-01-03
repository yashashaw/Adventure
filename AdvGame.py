# File: AdvGame.py

"""
This module defines the AdvGame class, which records the information
necessary to play a game.
"""

from AdvRoom import AdvRoom
from tokenscanner import TokenScanner
from AdvObject import AdvObject

# Constants
HELP_TEXT = [
    "Welcome to Adventure!",
    "Somewhere nearby is Colossal Cave, where others have found fortunes in",
    "treasure and gold, though it is rumored that some who enter are never",
    "seen again.  Magic is said to work in the cave.  I will be your eyes",
    "and hands.  Direct me with natural English commands; I don't understand",
    "all of the English language, but I do a pretty good job.",
    "",
    "It's important to remember that cave passages turn a lot, and that",
    "leaving a room to the north does not guarantee entering the next from",
    "the south, although it often works out that way.  You'd best make",
    "yourself a map as you go along.",
    "",
    "Much of my vocabulary describes places and is used to move you there.",
    "To move, try words like IN, OUT, EAST, WEST, NORTH, SOUTH, UP, or DOWN.",
    "I also know about a number of objects hidden within the cave which you",
    "can TAKE or DROP.  To see what objects you're carrying, say INVENTORY.",
    "To reprint the detailed description of where you are, say LOOK.  If you",
    "want to end your adventure, say QUIT."
]

class AdvGame:

    def __init__(self, prefix):
        self._prefix = prefix
        self._rooms = {}
        self._start_room = None

        with open(prefix + "Rooms.txt") as f:
            while True:
                room = AdvRoom.readRoom(f)
                if room is None:
                    break
                name = room.getName()
                if self._start_room is None:
                    self._start_room = name
                self._rooms[name] = room

    def getObjects(self):   #returns object name with a dictionary of what it has (name, description, location)
        self._objects = {}
        try:
            with open(self._prefix + "Objects.txt") as f:
                while True:
                    object = AdvObject.readObject(f)
                    if object is None:
                        break
                    name = object.getName()
                    self._objects[name] = object
                return self._objects
        except FileNotFoundError:
            return None

    def getSynonyms(self):      # returns dictionary of synonyms from the file
        self._synonyms = {}
        try:
            with open(self._prefix + "Synonyms.txt") as f:
                for line in f:
                    index = line.find("=")
                    ch = line[:index]
                    word = line[index + 1:].strip()
                    self._synonyms[ch] = word
                return self._synonyms
        except FileNotFoundError:
            return self._synonyms

    def printRooms(self, room):      #takes the room and either prints the long or short description
        if room.hasBeenVisited():
            print(room.getShortDescription())
        else:
            for line in room.getLongDescription():
                print(line)
            room.setVisited(True)

    def assignObjects(self, objs, inventory):        #assigns objects to its initial room locations (including PLAYER)
        if objs is not None:
            for obj in objs.values():
                objname = obj.getName()
                objlocation = obj.getInitialLocation()
                if objlocation in self._rooms:
                    self._rooms[objlocation].addObject(objname)
                if objlocation == "PLAYER":
                    inventory.append(objname)

    def printObjectDescription(self, objs, room):     #prints obj description if obj is in that room
        if objs is not None:
            for objname in room.getContents():
                if objname in objs:
                    print("There is " + objs[objname].getDescription() + " here.")

    def determineNextPassage(self, command, passages, inventory):     #determines which passage to go thru based upon items in inventory
        for passage in passages:
            if command == passage[0]:
                if passage[2] is None:
                    return passage[1]
                else:
                    try:
                        ind = inventory.index(passage[2])
                    except ValueError:
                        ind = -1
                    if ind != -1:
                        return passage[1]
                    else:
                        continue

    def moveToRoom(self, room_name, inventory, objs, force_long_desc=False, from_forced=False):   #move to a room and handle any forced passages. Returns the final room after all forced movements.

        room = self._rooms[room_name]

        # check if this room has a forced passage
        passages = room.getPassages()
        has_forced = any(passage[0] == "FORCED" for passage in passages)

        if has_forced:
            # for forced rooms, always show long description (the message)
            room.setVisited(False)
            self.printRooms(room)

            for passage in passages:
                if passage[0] == "FORCED":
                    next_room = self.determineNextPassage("FORCED", passages, inventory)
                    if next_room == "EXIT":
                        return None
                    #recursively move to forced destination, but don't print its description
                    return self.moveToRoom(next_room, inventory, objs, force_long_desc=False, from_forced=True)

        else:
            #normal room
            if force_long_desc:
                room.setVisited(False)

            #only print description if we're not arriving via a forced passage
            if not from_forced:
                self.printRooms(room)
                self.printObjectDescription(objs, room)

        return room

    def handleMovement(self, command, room, inventory, objs):    #handle movement commands and return the new room

        passages = room.getPassages()
        next_room = self.determineNextPassage(command, passages, inventory)

        if next_room is None:
            # check for * passage
            for passage in passages:
                if passage[0] == "*":
                    wildcard_dest = self.determineNextPassage("*", passages, inventory)
                    if wildcard_dest:
                        return self.moveToRoom(wildcard_dest, inventory, objs)
                    break
            print("I don't know how to apply that word here.")
            return room
        else:
            return self.moveToRoom(next_room, inventory, objs)

    def parseInput(self, answer):     # parse user input and return (command, item) tuple

        synonyms = self._synonyms  # Use synonyms
        scanner = TokenScanner(answer)
        scanner.ignoreWhitespace()

        inputlist = []
        while scanner.hasMoreTokens():
            token = scanner.nextToken()
            inputlist.append(token)

        # apply synonyms
        for i in range(len(inputlist)):
            if inputlist[i] in synonyms:
                inputlist[i] = synonyms[inputlist[i]]

        command = inputlist[0].upper() if len(inputlist) > 0 else ""
        item = inputlist[1].upper() if len(inputlist) > 1 else None

        return command, item

    def handleLook(self, room, objs):   #handle look command
        for line in room.getLongDescription():
            print(line)
        self.printObjectDescription(objs, room)

    def handleHelp(self):   #handle help command
        for line in HELP_TEXT:
            print(line)

    def handleInventory(self, inventory, objs):   #handle inventory command
        if len(inventory) == 0:
            print("You are empty-handed")
        else:
            print("You are carrying:")
            for item_name in inventory:
                if item_name in objs:
                    print("\t" + objs[item_name].getDescription())

    def handleDrop(self, item, room, inventory):   #handle drop command
        if item is None:
            print("You must specify what to drop.")
        elif item in inventory:
            room.addObject(item)
            inventory.remove(item)
            print("Dropped")
        else:
            print("I don't know what that is.")

    def handleTake(self, item, room, inventory):    #handle take command
        if item is None:
            print("You must specify what to take.")
        elif room.containsObject(item):
            inventory.append(item)
            room.removeObject(item)
            print("Taken")
        else:
            print("I don't know what that is.")

    def processCommand(self, command, item, room, inventory, objs): #process a single command and return the next room. Returns none to signal game should quit
        if command == "QUIT":
            return None
        elif command == "LOOK":
            self.handleLook(room, objs)
            return room
        elif command == "HELP":
            self.handleHelp()
            return room
        elif command == "INVENTORY":
            self.handleInventory(inventory, objs)
            return room
        elif command == "DROP":
            self.handleDrop(item, room, inventory)
            return room
        elif command == "TAKE":
            self.handleTake(item, room, inventory)
            return room
        else:
            return self.handleMovement(command, room, inventory, objs)

    def run(self):     #main game loop
        inventory = []
        objs = self.getObjects()
        self._synonyms = self.getSynonyms()  # Cache synonyms
        self.assignObjects(objs, inventory)

        room = self._rooms[self._start_room]
        self.printRooms(room)
        self.printObjectDescription(objs, room)

        while room is not None:
            answer = input("> ").strip().upper()
            command, item = self.parseInput(answer)

            if not command:
                continue

            room = self.processCommand(command, item, room, inventory, objs)