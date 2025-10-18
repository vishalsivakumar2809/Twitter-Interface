import sqlite3
import string
import re
from getpass import getpass
import datetime
import sys
import os 
import time

connection = None
cursor = None
MAIN_USER = None

# Sets values of globalised connection and cursor
def connect(path):
    global connection, cursor
    connection = sqlite3.connect(path)
    cursor = connection.cursor()
    cursor.execute(' PRAGMA foreign_keys=ON; ')
    connection.commit()
    return

# Gives user choice to login, sign-up or exit
def home_page():
    os.system('clear')
    global connection, cursor, MAIN_USER
    print("-" * 100 + "\n" + "Welcome to TWITTER!\n" + "-" * 100)

    while 1:
        print("Select one of these options:\n\nOPTION 1: Login\nOPTION 2: Create new account\nOPTION 3: Exit\n")
        option = int(input("Choose your option: "))
        if option not in [1,2,3]:
            print("\n- Invalid Input. Try Again. - \n")
            continue
        break
    
    if option == 1:
        login_site()    

    if option == 2:
        sign_up_user()

    if option == 3:
        print("Have a good day! Exited Successfully.")
        print("-" * 100)
        sys.exit(0)

# Interface to login the user after validations
def login_site():
    global connection, cursor, MAIN_USER
    print("\n" + "-" * 100 + "\n" + "LOGIN PAGE\n" + "-" * 100) 
    while 1: 
        # Accepting login details
        user_id = input("\nEnter User ID: ")
        password = getpass("Enter Password: ")

        # Searching if they already have a twitter account
        # Protect from SQL Injection Attacks
        query = "SELECT DISTINCT * FROM users u WHERE u.usr = ? AND u.pwd = ?"
        cursor.execute(query,(user_id,password))
        result = cursor.fetchone()

        # Printing the record
        if result != None:
            view_login(user_id)
            break
        else:
            print("Incorrect Username/Password. Try Again.")
            continue

# Login page 
def view_login(user_id):
    global connection, cursor, MAIN_USER
    MAIN_USER = int(user_id)

    time.sleep(5)
    os.system('clear')

    print("\n" + "-" * 100 + "\n" + "Logged In Successfully!\n" + "-" * 100) 

    # Getting the latest tweets
    query = """WITH combined AS (
                SELECT tweets.tid AS tweet_id, 
                    tweets.writer AS writer, 
                    tweets.tdate AS date, 'tweet' AS type
                FROM tweets
                JOIN follows ON tweets.writer = follows.flwee
                WHERE follows.flwer = ?

                UNION ALL

                SELECT retweets.tid AS tweet_id,
                    retweets.usr AS writer,
                    retweets.rdate AS date, 'retweet' AS type
                FROM retweets
                JOIN follows ON retweets.usr = follows.flwee
                WHERE follows.flwer = ?

            ), max_dates AS (
                SELECT tweet_id, writer, MAX(date) AS max_date
                FROM combined
                GROUP BY tweet_id, writer)

            SELECT DISTINCT c.tweet_id, c.writer, c.date, c.type
            FROM combined c
            JOIN max_dates m ON c.tweet_id = m.tweet_id AND c.writer = m.writer AND c.date = m.max_date
            ORDER BY date DESC;
            """
    
    cursor.execute(query, (user_id, user_id))
    rows = cursor.fetchall()

    if len(rows) == 0:
        print("You don't follow any users. Follow users to see tweets.") 

    temp_list = print_tweets(rows,5,0)

    if len(temp_list[0]) != 0:
        while 1:
            if temp_list[2] > 5:
                option = input("\nEnter F/f to follow a user\nB/b for previous page\nEnter S/s to select a tweet from the displayed tweets\nM/m for main menu: ")
            else:
                option = input("\nEnter F/f to follow a user\nEnter S/s to select a tweet from the displayed tweets\nM/m for main menu: ")
                
            if option in ['S','s']:
                user_inputted_select(temp_list[0])
                time.sleep(5)
                os.system('clear')
                print_tweets(rows,5,temp_list[2] - 5)

            elif option in ['B', 'b'] and temp_list[2] > 5:
                os.system('clear')
                print_tweets(rows,5,temp_list[2] - 10)

            elif option in ['M','m']:
                print("Okay. Taking you back to the menu.")
                menu()
                break

            elif option in ['F','f']:
                user_inputted_follow(temp_list[1])
                time.sleep(5)
                os.system('clear')
                print_tweets(rows,5,temp_list[2] - 5)
                
            else:
                print("- Invalid Input. Try Again. - ")
                continue      
    else:
        print("No Tweets Selected.")
        print("Okay. Taking you back to the menu.")
        menu()

