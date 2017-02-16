'''
Created on Jun 30, 2016

@author: Andre
'''




def reverse(expr):
    return "[^" + expr + "]"
def group(expr):
    return "[" + expr + "]"
def spaces(expr):
    return "\s*"+expr+"\s*"
def optional(expr):
    return expr+"?"
def conditional(expr,tag):
    "(?("+tag+")"+expr+")"
def lookahead(expr,flag):
    expr+"(?="+flag+")"

#TODO: improve regex; 
#currently characters bound by parentheses are a must (it is possible to make them optional)

#These are all the channels' standard format for tournament game titles

#the '\.?' in the middle is for the rare typo of V.s (at least one found)
versus = spaces("[vV]\.?[sS]\.?")


separator = ":\-"
tourn_sep = group(separator)
not_tourn_sep = reverse(separator)

#tournaments can have the following characters: 
#alphanumeric, space, @, ', !
tournament = "(?P<tourny>"+ not_tourn_sep +"+)"

#tags can have the following characters: 
#alphanumeric, space, |, [, ], ., ' [apostrophes may be errors]
char_sep = "\(\)"
#tag_symbols = "\w\s\|\[\]\.&'\-`#!$@~%"
tag1 = spaces("(?P<tag1>"+ reverse(char_sep) +"+)")
tag2 = spaces("(?P<tag2>"+ reverse(char_sep) +"+)")

#(playable) characters can have the following characters:
#alphanumeric space, ,, ., &,
character_symbols = "\w\s,\.&/\-"
characters1 = spaces("(?P<chars1>\(["+ character_symbols +"]+\))?")
characters2 = spaces("(?P<chars2>\(["+ character_symbols +"]+\))?")

bracket = "(?P<round>[\w\s]+)"
game_type = "(?P<type>[\w\s]+)?"
#matches the video id provided in the string, which immediately follows 'Video:' and is exactly 11 characters long
video_info = "Video:(?P<video>.{11})"

optional_separator = tourn_sep +"?"
optional_end = "([\s\S]+)"
#captures "- Teams"; meant to go before a separator ([:-1])
optional_teams = tourn_sep[:-1]+"\s+Teams\s+)?"



#VideoGameBootCamp
VGBC = ("^"+tournament + tourn_sep + tag1 + 
       characters1 + versus + tag2 + characters2 + 
       optional_separator + bracket + optional_separator + 
       game_type + optional_end + video_info)

#ShowdownGG
SDGG = ("^"+tournament+optional_teams+tourn_sep+bracket+
        tourn_sep+tag1+characters1+versus+tag2+characters2+
        optional_end+video_info)

SDGG_GENESIS3 = ("(?P<tourny>GENESIS 3)"+spaces(tourn_sep)+
                 tag1+characters1+versus+tag2+characters2+
                 spaces(tourn_sep)+bracket+optional_end+video_info)

#Geeky Goon Squad
GGS = (tournament+spaces(tourn_sep)+tag1+characters1+versus+
       tag2+characters2+spaces(tourn_sep)+bracket+optional_end+video_info)
       
#Battle of the Five Gods
##This is the top 8 format (which leads with the bracket ie WQ: Mango (Fox) vs. Westballz (Falco)
BOTFG = (bracket+spaces(tourn_sep)+tag1+characters1+versus+tag2+
         characters2+optional_end+video_info)

BOTFG2 = (tag1+characters1+versus+tag2+characters2+spaces(tourn_sep)+bracket+video_info)


#Beyond the Summit
BTS = (tag1+versus+tag2+spaces(tourn_sep)+bracket+spaces(tourn_sep)+tournament+optional_end+video_info)


#CLASH tournaments
CLASH = (tournament+spaces(tourn_sep)+tag1+characters1+versus+tag2
         +characters2+spaces(optional(tourn_sep))+optional(bracket)
         +spaces(tourn_sep)+game_type+optional_end+video_info)


