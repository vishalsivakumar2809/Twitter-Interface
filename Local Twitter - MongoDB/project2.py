"""
Project Name : Project 2
File Purpose : Main Python File
CCID & Name  : yaathesh & Yaatheshini Ashok Kumar
CCID & Name  : vsivakum & Vishal Sivakumar
"""

# Importing Modules
import sys
from pymongo import MongoClient
from bson import ObjectId
import time
import os
import pprint
import datetime

# Globalising the database and collection
global db, tweets

# Checking if Number of command line arguements is 2
n = len(sys.argv)   
if n != 2:
    print("- ERROR: INCORRECT NUMBER OF ARGUMENTS -")
    sys.exit(0)

# creating a MongoDb client connecting to host and given port
client = MongoClient('localhost', int(sys.argv[1]))
db = client['291db']        # Accessing database
tweets = db["tweets"]       # Accessing collection

# (1) -> Searching for Tweets 
def search_tweets():
    keywords = tweets_keyword_validation()      # Calling to validate inputted keywords
    oids = []
    count = 0

    # Query to check that for eg. for 'Fa Mers' tweets with both 'father','Boomers' etc turn up
    query = {"$and": [{"content": {"$regex": "\\b" + keyword + "\\b", "$options" :'i'}} for keyword in keywords]}
    results = list(db.tweets.find(query))       # Typecasting the results of find into a list
    if len(results) > 0:        # If there is atleast 1 or more results in the list
        for tweet in results:
            print("-" * 100,"\n")
            data = tweet.get("_id",{})
            if str(data) not in oids:
                oids.append(str(data))
                count += 1
                print("Tweet Number: ",count,"\n")
                print("Tweet ID: ",tweet.get("id"),"\n")
                print("Date:     ",tweet.get("date"),"\n")
                print("Content:  ",tweet.get("content"),"\n")
                user = tweet.get("user",{})
                print("Username: ",user.get("username"),"\n")
        
        print("-" * 100,"\n")
        while 1:
            print("S/s to Select a Tweet")
            choice = input("Press Enter to Continue to the Main Menu: ")
            if choice in ['S','s']:
                select_tweet(oids)
            else:
                break
        main()

    else:           # If there are no results in the list
        print("\nNo Tweets Match your Keywords.")
        print("-" * 100,"\n")
        print("S/s to Search Tweets for Other Keyword(s)")
        choice = input("Press Enter to Continue to the Main Menu: ")
        if choice in ['S','s']:
            search_tweets()         # Recursive Calling
        else:
            main()

# Validating if atleast a character has been entered to search and if more 
# words have been added, to split them by a space to search individually
def tweets_keyword_validation():
    keywords = input("\nEnter Keyword(s) to search for Tweets: ")
    if keywords.strip() != '':
        keywords = keywords.strip()
        keywords = keywords.strip(',')
        if ',' in keywords:
            keywords = keywords.split(",")      # to split keywords entered with commas
        else: 
            keywords = keywords.split(" ")      # to split keywords entered with spaces
        return keywords
    else:
        print("Invalid Keyword(s). Try Again. \n")
        tweets_keyword_validation() 

# Selecting a tweet based on choice and displaying all the details
def select_tweet(oids):
    print("-" * 100,"\n")
    oid = int(input("Enter Tweet Number to Search: "))
    print("-" * 100)
    if oid-1 in range(len(oids)):       # Checking if the tweet to be searched is in the oids list
        tid = oids[oid-1]
        tid_object = ObjectId(tid)
        query = {"_id": tid_object}
        result = db.tweets.find(query)
        for tweet in result:
            pprint.pprint(tweet)
        print("-" * 100)
    else:       # Can't choose a tweet that is not among the displayed records
        print("Tweet Number not among the Displayed. Try Again.")
        select_tweet(oids)

# (2) -> Searching for Users
def search_users():
    keyword = r'\b' + user_keyword_validation().lower() + r'\b'
    query = {
                "$or": [
                    {"user.displayname": {"$regex": keyword, "$options": 'i'}}, 
                    {"user.location": {"$regex": keyword, "$options": 'i'}}
                ]
            }
    # Pulling only the necessary parameters
    required_values = {"user.username": 1, "user.displayname": 1, "user.location": 1, "user.id": 1}
    output = db.tweets.find(query, required_values)
    temp_user_id = []
    found = False

    # Printing Neatly
    for temp_line in output:
        if temp_line['user']['id'] not in temp_user_id:
            found = True
            temp_user_id.append(temp_line['user']['id'])
            print("-" * 100,"\n")
            print("Sr. No:         ", str(len(temp_user_id)),"\n")
            print("Display Name:   ", temp_line['user']['displayname'] or 'None',"\n")
            print("User Name:      ", temp_line['user']['username'] or 'None',"\n")
            print("Location:       ", temp_line['user']['location'] or 'None',"\n")
    
    if found:       # If there is 1 or more results 
        condition_to_user(temp_user_id)
    
    if not found:       # If no results turn up for the same
        print("\n- NOTHING FOUND WITH THE INPUTTED KEYWORD -\n")

        user_input = input("Do you wish to SEARCH USERS [s/S] or go to MAIN MENU [enter any key]: ")
        if user_input in ['s','S']:
            search_users()
        else:
            print("Okay. Taking you back to the menu.")
            time.sleep(5)       # Waiting for 5 seconds before calling main and clearing terminal
            main()

