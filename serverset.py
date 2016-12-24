'''
Created on Jun 21, 2016

@author: Andre
'''
from __future__ import print_function
import pymysql.cursors
import re
import titleparser
import videogetter
from config import connect_dict
from logging import codecs
from datetime import datetime
from __builtin__ import str



"""
This module is a simple mediator between the python portion and the server portion of the bot;
it is able to make search requests to the server as well as build_inserts it.
"""


connection = pymysql.connect(**connect_dict)






TOURNAMENT = 1
PLAYER1 = 2
PLAYER2 = 4
BRACKET = 6
VIDEO = 7

column_names = ["gametype","tournament","player1","p1_characters","player2","p2_characters","bracket", "video", "text"]
columns_string = ",".join(column_names)
#tournament_columns denotes all tournament based identifying info (not game type or video id)
tournament_columns = column_names[TOURNAMENT:BRACKET+1]

table_name = "games"
game_type_def = "gametype VARCHAR(20)"
tournament_def = "tournament VARCHAR(200)"
player1_def = column_names[PLAYER1] + " VARCHAR(200), p1_characters VARCHAR(100)"
player2_def = column_names[PLAYER2] + " VARCHAR(200), p2_characters VARCHAR(100)"
bracket_def = "bracket VARCHAR(200)"
date_def = "matchdate DATE"
video_def = "video VARCHAR(11)"

server_setup = "CREATE TABLE {0} ({1},{2},{3},{4},{5},{6})"

table_join = "FROM games "

def create_table():
    make_update([server_setup.format(table_name,
                                     game_type_def,
                                     tournament_def,
                                     player1_def,
                                     player2_def,
                                     bracket_def,
                                     video_def
                                     #date_def #TODO: insert date
                                     )])


special_table = "specialvideos"
search_column = "term"

special_request = ("SELECT * FROM {table} WHERE {column} = ".format(table=special_table,
                                                                    column=search_column) + "{term}")

def search_special_request(search_term):
    pass

template = ",".join(["'{"+str(i)+"}'" for i in range(len(column_names))])
match_template = "INSERT INTO {table} ({names}) VALUES ({temp});".format(table=table_name,
                                                                        names=columns_string,
                                                                        temp=template)


def build_inserts(info):
    updates = []
    for entry in info:
        sanitize(entry)
        updates.append(match_template.format(entry["game"],
                                             entry["tourny"],
                                             entry["tag1"],
                                             entry["chars1"],
                                             entry["tag2"],
                                             entry["chars2"],
                                             entry["round"],
                                             entry["video"],
                                             entry["text"]
                                             ))
    return updates




add = " AND "
#TODO: clean up these templates
request_template = "SELECT {columns} FROM {table} WHERE {temp}".format(columns = "*",
                                                                      table = table_name,
                                                                      temp = "{temp}"
                                                                      )
"""
template works out to:

(player1 = PLAYER1 AND player2 = PLAYER2)
OR
(player1 = PLAYER2 AND player2 = PLAYER1)

when formatting is implemented
"""
player_template1 = ("("+column_names[PLAYER1]+"={p1} AND " +
                    column_names[PLAYER2]+"={p2}) OR (" +
                    column_names[PLAYER1]+"={p2} AND " +
                    column_names[PLAYER2]+"={p1})"
                    )


update_names_template = "UPDATE games SET player1='{p1}',player2='{p2}' WHERE video='{video_id}'"


get_latest_game = ("SELECT {column} FROM (SELECT {column} FROM {table}" +
                    " WHERE " + player_template1 + " ORDER BY date DESC) LIMIT 1;"
                    )


additional_template = "{column} = '{value}'"
    
def build_request(info):
    requests = []
    for entry in info:
        requests.append(request_template.format(temp=create_where_redo(entry)))


latest_tournament = (column_names[TOURNAMENT] + "=" + 
"""
(SELECT TOP 1 db_name FROM tournamentdates
ORDER BY date DESC)
""")
tournament_template = (
"""
(tournament = 
(SELECT db_name FROM tournaments
WHERE name = {query}))
""")

select_brackets = "bracket={0}"

