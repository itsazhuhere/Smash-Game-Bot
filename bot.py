
import praw
import re
import serverset
import titleparser
import traceback
import config
from serverrequest import *
from server_handler import make_db_request
from time import sleep
from prawcore.exceptions import RequestException
from praw.exceptions import ClientException

MAX_REQUESTS = 3
CHARACTER_LIMIT = 10000
BOT_NAME = config.praw_login["username"]

request_match = "\[\[(.+?)\]\]"
request_regex = re.compile(request_match, re.IGNORECASE)

player_split = "\s+vs\.?\s+"
player_split_regex = re.compile(player_split, re.IGNORECASE)

def search_messages(subreddit):
    #uses PRAW's Stream class, which will provide us the comments of the subreddit(s)
    #we have specified, as they become available (aka posted)
    num_comments = 0
    for comment in subreddit.stream.comments():
        try:
            comment.refresh()
        except ClientException:
            continue
        if num_comments < 100 and is_replied(comment):
            #PRAW streams return up to 100 historical comments
            #prevents multiple replies
            continue
        
        body = comment.body
        parsed = parse_message(body)
        db_return = []
        if parsed:
            db_return = make_db_request(build_request(parsed))
            #TODO: fix this, results from bad dependency on make_db_request
            if isinstance(db_return, list) and not isinstance(db_return[0], list):
                db_return = [db_return]
        else:
            continue
        reply = build_reply(db_return, parsed)
        try:
            reply_to_message(reply, comment)
        except praw.exceptions.APIException as e:
            #TODO: change to log and function call
            e = str(e)
            if "TOO_LONG" in e:
                pass
            else:
                minutes = re.search("(\d+) minute", str(e))
                if minutes:
                    sleep(int(minutes.group(1))*60)
                    reply_to_message(reply, comment)
        except Exception as e:
            print(e)
            pass
        
        num_comments += 1

def reply_to_message(reply, comment):
    if not reply:
        return
    if isinstance(reply,list):
        comment = comment.reply(reply.pop(0))
        reply_to_message(reply, comment)
    elif isinstance(reply,str) or isinstance(reply,unicode):
        comment.reply(reply)
    else:
        #TODO: implement logging here
        print("invalid type")
        print(type(reply))
        print(reply)

def parse_message(message):
    request_iter = request_regex.finditer(message)
    requests = []
    count = 0
    for request in request_iter:
        if count > MAX_REQUESTS:
            break
        requests.append(determine_request(request))
        count += 1
    return requests

def is_replied(comment):
    if comment.replies:
        for reply in comment.replies:
            if not reply.author:
                continue
            
            #TODO: determine if author.name is already lower()
            if(reply.author.name.lower() == BOT_NAME):
                return True
    return False

YOUTUBE_LINK = "https://www.youtube.com/watch?v="
#Reddit comment formatting tokens
BOLD = "**"         #bold requires the token to be on both sides of the text to bold
ENDL = "    \n"     #end line is four spaces followed by endline
LINE = "***" +ENDL  #creates a horizontal line, TODO: check if ENDL is needed

#links for the footer of the bot's reply message
#links will be superscripted (to appear smaller) and be separated by pipes [ | ]
#links are already formatted to Reddit's formatting standards
footer_sections_list = ["^(This was an automated response)",
                        "[^FAQ](https://www.reddit.com/r/SmashGameBot/wiki/index)",
                        "[^Report ^a ^problem/error/feedback](https://goo.gl/forms/vdghDKiEKRLD7tiB3)",
                        "[^Github](https://github.com/itsazhuhere/Smash-Game-Bot)"
                        ]
footer_sections = " ^\| ".join(footer_sections_list)

continued = "*Continued as a reply to this comment...*"+ENDL
footer = LINE + footer_sections
max_reply_characters = CHARACTER_LIMIT - len(footer) - len(continued)

def build_reply(results, parsed_categories):
    #TODO: make this the player search reply and tournament search have a separate reply
    #format for tournament searches
    """
    Creates the reddit comment reply based on the results from the database search.
    
    
    The format for a player vs player based search:
    <bold>[Player 1] vs [Player 2]:</bold>
        [Tournament]:
            <link>[Bracket]</link>
            (Chronological order if applicable)
            
    More formats to come (tournament based search and character based search currently planned)
    """
    
    #if the result is failed, return an empty string
    reply = []
    reply_string = ""
    if not results:
        return build_failure_reply(parsed_categories[0]) + footer
    for i in range(len(results)):
        entry = results[i]
        if not entry:
            entry_string = ""
            entry_string = build_failure_reply(parsed_categories[i])
            if len(reply_string) + len(entry_string) > max_reply_characters:
                reply_string += continued + footer
                reply.append(reply_string)
                reply_string = entry_string
            else:
                reply_string += entry_string
            continue
        entry_dicts = to_list(entry) #TODO: wrong place?
        if (parsed_categories[i]["player1"] or 
            parsed_categories[i]["player2"]):
            reply_string = build_player_reply(entry_dicts, reply_string, reply)
        else:
            reply_string = build_tournament_reply(entry_dicts, reply_string, reply)
    if reply_string:
        reply.append(reply_string + footer)
    #additionally add a footer to the message that gives info on the bot
    return reply

