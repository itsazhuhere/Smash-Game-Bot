'''
Created on Dec 13, 2016

@author: Andre
'''


import serverset


#TODO:should make this a static value and automatically update it instead
latest_tournament = ("tournament=" + 
"""
(SELECT TOP 1 db_name FROM tournamentdates
ORDER BY date DESC)
""")


player_template1 = ("(player1={p1} AND " +
                    "player2={p2}) OR (" +
                    "player1={p2} AND " +
                    "player2={p1})"
                    )

tournament_template = (
"""
(tournament = 
(SELECT db_name FROM tournaments
WHERE name = {query}))
""")

select_brackets = "bracket={0}"

request_template = "SELECT * FROM games WHERE {0}"

test_entries = [{"player1":"",
                 "player2":"",
                 "tournament":"LAST",
                 "bracket":"ALL",
                 "date":""
                 },
                
                ]

def create_where(entry):
    where = [player_template1.format(p1=entry["player1"],
                                    p2=entry["player2"])]
    
    if entry["tournament"] == "LAST":
        #adds an sql clause that limits search to the latest tournament
        where.append(latest_tournament)
        
        
    else:
        if type(entry["tournament"]) == list:
            #TODO: implement multiple tournament functionality
            pass
        else:
            #in this case only a single tournament is passed
            #if type(entry["tournament"]) == str:
            where.append(tournament_template.format(query=entry["tournament"]))
    #TODO: implement date functionality
    if (entry["date"]):
        pass
    
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
    
    return " AND ".join(where)

def build_request(info):
    requests = []
    for entry in info:
        requests.append(request_template.format(create_where(entry)))
        


if __name__ == "__main__":
    for entry in test_entries:
        print(create_where(entry))