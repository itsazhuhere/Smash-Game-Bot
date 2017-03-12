'''
Created on Dec 13, 2016

@author: Andre
'''

import re
import server_handler

#flags used to indicate how to format the date user input
START = 0
END = 1

#TODO:should make this a static value and automatically update it instead
latest_tournament = ( 
"""
tournament = 
(SELECT db_name FROM tournamentdates 
ORDER BY date DESC LIMIT 1)
""")

player_template = ("(player1='{0}' OR player2='{0}')")

player_template1 = ("((player1='{p1}' AND " +
                    "player2='{p2}') OR (" +
                    "player1='{p2}' AND " +
                    "player2='{p1}'))"
                    )

select_brackets = "bracket={0}"

request_template = (
"""SELECT DISTINCT * FROM 
games
NATURAL JOIN tournaments 
NATURAL JOIN tournamentdates 
NATURAL JOIN bracketnames
NATURAL JOIN brackets
WHERE {0}
ORDER BY ranking DESC""")


test_entries = [{"player1":"Armada",
                 "player2":"Hungrybox",
                 "tournament":"LAST",
                 "bracket":"ALL",
                 "date":"2016 2017"
                 },
                {"player1":"Leffen",
                 "player2":"Mango",
                 "tournament":"LAST",
                 "bracket":"ALL",
                 "date":""
                 },
                {"player1":"HBox",
                 "player2":"Armada",
                 "tournament":"LAST",
                 "bracket":"ALL",
                 "date":"2015"
                 },
                {"player1":"PPMD",
                 "player2":"Plup",
                 "tournament":"LAST",
                 "bracket":"ALL",
                 "date":"2016 2017"
                 }
                
                ]

query_template = ""

table_template = (
"""
(SELECT * FROM games NATURAL JOIN tournaments 
NATURAL JOIN tournamentdates NATURAL JOIN bracketnames
WHERE {0}) AS search
"""
)

date_template = "(date >= '{0}' AND date < '{1}')"


tournament_template = "tournament LIKE '{0}'"

def add_parentheses(statement):
    return "("+ statement + ")"

def create_query(entry):
    """
    Creates a complete query statement from the user info passed by the entry parameter.
    It can then be used as is in a MySQL database query.
    Parameters:
    
    entry -- a dict that contains the keys "p1", "p2", "tournament", and "bracket" ,
            and optionally a "date" key
            
    #######################################################
    TODO: add name variant support (ie HBox can be used for Hungrybox)
    Possible solution: 
    use MySQL variable assignment:
    
    SELECT @p1 := `player_name` FROM games WHERE alt_name = {0}
    SELECT @p2 := `player_name` FROM games WHERE alt_name = {1}
    where {0} and {1} will be assigned entry["player1"] and entry["player2"]
    
    Then use the literal strings "@p1" and "@p2" in the main select statement
    #######################################################
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
    elif no_tournament:
        #adds an sql clause that limits search to the latest tournament
        where.append(latest_tournament)
        
    
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
            where.append("("+" OR ".join(["bracket={0}".format(bracket) for bracket in entry["bracket"].split(",")])+")")
    
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

get_brackets_query = "select bracketproper from brackets"
brackets_set = set()
for bracket in server_handler.make_db_request(get_brackets_query):
    brackets_set.add(bracket["bracketproper"])

def is_bracket(input):
    return input in brackets_set

request_dict_base = {"player1":"",
                     "player2":"",
                     "tournament":"LAST",
                     "bracket":"ALL",
                     "date":""
                     }

player_split = "\s+vs\.?\s+"
player_split_regex = re.compile(player_split, re.IGNORECASE)

def determine_request(build_request):
    #build_request is a MatchObject with one group: everything between the double brackets [[ ]]
    request_dict = request_dict_base.copy()
    
    request_params = build_request.group(1).split(",")
    if player_split_regex.search(request_params[0]):
        #can be either single player or two player search
        #regardless, must contain 'vs'
        players = request_params.pop(0)
        players = player_split_regex.split(players)
        request_dict["player1"] = players[0].strip()
        request_dict["player2"] = players[1].strip()
        if request_params:
            #do more parsing based on arguments provided
            #if no additional arguments, defaults will be used
            for parameter in request_params:
                parameter = parameter.strip()
                if is_date(parameter):
                    request_dict["date"] = parameter
                elif is_bracket(input):
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
                elif is_bracket(input):
                    request_dict["bracket"] = parameter
            
        
        
    return request_dict
    
def build_request(info):
    requests = []
    for entry in info:
        requests.append(create_query(entry))
    return requests
        


if __name__ == "__main__":
    for entry in test_entries:
        print(create_query(entry))