# Providing a choice to select a particular user
def condition_to_user(list_of_id):
    print("-" * 100)
    while 1:
        user_input = input("Do you wish to select a user from the above? Yes: [Y/y], No: [N/n]: ")
        if user_input in ['y','Y']:
            print("-" * 100)
            select_user(list_of_id)         # Selecting a particular user
        elif user_input in ['n','N']:
            print("Okay. Taking you back to the menu.")
            time.sleep(5)       # Waiting for 5 seconds before calling main and clearing terminal
            main()
            break
        else:
            print("- ERROR: Invalid Input. Please try again. -")

# Ability to select a user based on choice
def select_user(temp_user_id):
    condition = True
    while condition:
        index = int(input("Enter a valid Sr. No from the displayed users: "))
        if index > len(temp_user_id) or index <= 0:
            print("- ERROR: INCORRECT VALUE ENTERED -\n")
        else:
            condition = False

    # retrieving results and neatly printing
    user_id = temp_user_id[index - 1]
    details_user = db.tweets.find_one({'user.id': user_id})
    print("-" * 100)
    pprint.pprint(details_user['user'])
    print("-" * 100)
    
# Checks whether a user inputted only one keyword for search_users
def user_keyword_validation():
    while 1:
        keyword = input("Enter Keyword to Search Users: ")
        temp = keyword.split(" ")
        if len(temp) != 1 or keyword == '':
            print("- Please Enter Valid Keyword. -\n")
        else:
            break
    return keyword

# (3) -> Listing Top Tweets
def list_top_tweets():
    user_value = int(input("Enter Number of Tweets to Display: "))
    print("-" * 100)
    
    print("\n1 : List Tweet with Highest Retweets")
    print("2 : List Tweet with Highest Number of Likes")
    print("3 : List Tweet with Highest Number of Quotes\n")
    print("-" * 100)
    
    choice = int(input("Enter your choice: "))      # User Input deciding how many records to display
    
    # Updating Value of x to chosen choice
    if choice == 1:
        x = "retweetCount"      

    elif choice == 2:
        x = "likeCount"

    elif choice == 3:
        x = "quoteCount"

    else:
        print("- ERROR: Invalid Choice of Listing. - ")
        print("-" * 100 + "\n")
        list_top_tweets()
        return 

    oids = top_tweets(x,user_value)

    while 1:
        print("S/s to Select a Tweet")
        choice = input("Press Enter to Continue to the Main Menu: ")
        if choice in ['S','s']:
            select_tweet(oids)
        else:
            break
    main()

# Accepts arguements - the x value, the number of tweets requested to be displayed
def top_tweets(x,user_value):
    query = {x: 1, "id": 1, "date": 1, "content": 1, "user.username": 1}
    results = db.tweets.find({},query).sort({x:-1})
    count = 0
    oids = []
    for tweet in results:
        print("-" * 100)
        count += 1
        if count <= user_value:
            data = tweet.get("_id",{})
            oids.append(str(data))      # Adding the oid into the oids list to later view only those
            print("\nTweet Number:  ",count,"\n")
            print("Tweet ID:      ",tweet.get("id"),"\n")
            print("Date:          ",tweet.get("date"),"\n")
            print("Content:       ",tweet.get("content"),"\n")
            user = tweet.get("user",{})
            print("Username:      ",user.get("username"),"\n")

            if x == "retweetCount":
                print("Retweet Count: ",tweet.get(x),"\n")
            elif x == "likeCount":
                print("Like Count:    ",tweet.get(x),"\n")
            elif x == "quoteCount":
                print("Quote Count:   ",tweet.get(x),"\n")
        else:
            break  
    return oids         # Returning oids of displayed records as a list