# Printing given number of tweets at a time 
def print_tweets(rows,modulus,count):
    temp = False
    option = '' 
    temp_list = []
    temp1_list = []
    format_string = "| TWEET ID | USER ID |    DATE    |     TYPE     |"

    print("-" * 50)
    print(format_string)
    print("-" * 50)
    
    if count < 0:
        count = 0
    
    while (count % modulus) != 0:
        count += 1
    
    while count != len(rows):
        if temp:
            temp = False
            print("-" * 50)
            print(format_string)
            print("-" * 50)

        if rows[count][0] not in temp_list:
            temp_list.append(rows[count][0])
        
        if rows[count][1] not in temp1_list:
            temp1_list.append(rows[count][1])
        
        print("|%s|%s| %s |%s|" % (str(rows[count][0]).center(10), str(rows[count][1]).center(9), rows[count][2], rows[count][3].center(14)))
        print("-" * 50)

        count += 1
        if count % modulus == 0 and count != len(rows):
            temp = True

            print("-" * 100)
            if count >= (modulus * 2):
                option = input("Enter Y/y to continue\nB/b for previous page\nF/f to follow user\nS/s to select a tweet from the displayed tweets\nM/m for main menu: ")
            else:
                option = input("Enter Y/y to continue\nF/f to follow user\nS/s to select a tweet from the displayed tweets\nM/m for main menu: ")

            if option in ['Y','y']:
                temp_list = []
                temp1_list = []
                os.system('clear')
                print("-" * 100)
                print("          Next Page:           ")

            elif option in ['B','b'] and count >= (modulus * 2):
                temp_list = []
                temp1_list = []
                count -= modulus * 2
                os.system('clear')
                print("-" * 100)
                print("         Previous Page:          ")

            elif option in ['F','f']:
                user_inputted_follow(temp1_list)
                count -= modulus
                time.sleep(5)
                os.system('clear')

            elif option in ['S','s']:
                user_inputted_select(temp_list)
                count -= modulus
                time.sleep(5)
                os.system('clear')

            elif option in ['M','m']:
                print("Okay. Taking you back to the menu.")
                menu()
                break

            else:
                print("- Invalid Input. Exited. - \n")
                count -= modulus

    if option not in ['S','s','M','m','F','f','B','b']:
        print("\nEnd of Feed.")
    print("-" * 100)
    return [temp_list, temp1_list, count]

# Accepting user input for S/s
def user_inputted_select(temp_list):
    condition = True
    while condition:
        print("-" * 100)
        choice = int(input("Enter Tweet ID Number: "))
        if choice in temp_list:
            condition = False
            select_tweet(choice)
            user_input = input("  1   - To reply to this tweet\n  2   - To retweet this tweet\nEnter - Do Neither: ")
            if user_input == '1':
                write_tweet(choice)
            elif user_input == '2':
                retweet(choice)
        else:
            print("\n- Invalid Tweet Selected. Try Again. - ")

# Accepting user input for F/f
def user_inputted_follow(temp1_list):
    condition = True
    while condition:
        print("-" * 100)
        choice = int(input("Enter the user you wish to follow: "))
        if choice in temp1_list:
            condition = False
            follow_user(choice)
        else:
            print("- Invalid Input. Please try again. - \n")
    
