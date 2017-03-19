
from __future__ import print_function
from __future__ import unicode_literals
from logging import codecs

import requests
import json
import os
import re
from config import youtube_dict
from datetime import datetime
from datetime import timedelta
#import serverset
import titleparser
import updateseparator

"""
Primarily grabs video info from the uploads of channels that contain videos of SmashBros
tournament games. 
Grabs the title, video ID, and channel ID
Grabbed info gets recorded into a text file
"""

VIDEO_BASE = "{title}\tVideo:{videoId}\tChannel:{channelId}"



YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"


URL = "https://www.googleapis.com/youtube/v3/search"
CHANNELURL = "https://www.googleapis.com/youtube/v3/channels"
PLAYLISTURL = "https://www.googleapis.com/youtube/v3/playlistItems"
VIDEOURL = "https://www.googleapis.com/youtube/v3/videos"

CHANNELNAME = "HTC" + ".txt"
CHANNEL = "UCcLgWeVW3Z_ZWCYURqfgvaQ"
DIRECTORY = "\Channels"
 
MAX_RESULTS = 50


NOTOKEN = -1
ENDOFSEARCH = 0
NEXTSEARCHTOKEN = ""
MIN_VIEWS = 1000

END_FILE = "----------------------------"

US = updateseparator.UpdateSeparator()

def get_playlist_id(channel_id):
    search_options = {"key": youtube_dict["key"],
                      "id": channel_id,
                      "part" : "contentDetails",
                      }
    return requests.get(CHANNELURL, search_options).json()["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

#this gets the playlist id of the uploads of the user, which contains all videos it has submitted
#since we use channel id to find the channel, there will always be one item in the "items" of the json

playlist_id = get_playlist_id(CHANNEL)

search_options = {"key": youtube_dict["key"],
                  "playlistId": "",
                  "part" : "snippet",
                  "maxResults": str(MAX_RESULTS)
                  }

def get_search_options(channel = CHANNEL):
    if not search_options["playlistId"]:
        search_options["playlistId"] = get_playlist_id(channel)
    return search_options.copy()

def get_video_by_ids(video_ids):
    results = []
    video_ids_len = len(video_ids)
    for i in range(0,video_ids_len,MAX_RESULTS):
        #make_db_request returns a json with an items section containing all videos
        #max per search: MAX_RESULTS
        
        results += make_request({"key":youtube_dict["key"],
                                 "id":",".join(video_ids[i:min(i+MAX_RESULTS,video_ids_len)]),
                                 "part":"snippet,id",
                                 "maxResults":MAX_RESULTS})["items"]
                                 
                                 
    return results

def get_videos_by_channel(options, nextSearch, stop_id=""):
    new_options = options.copy()
    if nextSearch == NOTOKEN:
        pass
    elif nextSearch == ENDOFSEARCH:
        return []
    else:
        new_options["pageToken"] = nextSearch
    try:
        json = make_request(new_options)
        if json["items"]:
            print(json)
            games_list = to_list(json, stop_id)
            if games_list[-1]["id"] == stop_id:
                return games_list[:-1]
            return games_list+get_videos_by_channel(options, get_nextPageToken(json), stop_id)
        else:
            return []
    except:
        return []

def extended_search(channel):
    #uses get_videos_by_channel then either commits it to a file or directly to db
    options = get_search_options()
    search_result = get_videos_by_channel(options, NOTOKEN)
    to_file(search_result, channel)
    #to_db(search_result)
        
def renew_info(data_file):
    with codecs.open(data_file,"r",encoding="utf-8") as videos:
        updates = []
        for line in videos.read().split("\n"):
            row = line.split("\t")
            video_id = row[7]

def to_list(json, stop_id=""):
    items = json["items"]
    games_list = []
    for item in items:
        #there is currently no view based processing; that can be done through a separate
        #query to the youtube api
        
        games_dict = {"id": item["snippet"]["resourceId"]["videoId"],
                      "channelId": item["snippet"]["channelId"],
                      "title": item["snippet"]["title"],
                      "date": item["snippet"]["publishedAt"]
                      }
        games_list.append(games_dict)
        if games_dict["id"] == stop_id:
            break
    return games_list
    
def get_nextPageToken(json):    
    try:
        
        nextPageToken = json["nextPageToken"]
    except KeyError:
        nextPageToken = ENDOFSEARCH
    NEXTSEARCHTOKEN = nextPageToken
    return nextPageToken if nextPageToken else ENDOFSEARCH


def make_request(options):
    print("Query Successful")
    return requests.get(PLAYLISTURL, options).json()
    
    
def to_file(game_list, file_name):
   
    with codecs.open(file_name, "a", encoding="utf-8") as infile:
        n = 0
        for game in game_list:
            try:
                print("{title}\tVideo:{videoId}\tChannel:{channelId}".format(title=game["title"],  
                                                                       videoId=game["id"], 
                                                                       channelId=game["channelId"]), 
                      file= infile)
            
            except UnicodeError:
                print(str(n), file=infile)
                print("Added video")
                n+=1
        print(US.get_separator(),file=infile)  
        print(n)
    print("Finished adding")

video_regex = re.compile("[\s\S]+Video:(?P<video_id>[\s\S]{11})")


def update_files():
    """
    Creates a file with all of the videos that were uploaded from now up until
    the first video of the last update has been reached. 
    
    
    Potential problems in the case where the latest video has been deleted
    """
    
    cwd = os.getcwd() + DIRECTORY
    for directory in os.listdir(cwd):
        directory = cwd+"\\"+directory
        if not os.path.isdir(directory):
            continue
        directory += "\\"
        
        json_path = directory+"channel_info.json"
        
        channel_info = ""
        with open(json_path,"r") as json_file:
            channel_info = json.load(json_file)
            
        options = search_options.copy()
        options["playlistId"] = get_playlist_id(channel_info["channel_id"])
        result = get_videos_by_channel(options, NOTOKEN, channel_info["latest"])
        new_path = directory+"new.txt"
        to_file(result, new_path)
        
        with open(new_path,"r") as new_file:
            latest_entry = new_file.readline()
            video_regex_match = video_regex.search(latest_entry)
            if video_regex_match:
                channel_info["latest"] = video_regex_match.groupdict()["video_id"]
            
        with open(json_path, "w") as json_file:
            json_file.write(json.dumps(channel_info))
        
    
def concat_files(new_file_path, old_file_path):
    with open(new_file_path,"a") as new_file:
        with open(old_file_path, "r") as old_file:
            new_file.write(old_file.read())
    os.remove(old_file_path)
    os.rename(new_file_path,old_file_path)
    
def concat_all_new_files():
    cwd = os.getcwd() + DIRECTORY
    for directory in os.listdir(cwd):
        directory = cwd+"\\"+directory
        if not os.path.isdir(directory):
            continue
        directory += "\\"
        
        json_path = directory+"channel_info.json"
        
        channel_info = ""
        with open(json_path,"r") as json_file:
            channel_info = json.load(json_file)
        
        #all channel directories contain the name of the main file including the extension
        #TODO: remove extension so this is less awkward
        channel_file = channel_info["file"].replace(".txt","")
        concat_files(directory+"new.txt",directory+channel_file+".txt")
        concat_files(directory+"errors.txt",directory+channel_file+"errors.txt")
        concat_files(directory+"matches.txt",directory+channel_file+"matches.txt")
        

if __name__ == "__main__":
    #extended_search(CHANNELNAME)
    update_files()
    
    
    
    
    