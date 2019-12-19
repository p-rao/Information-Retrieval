# -*- coding: utf-8 -*-
"""
Created on Sun Sep  8 20:53:12 2019

@author: Priya Rao
"""
import string
import tweepy as tp
import time
import emoji
import regex
from datetime import datetime
from datetime import timedelta
import json
from collections import Counter
import preprocessor

api_key = "BAzvDVt5Jp7XfecxkkAoGi3xA"
api_secret_key = "jDxrsc2iLLRT7QBqBsKtvsYqS7bxT9ISj6YdwYi9QgErdXMvYB"
access_token = "1166211517370511363-Qta8gyKHCNc4VjYdRLL5FuUBxhCZto"
access_token_secret = "WsfrenCdDodyWYgAMO2K1O8TTTp0QjZlM2gmABz5agz5i"

twitter_handles_usa = ["JoeBiden", "realDonaldTrump", "SenSanders", "KamalaHarris", "VP"]
twitter_handles_india = ["myogiadityanath", "sardanarohit", "yadavtejashwi", "NitishKumar", "yadavakhilesh"]
twitter_handles_brazil = ["jairbolsonaro", "MarinaSilva", "geraldoalckmin", "jdoriajr", "joseserra_"]

emoticons = {':-)', ':)', ';)', ':o)', ':]', ':3', ':c)', ':>', '=]', '8)', '=)', ':}', ':^)', ':-D', ':D', '8-D',
             '8D', 'x-D', 'xD', 'X-D', 'XD', '=-D', '=D', '=-3', '=3', ':-))', ":'-)", ":')", ':*', ':^*', '>:P',
             ':-P', ':P', 'X-P', 'x-p', 'xp', 'XP', ':-p', ':p', '=p', ':-b', ':b', '>:)', '>;)', '>:-)', '<3', ':L',
             ':-/', '>:/', ':S', '>:[', ':@', ':-(', ':[', ':-||', '=L', ':<', ':-[', ':-<', '=\\', '=/', '>:(', ':(',
             '>.<', ":'-(", ":'(", ':\\', ':-c', ':c', ':{', '>:\\', ';('}

languages = ['en', 'hi', 'pt']


