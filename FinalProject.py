import YouTubeData
import sqlite3
import requests
import matplotlib.pylab as plt
# Imports required for Reddit data parsing
import praw
import prawcore
import pandas as pd
from datetime import datetime as dt
# imports necessary for TMDB
import tmdbsimple as tmdb

## Getting Data from Movie Database
## Input: Three movie titles
## Output: returns dictionary with key-pair (title-revenue)
def TMDBData(movie1, movie2, movie3):
    dic = {}
    tmdb.API_KEY = '7c324bb557705b2cf106bcc607ee0f78'
    search = tmdb.Search()
    ## Loop searches TMDB for the three variable movies
    for x in [movie1, movie2, movie3]:
        response = search.movie(query=x)
        for s in search.results:
            year = s['release_date'].split('-')[0]
            ## Checks to see if the movie was released in 2018 to ensure it is the correct movie
            if year == '2018':
                id = s['id']
                ## Takes the movie ID from the search, and gets more information to get revenue data
                movie = tmdb.Movies(id)
                response = movie.info()
                dic[response['original_title']] = response['revenue']
            else:
                continue
    ## Print statmenet for how much revenue each movie has made
    for rev in dic.items():
        print('{} has made ${} in revenue thus far.'.format(rev[0], rev[1]))
    return dic

# Getting Data from Reddit
## Input: Three movie titles
## Output: returns info list on them to be used in table
##        List of lists with [author, movie id, # comments, score, date created, movie title]
def redditData(m1, m2, m3):
    secret = 'ju7N0ec4KXpdNroFdoYhpqadcQQ'
    script = 'GCcNlMHif5lyDA'

    ## Grants premission to use reddit API
    reddit = praw.Reddit(client_id= script, \
                         client_secret= secret, \
                         user_agent= 'SI 206', \
                         username='primefour', \
                         password='Griffiep1997.')
    info = []
    ## Goes through reddit and searches the movie title
    for x in [m1, m2, m3]:
        subreddit = reddit.subreddit('all').search(x, limit = 200)
        for sub in subreddit:
            info.append([sub.author, sub.id, sub.num_comments, sub.score, sub.created_utc, x])
    return info

## Put data from YouTube into SQL database
## Input: Three movie titles
## Output: Returns nothing
def YouTubeSql(movie1, movie2, movie3):
    ## Connects to database and creates table
    conn = sqlite3.connect('YouTubeData.sqlite')
    cur= conn.cursor()
    cur.execute(''' DROP TABLE IF EXISTS YouTubeData ''')
    cur.execute(''' CREATE TABLE IF NOT EXISTS YouTubeData
                (q TEXT,
                 title TEXT,
                 time_posted TIMESTAMP,
                 views INTEGER,
                 likes INTEGER,
                 comments INTEGER)''')
    ## Calls YouTube helper file to authenticate API, and get information on movies
    info = YouTubeData.main(movie1, movie2, movie3)
    ## Goes through information received from other file and
    for x in info:
        y = x[0]['items'][0]
        q = x[1]
        try:
            title = y['snippet']['title']
        except:
            title = 'N/A'
        try:
            time = y['snippet']['publishedAt']
        except:
            time = 'N/A'
        try:
            views = y['statistics']['viewCount']
        except:
            views = 'N/A'
        try:
            likes = y['statistics']['likeCount']
        except:
            likes = 'N/A'
        try:
            comments = y['statistics']['commentCount']
        except:
            comments = 'N/A'
        cur.execute('''
                    INSERT INTO YouTubeData (q, title, time_posted, views, likes, comments)
                    VALUES (?, ?, ?, ?, ?, ?)''', (q, title, time, views, likes, comments))
    conn.commit()
    cur.close()
    return

## Creates SQL table for Reddit data
## Input: Three movie titles
## Output: returns nothing
def redditSQL(movie1, movie2, movie3):
    ## Sets up the table
    conn = sqlite3.connect('RedditData.sqlite')
    cur= conn.cursor()
    cur.execute(''' DROP TABLE IF EXISTS RedditData ''')
    cur.execute(''' CREATE TABLE IF NOT EXISTS RedditData
                (q TEXT,
                 author TEXT,
                 id TEXT,
                 comments INTEGER,
                 upvotes INTEGER,
                 time_posted TIMESTAMP)''')
    ## Parces data to add data to teh table
    for x in redditData(movie1, movie2, movie3):
        author = str(x[0])
        id = x[1]
        comm = x[2]
        up = x[3]
        q = x[5]
        timestamp = dt.fromtimestamp(x[4])
        time = timestamp.strftime('%Y-%m-%d %H:%M:%S')
        cur.execute('''
                    INSERT INTO RedditData (q, author, id, comments, upvotes, time_posted)
                    VALUES (?, ?, ?, ?, ?, ?)''', (q, author, id, comm, up, time))
    conn.commit()
    cur.close()
    return