# Selects tweet from the tweets displayed
def select_tweet(choice):
    global connection, cursor
    while 1:
        query = """SELECT DISTINCT t.tid, t.text,
                (SELECT COUNT(*) FROM retweets WHERE tid = t.tid) as retweet_count,
                (SELECT COUNT(*) FROM tweets WHERE replyto = t.tid) as reply_count
                FROM tweets t
                WHERE t.tid = ?;
                """
        cursor.execute(query,(choice,))
        row = cursor.fetchone()
        
        if row:
            print("-" * 119)
            format_string = "| TWEET ID |                                   TEXT                                   | RETWEET COUNT | REPLIES COUNT |"
            print(format_string)
            print("-" * 119)

            term = row[1]
            if len(term) > 75:
                term = term[0:74]

            print("|%s|%s|%s|%s|" % (str(row[0]).center(10), term.center(74), str(row[2]).center(15), str(row[3]).center(15)))
            print("-" * 119)
        else:
            print("ERROR: INCORRECT TWEET INPUTTED.")
    
        break      

# Main Menu showing all the major options
def menu():
    time.sleep(5)
    os.system('clear')
    while 1: 
        # Display Choices
        print("\n" + "-" * 100 + "\n" + "Welcome to Main Menu!\n" + "-" * 100) 
        print("\n1 : Search Tweets")
        print("2 : Search Users")
        print("3 : Write Tweet")
        print("4 : Show Followers")
        print("5 : Logout\n")
        print("-" * 100)
        option = int(input("Choose your option: "))
        if option in [1,2,3,4,5]:
            break
        else:
            print("- Invalid Input. Try Again. - ")

    if option == 1:
        search_keywords()
            
    elif option == 2:
        search_users()

    elif option == 3:
        write_tweet(None)
        print("Okay. Taking you back to the menu.")
        menu()
            
    elif option == 4:
        show_followers()

    elif option == 5:
        choice = input("Enter Y/y to confirm logout: ")
        if choice in ['Y','y']:
            home_page()

# Searches for keywords in the tweets table
def search_keywords():
    global connection, cursor, MAIN_USER
    keywords = input("Enter Keywords to search for with appropriate spaces: ")
    main_dictionary = {}

    for word in keywords.split(" "):
        if len(word) != 0 and word[0] == '#':
            term = word[1:].lower()
            query1 = """
                     SELECT DISTINCT t1.tid, t1.tdate FROM tweets t1
                     LEFT JOIN mentions m1 ON t1.tid = m1.tid
                     WHERE lower(m1.term) = ?
                     ORDER BY t1.tdate DESC
                     ;"""
            cursor.execute(query1,(term,))
            rows1 = cursor.fetchall()
            for row in rows1:
                if row[0] not in main_dictionary:
                    main_dictionary[row[0]] = row[1]
            
        elif len(word) != 0:
            term = word.lower()
            query2 = """
                    SELECT DISTINCT tid, tdate FROM tweets
                    WHERE lower(text) LIKE '%' || ? || '%'
                    ORDER BY tdate DESC;
                    """
            cursor.execute(query2,(term,))
            rows2 = cursor.fetchall()
            for row in rows2:
                if row[0] not in main_dictionary:
                    main_dictionary[row[0]] = row[1]
    
    main_dictionary = dict(sorted(main_dictionary.items(), key=lambda x:x[1], reverse=True))
    search_tweets(main_dictionary.keys())

# This function returns a particular tweet based on tid value
def search_tweets(keys):
    global connection, cursor
    rows = []

    if len(keys) != 0 :
        for key in keys:
            query = """
                    SELECT t.tid, t.writer, t.tdate,
                            CASE 
                                WHEN replyto IS NOT NULL THEN 'reply'
                                ELSE 'tweet'
                    END AS type
                    FROM tweets t
                    WHERE t.tid = ?;
                    """
            cursor.execute(query,(key,))
            row = cursor.fetchone()
            
            if row:
                rows.append(row)
                
        temp_list = print_tweets(rows,5,0)
        if len(temp_list[0]) != 0:
            while 1:
                if temp_list[2] > 5:
                    option = input("\nEnter F/f to follow a user\nB/b for previous page\nEnter S/s to select a tweet from the displayed tweets\nM/m for main menu: ")
                else:
                    option = input("\nEnter F/f to follow a user\nEnter S/s to select a tweet from the displayed tweets\nM/m for main menu: ")
                
                if option in ['S','s']:
                    user_inputted_select(temp_list[0])
                    time.sleep(5)
                    os.system('clear')
                    print_tweets(rows,5,temp_list[2] - 5)

                elif option in ['B', 'b'] and temp_list[2] > 5:
                    os.system('clear')
                    print_tweets(rows,5,temp_list[2] - 10)

                elif option in ['M','m']:
                    print("Okay. Taking you back to the menu.")
                    menu()
                    break

                elif option in ['F','f']:
                    user_inputted_follow(temp_list[1])
                    time.sleep(5)
                    os.system('clear')
                    print_tweets(rows,5,temp_list[2] - 5)
                else:
                    print("- Invalid Input. Try Again. - ")
                    continue      
        else:
            print("No Tweets Selected.")
            print("Okay. Taking you back to the menu.")
            menu()
        
    else: 
        print("No Tweets Found.")
        print("Okay. Taking you back to the menu.")
        menu()