#Event Horizon Gaming
#TODO: 2 SNS2 games need to be added manually
EHG = (tournament+spaces(tourn_sep)+tag1+characters1+versus+
       tag2+characters2+optional(spaces(tourn_sep))+optional(bracket)+
       optional_end+video_info)

#Tourney Locator
TL = (tournament+spaces(tourn_sep)+tag1+characters1+versus+tag2+characters2+
      bracket+spaces(tourn_sep)+optional_end+video_info)

#Smash Studios
SS = ()

#WTFOX 2 specific
SS_WTFOX2 = (tournament+spaces(tourn_sep)+game_type+spaces(tourn_sep)+tag1+
      characters1+versus+tag2+characters2+spaces(tourn_sep)+optional_end+video_info)

#EVO 2016
#channel is dedicated to the one tournament
#possible optional bracket format
#"(?P<round>[^:\-]+[:\-])?"
EVO2016 = ("(?P<round>[^:\-]+[:\-])?\s*"+tag1+characters1+versus+
           tag2+characters2+optional_end+video_info)


#Most Valuable Gaming
MVG = (tournament+spaces(tourn_sep)+bracket+spaces(tourn_sep)+tag1+characters1+
       versus+tag2+characters2+video_info)

#Melbourne Melee
MM = ((tournament+spaces(tourn_sep)+bracket+spaces(tourn_sep)+tag1+characters1+
       versus+tag2+characters2+video_info))
MMBAM7 = ("(?P<tourny>Bam\s?7)[\s\S]+"+spaces(tourn_sep)+tag1+versus+tag2+video_info)

#Even Matchup Gaming
EMG = (tournament+spaces(tourn_sep)+tag1+characters1+versus+tag2+characters2+
       spaces(tourn_sep)+bracket+video_info)

#Melee Milwaukee
##Doubles needed to be adjusted for
#Example: SNS - Plup (P1) + COG | Wizzrobe (P4) vs Mark0w (P2) + Thick Nickel (P3) - Melee Doubles    Video:oLFKp_9Lmic    Channel:UCiz8Ls57DOSu2Vmz61hnynw
#Multiple parentheses, no characters
MMil = (tournament+spaces(tourn_sep)+tag1+characters1+versus+tag2+characters2+
        spaces(tourn_sep)+bracket+video_info)

#Evo2kVids
#TODO:The videos for EVO 2015 are doubled up; some are two matches per video. 
#Create a workaround, preferably with a timestamp
EVO2K = ("(?P<tourny>Evo 2015)"+spaces(tourn_sep)+"(?P<type>SSBM)"+bracket+
         spaces(tourn_sep)+tag1+versus+tag2)

#HTC Esports
HTC = (tournament+spaces(tourn_sep)+bracket+spaces(tourn_sep)+optional_end+     #they name the bracket using a separator
       spaces(optional(tourn_sep))+tag1+characters1+versus+tag2+characters2+
       optional_end+video_info)

#attempts to parse title primarily based on the presence of a "vs" in most forms
#one is able to add additional separators to this, as this alone only splits into 3 groups:
#before "vs", after "vs", and the "vs" itself
pre_versus = "(?=vs\.?)"

regex_dict = {"VGBC":VGBC,
              "SDGG":SDGG,
              "GGS":GGS,
              "BOTFG":BOTFG,
              "BOTFG2":BOTFG2,
              "BTS":BTS,
              "CLASH":CLASH,
              "EHG":EHG,
              "TL":TL,
              "SS":SS_WTFOX2,
              "EVO2016":EVO2016,
              "EVO2K":EVO2K,
              "MVG":MVG,
              "MM":MM,
              "EMG":EMG,
              "MMil":MMil,
              "HTC":HTC
              }


lines = "\n-------------\n"
print_format = "Tournament Name: {0}\nPlayer 1: {1} {2}\nPlayer 2: {3} {4}\nBracket: {5}\nGame: {6}" + lines

if __name__ == "__main__":
    print(GGS)