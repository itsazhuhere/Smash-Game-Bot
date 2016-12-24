'''
Created on Jun 14, 2016

@author: Andre
'''
import re

class Game:
    def __init__(self, names):
        self.title = names[0]
        self.names = names
        self.regex = self.to_regex(self.names)
        self.chars = []
        
    def get_names(self):
        return self.names
    
    def get_title(self):
        return self.title
    
    def has_name(self, name):
        for regex in self.regex:
            result = regex.search(name)
            if result:
                return True
        return False
    
    def to_regex(self, names):
        regexes = []
        for name in names:
            regexes.append(re.compile(name,flags=re.IGNORECASE))
        return regexes
    
    def add_chars(self, chars):
        self.chars.extend(chars)
    
    
    def __getitem__(self, index):
        return self.has_name(index)
    


sixtyfour = Game(["SS64", "SSB64", "Smash 64"])
melee = Game(["Melee", "SSBM", "Super Smash Bros Melee"])
brawl = Game(["SSBB", "Brawl"])
smash4 = Game(["SSB4", "Smash 4", "Wii U"])

games_list = [smash4, melee, sixtyfour, brawl]


    
    
def find_new_names():
    pass
    #temporary function for finding the potentially unconventional names for the games that some
    #titles will use/some channels will have