# print users that have the keyword in their name and then city in ascending order of name and city length respectively
def search_users():
    global connection, cursor
    keyword = user_keyword_validation().lower()
    query = """SELECT DISTINCT usr, name, city FROM (
            SELECT * FROM (
            SELECT usr, name, city, 
            LENGTH(name) AS length_name, 1 AS sort_order
            FROM users
            WHERE LOWER(name) LIKE '%' || ? || '%'
        
            UNION 
        
            SELECT DISTINCT usr, name, city, 
            LENGTH(city) AS length_city, 2 AS sort_order
            FROM users
            WHERE LOWER(city) LIKE '%' || ? || '%')

            ORDER BY sort_order ASC, length_name ASC);"""
    
    cursor.execute(query,(keyword,keyword))
    rows = cursor.fetchall()

    if len(rows) == 0:
        print("No User Match Your Keywords.")
    temp_list = print_five_users(rows, 0)

    if len(temp_list[0]) != 0:
        while 1:
            if temp_list[1] > 5:
                option = input("Enter S/s to select a user from the displayed users\nB/b for previous page\nM/m for main menu: ")
            else:
                option = input("Enter S/s to select a user from the displayed users\nM/m for main menu: ")
            
            if option in ['S','s']:
                search_select(temp_list[0])
                time.sleep(5)
                os.system('clear')
                print_five_users(rows, temp_list[1] - 5)
            
            elif option in ['B', 'b'] and temp_list[1] > 5:
                os.system('clear')
                print_five_users(rows,temp_list[1] - 10)

            elif option in ['M','m']:
                print("Okay. Taking you back to the menu.")
                menu()
                break

            else:
                print("- Invalid Input. Try Again. - ")
                continue          
    else:
        print("No Users Selected.")
        print("Okay. Taking you back to the menu.")
        menu()

# modulus is taken as five and count is used to backtrack
def print_five_users(rows, count):
    # Printing 5 users at a time 
    temp = False
    option = '' 
    temp_list = []
    format_string = "| USER ID |               NAME               |               CITY               |"

    print("-" * 81)
    print(format_string)
    print("-" * 81)

    if count < 0:
        count = 0
    
    while (count % 5) != 0:
        count += 1
    
    while count != len(rows):
        if temp:
            temp = False
            print("-" * 81)
            print(format_string)
            print("-" * 81)
        
        # truncates our name and city inputs to length 34
        if len(rows[count][1]) > 34:
            rows[count][1] = rows[count][1][0:34]
        
        if len(rows[count][2]) > 34:
            rows[count][2] = rows[count][2][0:34]

        temp_list.append(rows[count][0])
        print("|%s|%s|%s|" % (str(rows[count][0]).center(9), rows[count][1].center(34), rows[count][2].center(34)))
        print("-" * 81)

        count += 1
        if count % 5 == 0 and count != len(rows):
            temp = True

            print("-" * 100)
            if count >= 10:
                option = input("Enter Y/y to continue\nB/b for previous page\nS/s to select a user from the displayed users\nM/m for main menu: ")
            else:
                option = input("Enter Y/y to continue\nS/s to select a user from the displayed users\nM/m for main menu: ")

            if option in ['Y','y']:
                print("-" * 100)
                print("                             Next Page:                                  ")
                temp_list = []
                os.system('clear')

            elif option in ['B','b'] and count >= 10:
                print("-" * 100)
                print("                             Previous Page:                                  ")
                temp_list = []
                count -= 10
                os.system('clear')

            elif option in ['S','s']:
                search_select(temp_list)
                count -= 5
                time.sleep(5)
                os.system('clear')

            elif option in ['M','m']:
                print("Okay. Taking you back to the menu.")
                menu()
                break

            else:
                print("- Invalid Input. Exited. - ")
                count -= 5

    if option not in ['S','s','M','m','B','b']:
        print("\n\nEnd of Search.")

    print("-" * 100)
    return [temp_list,count]