## Helper function for YouTube Plotting function
## Input: Cursor from SQL, ax object for plotting, movie title, desired color for Line
## Output: Returns nothing
def helperYT(cur, ax, movie, color):
    l = []
    ## looks at information in cursor and gets info on likes and comments for each movie
    for x in cur:
        if x[0] == movie:
            temp = x[1].split('T')[0].split('-')
            ## Checks to see if the video was uploaded in 2018 to ensure currency
            if temp[0] == '2018':
                i = int(x[3]) + int(x[4])
                l.append(i)
    sort = sorted(l, key = lambda x: x, reverse = True)
    ## Limits the number of datapoints (videos) to the top 10
    if len(sort) > 10:
        for y in range(10, len(sort)):
            sort.remove(sort[10])
    xs = []
    ys = []
    lth = len(sort)
    for f in range(lth):
        xs.append(f + 1)
        ys.append(l[f])
    print('The top-10 most viewed YouTube videos about {} received:'.format(movie))
    print('{} likes and comments combined'.format(sum(ys)))
    ax.plot(xs, ys, color, label=movie)
    return

## Creates and plots line graph for YouTube data found
## Input: Three movie titles
## Output: Nothing, but creates and shows a line graph
def plotYT(m1, m2, m3):
    conn = sqlite3.connect('YouTubeData.sqlite')
    cur = conn.cursor()
    ## Finds all videos with over 70k views to make sure all are relatively popular
    cur.execute('''
                SELECT q, time_posted, views, likes, comments
                FROM YouTubeData
                WHERE time_posted <> 'N/A'
                AND views <>'N/A'
                AND views > '70000'
                AND likes <> 'N/A'
                AND comments <> 'N/A' ''')
    ## Sorts videos by date
    sort = sorted(cur, key = lambda q: (int(q[1].split('T')[0].split('-')[0]), int(q[1].split('T')[0].split('-')[1])))
    fig, ax = plt.subplots()

    helperYT(sort, ax, m1, '-b')
    helperYT(sort, ax, m2, '-y')
    helperYT(sort, ax, m3, '-r')
    ## Creates graph
    ax.legend()
    ax.set(xlabel='Data Point #', ylabel='Calculated Engagement',
        title='Line Graph of Video Engagement Over Time')
    ax.grid()
    fig.savefig("YouTube_LineGraph.png")
    plt.show()
    return

## Helper function for the Reddit plot
## Input: Cursor from SQL, movie title
## Output: returns tuple with (movie and comments + upvotes)
def helperReddit(cur, movie):
    i = 0
    cur.execute('''
                SELECT q, comments, upvotes, time_posted
                FROM RedditData
                WHERE q = ?''', (movie,))
    # Makes sure year is 2018 and adds the comments and upvotes to be used
    for x in cur:
        year = x[-1].split()[0].split('-')[0]
        if year == '2018':
            count = int(x[1]) + int(x[2])
            i = i + count
    return(movie, i)

## Function that plots reddit data
## Input: Three movie titles
## Output: nothing, but creates and shows bar graph
def plotReddit(m1, m2, m3):
    ## Connects to SQL Database
    conn = sqlite3.connect('RedditData.sqlite')
    cur = conn.cursor()
    l = list()
    ## Call helper functions to get movie and upvotes+comments
    l.append(helperReddit(cur, m1))
    l.append(helperReddit(cur, m2))
    l.append(helperReddit(cur, m3))
    xval = []
    yval = []
    for x in l:
        xval.append(x[0])
        yval.append(x[1])
    ## Prints the outcome of API search
    print('Analyzing the Reddit API shows:')
    for y in l:
        print('{} has {} currently has comments and upvotes.'.format(y[0], y[1]))
    ## Create the graph
    plt.title('Bar Graph of Reddit Calculated Popularity for Movie')
    plt.xlabel('Movie Title')
    plt.ylabel('Calculated Popularity')
    plt.bar(xval, yval, color = 'byr')
    plt.savefig('Reddit_BarGraph.png')
    plt.show()
    return

## Creats Bar Graph of revenue for each movie
## Input: Three movie titles
## Output: returns nothing, but creates and shows a bar graph
def plotRevenue(m1, m2, m3):
    ## gets data from TMDB function
    d = TMDBData(m1, m2, m3)
    ## Creates graph
    plt.title('Bar Graph of Movie Revenue per TMDB')
    plt.xlabel('Movie Title')
    plt.ylabel('Revenue in Dollars')
    xval = []
    yval = []
    for x in d.items():
        xval.append(x[0])
        yval.append(x[1])
    plt.bar(xval, yval, color = 'byr')
    plt.savefig('Revenue_BarGraph.png')
    plt.show()
    return

## Main function. Takes in movies and runs whole program.
## Input: Three movie titles
## Ouptut: Returns nothing, but runs entire program.
def main(m1, m2, m3):
    # print('Creating SQL DB for YouTube Data')
    # YouTubeSql(m1, m2, m3)
    # print('Creating SQL DB for Reddit Data')
    # redditSQL(m1, m2, m3)
    print('---------------------------------------')
    print('YouTube Graph')
    plotYT(m1, m2, m3)
    print('---------------------------------------')
    print('Reddit Graph')
    plotReddit(m1, m2, m3)
    print('---------------------------------------')
    print('Revenue Graph')
    plotRevenue(m1, m2, m3)
    print('Finished')
    return

main('Avengers: Infinity War', 'Fantastic Beasts: The Crimes of Grindelwald', 'A Star is Born')
