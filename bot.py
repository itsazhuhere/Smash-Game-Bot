
import praw
import re
import serverset
import titleparser
import traceback
import config
from serverrequest import *
from time import sleep
from prawcore.exceptions import RequestException
from praw.exceptions import ClientException

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
        db_return = parse_message(body)
        reply = build_reply(db_return)
        if reply and reply[0]:
            try:
                reply_message(reply, comment)
            except praw.exceptions.APIException as e:
                e = str(e)
                if "TOO_LONG" in e:
                    pass
                else:
                    minutes = re.search("(\d+) minute", str(e))
                    if minutes:
                        sleep(int(minutes.group(1))*60)
                        reply_message(reply, comment)
            except Exception as e:
                print(e)
                pass
        else:
            #TODO: decide if in a failed query, to send the user a private
            #message displaying what their search was parsed into
            pass
        num_comments += 1

def reply_message(reply, comment):
    if not reply:
        return
    if isinstance(reply,list):
        comment = comment.reply(reply.pop(0))
        reply_message(reply, comment)
    else:
        #reply is a str
        comment.reply(reply)

def parse_message(message):
    request_iter = request_regex.finditer(message)
    requests = []
    for request in request_iter:
        print(request)
        requests.append(determine_request(request))
    if requests:
        results = serverset.build_request(requests)
        return results

def is_date(input):
    """
    Date format must be either a single number (i.e. 2007), or
    use date separators (/ or - or 'to')
    """
    if isinstance(input, int):
        return True
    #input is a str
    else:
        return input.find("/") != -1 or input.find("-") != -1 or input.find("to") != -1

get_brackets_query = "select bracket from brackets"
brackets_set = set()
for bracket in serverset.make_db_request(get_brackets_query):
    brackets_set.add(bracket["bracket"])

def is_bracket(input):
    return input in brackets_set

request_dict_base = {"player1":"",
                     "player2":"",
                     "tournament":"LAST",
                     "bracket":"ALL",
                     "date":""
                     }

def is_replied(comment):
    if comment.replies:
        for reply in comment.replies:
            if not reply.author:
                continue
            
            #TODO: determine if author.name is already lower()
            if(reply.author.name.lower() == BOT_NAME):
                return True
    return False

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
    results = []
    for entry in info:
        requests.append(create_query(entry))
    for request in requests:
        results.append(serverset.make_db_request(request))
    return results


YOUTUBE_LINK = "https://www.youtube.com/watch?v="
#Reddit comment formatting tokens
BOLD = "**"         #bold requires the token to be on both sides of the text to bold
ENDL = "    \n"     #end line is four spaces followed by endline
LINE = "***" +ENDL  #creates a horizontal line, TODO: check if ENDL is needed


section_format = "{player1} vs. {player2}:"
video_format = "[{bracket}](" + YOUTUBE_LINK + "{video_id})" + ENDL

continued = "*Continued as a reply to this comment...*"+ENDL
footer = LINE + "^(This was an automated response) ^\| ^[FAQ](#) \| ^([Report a problem/error](#)) \| ^([Github](#))"
max_reply_characters = CHARACTER_LIMIT - len(footer) - len(continued)

def build_reply(results):
    #TODO: make this the player search reply and have a separate reply
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
    if results:
        print(results)
        reply_string = ""
        for entry in results:
            if not entry:
                continue
            entry_string = ""
            entry_dicts = sort_results(entry)
            tournament_set = set()
            entry_string += make_section(entry_dicts)
            for row in entry_dicts:
                formatted_line = ""
                if row["tournament"] not in tournament_set:
                    #make a tournament heading
                    formatted_line += row["tournament"] + ":" + ENDL
                    tournament_set.add(row["tournament"])
                formatted_line += video_format.format(bracket=row["bracketproper"],
                                                      video_id=row["video"]
                                                      )
                if len(reply_string)+len(entry_string)+len(formatted_line)>= max_reply_characters:
                    reply_string += entry_string + continued + footer
                    reply.append(reply_string)
                    reply_string = ""
                    entry_string = formatted_line
                else:
                    entry_string += formatted_line
                    
            reply_string += entry_string + LINE
        if reply_string:
            reply.append(reply_string+footer)
    #additionally add a footer to the message that gives info on the bot
    return reply


def build_failure_reply():
    pass



bracket_hierarchy = {}

def make_section(entry_dicts):
    return BOLD + section_format.format(player1=entry_dicts[0]["player1"],player2=entry_dicts[0]["player2"]) + BOLD + ENDL

def sort_results(entry_dicts):
    #TODO: for now do not do any sorting, will later implement a sort based on bracket
    #sorting will now be done within the database; results will be returned in the
    #order that they should be displayed
    return entry_dicts

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
    



        