# This module provides the api twython object, which is used to access the api

# import time, to enable the sleep function
import time
# Import twython
from twython import Twython
from twython import Twython
# import the api keys
import apikeys
# import threading, to schedule the reset
from threading import Timer
# import datetime
from datetime import datetime
# import setup to get the screen name
import setup
import random
import follow
import content


# time of ast request is used to be able to reset the requests,
# if more than 16 minutes have elapsed between the requests
# get the utc time to not be bothered by summer time
time_of_last_request = datetime.utcnow()

user_list = None


# The api variable is the way to access the api
def authorize():
    # if more than 16 minutes have elapsed since last request, the requests can be reset
    check_if_requests_can_be_reset()
    # Increment number of requests made
    global requests_since_last_sleep
    requests_since_last_sleep += 1
    # authorize
    return Twython(apikeys.CONSUMER_KEY, apikeys.CONSUMER_SECRET, apikeys.ACCESS_TOKEN, apikeys.ACCESS_TOKEN_SECRET)

# this method sends a tweet, by first checking with me
def send_tweet(tweet, in_reply_to_status_id=0):

    # send tweet
    if check_if_requests_are_maximum(14):
        # if requests are maximum, then return directly
        # this is to not build up a queue in massinvandring_streamer
        return
    # maybe send it in reply to another tweet
    if in_reply_to_status_id == 0:
        # standalone tweet
        authorize().update_status(status=tweet)
    else:
        # tweet is a reply
        authorize().update_status(status=tweet, in_reply_to_status_id=in_reply_to_status_id)
    print("sent tweet: " + tweet)



def send_rant(tweets, in_reply_to_status_id=0):

    global user_list

    print "in send_rant"
    # send tweets with an interval of 30 secoonds

    # if requests are above maximum minus number of tweets, then return directly
    # either the entire rant will be sent, or no rant at all
    if check_if_requests_are_maximum(6-len(tweets)):
        # return false, so the caller will know that the rant wasn't sent this time
        print "max requests"
        return False


    time.sleep((1+ random.random())* 30)
    # check if https://twitter.com/AChristLife has a new
    # tweet and RT it
    string = content.timeline_content(authorize())
    if string is not None:
        print 'filler is ' + string
        authorize().update_status(status=string)
    # check for new replies
    # follow a user
    time.sleep((1+ random.random())* 30)
    print "user_list " + str(user_list)
    try:
        if user_list is None:
            user_list = follow.get_users(authorize())
            print "got user list"

        next_user = user_list.next()
        print "going to follow " + next_user
        follow.do_follow(authorize(), next_user)
    except Exception, e:
        print "Exception!"
        print e
        time.sleep(30)
    # wait for 30-50 minutes to be more life-like
    time.sleep(30 * 60 + (random.random()* 20 * 60))

    last_status_id = in_reply_to_status_id
    for tweet in tweets:
        if last_status_id == 0:
            # standalone tweet
            authorize().update_status(status=tweet)
        else:
            # tweet is a reply
            authorize().update_status(status=tweet, in_reply_to_status_id=last_status_id)
        print("sent tweet: " + tweet)
        # sleep for 30 seconds
        time.sleep(20)
        # get the status ad of the newly sent tweet
        last_status_id = authorize().get_user_timeline(screen_name=setup.screen_name, count=1, trim_user=True, exclude_replies=False)[0]["id"]

    # return true, since the rant was successfully sent
    #time.sleep(60 * 60 * 4) # 4 hours
    #reset_requests()
    #content.timeline_content(authorize())
    #time.sleep(60 * 60 * 4) # 4 hours
    #reset_requests()
    #content.timeline_content(authorize())
    return True

# not sleeping by default
is_sleeping = False
# Store number of requests, so that they won't exceed the rate limit
requests_since_last_sleep = 0
# This method is called every time a request is to be made
# If the requests variable is over limit, the it returns true
# it also sets the bool is_sleeping
# finally, it schedules the bool to be set to false and the requests to be reset after 16 minutess
# if the requests variable isn't over limit, then do nothing
def check_if_requests_are_maximum(limit):
    global requests_since_last_sleep
    global is_sleeping
    print("Requests since last sleep: " + str(requests_since_last_sleep))
    if requests_since_last_sleep >= limit:
        # set the is_sleeping to true
        if not is_sleeping:
            is_sleeping = True
            # delay for 16 minutes
            #Timer(16*60, reset_requests).start()
            time.sleep((16 * 60) + (600 * random.random()))
            reset_requests()
        #return True
    return False

def set_sleep(sleeping=True):
    is_sleeping = sleeping


# if more than 16 minutes hace elapsed since the last request, reset the requests
def check_if_requests_can_be_reset():
    global time_of_last_request, requests_since_last_sleep
    # use utctime to not have to care about summer time
    now_time = datetime.utcnow()
    # compare the now_time and last time
    # if more than 16 minutes have elapsed, reset the requests
    if (now_time - time_of_last_request).total_seconds() > 16*60:
        # reset requests
        requests_since_last_sleep = 0
    # update the last time
    time_of_last_request = now_time


# this function resets the requests
def reset_requests():
    requests_since_last_sleep = 0
    is_sleeping = False
