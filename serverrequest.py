from __future__ import unicode_literals
import re
from server_handler import make_db_request

#flags used to indicate how to format the date user input
START = 0
END = 1

player_template = ("(player1='{0}' OR player2='{0}')")

player_template1 = ("((player1='{p1}' AND " +
                    "player2='{p2}') OR (" +
                    "player1='{p2}' AND " +
                    "player2='{p1}'))"
                    )

select_brackets = "bracket={0}"

request_template = (
"""SELECT DISTINCT 
bracket, tournament, gametype, player1, player2, video
FROM games
NATURAL JOIN tournaments 
NATURAL JOIN tournamentdates 
NATURAL JOIN bracketnames
NATURAL JOIN brackets
WHERE {0}
ORDER BY date DESC, ranking DESC""")

date_template = "(date >= '{0}' AND date < '{1}')"

tournament_template = "tournamentvariant LIKE '{0}'"

type_template = "gametype = '{0}'"

def add_parentheses(statement):
    return "("+ statement + ")"

def create_query(entry):
    """
    Creates a complete query statement from the user info passed by the entry parameter.
    It can then be used as is in a MySQL database query.
    Parameters:
    
    entry -- a dict that contains the keys "p1", "p2", "tournament", and "bracket" ,
            and optionally a "date" key

    """
    where = []
    if entry["player1"]:
        where.append(player_template.format(entry["player1"]))
    if entry["player2"]:
        where.append(player_template.format(entry["player2"]))
                     
    
    no_tournament = (entry["tournament"] == "LAST")
    
    if type(entry["tournament"]) == list:
        #TODO: implement multiple tournament functionality
        pass
    elif not no_tournament:
        #in this case only a single tournament is passed
        #if type(entry["tournament"]) == str:
        where.append(tournament_template.format(make_like(entry["tournament"])))
    if (entry["date"]):
        #TODO: add functionality to search general title name, like Smash 'n Splash, with year
        #rather than searching Smash 'n Splash 2. Default (no date) behavior gives the original tournament,
        #Smash 'n Splash 1 in this case
        where.append(create_dates(entry["date"]))
        
    """ ###No longer needed
        elif no_tournament:
        #adds an sql clause that limits search to the latest tournament
        where.append(latest_tournament)
    """
    
    if entry["bracket"] == "ALL":
        #do nothing here; database will return all brackets by default
        pass
    else:
    #in this case a bracket has been specified
    #there are two formats: one where specific brackets are named,
    #another where a range is given[this one uses "-"]
        if "-" in entry["bracket"]:
            #TODO: implement bracket ranges (currently only single brackets are implemented)
            pass
        else:
            #combines all bracket selection into a single clause
            where.append("("+" OR ".join(["bracketvariant='{0}'".format(bracket) for bracket in entry["bracket"].split(",")])+")")
    if entry["type"]:
        where.append(type_template.format(entry["type"]))
    
    print(request_template.format(" AND ".join(where)))
    return request_template.format(" AND ".join(where))

#ugly but the best way I could find for a versatile date entry
date_pattern = "(\d{4})(?P<sep>[/-])?(\d{2})?(?(sep)(?P=sep))?(\d{2})?(?!\d{2})"
date_regex = re.compile(date_pattern)

def create_dates(dates):
    #restricts the tournament search to only those within the specified dates
    dates = date_regex.finditer(dates)
    matches = 0
    start_end = []
    for date in dates:
        groups = date.groups()
        
        #if user doesn't follow YYYY or YYYYMMDD format, the input will not be accepted
        if date.lastindex == 1:
            if matches == END:
                start_end.append(add_year(groups[0]+"-01-01"))
            else:
                #matches==START
                start_end.append(groups[0]+"-01-01")
            matches+=1
        elif date.lastindex == 4:
            start_end.append(groups[0]+"-"+groups[2]+"-"+groups[3])
            matches+=1
        if matches >= 2:
            #limits the number of dates read to 2 (one start date and one end date)
            break
    if len(start_end)==1:
        start_end.append(add_year(start_end[0]))
    
    return date_template.format(start_end[0],start_end[1])

def add_year(start_year):
    #date will be in the YYYYMMDD format
    next_year = str(eval(start_year[0:4])+1)
    return next_year + start_year[4:]

def make_like(search):
    return "%"+search+"%"
    
def is_date(input):
    """
    Date format must be either a single number (i.e. 2007), or
    use date separators (/ or - or 'to')
    """
    try:
        int(input)
        return True
    except:
        return input.find("/") != -1 or input.find("-") != -1 or input.find("to") != -1

request_match = "\[\[(.+?)\]\]"
request_regex = re.compile(request_match, re.IGNORECASE)

get_brackets_query = "select bracketvariant from bracketnames"
brackets_set = set()
for bracket in make_db_request(get_brackets_query):
    brackets_set.add(bracket["bracketvariant"].lower())

def is_bracket(parameter):
    return parameter.lower() in brackets_set

gametype_list = ["Melee", "SSBM",
                 "Smash 4", "Wii U", "Sm4sh", "SSB4",
                 "Smash 64", "SSB64", "SS64"
                 ]
gametype_set = set()
for gametype in gametype_list:
    gametype_set.add(gametype.lower())

def is_type(parameter):
    return parameter.lower() in gametype_set


player_split = "\s*vs\.?\s*"
player_split_regex = re.compile(player_split, re.IGNORECASE)

request_dict_base = {"player1":"",
                     "player2":"",
                     "tournament":"LAST",
                     "bracket":"ALL",
                     "date":"",
                     "type":""
                     }

def determine_request(build_request):
    #build_request is a MatchObject with one group: everything between the double brackets [[ ]]
    request_dict = request_dict_base.copy()
    
    request_params = build_request.group(1).split(",")
    if player_split_regex.search(request_params[0]):
        #can be either single player or two player search
        #regardless, must contain 'vs'
        players = request_params.pop(0)
        players = player_split_regex.split(players)
        request_dict["player1"] = set_alt(players[0].strip())
        request_dict["player2"] = set_alt(players[1].strip())
        if request_params:
            #do more parsing based on arguments provided
            #if no additional arguments, defaults will be used
            for parameter in request_params:
                parameter = parameter.strip()
                if is_date(parameter):
                    request_dict["date"] = parameter
                elif is_type(parameter):
                    request_dict["type"] = parameter
                elif is_bracket(parameter):
                    request_dict["bracket"] = parameter
                else:
                    #the parameter will be inserted as a tournament search
                    request_dict["tournament"] = parameter
            pass
    else:
        #non player search case, search for tournament
        request_dict["tournament"] = request_params.pop(0)
        if request_params:
            for parameter in request_params:
                parameter = parameter.strip()
                if is_date(parameter):
                    request_dict["date"] = parameter
                elif is_bracket(parameter):
                    request_dict["bracket"] = parameter
            
        
        
    return request_dict

player_alt_request = """
SELECT * FROM alt_names
"""

player_alt_results = make_db_request(player_alt_request)
player_alts = dict()
for result in player_alt_results:
    player_alts[result["alt_tag"].lower()] = result["proper_tag"]
    
def set_alt(player):
    if player.lower() in player_alts.keys():
        return player_alts[player]
    return player
    
def build_request(info):
    requests = []
    for entry in info:
        requests.append(create_query(entry))
    return requests
        


if __name__ == "__main__":
    pass