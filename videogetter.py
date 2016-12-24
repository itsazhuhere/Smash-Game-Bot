'''
Created on Jun 14, 2016

@author: Andre
'''
from __future__ import print_function
from logging import codecs

import requests
import json
from config import youtube_dict
from datetime import datetime
from datetime import timedelta
#import serverset
import titleparser



VIDEO_BASE = "{title}\tVideo:{videoId}\tChannel:{channelId}"



YOUTUBE_API_SERVICE_NAME = "youtube"
YOUTUBE_API_VERSION = "v3"


URL = "https://www.googleapis.com/youtube/v3/search"
CHANNELURL = "https://www.googleapis.com/youtube/v3/channels"
PLAYLISTURL = "https://www.googleapis.com/youtube/v3/playlistItems"
VIDEOURL = "https://www.googleapis.com/youtube/v3/videos"

CHANNELNAME = "HTC" + ".txt"
CHANNEL = "UCcLgWeVW3Z_ZWCYURqfgvaQ"

MAX_RESULTS = 50


NOTOKEN = -1
ENDOFSEARCH = 0
NEXTSEARCHTOKEN = ""
MIN_VIEWS = 1000


get_playlist_options = {"key": youtube_dict["key"],
                        "id": CHANNEL,
                        "part" : "contentDetails",
                        }
#this gets the playlist id of the uploads of the user, which contains all videos it has submitted
#since we use channel id to find the channel, there will always be one item in the "items" of the json
playlist_id = requests.get(CHANNELURL, get_playlist_options).json()["items"][0]["contentDetails"]["relatedPlaylists"]["uploads"]

search_options = {"key": youtube_dict["key"],
                  "playlistId": playlist_id,
                  "part" : "snippet",
                  "maxResults": str(MAX_RESULTS)
                  }


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




def get_videos_by_channel(options, nextSearch):
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
            return to_list(json)+get_videos_by_channel(options, get_nextPageToken(json))
        else:
            return []
    except:
        return []

def extended_search():
    #uses the recursive function get_videos_by_channel then either commits it to a file or directly to db
    options = search_options.copy()
    search_result = get_videos_by_channel(options, NOTOKEN)
    to_file(search_result)
    #to_db(search_result)
        
def renew_info(data_file):
    with codecs.open(data_file,"r",encoding="utf-8") as videos:
        updates = []
        for line in videos.read().split("\n"):
            row = line.split("\t")
            video_id = row[7]

def to_list(json):
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
    return games_list
    
def get_nextPageToken(json):    
    try:
        
        nextPageToken = json["nextPageToken"]
    except KeyError:
        nextPageToken = ENDOFSEARCH
    NEXTSEARCHTOKEN = nextPageToken
    return nextPageToken if nextPageToken else ENDOFSEARCH


def get_channel_id(channel_name):
    pass

def make_request(options):
    print("Query Successful")
    return requests.get(PLAYLISTURL, options).json()
    
    
def to_file(game_list):
   
    with codecs.open(CHANNELNAME, "a+", encoding="utf-8") as infile:
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
        
        print(n)
    print("Finished adding")
    
def to_db(game_list):
    parser = titleparser.TitleParser()
    parser.set_pattern(titleparser.VGB)
    parser.set_files("db_match.txt", "db_error.txt")
    game_strings = []
    for game in game_list:
        try:
            game_strings.append("{title}\tVideo:{videoId}\tChannel:{channelId}".format(title=game["title"],  
                                                                                       videoId=game["id"], 
                                                                                       channelId=game["channelId"]))
        
        except UnicodeError:
            print(game["id"])
    parser.filter_video_list(game_strings, True)
    
    
    


if __name__ == "__main__":
    extended_search()
    
    
    
    
    