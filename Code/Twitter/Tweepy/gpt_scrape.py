import tweepy
from tweepy import OAuthHandler
import json
import datetime as dt
import time
import os
import pandas as pd
import sys
import configparser as cp

def load_api():
    ''' Function that loads the twitter API after authorizing the user. '''

    config = cp.ConfigParser()
    config.read('config.ini')
    api_key = config['twitter']['api_key']
    api_key_secret = config['twitter']['api_key_secret']
    access_token = config['twitter']['access_token']
    access_token_secret =config['twitter']['access_token_secret']

    #Setup authentication for Tweepy
    auth = tweepy.OAuthHandler(api_key,api_key_secret)
    auth.set_access_token(access_token,access_token_secret)
    # load the twitter API via tweepy
    return tweepy.API(auth)


def tweet_text_refine(text):
    ''' Function that refines the text and remove the newline character. This is neede as it can add line breaks in csv''' 
    text.replace('\n\n', '\\n').replace('\n', '\\n')
    return text


def tweet_search(api, query, max_tweets, max_id, since_id, GPT_id):
    ''' Function that takes in a search string 'query', the maximum
        number of tweets 'max_tweets', and the minimum (i.e., starting)
        tweet id. It returns a list of tweepy.models.Status objects. '''

    searched_tweets = []
    while len(searched_tweets) < max_tweets:
        remaining_tweets = max_tweets - len(searched_tweets)
        try:
            new_tweets = api.search_tweets(q=query, count=remaining_tweets,
                                    # since_id=str(since_id),
				                    # max_id=str(max_id-1),
                                    result_type='popular')
#                                    geocode=geocode)
            print('found',len(new_tweets),'tweets')
            if not new_tweets:
                print('no tweets found')
                break
            for tweet in new_tweets:
                searched_tweets.append([GPT_id,query,tweet.id,tweet.created_at,tweet_text_refine(tweet.text),tweet.source,tweet.user.id,tweet.user.name,tweet.user.screen_name,tweet.user.location,tweet.retweet_count,tweet.favorite_count])
            max_id = new_tweets[-1].id
        except tweepy.errors.TweepyException:
            print('exception raised, waiting 15 minutes')
            print('(until:', dt.datetime.now()+dt.timedelta(minutes=15), ')')
            time.sleep(15*60)
            break # stop the loop
    return searched_tweets, max_id


def get_tweet_id(api, date='', days_ago=9, query='a'):
    ''' Function that gets the ID of a tweet. This ID can then be
        used as a 'starting point' from which to search. The query is
        required and has been set to a commonly used word by default.
        The variable 'days_ago' has been initialized to the maximum
        amount we are able to search back in time (9).'''

    if date:
        # return an ID from the start of the given day
        td = date + dt.timedelta(days=1)
        tweet_date = '{0}-{1:0>2}-{2:0>2}'.format(td.year, td.month, td.day)
        tweet = api.search_tweets(tweet_dateq=query, count=1, until=tweet_date)
    else:
        # return an ID from __ days ago
        td = dt.datetime.now() - dt.timedelta(days=days_ago)
        tweet_date = '{0}-{1:0>2}-{2:0>2}'.format(td.year, td.month, td.day)
        # get list of up to 10 tweets
        tweet = api.search_tweets(q=query, count=10, until=tweet_date)
        print('search limit (start/stop):',tweet[0].created_at)
        # return the id of the first tweet in the list
        return tweet[0]

def get_search_phrases(filename):
    '''Funtion that fetches the hashtags from the files'''
    with open(filename) as f:
        lines = f.read().splitlines()
    return lines

def write_tweets(tweets, filename):
    ''' Function that appends tweets to a file. '''

    # Make data frame of above data
    df = pd.DataFrame(tweets)
 
    # append data frame to CSV file
    df.to_csv(filename, mode='a', index=False, header=False,na_rep='Unknown')
    return len(df)

search_phrases = get_search_phrases('GPTKeywords.txt')
# search_phrase = '#ChatGPT'
max_count = 3333                           # max count for a GPT id
max_tweets = 100                           # number of tweets per search (will be
                                           # iterated over) - maximum is 100