# Checks if inputted usr (choice) is among the displayed users (temp_list).
def search_select(temp_list):
    condition = True
    while condition:
        choice = int(input("Enter User ID to Search: "))
        if choice in temp_list:
            condition = False
            select_user(choice)
        else:
            print("- Invalid ID Selected. Try Again. - \n")

# Prints all the details of the user and their three latest tweets/retweets
def select_user(choice):
    global connection, cursor, MAIN_USER
    os.system('clear')
    query1 = """
            SELECT DISTINCT u1.usr,
            ((SELECT COUNT(*) FROM tweets WHERE writer = u1.usr) +
            (SELECT COUNT(*) FROM retweets WHERE usr = u1.usr)) as total_count,
            (SELECT COUNT(*) FROM follows WHERE flwer = u1.usr) as following_count,
            (SELECT COUNT(*) FROM follows WHERE flwee = u1.usr) as followers_count
            FROM users u1
            WHERE u1.usr = ?; 
            """

    query2 = """SELECT tid, usr, MAX(date) AS date, type
            FROM    
                (SELECT t1.tid AS tid, u1.usr, t1.tdate AS date, 'tweet' AS type
                FROM users u1
                JOIN tweets t1 ON u1.usr = t1.writer

                UNION ALL

                SELECT DISTINCT t2.tid AS tid, u1.usr, r1.rdate AS date, 'retweet' AS type
                FROM users u1
                JOIN retweets r1 ON u1.usr = r1.usr
                JOIN tweets t2 ON r1.tid = t2.tid) AS subquery
            WHERE usr = ?
            GROUP BY tid, usr
            ORDER BY date DESC;
            """
    cursor.execute(query1,(choice,))
    rows1 = cursor.fetchall()
    format_print_user_details(rows1)

    cursor.execute(query2, (choice,))
    rows = cursor.fetchall()
    if len(rows) == 0:
        print("No Tweets to Show.")
        follow_user(choice)
    
    else:
        temp_list = print_tweets(rows,3,0)
        if len(temp_list[0]) != 0:
            while 1:
                if temp_list[2] > 3:
                    option = input("\nEnter F/f to follow a user\nB/b for previous page\nEnter S/s to select a tweet from the displayed tweets\nM/m for main menu: ")
                else:
                    option = input("\nEnter F/f to follow a user\nEnter S/s to select a tweet from the displayed tweets\nM/m for main menu: ")
                
                if option in ['S','s']:
                    user_inputted_select(temp_list[0])
                    time.sleep(5)
                    os.system('clear')
                    format_print_user_details(rows1)
                    print_tweets(rows,3,temp_list[2] - 3)

                elif option in ['B', 'b'] and temp_list[2] > 3:
                    os.system('clear')
                    format_print_user_details(rows1)
                    print_tweets(rows,3,temp_list[2] - 6)

                elif option in ['M','m']:
                    print("Okay. Taking you back to the menu.")
                    menu()
                    break

                elif option in ['F','f']:
                    user_inputted_follow(temp_list[1])
                    time.sleep(5)
                    os.system('clear')
                    format_print_user_details(rows1)
                    print_tweets(rows,5,temp_list[2] - 3)
                    
                else:
                    print("- Invalid Input. Try Again. - ")
                    continue
        else:
            print("No Tweets Selected.")
            print("Okay. Taking you back to the menu.")
            menu()      

