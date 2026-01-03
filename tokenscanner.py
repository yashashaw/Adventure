"""
This module implements a token scanner abstraction.
"""

class ScannerError(Exception):
    pass

class TokenScanner:

# Public constants

    EOF = "EOF"
    SEPARATOR = "SEPARATOR"
    WORD = "WORD"
    NUMBER = "NUMBER"
    STRING = "STRING"
    OPERATOR = "OPERATOR"

# Private constants

    _MAX_TO_STRING_LENGTH = 20
    _INITIAL_STATE = 0
    _BEFORE_DECIMAL_POINT = 1
    _AFTER_DECIMAL_POINT = 2
    _STARTING_EXPONENT = 3
    _FOUND_EXPONENT_SIGN = 4
    _SCANNING_EXPONENT = 5
    _LEADING_ZERO = 6
    _SCANNING_HEX = 7
    _FINAL_STATE = 8

# Constructor

    def __init__(self, input_str=""):
        self._ignoreWhitespaceFlag = False
        self._ignoreCommentsFlag = False
        self._scanNumbersFlag = False
        self._scanStringsFlag = False
        self._operators = set()
        self._wordChars = ""
        self.setInput(input_str)

# Sets the scanner input to the specified string or file.

    def setInput(self, input_source):
        self._savedTokens = [ ]
        self._savedCharacters = [ ]
        self._cp = 0
        if type(input_source) is str:
            self._file = None
            self._buffer = input_source
        else:
            self._file = input_source
            self._buffer = ""

# Returns True if there are more tokens for this scanner to read.

    def hasMoreTokens(self):
        token = self.nextToken()
        self.saveToken(token)
        return token != ""

# Returns the next token from this scanner.

    def nextToken(self):
        if len(self._savedTokens) != 0:
            return self._savedTokens.pop()
        while True:
            if self._ignoreWhitespaceFlag:
                self.skipSpaces()
            ch = self.getChar()
            if ch == "":
                return ""
            if ch == "/" and self._ignoreCommentsFlag:
                ch = self.getChar()
                if ch == "/":
                    ch = self.getChar()
                    while ch != "\n" and ch != "\r" and ch != "":
                        ch = self.getChar()
                    continue
                elif ch == "*":
                    prev = ""
                    while ch != "" and not(prev == "*" and ch == "/"):
                        prev = ch
                        ch = self.getChar()
                    continue
                self.saveChar(ch)
                ch = "/"
            if (ch == "'" or ch == "\"") and self._scanStringsFlag:
                self.saveChar(ch)
                return self.scanString()
            if ch.isdigit() and self._scanNumbersFlag:
                self.saveChar(ch)
                return self.scanNumber()
            if self.isWordCharacter(ch):
                self.saveChar(ch)
                return self.scanWord()
            op = ch
            while self.isOperatorPrefix(op):
                ch = self.getChar()
                if ch == "": break
                op += ch
            while len(op) > 1 and not self.isOperator(op):
                self.saveChar(op[-1])
                op = op[0:-1]
            return op

# Saves one token to reread later.

    def saveToken(self, token):
        self._savedTokens.append(token)

# Reads the next token and makes sure it matches the string expected.

    def verifyToken(self, expected):
        token = self.nextToken()
        if token != expected:
            msg = ""
            if token == "":
                msg = "Missing " + expected
            else:
                msg = "Found " + token + " when expecting " + expected
            raise ScannerError(msg)

# Causes the scanner to ignore whitespace characters.

    def ignoreWhitespace(self):
        self._ignoreWhitespaceFlag = True

# Tells the scanner to ignore comments.

    def ignoreComments(self):
        self._ignoreCommentsFlag = True

# Controls how the scanner treats tokens that begin with a digit.

    def scanNumbers(self):
        self._scanNumbersFlag = True

# Controls how the scanner treats tokens enclosed in quotation marks.

    def scanStrings(self):
        self._scanStringsFlag = True

# Adds the characters in chars to the set of characters that are acceptable
# in an identifier.

    def addWordCharacters(self, chars):
        self._wordChars += chars

# Defines a new multicharacter operator.

    def addOperator(self, op):
        self._operators.add(op)

# Returns the current position of the scanner in the buffer stream.

    def getPosition(self):
        nTokens = len(self._savedTokens)
        if nTokens == 0:
            return self._cp
        elif nTokens == 1:
            return self._cp - len(self._savedTokens[0])
        else:
            raise ScannerError("Internal error: getPosition after two saves")

# Returns True if the token is a valid identifier.

    def isValidIdentifier(self, token):
        if len(token) == 0:
            return False
        ch = token[0]
        if not self.isWordCharacter(ch) or ch.isdigit():
            return False
        for ch in token:
            if not self.isWordCharacter(ch):
                return False
        return True

# Returns True if the character is valid in a word.

    def isWordCharacter(self, ch):
        return ch.isalnum() or self._wordChars.find(ch) != -1

# Returns True if the character ch is a hexadecimal digit.

    def isHexDigit(self, ch):
        return len(ch) == 1 and "0123456789ABCDEFabcdef".find(ch) != -1