def create_where_redo(entry):
    where = player_template1.format(p1=entry["player1"],
                                    p2=entry["player2"])
    
    if entry["tournament"] == "LAST":
        #adds an sql clause that limits search to the latest tournament
        where += "AND" + latest_tournament
        
    else:
        if type(entry["tournament"]) == list:
            #TODO: implement multiple tournament functionality
            pass
        else:
            #in this case only a single tournament is passed
            #if type(entry["tournament"]) == str:
            where += "AND" + tournament_template.format(query=entry["tournament"])
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
            where += "(AND "
            #combines all bracket selection into a single clause
            where += " OR ".join([select_brackets.format(bracket) for bracket in entry["bracket"].split(",")])
            where += ")"
    
    return where

date_regexes = [
                ]

    
def determine_dates(date_entry):
    pass


def renew_info(data_file):
    with codecs.open(data_file,"r",encoding="utf-8") as videos:
        updates = []
        for line in videos.read().split("\n"):
            row = line.split("\t")
            updates.append(update_names_template.format(request_p1=sanitize(row[PLAYER1]),
                                                        request_p2=sanitize(row[PLAYER2]),
                                                        video_id=row[VIDEO]
                                                        
                                                        ))
        make_update(updates)





def sanitize(entry):
    if type(entry) is dict:
        for key in entry.keys():
            try:
                entry[key] = entry[key].strip()
                entry[key] = entry[key].replace("'", "\\'")
                entry[key] = entry[key].replace('"', '\\"')
                
            except AttributeError:
                pass
    elif type(entry) is str or type(entry) is unicode:
        new_entry = entry.replace("'", "\\'")
        new_entry = new_entry.replace('"', '\\"')
        return new_entry
        

def create_tournament_table():
    make_update("CREATE TABLE tournaments (name VARCHAR(30),db_name VARCHAR(30));")
    make_update("CREATE TABLE tournamentdates (db_name VARCHAR(30),date DATE);")
                

tourny_name_temp = "INSERT INTO tournaments (name, db_name) VALUES ({0},{1})"
tourny_date_temp = "INSERT INTO tournamentdates (db_name, date) VALUES ({0},{1})"

def update_tournament_table(tournament_file):
    with open(tournament_file, "r") as tournaments:
        for line in tournaments.read().split("\n"):
            # "-" is the text file's separator for info on each line
            tournament_info = line.split("-")
            proper_name = quote(tournament_info[0].strip())
            #tournament_info[1] will hold the date data
            print(tourny_date_temp.format(proper_name, date_format(tournament_info[1].strip())))
            make_update(tourny_date_temp.format(proper_name, date_format(tournament_info[1].strip())))
            #because the proper name will always be considered a name for the tournament,
            #it can be inserted into the table as is
            make_update(tourny_name_temp.format(proper_name,
                                                  proper_name))
            
            if len(tournament_info) == 3:
                alt_names = tournament_info[2].split(",")
                for name in alt_names:
                    make_update(tourny_name_temp.format(quote(name.strip()), proper_name))

def quote(string):
    return '"' + string + '"'

date_input_format =  "%B %d %Y"
date_output_format = "%Y-%m-%d"
            
def date_format(date):
    #input format will be month[fully spelled] day year
    tournament_date = datetime.strptime(date, date_input_format)
    return quote(tournament_date.strftime(date_output_format))

team_tag_pattern = "[^&]*[\|\.]"
team_tag_regex = re.compile(team_tag_pattern)

def remove_teams():
    #This is currently only tailored towards VGBC's specific player format, '[Team] | [Player Tag]'
    #Most channels with tournament videos use either the '[Team] | [Player Tag]' or '[Team].[Player Tag]' format
    #However this function will greatly mess up doubles games format
    request = """SELECT * FROM games 
                WHERE {p1} LIKE {team1} OR 
                {p1} LIKE {team2} OR
                {p2} LIKE {team1} OR
                {p2} LIKE {team2}""".format(p1 = "player1",
                                           p2 = "player2",
                                           team1 = "'%|%'", #if the player name contains "|"
                                           team2 = "'%.%'" #if the player name contains "."
                                           )
    result = make_db_request([request])
    updates = []
    for row in result[0]:
        player1 = sanitize(team_tag_regex.sub("",row["player1"]).strip())
        player2 = sanitize(team_tag_regex.sub("",row["player2"]).strip())
        update_request = update_names_template.format(p1=player1,
                                                      p2=player2,
                                                      video_id=row["video"]
                                                      )
        updates.append(update_request)
    make_update(updates)