failed_reply_start = "I couldn't find anything with the following categories:" + ENDL
def build_failure_reply(categories):
    reply = failed_reply_start
    categories_found = categories.keys()
    if categories["player1"]:
        reply += "Player: " + categories["player1"] + ENDL
    if categories["player2"]:
        reply += "Player: " + categories["player2"] + ENDL
    if categories["tournament"]:
        reply += "Tournament: " + categories["tournament"] + ENDL
    if categories["bracket"]:
        reply += "Bracket: " + categories["bracket"] + ENDL
    if categories["date"]:
        reply += "Date: " + categories["date"] + ENDL
    return reply + LINE

tournament_video_format = ("[{p1} vs {p2} - {bracket}](" + 
                           YOUTUBE_LINK + "{video_id})" + ENDL)

def build_tournament_reply(entry_dicts, reply_string, reply_list):
    new_section = make_tournament_section(entry_dicts[0])
    reply_string = add_line(new_section, reply_string, reply_list)
    tournament_set = set()
    tournament_set.add(entry_dicts[0]["db_name"])
    for row in entry_dicts:
        formatted_line = ""
        if row["db_name"] not in tournament_set:
            formatted_line = make_tournament_section(row)
            tournament_set.add(row["db_name"])
        formatted_line += tournament_video_format.format(p1=row["player1"],
                                                         p2=row["player2"],
                                                         bracket=row["bracketproper"],
                                                         video_id=row["video"]
                                                         )
        reply_string = add_line(formatted_line, reply_string, reply_list)
                
    reply_string = add_line(LINE, reply_string, reply_list)
    return reply_string

player_video_format = "[{bracket}](" + YOUTUBE_LINK + "{video_id})" + ENDL

def build_player_reply(entry_dicts, reply_string, reply_list):
    new_section = make_player_section()
    reply_string = add_line(new_section, reply_string, reply_list)
    tournament_set = set()
    for row in entry_dicts:
        formatted_line = ""
        if row["db_name"] not in tournament_set:
            #make a tournament heading
            formatted_line += row["db_name"] + ":" + ENDL
            tournament_set.add(row["db_name"])
        formatted_line += player_video_format.format(bracket=row["bracketproper"],
                                                     video_id=row["video"]
                                                     )
        reply_string = add_line(formatted_line, reply_string, reply_list)
                
    reply_string = add_line(LINE, reply_string, reply_list)
    return reply_string

def add_line(next_line, reply_string, reply_list):
    if len(reply_string) + len(next_line) > max_reply_characters:
        reply_string += continued + footer
        reply_list.append(reply_string)
        reply_string = next_line
    else:
        reply_string += next_line
    return reply_string

bracket_hierarchy = {}

one_player_format = "{0}:"
two_player_format = "{0} vs. {1}:"
def make_player_section(first_row, parsed):
    if parsed["player1"] and parsed["player2"]:
        return BOLD + two_player_format.format(first_row["player1"],
                                               first_row["player2"]) + BOLD + ENDL
    elif parsed["player1"]:
        return BOLD + one_player_format.format(first_row["player1"]) + BOLD + ENDL
    elif parsed["player2"]:
        return BOLD + one_player_format.format(first_row["player2"]) + BOLD + ENDL
    else:
        #should not happen; TODO: consider raising exception
        return None

def make_tournament_section(row):
    return BOLD + row["db_name"] + BOLD + ENDL
    pass

def to_list(entry_dicts):
    if isinstance(entry_dicts, list):
        return entry_dicts
    return [entry_dicts]

def main():
    reddit = praw.Reddit(**config.praw_login)
    subreddit = reddit.subreddit(config.subreddit_name)
    search_messages(subreddit)
    

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
                
test_messages = ["",
                 "[[duck vs colbol, 2010-08-01-2016-12-31, genesis]]",
                 "asdf"
                 
                 
                 ]

if __name__ == "__main__":
    #main bot loop 

    while True:
        try:
            main()
        except RequestException:
            #do logging
            continue
        """
        except Exception as e:
            #Log e
            print("Unknown Error")
            print(e)
            continue
        """

    #testing
    """
    for test in test_messages:
        print(build_reply(parse_message(test)))
    """
"""
    reddit = praw.Reddit(**config.praw_login)
    subreddit = reddit.subreddit("leagueoflegends")
    comment = reddit.comment("dctgttv")
    comment.refresh()
    for reply in comment.replies:
        print(reply.author.name)
        print(BOT_NAME)
"""
    



        