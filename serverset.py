from __future__ import print_function
from __future__ import unicode_literals
import pymysql.cursors
import re
import titleparser
import videogetter
import os
from server_handler import *
from serverrequest import *
from config import connect_dict
from logging import codecs
from datetime import datetime
from collections import defaultdict
from __builtin__ import str



"""
This module is a simple mediator between the python portion and the server portion of the bot;
it is able to make search requests to the server as well as modify it.
"""

column_names = ["gametype","tournament","player1","p1_characters","player2","p2_characters","bracket", "video", "text"]
columns_string = ",".join(column_names)
#tournament_columns denotes all tournament based identifying info (not game type or video id)
tournament_columns = column_names[1:7]

table_name = "games"
game_type_def = "gametype VARCHAR(20)"
tournament_def = "tournament VARCHAR(200)"
player1_def = "player1 VARCHAR(200), p1_characters VARCHAR(100)"
player2_def = "player2 VARCHAR(200), p2_characters VARCHAR(100)"
bracket_def = "bracket VARCHAR(200)"
video_def = "video VARCHAR(11)"
text_def = "text VARCHAR(300)"
type_defs = [game_type_def,
             tournament_def,
             player1_def,
             player2_def,
             bracket_def,
             video_def,
             text_def]

server_setup = "CREATE TABLE {0} ({1},{2},{3},{4},{5},{6})"


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


number_template = ",".join(["'{"+str(i)+"}'" for i in range(len(column_names))])
table_template = "INSERT INTO {table} "
match_template = "({names}) VALUES ({temp});".format(names=columns_string,
                                                     temp=number_template)
                  

