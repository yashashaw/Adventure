# File: AdvObject.py

"""
This module defines a class that models an object in Adventure.
"""

class AdvObject:

    def __init__(self, name, description, location):
        self._name = name
        self._description = description
        self._location = location

    def getName(self):
        return self._name

    def getDescription(self):
        return self._description

    def getInitialLocation(self):
        return self._location

    @staticmethod
    def readObject(f):

        while True:     #use while true loop to continue after the blank line to the next object
            name = f.readline()
            if name == "":
                return None
            name = name.strip()
            if name:
                break

        description = f.readline().rstrip()
        location = f.readline().rstrip()

        return AdvObject(name, description, location)