# Inserting a record into follows table
def follow_user(choice):
    global connection, cursor, MAIN_USER
    while 1:
        user_input = input("\nDo you wish to follow this user? Yes [Y/y] or No [N/n]: ")
        if user_input in ['Y','y']:
            if check_follow_possible(choice):
                data = (MAIN_USER, choice, datetime.date.today())
                query = '''
                        INSERT INTO follows (flwer, flwee, start_date) VALUES
                        (?,?,?);
                        '''
                cursor.execute(query, data)
                connection.commit()
                print("-" * 100 + "\n" + "SUCCESSFULLY FOLLOWED!\n" + "-" * 100)
            break
        
        elif user_input in ['N', 'n']:
            break
      
        else:
            print("Invalid Input. Try Again.")
    
# Checks if the logged in user follows himself or already follows the chosen user.
def check_follow_possible(choice):
    global connection, cursor, MAIN_USER
    if choice == MAIN_USER:
        print("Cannot follow yourself!")
        return False

    query = '''
            SELECT DISTINCT flwee FROM follows
            WHERE flwer = ?
            '''
    
    cursor.execute(query,(MAIN_USER,))
    rows = cursor.fetchall()
    for i in range(len(rows)):
        if choice == rows[i][0]:
            print("User is already followed by you.")
            return False
    return True

# Formatting select_user print outputs
def format_print_user_details(rows1):
    print("-" * 62)
    format_string = "| USER ID | TOTAL TWEETS | FOLLOWING COUNT | FOLLOWERS COUNT |"
    print(format_string)
    print("-" * 62)
    print("|%s|%s|%s|%s|" % (str(rows1[0][0]).center(9), str(rows1[0][1]).center(14), str(rows1[0][2]).center(17), str(rows1[0][3]).center(17)))
    print("-" * 62)

# Checks whether a user inputted only one keyword for search_users
def user_keyword_validation():
    while 1:
        keyword = input("Enter Keyword to Search Users: ")
        temp = keyword.split(" ")
        if len(temp) != 1:
            print("- Please Enter Valid Keyword. -")
        else:
            return keyword

# writing a tweet and inserting the record into tweets table
def write_tweet(reply_to):
    global connection, cursor, MAIN_USER
    text = input("Write Your Tweet: ")

    # add the tweet to the tweets table
    cursor.execute("SELECT max(tid) FROM tweets;")
    temp = cursor.fetchone() 
    tid = 1

    # tests if fetchone returns none
    if temp:
        tid += temp[0]

    writer = MAIN_USER
    current_date = datetime.date.today()
    query1 = """INSERT INTO tweets (tid, writer, tdate, text, replyto) 
            VALUES (?, ?, ?, ?, ?);"""
    cursor.execute(query1,(tid,writer,current_date,text,reply_to))
    connection.commit()
    print("You Posted a Tweet!\n")

    text_words = text.split(" ")
    for j in text_words:
        if len(j) != 0 and j[0] == '#':
            term = j[1:]
            # check if the word is in the hashtags table and add if not
            if not check_hashtag(term.lower()):
                query2 = """INSERT INTO hashtags (term) VALUES (?);"""
                cursor.execute(query2,(term,))
                connection.commit()
            query3 = """INSERT INTO mentions (tid, term) VALUES (?, ?);"""
            cursor.execute(query3,(tid,term))
            connection.commit()

# retweeting a tweet
def retweet(choice):
    global connection, cursor, MAIN_USER
    row = retweeted_already(choice)

    # checks if row returned None 
    if row == False:
        query = """INSERT INTO retweets (usr, tid, rdate) VALUES (?, ?, ?);"""
        cursor.execute(query,(MAIN_USER,choice,datetime.date.today()))
        connection.commit()
        print("-" * 100 + "\n" + "RETWEETED!\n" + "-" * 100) 
    else: 
        print("Already retweeted previously. Cannot retweet same tweet again.")

# checks if user already retweeted this particular tweet    
def retweeted_already(choice):
    global connection, cursor, MAIN_USER
    query = """SELECT DISTINCT * FROM retweets WHERE usr = ? AND tid = ?;"""
    cursor.execute(query,(MAIN_USER,choice))
    row = cursor.fetchone()
    if row is not None:
        return True
    return False