# (4) -> Listing Top Users
def list_top_users():
    
    # user id as dictionary key and user details as a list of values
    followers_dictionary = {}
    user_input = validate_user_input()
    
    # Retrieving only the required_values
    required_values = {"user.id": 1, "user.followersCount": 1, "user.displayname": 1, "user.username": 1}
    users_followers_count = db.tweets.find({}, required_values)

    for follower_count in users_followers_count:
        user_id = follower_count['user']['id']
        temp1 = follower_count['user']['username']
        temp2 = follower_count['user']['displayname']
        max_followers = follower_count['user']['followersCount']
        
        if user_id not in followers_dictionary or max_followers > followers_dictionary[user_id][2]:
            followers_dictionary[user_id] = [temp1, temp2, max_followers]
    
    # Sorting the dictionary
    followers_dictionary = dict(sorted(followers_dictionary.items(), key=lambda x:x[1][2], reverse=True))
    followers_user_id = list(followers_dictionary.keys())
    followers_details = list(followers_dictionary.values())

    for temp in range(user_input):
        print("-" * 100,"\n")
        print("Sr. No:         ", str(temp + 1),"\n")
        print("Display Name:   ", followers_details[temp][0] or 'None',"\n")
        print("User Name:      ", followers_details[temp][1] or 'None',"\n")
        print("Followers Count:", followers_details[temp][2] or 'None',"\n")
    
    # Providing options for user to choose
    condition_to_user(followers_user_id[0:user_input])

# Validating that the entered user to search for is only from the displayed records
def validate_user_input():
    while 1:
        user_input = int(input("Enter how many users you wish to see: "))
        if user_input <= 0:
            print("- ERROR: INCORRECT INPUT. TRY AGAIN -\n")
        else:
            break
    return user_input

# (5) -> Composing Tweets
def write_tweet():
    content = input("Enter the content you wish to add to the tweet: ")

    # Getting the current date and time to match the necessary date and time format
    date_time_str = ((datetime.datetime.now(datetime.timezone.utc)).replace(microsecond = 0)).isoformat()
    user_name = "291user"

    # Setting values for MongoDB
    tweet_import =  {
                    "url": None,
                    "date": date_time_str,
                    "content": content,
                    "renderedContent": None,
                    "id": None,
                    "user": {
                        "username": user_name,
                        "displayname": None,
                        "id": None,
                        "description": None,
                        "rawDescription": None,
                        "descriptionUrls": None,
                        "verified": False,
                        "created": None,
                        "followersCount": 0,
                        "friendsCount": 0,
                        "statusesCount": 0,
                        "favouritesCount": 0,
                        "listedCount": 0,
                        "mediaCount": 0,
                        "location": None,
                        "protected": None,
                        "linkUrl": None,
                        "linkTcourl": None,
                        "profileImageUrl": None,
                        "profileBannerUrl": None,
                        "url": None
                    },
                    "outlinks": None,
                    "tcooutlinks": None,
                    "replyCount": 0,
                    "retweetCount": 0,
                    "likeCount": 0,
                    "quoteCount": 0,
                    "conversationId": None,
                    "lang": None,
                    "source": None,
                    "sourceUrl": None,
                    "sourceLabel": None,
                    "media": [
                        {
                        "previewUrl": None,
                        "fullUrl": None,
                        "type": None
                        }
                    ],
                    "retweetedTweet": None,
                    "quotedTweet": None,
                    "mentionedUsers": None
                    }
    tweets.insert_one(tweet_import)         # Inserting a record into the MongoDB
    print("-" * 100)
    print("You Posted a Tweet!")
    print("-" * 100)
    print("Okay. Taking you back to the menu.")
    time.sleep(5)
    main()
    
# main menu
def main():
    condition = True
    while condition:
        os.system('clear')
        print("\n" + "-" * 100 + "\n" + "Welcome to Twitter!\n" + "-" * 100) 
        print("\n1 : Search Tweets")
        print("2 : Search Users")
        print("3 : List Top Tweets")
        print("4 : List Top Users")
        print("5 : Compose Tweet")
        print("6 : Exit\n")
        print("-" * 100)
        option = int(input("Choose your option: "))

        if option in [1,2,3,4,5,6]:
            condition = False
        else:
            print("- ERROR: INCORRECT INPUT. TRY AGAIN -")
            time.sleep(5)
        
    print('-'*100)
        
    if option == 1:
        search_tweets()
                
    elif option == 2:
        search_users()

    elif option == 3:
        list_top_tweets()
                
    elif option == 4:
        list_top_users()

    elif option == 5:
        write_tweet()

    elif option == 6:
        print("Have a good day! Exited Successfully.")
        print("-" * 100)
        
        
if __name__ == '__main__':
    main()