def hour_rounder(t):
    return (t.replace(second=0, microsecond=0, minute=0, hour=t.hour)
            + timedelta(hours=t.minute // 30))


def strip_smileys_emojis(text):
    smileys_emojis = []
    data = regex.findall(r'\X', text)
    for word in data:
        if any(char in emoji.UNICODE_EMOJI for char in word):
            smileys_emojis.append(word)
    for item in emoticons:
        if str(text).replace(" ", "").__contains__(item):
            smileys_emojis.append(item)
    return smileys_emojis


#BUILD THE FINAL TWEET OBJECT
def add_edit_tweet_fields(tweet, language, poi_tweet):
    atweet = {}
    atweet["poi_name"] = tweet["user"]["screen_name"] if tweet["in_reply_to_screen_name"] is None else tweet["in_reply_to_screen_name"]
    atweet["poi_id"] = poi_tweet["user"]["id"] if tweet["in_reply_to_user_id"] is None else tweet["in_reply_to_user_id"]
    atweet["replied_to_tweet_id"] = None if tweet["in_reply_to_status_id"] is None or poi_tweet["user"]["screen_name"] != tweet["user"]["screen_name"] else tweet["in_reply_to_status_id"]
    atweet["replied_to_user_id"] = None if tweet["in_reply_to_user_id"] is None or poi_tweet["user"]["screen_name"] != tweet["user"]["screen_name"] else tweet["in_reply_to_user_id"]
    atweet["reply_text"] = None if atweet["replied_to_tweet_id"] is None else tweet["full_text"]
    atweet["tweet_text"] = tweet["full_text"]
    atweet["tweet_lang"] = tweet["lang"]
    atweet["mentions"] = None if tweet['entities']['user_mentions'] is None else [d['screen_name'] for d in tweet['entities']['user_mentions']]
    atweet["tweet_urls"] = None if tweet['entities']['urls'] is None else [d['url'] for d in tweet['entities']['urls']]
    atweet["hashtags"] = None if tweet['entities']['hashtags'] is None else [d['text'] for d in tweet['entities']['hashtags']]
    emoticon_list = []
    emoticon_list = strip_smileys_emojis(tweet['full_text'])
    atweet["tweet_emoticons"] = None if len(emoticon_list) == 0 else str(emoticon_list)
    atweet["country"] = "USA"  ############# CHANGE THIS AS PER THE PERSON
    atweet["full_text"] = tweet["full_text"].replace("&lt;", "<").replace("&amp;", "&").replace("&gt;", ">")
    atweet['created_at'] = str(
        hour_rounder(datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S %z %Y')).strftime(
            "%Y-%m-%dT%H:%M:%SZ"))
    fieldname = "text_" + tweet["lang"]
    tweet_string = tweet['full_text']
    for smiley in emoticon_list:
        if(tweet_string.__contains__(smiley)):
            tweet_string = tweet_string.replace(smiley, "")
    tweet_string = preprocessor.clean(tweet_string)
    tweet_string = tweet_string.translate(str.maketrans('', '', string.punctuation))
    atweet[fieldname] = tweet_string
    atweet['tweet_loc'] = None
    for lang in languages:
        if lang != tweet["lang"]:
            fieldname = "text_" + lang
            atweet[fieldname] = None
    return atweet


def get_tweets(user, language):
    get_auth = tp.OAuthHandler(api_key, api_secret_key)
    get_auth.set_access_token(access_token, access_token_secret)
    twitter_api = tp.API(get_auth)
    data = []
    final_count = 0
    recentmost_tweet = twitter_api.user_timeline(id=user, count=1, include_rts=False, tweet_mode='extended')[0]
    final_id = recentmost_tweet.id

    for count in range(1, 1601, 200):
        older_tweets = twitter_api.user_timeline(id=user, count=200, max_id=final_id, include_rts=False,
                                                 tweet_mode='extended')
        for tweet in older_tweets:
            if tweet.lang == language:
                final_id = tweet.id
                data.append(tweet._json)
                final_count += 1

    id_list = []
    relevant_tweets = []
    for tweet in data:
        temp = datetime.strptime(str(tweet['created_at']), '%a %b %d %H:%M:%S %z %Y').date()
        if datetime.strptime('2019-09-08', '%Y-%m-%d').date() >= temp >= datetime.strptime('2019-09-04',
                                                                                           '%Y-%m-%d').date():
            relevant_tweets.append(tweet)
            id_list.append(tweet['id'])
        relevant_tweets.append(add_edit_tweet_fields(tweet, language, recentmost_tweet._json))

    filename = user + "__tweets.json"
    with open(filename, 'w', encoding="utf-8") as f:
        json.dump(relevant_tweets, f, ensure_ascii=False, indent=4)

    time.sleep(60)
    relevant_tweets.clear()

    print(final_count)
    print(id_list)
    minimum_id = id_list[-1]

    replies = []
    tweet_reply_ids = []
    reply_count = 0
    last_id = 0
    tweet_reply_ids_dict = {}
    for m in range(0, 20):
        if m == 0:
            for tweet in tp.Cursor(twitter_api.search, q=f'to:{user}', since_id=minimum_id, result_type='recent',
                                   timeout=999999, tweet_mode='extended').items(200):
                if hasattr(tweet, 'in_reply_to_status_id'):
                    for j in id_list:
                        if tweet.in_reply_to_status_id == j:
                            replies.append(tweet._json)
                            tweet_reply_ids.append(j)
                            tweet_reply_ids_dict = Counter(tweet_reply_ids)
                            reply_count += 1
                last_id = tweet.id
                print(reply_count)
            print(len(replies))
            if (len(tweet_reply_ids_dict) != 0 and tweet_reply_ids_dict[
                min(tweet_reply_ids_dict.keys(), key=(lambda k: tweet_reply_ids_dict[k]))] >= 20 and set(
                id_list) == set(tweet_reply_ids)):
                break
            else:
                continue
        else:
            if m == 10:
                time.sleep(900)
            for tweet in tp.Cursor(twitter_api.search, q=f'to:{user}', since_id=minimum_id, max_id=last_id,
                                   result_type='recent', timeout=999999, tweet_mode='extended').items(200):
                if hasattr(tweet, 'in_reply_to_status_id'):
                    for j in id_list:
                        if tweet.in_reply_to_status_id == j:
                            # print("")
                            # print('t',j)
                            # print("r", tweet.in_reply_to_status_id, "   ", tweet.full_text)
                            replies.append(tweet._json)
                            reply_count += 1
                            tweet_reply_ids.append(j)
                            tweet_reply_ids_dict = Counter(tweet_reply_ids)
                last_id = tweet.id
                print(reply_count)
            print(len(replies))
            if (len(tweet_reply_ids_dict) != 0 and tweet_reply_ids_dict[
                min(tweet_reply_ids_dict.keys(), key=(lambda k: tweet_reply_ids_dict[k]))] >= 20 and set(
                id_list) == set(tweet_reply_ids)):
                break
            else:
                continue

    for reply in replies:
        relevant_tweets.append(add_edit_tweet_fields(reply, language, recentmost_tweet._json))

    filename = user + "__replies.json"
    with open(filename, 'w', encoding="utf-8") as f:
        json.dump(replies, f, ensure_ascii=False, indent=4)

    mentions_data = []
    time.sleep(900)
    mentions_id = []
    ############## ADD EXPLICIT HASHTAGS OR MENTIONS IF NEEDED
    for counter in range(0, 1501, 200):
        if(counter == 0):
            for tweet in tp.Cursor(twitter_api.search, q=f"#{user} OR @{user}", count=200, lang="en",
                                   tweet_mode='extended', include_rts=False, since_id=minimum_id).items(200):
                mentions_data.append(add_edit_tweet_fields(tweet._json, language, recentmost_tweet._json))
                mentions_id.append(tweet._json['id'])
        else:
            for tweet in tp.Cursor(twitter_api.search, q=f"#{user} OR @{user}", count=200, lang="en",
                                   tweet_mode='extended', include_rts=False, since_id=max(set(mentions_id))).items(200):
                mentions_data.append(add_edit_tweet_fields(tweet._json, language, recentmost_tweet._json))
                mentions_id.append(tweet._json['id'])

    filename = user + "__mentions__hashtags.json"
    with open(filename, 'w', encoding="utf-8") as f:
        json.dump(mentions_data, f, ensure_ascii=False, indent=4)


if __name__ == '__main__':
    get_tweets("NICKIMINAJ", "en")  ###### CHANGE AS PER USER'S HANDLE AND THE LANGUAGE YOU WANT TO FETCH