# Checks if term without the ‘#’ exists in the hashtags table
def check_hashtag(term):
    global connection, cursor, MAIN_USER
    query = '''SELECT DISTINCT * from hashtags
            WHERE lower(term) = ?;'''
    cursor.execute(query,(term,))
    row = cursor.fetchone()
    if row:
        return True
    return False

# Prints all followers of the logged in user from follows table
def show_followers():
    global connection, cursor, MAIN_USER 
    query = '''
            SELECT DISTINCT f1.flwer, u1.name FROM follows f1
            JOIN users u1 ON f1.flwer = u1.usr
            WHERE f1.flwee = ?;
            '''
    cursor.execute(query, (MAIN_USER,))
    rows = cursor.fetchall()
    temp_list = []

    if len(rows) != 0:
        print("-" * 50)
        format_string = "| FOLLOWER ID |               NAME               |"
        print(format_string)
        print("-" * 50)

        for row in rows:
            term = row[1]
            if len(term) > 34:
                term = term[0:34]
            print("|%s|%s|" % (str(row[0]).center(13), term.center(34)))
            print("-" * 50)
            temp_list.append(row[0])

    else:
        print("No followers to show.")
        print("Okay. Taking you back to the menu.")
        menu()
    
    while 1:
        user_input = input("\nDo you wish to select a user from these followers? Yes: [Y/y], No: [N/n]: ")
        if user_input in ['y','Y']:
            search_select(temp_list)
            break
        elif user_input in ['n','N']:
            print("Okay. Taking you back to the menu.")
            menu()
            break
        else:
            print("- Invalid Input. Please try again. -")
        
# signs up the user into the database, and logs them in.
def sign_up_user():
    global connection, cursor
    print("-" * 100 + "\n" + "SIGN UP PAGE\n" + "-" * 100) 
    
    username = generate_username()
    email = generate_email()
    city = generate_city()
    time_zone = round(float(input("Enter Timezone: ")), 1)
    password = generate_password()

    cursor.execute("SELECT max(usr) FROM users;")
    temp = cursor.fetchone() 

    user_id = 1

    # tests if fetchone returns none
    if temp:
        user_id += temp[0]
    
    print("-" * 100) 
    print("USER GENERATED VALUE IS:", user_id)
    print("-" * 100)

    data = (user_id, password, username, email, city, time_zone)
    insert_user =   '''
                    INSERT INTO users (usr, pwd, name, email, city, timezone) VALUES
                    (?,?,?,?,?,?);
                    '''
    cursor.execute(insert_user, data)
    connection.commit()
    view_login(user_id)
    return 

# generates username from user
def generate_username():
    while 1:
        username = input("Enter Username: ")
        if check_username_or_city(username):
            return username
        print("- Invalid Username. Try Again. - \n")

# generates email from user
def generate_email():
    while 1:
        email = input("Enter Email: ")
        if check_email(email):
            return email
        print("- Invalid Email. Try Again. - \n")

# generates city from user
def generate_city():
    while 1:
        city = input("Enter City: ")
        if check_username_or_city(city):
            return city
        print("- Invalid City. Try Again. - \n")

# generates hidden password from user
def generate_password():
    while 1:
        password = getpass("Enter Password (minimum 8 characters): ")
        if len(password) >= 8 and check_password(password):
            return password
        print("- Invalid Password. Try Again. - \n")

# checks if user inputted name/city is valid 
def check_username_or_city(name):
    for char1 in name:
        if char1 not in string.ascii_letters + string.whitespace:
            return False
    return True

# checks email validity: cited from https://www.geeksforgeeks.org/check-if-email-address-valid-or-not-in-python/
def check_email(email):
    format = r'\b[a-za-z0-9._%+-]+@[a-za-z0-9.-]+\.[a-z|a-z]{2,7}\b'
    if not re.match(format, email):
        return False
    return True

# checks if user inputted password is valid 
def check_password(password):
    for char1 in password:
        if char1 not in string.ascii_letters + string.digits + string.punctuation:
            return False
    return True

def main():
    # Accepting database name via user input, and connecting to it
    database_name = input("Enter valid database name [DON'T ENTER './']: ")
    database_name = './' + database_name
    connect(database_name)

    # Calling Home Page
    home_page()

if __name__ == '__main__':
    main()