min_days_old, max_days_old = 1, 8          # search limits e.g., from 7 to 8
                                           # gives current weekday from last week,
                                           # min_days_old=0 will search from right now

cols = ['GPTID','Keyword','ID','Created_At','Text','Source','UserID','Username','User_ScreenName','Location','Retweet_Count','Like_Count']


# ### Main Code to run the script
# This script will run and fetch the date from when to start and the id to start fetching tweets. It will fetch all the tweeets until the max count is reached and will also wait if there are any request timeout for 15 mins. Once fetched it will write the data to a csv.

print('Search phrase =', search_phrases)

''' other variables '''
if not os.path.exists("popular"):
    os.mkdir("popular")

name = 'GPTMegaData'
csv_file_root = 'popular' + '/'  + name
os.makedirs(os.path.dirname(csv_file_root), exist_ok=True)
read_IDs = False

# open a file in which to store the tweets
if max_days_old - min_days_old == 1:
    d = dt.datetime.now() - dt.timedelta(days=min_days_old)
    print('Checking date',d)
    day = '{0}-{1:0>2}-{2:0>2}'.format(d.year, d.month, d.day)
else:
    d1 = dt.datetime.now() - dt.timedelta(days=max_days_old-1)
    d2 = dt.datetime.now() - dt.timedelta(days=min_days_old)
    day = '{0}-{1:0>2}-{2:0>2}_to_{3}-{4:0>2}-{5:0>2}'.format(
        d1.year, d1.month, d1.day, d2.year, d2.month, d2.day)
csv_file = csv_file_root + '.csv'
if os.path.isfile(csv_file):
    print('Appending tweets to file named: ',csv_file)
    read_IDs = True

# authorize and load the twitter API
api = load_api()
# set the 'starting point' ID for tweet collection
if read_IDs:
    # open the csv file and get the latest tweet ID
    df = pd.read_csv(csv_file)
    if not (df.loc[df['GPTID'] == 0]).empty:
        max_id = df.loc[df['GPTID'] == 0].iloc[-1]['ID']
        print('Searching from the bottom ID in file')
    else:
        if min_days_old == 0:
            max_id = -1
        else:
            tweet = get_tweet_id(api, days_ago=(min_days_old-1))
            max_id = tweet.id
            s_date = tweet.created_at
else:
    df = pd.DataFrame(columns=cols)
    df.to_csv(csv_file,index=False)
    # get the ID of a tweet that is min_days_old
    if min_days_old == 0:
        max_id = -1
    else:
        tweet = get_tweet_id(api, days_ago=(min_days_old-1))
        max_id = tweet.id
        s_date = tweet.created_at
# set the smallest ID to search for
tweet = get_tweet_id(api, days_ago=(max_days_old-1))
since_id = tweet.id
e_date = tweet.created_at
print('max id (starting point) =', max_id)
print('since id (ending point) =', since_id)


''' tweet gathering loop  '''


for search_phrase in search_phrases:
    count, exitcount = 0, 0
    rows = 0
    tic = time.perf_counter()
    while rows < max_count:
        count += 1
        print('count =',count)
        # collect tweets and update max_id

        tweets, max_id = tweet_search(api, search_phrase, max_tweets,
                                    max_id=max_id, since_id=since_id,GPT_id = 0)
        # write tweets to file in JSON format
        if tweets:
            rows += write_tweets(tweets, csv_file)
            exitcount = 0
        else:
            exitcount += 1
            if exitcount == 3:
                toc = time.perf_counter()
                print('TOTAL NUMBER OF RECORDS ', str(rows))
                print(f'TIME TAKEN = {toc - tic:0.4f} seconds')
                sys.exit('Maximum number of empty tweet strings reached - exiting')
    toc = time.perf_counter()
    print(f'Scraping has completed for {search_phrase} !')
    print('TOTAL NUMBER OF RECORDS ', str(rows))
    print(f'TIME TAKEN = {toc - tic:0.4f} seconds')