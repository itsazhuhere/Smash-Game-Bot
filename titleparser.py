
from __future__ import print_function
import re
from logging import codecs
import serverset
import os
import json
import updateseparator
from titles import *

DIRECTORY = "\Channels"
END_FILE = "----------------------------"



class TitleParser:
    keys = ["tourny","chars1","tag1","chars2","tag2","round","game"]
    games = {"Melee": ["SSBM"],
             "Smash 4" : ["Wii U","Sm4sh","SSB4"],
             "Smash 64" : ["SSB64"]
             }
    
    def __init__(self):
        for game in self.games.keys():
            all_names = [re.compile(game,re.IGNORECASE)]
            for name in self.games[game]:
                all_names.append(re.compile(name,re.IGNORECASE))
            
            self.games[game] = all_names
    
    def set_pattern(self, pattern):
        self.pattern = re.compile(pattern)
        
    def set_postmatch_pattern(self, postmatches,flags=lambda x:0):
        self.postmatches = []
        for pattern in postmatches:
            if pattern.isupper():
                pattern = at_least_one_space(pattern)
            self.postmatches.append(re.compile(pattern, flags(pattern)))
            
        
    def set_files(self, matched_file, error_file):
        self.match = matched_file
        self.error = error_file
    
    def filter_video_file(self, file_name, to_db, db_table="", write_mode="w", defaults=dict(),restrictions=dict()):
        with codecs.open(self.match, write_mode, encoding="utf-8") as matched,\
        codecs.open(self.error, write_mode, encoding="utf-8") as error,\
        codecs.open(file_name, "r", encoding="utf-8") as infile:
            results = []
            for title in infile.read().split("\n"):
                if "--------------" in title:
                    break
                result = self.pattern.match(title)
                if result:
                    accepted = True
                    r_dict = result.groupdict()
                    r_dict["text"] = title
                    self.fix_r_dict(r_dict,defaults)
                    for key in restrictions.keys():
                        if restrictions[key] != r_dict[key]:
                            print(title+" MATCH FAIL: "+key,file=error)
                            print("error")
                            accepted = False
                            break
                    if accepted:
                        results.append(r_dict)
                        print(print_format.format(r_dict["tourny"],
                                                  r_dict["tag1"],
                                                  r_dict["chars1"],
                                                  r_dict["tag2"],
                                                  r_dict["chars2"],
                                                  r_dict["round"],
                                                  r_dict["game"]), 
                        
                        file = matched) 
                else:
                    print(title, file = error)
            if to_db and db_table:
                updates = serverset.build_inserts(results,db_table)
                serverset.make_update(updates)
            else:
                return results
    
    def fix_r_dict(self, r_dict, defaults):
        for key in defaults.keys():
            r_dict[key] = defaults[key]
        for key in self.keys:
            if key not in r_dict.keys():
                r_dict[key] = "Unknown"
        title_text = r_dict["text"]
        for game in self.games.keys():
            for name in self.games[game]:
                if name.search(title_text):
                    r_dict["game"] = game
                    break
                
    def additional_parsing(self):
        #implement the functions in serverset that use the titlerparser module here #hollaaaa
        pass
    def match_postmatch_pattern(self, text):
        #This function assumes the pattern will be a dictionary,
        #as returned by a db query
        for match in self.postmatches:
            #match is a regex object
            result = match.search(text)
            if result:
                return match.pattern
        return "Bracket N/A"
   
def at_least_one_space(pattern):
    return "(^|[\s:\-])"+pattern+"[\s:\-]"   
            
        
def print_file(file_name):
    with codecs.open(file_name, "r", encoding="utf-8") as infile:
        n = 0
        for line in infile.read().split("\n"):
            if n>10000:
                break
            print(line)
            n+=1
            
def add_new_videos(dir, to_server):
    #Use this function by itself to test the changes out
    #(by viewing the output files)
    #Commit to database in the serverset module
    titleparser = TitleParser()
    cwd = os.getcwd() + dir
    for directory in os.listdir(cwd):
        directory = cwd+"\\"+directory
        if not os.path.isdir(directory):
            continue
        directory += "\\"
        
        json_path = directory+"channel_info.json"
        
        channel_info = ""
        with open(json_path,"r") as json_file:
            channel_info = json.load(json_file)
        channel_file = channel_info["file"].replace(".txt","")
        titleparser.set_pattern(regex_dict[channel_file])
        titleparser.set_files(directory+"matches.txt",directory+"errors.txt")
        titleparser.filter_video_file(directory+"new.txt",
                                      to_server,
                                      db_table="new_games"
                                      )
        
    
if __name__ == "__main__":
    """
    test_string = "S@X 153 - Pinkfresh (Bayonetta) Vs. DA | Venia (Greninja) SSB4 Grand Finals - Smash Wii U - Smash 4"
    test_pattern = tournament
    result = re.search(test_pattern, test_string)
    print(result.group())
    """
    """
    parser = TitleParser()
    parser.set_pattern(HTC)
    parser.set_files("HTCmatches.txt", "HTCerrors.txt")
    parser.filter_video_file("HTC.txt", 
                             True,
                             db_table="games",
                             defaults=dict(),
                             restrictions=dict())
    """
    
    add_new_videos(DIRECTORY, True)
    