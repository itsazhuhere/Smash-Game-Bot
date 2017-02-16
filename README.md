# Smash-Game-Bot
A reddit bot to provide direct links to tournament games of the Super Smash Bros series.


A heavily WIP project.

Personal information (such as the database login info and YouTube API key) is stored in a config.py module. 
You can make your own to make the project work for yourself.

```

#config.py

import pymysql.cursors

connect_dict = dict(host="localhost",
                    user=<user>,
                    password=<password>,
                    db=<database>,
                    charset='utf8mb4',
                    cursorclass=pymysql.cursors.DictCursor)

youtube_dict = dict(key=<key>
                    )

```
Dependencies:

PRAW

pymysql