# Returns the type of this token.

    def getTokenType(self, token):
        if token == "":
            return TokenScanner.EOF
        ch = token[0]
        if ch.isspace():
            return TokenScanner.SEPARATOR
        if ch == "'" or ch == '"':
            return TokenScanner.STRING
        if ch.isdigit():
            return TokenScanner.NUMBER
        if self.isWordCharacter(ch):
            return TokenScanner.WORD
        return TokenScanner.OPERATOR

# Returns the actual string value corresponding to a string token.

    def getStringValue(self, token):
        return eval(token)

# Returns the numeric value corresponding to a number token.

    def getNumberValue(self, token):
        return float(token)

# Returns a printable representation of this scanner.

    def __str__(self):
        s = type(self).__name__ 
        if len(self._buffer) < self._MAX_TO_STRING_LENGTH:
            s += "(\"" + self._buffer + "\")"
        else:
            s += "(" + str(len(self._buffer)) + " chars)"
        return s

# Skips over any whitespace characters before the next token.

    def skipWhitespace(self):
        while True:
            ch = self.getChar()
            if ch == "" or not ch.isspace():
                self.saveChar(ch)
                break

# Private methods 

    def getChar(self):
        if len(self._savedCharacters) == 0:
            if self._cp >= len(self._buffer):
                if self._file is None:
                    return ""
                self._buffer = self._file.readline()
                if self._buffer == "":
                    return ""
                self._cp = 0
            self._cp += 1
            return self._buffer[self._cp - 1]
        else:
            return self._savedCharacters.pop()

    def saveChar(self, ch):
        self._savedCharacters.append(ch)

    def skipSpaces(self):
        while True:
            ch = self.getChar()
            if ch == "":
                return
            if not ch.isspace() or ch in self._operators:
                self.saveChar(ch)
                return

    def scanWord(self):
        token = ""
        while True:
            ch = self.getChar()
            if ch == "": break
            if not self.isWordCharacter(ch):
                self.saveChar(ch)
                break
            token += ch
        return token

    def scanNumber(self):
        token = ""
        state = self._INITIAL_STATE
        while state != self._FINAL_STATE:
            ch = self.getChar()
            xch = "e"
            if state == self._INITIAL_STATE:
                if ch == "0":
                    state = self._LEADING_ZERO
                else:
                    state = self._BEFORE_DECIMAL_POINT
            elif state == self._BEFORE_DECIMAL_POINT:
                if ch == ".":
                    state = self._AFTER_DECIMAL_POINT
                elif ch == "E" or ch == "e":
                    state = self._STARTING_EXPONENT
                    xch = ch
                elif not ch.isdigit():
                    self.saveChar(ch)
                    state = self._FINAL_STATE
            elif state == self._AFTER_DECIMAL_POINT:
                if ch == "E" or ch == "e":
                    state = self._STARTING_EXPONENT
                    xch = ch
                elif not ch.isdigit():
                    self.saveChar(ch)
                    state = self._FINAL_STATE
            elif state == self._STARTING_EXPONENT:
                if ch == "+" or ch == "-":
                    state = self._FOUND_EXPONENT_SIGN
                elif ch.isdigit():
                    state = self._SCANNING_EXPONENT
                else:
                    self.saveChar(ch)
                    state = self._FINAL_STATE
            elif state == self._FOUND_EXPONENT_SIGN:
                if ch.isdigit():
                    state = self._SCANNING_EXPONENT
                else:
                    self.saveChar(ch)
                    self.saveChar(xch)
                    state = self._FINAL_STATE
            elif state == self._SCANNING_EXPONENT:
                if not ch.isdigit():
                    self.saveChar(ch)
                    state = self._FINAL_STATE
            elif state == self._LEADING_ZERO:
                if ch == "x" or ch == "X":
                    state = self._SCANNING_HEX
                elif ch == ".":
                    state = self._AFTER_DECIMAL_POINT
                elif ch == "E" or ch == "e":
                    state = self._STARTING_EXPONENT
                    xch = ch
                elif not ch.isdigit():
                    self.saveChar(ch)
                    state = self._FINAL_STATE
            elif state == self._SCANNING_HEX:
                if not self.isHexDigit(ch): 
                    self.saveChar(ch)
                    state = self._FINAL_STATE
            else:
                state = self._FINAL_STATE
            if state != self._FINAL_STATE:
                token += ch
        return token

    def scanString(self):
        token = ""
        delim = self.getChar()
        token += delim
        while True:
            ch = self.getChar()
            if ch == "":
                raise ScannerError("Unterminated string")
            if ch == delim: break
            if ch == "\\":
                token += self.scanEscapeCharacter() 
            else:
                token += ch
        return token + delim

    def scanEscapeCharacter(self):
        s = "\\"
        ch = self.getChar()
        s += ch
        if ch.isdigit() or ch == "x" or ch == "u":
            hex_mode = not ch.isdigit()
            while True:
                ch = self.getChar()
                if hex_mode:
                    if not self.isHexDigit(ch): break
                else:
                    if not ch.isdigit(): break
                s += ch
            self.saveChar(ch)
        return s

    def isOperator(self, op):
        return op in self._operators

    def isOperatorPrefix(self, op):
        for name in self._operators:
            if name.startswith(op):
                return True
        return False

# Startup code

if __name__ == "__main__":
    print("tokenscanner.py compiled successfully")