def build_inserts(info,table):
    updates = []
    for entry in info:
        sanitize(entry)
        updates.append(table_template.format(table=table)+
                       match_template.format(entry["game"],
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

"""
(player1 = PLAYER1 AND player2 = PLAYER2)
OR
(player1 = PLAYER2 AND player2 = PLAYER1)
"""

additional_template = "{column} = '{value}'"
    
def build_request(info):
    requests = []
    results = []
    for entry in info:
        requests.append(create_query(entry))
    for request in requests:
        results.append(make_db_request(request))
    return results

def sanitize(entry):
    if type(entry) is dict:
        for key in entry.keys():
            try:
                entry[key] = entry[key].strip()
                entry[key] = entry[key].replace("'", "\\'")
                entry[key] = entry[key].replace('"', '\\"')
                
            except AttributeError:
                pass
    elif isinstance(entry,str) or isinstance(entry,unicode):
        new_entry = entry.replace("'", "\\'")
        new_entry = new_entry.replace('"', '\\"')
        
        return new_entry
        

def create_tournament_table():
    make_update("CREATE TABLE tournaments (name VARCHAR(30),db_name VARCHAR(30));")
    make_update("CREATE TABLE tournamentdates (db_name VARCHAR(30),date DATE);")
                

tourny_name_temp = "INSERT INTO tournaments (tournament, db_name) VALUES ({0},{1})"
tourny_date_temp = "INSERT INTO tournamentdates (db_name, date) VALUES ({0},{1})"

def update_tournament_table(tournament_file):
    make_update("TRUNCATE tournaments")
    make_update("TRUNCATE tournamentdates")
    with open(tournament_file, "r") as tournaments:
        for line in tournaments.read().split("\n"):
            # "-" is the text file's separator for info on each line
            tournament_info = line.split("-")
            tournament_name = tournament_info[0]
            if tournament_name[0] == "#":
                tournament_name = tournament_name[1:]
            proper_name = quote(tournament_name.strip())
            #tournament_info[1] will hold the date data
            date = remove_comment(tournament_info[1].strip())
            make_update(tourny_date_temp.format(proper_name, date_format(date)))
            #because the proper name will always be considered a name for the tournament,
            #it can be inserted into the table as is
            make_update(tourny_name_temp.format(proper_name,
                                                  proper_name))
            
            #for when the tournament has alternate names (i.e. Smash n' Splash and SNS)
            if len(tournament_info) == 3:
                alt_names = remove_comment(tournament_info[2])
                    
                alt_names_list = alt_names.split(",")
                for name in alt_names_list:
                    make_update(tourny_name_temp.format(quote(name.strip()), proper_name))

def remove_comment(entry):
    comment_index = entry.find("#")
    if comment_index != -1:
        return entry[:comment_index].strip()
    return entry

def quote(string):
    return '"' + string + '"'

date_input_format =  "%B %d %Y"
date_output_format = "%Y-%m-%d"
            
def date_format(date):
    #input format will be month[fully spelled] day year
    tournament_date = datetime.strptime(date, date_input_format)
    return quote(tournament_date.strftime(date_output_format))

team_tag_pattern = "[^&]*?['`:\|\.\-]"
#the tokens: ' ` : | . -
team_tag_regex = re.compile(team_tag_pattern)

def remove_teams(table):
    #Most channels with tournament videos use either the '[Team] | [Player Tag]' or '[Team].[Player Tag]' format
    
    update_names_template = ("UPDATE "+ table
                             +" SET player1='{p1}',player2='{p2}' WHERE video='{video_id}'")
    
    result = make_db_request("SELECT * FROM {0}".format(table))
    team_tags = make_db_request("SELECT tag FROM team_tags")
    for i in range(len(team_tags)):
        team_tags[i] = re.compile(team_tags[i]["tag"]+"\s+",re.IGNORECASE)
    
    count = 0
    for row in result:
        player1 = team_tag_regex.sub("",row["player1"])
        player2 = team_tag_regex.sub("",row["player2"])
        for tag in team_tags:
            player1 = tag.sub("",player1)
            player2 = tag.sub("",player2)
        if player1 != row["player1"] or player2 != row["player2"]:
            #only apply update if a change will be made
            count += 1
            print(count)
            update_request = update_names_template.format(p1=player1,
                                                          p2=player2,
                                                          video_id=row["video"]
                                                          )
            add_update(update_request)
    stop_update()

def fix_alternate_names(table):
    
    update_names_template = ("UPDATE "+ table
                             +" SET player1='{p1}',player2='{p2}' WHERE video='{video_id}'")
    
    result = make_db_request("SELECT * FROM " + table)
    alt_names = make_db_request("SELECT * FROM alt_names")
    alt_names_dict = dict()
    for name in alt_names:
        name_regex = re.compile(escape_special_chars(name["alt_tag"]),re.IGNORECASE)
        if name["proper_tag"] in alt_names_dict:
            alt_names_dict[name["proper_tag"]].append(name_regex)
        else: 
            alt_names_dict[name["proper_tag"]] = [name_regex]
    for row in result:
        player1 = row["player1"]
        player2 = row["player2"]
        for alt_name in alt_names_dict.keys():
            for name_regex in alt_names_dict[alt_name]:
                player1 = name_regex.sub(alt_name, player1)
                player2 = name_regex.sub(alt_name, player2)
        if player1 != row["player1"] or player2 != row["player2"]:
            update_request = update_names_template.format(p1=player1,
                                                          p2=player2,
                                                          video_id=row["video"]
                                                          )
            add_update(update_request)
    stop_update()
            
def escape_special_chars(text):
    return text.replace("[","\[").replace("]","\]")

info_columns = ",".join(["{0}={1}".format(tournament_columns[i],"'{"+str(i)+"}'") for i in range(len(tournament_columns))])
update_row_template = "UPDATE {table} SET {set} WHERE {where}".format(table=table_name,
                                                                      set=info_columns,
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
    for row in db_results:
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
    #list anymore
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
            
def create_brackets_table(file_name):
    """
    Creates the brackets table in the database, which holds all of the proper names
    for the brackets, as well as their ranking to allow for sorted database query returns.
    Grand Finals is given the lowest number ranking, and the ranking goes up with each
    bracket (in the event of additional brackets being added to the format this can 
    be run again to update the server's table)
    """
    with open(file_name,"r") as bracket_names:
        make_update("TRUNCATE brackets")
        brackets_insert_query = "INSERT INTO brackets VALUES('{0}',{1});"
        proper_names = []
        for bracket in bracket_names.read().split("\n"):
            if bracket[0] == "@":
                proper_names.append(bracket[1:])
        for index, bracket in enumerate(proper_names):
            make_update(brackets_insert_query.format(sanitize(bracket), index))
            
def create_alternate_names_table(source_file, table_name, alt_col_name, proper_col_name):
    """
    Creates a table of names in the database based on a source file. Used for situations
    where users may use alternate names in searching things, i.e. LF for Loser's Finals or 
    HBox for HungryBox, etc
    
    Source file must have the proper name on a line, with a preceding @ (@Hungrybox), and
    the lines under it will be of the alternate names
    """
    with open(source_file,"r") as names:
        make_update(
        """CREATE TABLE IF NOT EXISTS 
        {0} ({1} VARCHAR(50), {2} VARCHAR(50))""".format(table_name,
                                                         alt_col_name,
                                                         proper_col_name));
        make_update("TRUNCATE "+ table_name)
        names_insert_query = "INSERT INTO " + table_name + " VALUES('{0}','{1}');"
        proper_name = ""
        for name in names.read().split("\n"):
            #skips empty lines
            if not name:
                continue
            if name[0] == "@":
                name = name[1:]
                proper_name = sanitize(name)
            make_update(names_insert_query.format(sanitize(name),proper_name))
            
def create_team_tags_table(tags_file):
    with open(tags_file,"r") as team_tags:
        make_update("CREATE TABLE IF NOT EXISTS team_tags (tag VARCHAR(10))")
        make_update("TRUNCATE team_tags")
        tag_insert_query = "INSERT INTO team_tags VALUES('{0}')"
        for tag in team_tags.read().split("\n"):
            make_update(tag_insert_query.format(tag))

def case_sensitive(pattern):
    return re.IGNORECASE if len(pattern)!=2 else 0

def standardize_column(table_name,column,alt_table,alt_col,proper_col):
    alt_names_dict = table_to_dict(alt_table, alt_col, proper_col)
    table = make_db_request("SELECT * FROM "+table_name)
    change_col_query = "UPDATE {0} SET {1} = '{2}' WHERE video='{3}'"
    for row in table:
        new_entry = ""
        old_entry = row[column].lower()
        for key in alt_names_dict.keys():
            for name in alt_names_dict[key]:
                if name == old_entry:
                    new_entry = key
        if new_entry and new_entry.lower() != old_entry:
            add_update(change_col_query.format(table_name,
                                               column,
                                               sanitize(new_entry),
                                               row["video"]))
    stop_update()

def table_to_dict(table_name,alt_col,proper_col):
    table = make_db_request("SELECT * FROM "+table_name)
    table_dict = defaultdict(list)
    for row in table:
        table_dict[row[proper_col]].append(row[alt_col].lower())
    return table_dict

def dict_to_regex(to_regex):
    regex_dict = defaultdict(list)
    for key in to_regex.keys():
        for i in range(len(to_regex[key])):
            regex_dict[key].append(re.compile(to_regex[key][i], re.IGNORECASE))
        
    return regex_dict
            

def dict_to_list(dict_list, keyword):
    for i in range(len(dict_list)):
        dict_list[i] = dict_list[i][keyword]

def fix_brackets(table):
    ###*****TODO:custom bracket rankings using the double elimination naming format (see GENESIS 3 brackets)
    #TODO: add this to the titleparser module
    
    #goes through every entry in the database, and searches the title text
    #for a bracket identifier, and then inserts that into the bracket column of the entry
    
    #get all possible bracket names from the brackets table of the db
    bracket_names_query = "SELECT bracket FROM bracketnames;"
    bracket_names = make_db_request([bracket_names_query])
    dict_to_list(bracket_names, "bracket")
    ####TODO:convert query result into a list of bracket names
    
    #insert bracket names list into the titleparser object
    bracket_parser = titleparser.TitleParser()
    bracket_parser.set_postmatch_pattern(bracket_names,case_sensitive)
    #query the games table for every row (first run through)
    #subsequent run throughs should only consider rows with bracket=UNKNOWN
    all_rows_query = "SELECT * FROM `{0}`;".format(table)
    all_rows = make_db_request(all_rows_query)
    #call the postmatch matching method on every entry, inserting the result into the
    #bracket column of the row
    bracket_insert_query = "UPDATE {0}".format(table)+" SET bracket='{0}' WHERE video='{1}';"
    #test_file = open("bracket_test.txt","w")
    count = 0
    for row in all_rows:
        count += 1
        bracket_value = bracket_parser.match_postmatch_pattern(row["text"])
        bracket_value = clean_regex(bracket_value)
        #print(bracket_value+" "+row["text"],file=test_file)
        #print(bracket_value+" "+row["text"])
        if bracket_value != row["bracket"]:
            #only update row if it will change the bracket column value
            print(count)
            add_update(bracket_insert_query.format(sanitize(bracket_value),row["video"]))
    stop_update()
        
def clean_regex(pattern):
    #only cleans the specific regex created for matching brackets
    return pattern.replace("(^|[\s:\-])","").replace("[\s:\-]","")


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
    results = make_db_request(get_brackets_request)
    with open("brackets.txt", "w") as brackets_file:
        for bracket in results:
            print(bracket, file=brackets_file)
        
def check_row(check_query):
    is_in_db = False
    try:
        with connection.cursor() as cursor:
            cursor.execute(check_query)
            is_in_db = bool(cursor.fetchone())
    finally:
        return is_in_db
    
add_column_query = """
ALTER TABLE {0}
ADD {1}
"""
def add_column(table_name, column_name):
    #column_name will include the column's datatype
    make_update(add_column_query.format(table_name, column_name))
    

new_table_template = ("CREATE TABLE IF NOT EXISTS `new_games` (" +
                      ",".join(["{"+str(i)+"}" for i in range(len(type_defs))]) + ")"
                      ).format(*type_defs)

def update_tables():
    #backup all channel files
    make_update(new_table_template)
    videogetter.update_files()
    titleparser.add_new_videos(titleparser.DIRECTORY, True)
    fix_brackets("new_games")
    remove_teams("new_games")
    fix_alternate_names("new_games")
    merge_tables("new_games","games")
    make_update("TRUNCATE new_games")
    videogetter.concat_all_new_files()

merge_tables_template = """
INSERT INTO {0}
SELECT * FROM {1} n WHERE n.video NOT IN
(SELECT video FROM {0} WHERE video IS NOT NULL)
"""

def merge_tables(new_table,old_table):
    try:
        make_update(merge_tables_template.format(old_table,new_table))
    except Exception as e:
        print("Merge failed")
        print(e)
if __name__ == "__main__":
    #create_table()
    #update_tournament_table("tournament names.txt")

    #get_brackets()
    #add_column("games", "tournamentdate DATE")
    #add_column("games", "bracketvalue BIT")
    #create_brackets_table()
    #create_alternate_names_table("botdatabasebackup\\bracket names.txt", "bracketnames", "bracket", "bracketproper")
    #fix_brackets("new_games")
    #fix_alternate_names("games")
    
    #update_tables()
    
    #create_team_tags_table("botdatabasebackup\\team_names.txt")
    #remove_teams("games")
    
    create_brackets_table("botdatabasebackup\\bracket names.txt")
    standardize_column("games", "bracket", "bracketnames", "bracket", "bracketproper")
    
    update_tournament_table("botdatabasebackup\\tournament names.txt")
    standardize_column("games", "tournament", "tournaments", "tournament", "db_name")
    
    #create_alternate_names_table("botdatabasebackup\\player_names.txt", "alt_names", "alt_tag","proper_tag")
    #fix_alternate_names("games")
    
    pass