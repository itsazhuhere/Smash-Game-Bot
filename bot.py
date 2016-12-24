'''
Created on Jun 23, 2016

@author: Andre
'''


import praw
import re
import serverset
import titleparser
import traceback
from time import sleep


r = praw.Reddit("Smash game finder bot")
#establishes the connection to reddit
serverset.make_update('CREATE TABLE IF NOT EXISTS oldposts(id VARCHAR(20)')
#establishes a table for storing searched post ids
#r.login()

subreddit_name = "smashbros"
subreddit = r.get_subreddit(subreddit_name)

MAX_COMMENTS = 100
SLEEP_TIME = 30
#time to wait before searching subreddit comments again
CLEAN_CYCLES = 10
#number of cycles to do before clearing database

request_match = "\[\[(.+)\]\]"
request_regex = re.compile(request_match, re.IGNORECASE)

player_split = " vs\.? "
player_split_regex = re.compile(player_split, re.IGNORECASE)


request_dict_base = {"player1":"",
                     "player2":"",
                     "tournament":"LAST",
                     "bracket":"ALL",
                     "date":""
                     }

settings = {"useragent":"Smash Game Bot",
            "secret":"Hvdnd4uU8UDtafrd5tSm6Xgq_4k",
            "subreddit":"smashbros"
            
            
            }





def bot_setup():
    r = praw.Reddit(settings["useragent"])
    

last_comment = ""
def get_sub_comments():
    return subreddit.get_comments(limit=MAX_COMMENTS,
                                  place_holder = last_comment)
    
    
searched = set()

def search_comments(comments):
    #comments is a generator created by the PRAW api that contains comments
    #from the subreddit's comments list
    
    #use enumerate?

    for comment in comments:
        try:
            cauthor = comment.author.name
        except AttributeError:
            #delete author case, comment ignored
            continue
        
        if cauthor.lower() == r.user.name.lower():
            #do not reply to yourself
            #this case is likely never going to happen, as the reply format
            #does not contain the trigger "[[]]" usually
            continue
        
        if serverset.check_comment(comment.id):
            break
            #break here because comments should be in chronological order,
            #and hitting an old comment means the rest of the comments are old
            
        
        parse_message(comment)
        last_comment = comment.id
        
        serverset.add_comment(id)
        
        
        searched.add(comment.id)
    
def parse_message(message):
    """
    PRAW's Inboxable objects will cover both private messages and comments
    """
    request_iter = request_regex.finditer(message.body())
    requests = []
    for build_request in request_iter:
        requests.append(determine_request(build_request))
    if requests:
        results = serverset.build_request(requests)
        message.reply(build_reply(results))
    
def determine_request(build_request):
    #build_request is a MatchObject with one group: everything between the double brackets [[ ]]
    request_dict = request_dict_base.copy()
    
    request_params = build_request.group(1).split(",")
    if player_split_regex.search(request_params[0]):
        players = request_params.pop(0)
        players = player_split_regex.split(players)
        request_dict["player1"] = players[0].strip()
        request_dict["player2"] = players[1].strip()
        if request_params:
            #do more parsing based on arguments provided
            #if no additional arguments, defaults will be used
            pass
    else:
        #special video case (where there is no "vs" in the first group)
        #should there be commas in this case, then only the first group (request_params[0]) will be used
        
        #build a database search of the string and use the returned key to retrieve the 
        #corresponding video
        pass
        
    return request_dict





YOUTUBE_LINK = "https://www.youtube.com/watch?v="


def build_reply(results, is_list):
    """
    Creates the reddit comment reply based on the results from the database search.
    
    
    The format for a player vs player based search:
    <bold>[Player 1] vs [Player 2]:</bold>
        [Tournament]:
            <link>[Bracket]</link>
            (Chronological order if applicable)
            
    More formats to come (tournament based search and character based search currently planned)
    """
    
    

    #results and requests should be of the same size
    #additionally, a failed result should be represented by an empty entry
    reply_string = ""
    #sort(results)
    for entry in range(len(results)):
        entry_string = ""
        entry_dicts = sort_results(results[entry])
        tournament_set = set()
        if is_list:
            entry_string += make_section(entry_dicts)
            for row in entry_dicts:
                if row["tournament"] not in tournament_set:
                    #make a tournament heading
                    entry_string += row["tournament"] + ":" + ENDL
                    tournament_set.add(row["tournament"])
                entry_string += video_format.format(bracket=row["bracket"],
                                                    video_id=row["video"]
                                                    )
            reply_string += entry_string + LINE
        else:
            pass
    #additionally add a footer to the message that gives info on the bot
    return reply_string
#Reddit comment formatting tokens
BOLD = "**"         #bold requires the token to be on both sides of the text to bold
ENDL = "    \n"     #end line is four spaces followed by endline
LINE = "***" +ENDL  #creates a horizontal line, TODO: check if ENDL is needed


section_format = "{player1} vs. {player2}:"
video_format = "[{bracket}](" + YOUTUBE_LINK + "{video_id})" + ENDL

bracket_hierarchy = {}

def make_section(entry_dicts):
    return BOLD + section_format.format(player1=entry_dicts[0]["player1"],player2=entry_dicts[0]["player2"]) + BOLD + ENDL

def sort_results(entry_dicts):
    #TODO: for now do not do any sorting, will later implement a sort based on bracket
    #sorting will now be done within the database; results will be returned in the
    #order that they should be displayed
    return entry_dicts


test_results = [[{"tournament":"The Big House 5",
                  "bracket":"Pools",
                  "player1":"HBox",
                  "player2":"Mew2King",
                  "video":"7XyGIF9EoPM"
                  },
                 {"tournament":"The Big House 5",
                  "bracket":"Winners Semis",
                  "player1":"HBox",
                  "player2":"Mew2King",
                  "video":"TU8f7U0Y4MY"
                  } ,
                 {"tournament":"The Big House 5",
                  "bracket":"Winners ",
                  "player1":"HBox",
                  "player2":"Mew2King",
                  "video":"7XyGIF9EoPM"
                  },
                 {"tournament":"The Big House 5",
                  "bracket":"Pools",
                  "player1":"HBox",
                  "player2":"Mew2King",
                  "video":"7XyGIF9EoPM"
                  }
                 ], 
                [{"tournament":"The Big House 5",
                  "bracket":"Winners Finals",
                  "player1":"Leffen",
                  "player2":"PPMD",
                  "video":"Gv74JXJBFwk"
                  },
                 {"tournament":"The Big House 5",
                  "bracket":"Grand Finals",
                  "player1":"Leffen",
                  "player2":"Mew2King",
                  "video":"Gv74JXJBFwk"
                  }]]
                



clean_cycles_query = 'DELETE FROM oldposts WHERE id NOT IN (SELECT id FROM oldposts ORDER BY id DESC LIMIT {0})'

if __name__ == "__main__":
    #main bot loop 
    
    #do login stuff
    
    cycles = 0
    #message checking loop
    while True:
        try:
            
            search_comments(get_sub_comments())
            cycles +=1
        except Exception as e:
            traceback.print_exc()
        if cycles >= CLEAN_CYCLES:
            serverset.make_update([clean_cycles_query.format(MAX_COMMENTS)])
            cycles = 0
            
        sleep(SLEEP_TIME)
        