def remove_nonmajor():
    nonmajor_query = """
    DELETE FROM games
    WHERE NOT EXISTS(SELECT *
                    FROM tournaments t
                    WHERE t.name = tournament)
    """
    make_update(nonmajor_query)

CB2016pools = {"id_column":"CB2016 Pools",
                }

update_row_template = "UPDATE {table} SET {set} WHERE {where}".format(table=table_name,
                                                                      set=",".join(["{0}={1}".format(tournament_columns[i],"'{"+str(i)+"}'") for i in range(len(tournament_columns))]),
                                                                      where="video={video}"
                                                                      )      
def change_rows(id_column, id, update_pattern):
    """
    This function attempts to fix inconsistencies in a channel's title format
    that have made it past the first parsing but create misformatted database rows;
    it is best used on a tournament by tournament basis, as those formats are 
    unlikely to change.  Patterns must be created manually (although the titles
    module will contain basic title pieces)
    """
    #TODO: add this to the tilteparser module, remove titleparser import from this module
    parser = titleparser.TitleParser()
    parser.set_pattern(update_pattern)
    request = request_template.format(columns=id_column,
                                      temp=id
                                      )
    db_results = make_db_request([request])
    updates = []
    video_ids = []
    
    #search youtube api (through videogetter) for the video using video id, then 
    #get the title and run the parser through the title, taking the new info and updating the server with it
    for row in db_results[0]:
        video_ids.append(row["video"])
    
    video_results = videogetter.get_video_by_ids(video_ids)
    for video in video_results:
        #the pattern provided for the parser should have named groups in it
        #required named groups:
        #player1,player2,tournament,bracket,video
        match_obj = parser.match(video["snippet"]["title"])
        match_dict = match_obj.groupdict()
        fix_groups(match_dict)
        updates.append(match_dict)
    
    make_update(build_updates(updates))
    
def build_updates(info):
    #TODO: in place modifications of lists (don't create new lists when you dont need to use the old
    #list anymore after this
    updates = []
    for entry in info:
        sanitize(entry)
        updates.append(update_row_template.format(entry["tourny"],
                                                  entry["tag1"],
                                                  entry["chars1"],
                                                  entry["tag2"],
                                                  entry["chars2"],
                                                  entry["round"],
                                                  video=entry["video"]
                                                  ))
    return updates


optional_groups = ["chars1","chars2"]
db_none = "'None'"
def fix_groups(dict_to_fix):
    #TODO: deprecated
    #fills in the optional groups if they weren't matched to anything
    to_fix_keys = dict_to_fix.keys()
    for group in optional_groups:
        if group not in to_fix_keys:
            dict_to_fix[group] = db_none
def create_brackets_table():
    """
    Creates the brackets table in the database, which holds all of the proper names
    for the brackets, as well as their ranking to allow for sorted database query returns.
    Grand Finals is given the lowest number ranking, and the ranking goes up with each
    bracket (in the event of additional brackets being added to the format this can 
    be run again to update the server's table)
    """
    with open("bracket names.txt","r") as bracket_names:
        make_update("TRUNCATE brackets")
        brackets_insert_query = "INSERT INTO brackets VALUES('{0}',{1});"
        proper_names = []
        for bracket in bracket_names.read().split("\n"):
            if bracket[0] == "@":
                proper_names.append(bracket)
        for index, bracket in enumerate(proper_names):
            make_update(brackets_insert_query.format(sanitize(bracket), index))
            
def create_bracketnames_table():
    """
    Creates the bracketnames table in the database.  This table holds all
    the variants of the possible brackets in a tournament.
    """
    with open("bracket names.txt","r") as bracket_names:
        make_update(
        """CREATE TABLE IF NOT EXISTS 
        bracketnames(bracketvariant VARCHAR(50), bracket VARCHAR(50))""");
        make_update("TRUNCATE bracketnames")  #to prevent duplicate rows in case of rerunning the function
        bracketnames_insert_query = "INSERT INTO bracketnames VALUES('{0}','{1}');"
        proper_name = ""
        for bracket in bracket_names.read().split("\n"):
            if bracket[0] == "@":
                bracket = bracket[1:]
                proper_name = sanitize(bracket)
            make_update(bracketnames_insert_query.format(sanitize(bracket),proper_name))

def case_sensitive(pattern):
    return re.IGNORECASE if len(pattern)!=2 else 0

def dict_to_list(dict_list, keyword):
    for i in range(len(dict_list)):
        dict_list[i] = dict_list[i][keyword]

def fix_brackets():
    ###*****TODO:custom bracket rankings using the double elimination naming format (see GENESIS 3 brackets)
    #TODO: add this to the titleparser module
    
    #goes through every entry in the database, and searches the title text
    #for a bracket identifier, and then inserts that into the bracket column of the entry
    
    #get all possible bracket names from the brackets table of the db
    bracket_names_query = "SELECT bracketvariant FROM bracketnames;"
    bracket_names = make_db_request([bracket_names_query])[0]     #only need first entry in the list
    print(bracket_names)
    dict_to_list(bracket_names, "bracketvariant")
    ####TODO:convert query result into a list of bracket names
    
    #insert bracket names list into the titleparser object
    bracket_parser = titleparser.TitleParser()
    bracket_parser.set_postmatch_pattern(bracket_names,case_sensitive)
    #query the games table for every row (first run through)
    #subsequent run throughs should only consider rows with bracket=UNKNOWN
    all_rows_query = "SELECT * FROM games;"
    all_rows = make_db_request(all_rows_query)[0]
    #call the postmatch matching method on every entry, inserting the result into the
    #bracket column of the row
    bracket_insert_query = "UPDATE games SET bracket='{0}' WHERE video='{1}';"
    for row in all_rows:
        bracket_value = bracket_parser.match_postmatch_pattern(row["text"])
        make_update(bracket_insert_query.format(bracket_value,row["video"]))
        

def fix_at(title):
    return title.replace("@", "at")
    
def fix_parentheses(characters):
    try:
        return characters[1:-1]
    except TypeError:
        return "Unknown"


def get_brackets():
    get_brackets_request = """
    SELECT DISTINCT brackets FROM games
    """
    results = make_db_request(get_brackets_request)[0]  #one request = single item list
    with open("brackets.txt", "w") as brackets_file:
        for bracket in results:
            print(bracket, file=brackets_file)
    

def make_db_request(requests):
    if type(requests) != list:
        requests=[requests]
    results = []
    try:
        with connection.cursor() as cursor:
            for request in requests:
                cursor.execute(request)
                results.append(cursor.fetchall())
    except Exception as e:
        print(e)
    finally:
        return results
        
def make_update(updates):
    if type(updates) != list:
        updates = [updates]
    try:
        with connection.cursor() as cursor:
            for update in updates:
                cursor.execute(update)
                connection.commit()
    except Exception as e:
        print(e)
    finally:
        pass
        
def check_row(check_query):
    is_in_db = False
    try:
        with connection.cursor() as cursor:
            cursor.execute(check_query)
            is_in_db = bool(cursor.fetchone())
    finally:
        return is_in_db
    
check_comment_query = "SELECT * FROM oldposts WHERE id = {0}"
def check_comment(id):
    return check_row(check_comment_query.format(id))

add_comment_query = "INSERT INTO oldposts VALUES({0})"
def add_comment(id):
    make_update(add_comment_query.format(id))
    
add_column_query = """
ALTER TABLE {0}
ADD {1}
"""
def add_column(table_name, column_name):
    #column_name will include the column's datatype
    make_update(add_column_query.format(table_name, column_name))

if __name__ == "__main__":
    #create_table()
    remove_teams()
    #renew_info("Query 7.txt")
    #update_tournament_table("tournament names.txt")
    #get_brackets()
    #add_column("games", "tournamentdate DATE")
    #add_column("games", "bracketvalue BIT")
    #create_brackets_table()
    #create_bracketnames_table()
    #fix_brackets()
    pass