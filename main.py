#!/usr/bin/python
from bsddb3 import db
import subprocess

# Initial print of commands to guide the user through the program
def init():

    print("\nPlease select one of the following options:")
    print("A) To sort and index all files")
    print("B) To retrieve data")
    print("C) To exit\n")

# Creates reference to the databases
def initDB():
    global outputFlag, pt, rt, sc, rw

    # Flag for queries - True is Full, False is brief
    outputFlag = False;

    # Creating db objects for our indexes
    pt = db.DB() # -> title terms
    rt = db.DB() # -> review terms
    sc = db.DB() # -> scores
    rw = db.DB() # -> review ids

    # Open with the corresponding data base type
    pt.open("Index/pt.idx", None, db.DB_BTREE, db.DB_RDONLY)
    rt.open("Index/rt.idx", None, db.DB_BTREE, db.DB_RDONLY)
    sc.open("Index/sc.idx", None, db.DB_BTREE, db.DB_RDONLY)
    rw.open("Index/rw.idx", None, db.DB_HASH, db.DB_RDONLY)

# Handles the navigation of the program from user input for Part 2
def option():

    selectedProcess = input("Option Selected: ")

    # Part 1: Build indexs
    # NOTE: Expects files: reviews.txt, scores.txt, rterms.txt, pterms.txt in RawData
    if (selectedProcess.lower() == "a"):

        # Call the other .py file that sorts, formats and builds the indexs
        bashCommand = "python3 buildDB.py"
        process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
        print("\nThe files have been successfuly sorted and indexed!")
        init()
        return False

    # Part 2: Data queries
    elif (selectedProcess.lower() == "b"): # Sort all files (provided they are formatted)
        # Data queries
        return True

    elif (selectedProcess.lower() == "c"):
        print("\nExiting program...")
        exit()

    else:
        print("\nERROR: Entry " + selectedProcess + " is not a valid option, please try again\n")
        return False

# Listens for a output change or exit at any time
def customIn(prompt = ""):
    global outputFlag, pt, rt, sc, rw

    myInput = input(prompt).lower()
    if (myInput == "output=brief"):
        outputFlag = False
        print("The output format has been changed to: Brief")
        return "modeChange"

    elif (myInput == "output=full"):
        outputFlag = True
        print("The output format has been changed to: Full")
        return "modeChange"

    elif (myInput == "exit"):
        print("\nExiting program...")
        pt.close()
        rt.close()
        sc.close()
        rw.close()
        exit()

    else:
        return myInput

# Runs a query on the hash database and prints the returned data
def printQuery(listofIDs):
    # Flag for queries - True is Full, False is brief
    global outputFlag, rw

                                #### OUTPUT ####
    # Brief: review id , the product title and the review score of all matching reviews.
    # Full: output will include all review fields (All data from rw.idx on key id)
    if(listofIDs == None):
        print("No Results Found!")
        return

    else:
        # Removes the trailing \r from decoding (Database returns byte value)
        for ID in listofIDs:

            # Point cursor to the provided ID in the reviews database
            curs = rw.cursor()
            result = curs.set(ID.encode("utf-8"))
            curs.close()

            # If the ID exists -> get data!
            if (result != None):
                value =result[1].decode("utf-8")
                value = value.split(",")

                # Inconsistency in the indexs of reviews data -> Search for score(ex. 5.0)
                for i in value:
                    if (len(i) == 3) and (int(i[0]) <= 5) and (i[1] == "."):
                        score = str(i)
                        break

                if (outputFlag is False): # PRINT: BRIEF SUMMARY

                    # Grab the desired data and print
                    Brief_Summary = ("\nReview ID: " + str(result[0].decode("utf-8"))
                                    + "\nProduct Title: " + str(value[1])
                                    + "\nReview Score: " + score)
                    print(Brief_Summary)

                else: # PRINT: FULL SUMMARY

                    print("\nFull Summary: ")
                    print(value)
                    # for term in value:
                    #     print(str(term))

            else:
                print("ERROR: PrintQuery")
        print("\nTotal number of hits: " + str(len(listofIDs)))

# Given a specified database in a query, return the pointer
def determineDB(database):
    global pt, rt, sc

    if database == "pterm":
        return pt
    elif database == "rterm":
        return rt
    elif database == "score":
        return sc
    else:
        print("Not a valid database")

# Range Query - copy below function, apply in the greater than, less than from the query deconstruction below! use the set_range()

# make it take in date, price or score, then put it through an if statement to see which one to do
# score should be easy, you have a table just for that, date and range will be fun bc they are baked into the review table

# if it gives me a score of 3, cast it to 3.0 bc thats how its stored in the db
def runRangeQuery(database, query, dateLo = None, dateUp = None, priceLo = None, priceUp = None, scoreLo = None, scoreUp = None):
    global pt, rt, sc

    db = determineDB(database)
    if (db is None):
        return

    curs = db.cursor()
    result = curs.set(query.encode("utf-8"))
    listofIDs = list()

    if result != None:
        #DEBUG
        # print("\nList of all reviews found using input '" + query + "'")

        while result != None:
            if(str(result[0].decode("utf-8")) != query):
                break

            # Only keep track of new IDs! (Not sure if we should do this)
            ReviewID = str(result[1].decode("utf-8"))
            ReviewID = ReviewID.replace('\r', '')

            if ReviewID not in listofIDs:
                listofIDs.append(ReviewID)

            result = curs.next()
    curs.close()
    return listofIDs # Returns a list of the ID's that matched (Exact)

# Runs a query on the B+-Tree database 's given a specific key returning the IDs
def runQuery(database, query):
    global pt, rt, sc

    db = determineDB(database)
    if (db is None):
        return

    curs = db.cursor()
    result = curs.set(query.encode("utf-8"))
    listofIDs = list()

    if result != None:
        print("\nList of all reviews found using input '" + query + "'")

        while result != None:
            if(str(result[0].decode("utf-8")) != query):
                break

            # Only keep track of new IDs! (Not sure if we should do this)
            ReviewID = str(result[1].decode("utf-8"))
            ReviewID = ReviewID.replace('\r', '')

            if ReviewID not in listofIDs:
                listofIDs.append(ReviewID)

            result = curs.next()
    curs.close()
    return listofIDs # Returns a list of the ID's that matched (Exact)

# Runs the original query to retrieve Review ID
def testQuery(query):
    global pt, rt, sc

        #### NOTE ####         [key        , data              ]
    # rw.idx -> (review ids)   [review id  , full review record]
    # rt.idx -> (review terms) [terms      , review id         ]
    # pt.idx -> (title terms)  [terms      , review id         ]
    # sc.idx -> (scores)       [score      , review id         ]

    # Keys: rt, pt & sc can have duplicates, rw cannot
    # Data: only the ID for rt, pt & sc, you have to iterate through rw data

                ########### Query 1) pterm:guitar ###########
    curs = pt.cursor()
    query = "guitar"
    result = curs.set(query.encode("utf-8"))

    if result != None:
        print("\nList of all reviews found using input '" + query + "'")
        listofIDs = list()

        while result != None:
            if(str(result[0].decode("utf-8")) != query):
                break

            # Only keep track of new IDs! (Not sure if we should do this)
            ReviewID = str(result[1].decode("utf-8"))
            if ReviewID not in listofIDs:
                listofIDs.append(ReviewID)

            result = curs.next()

    curs.close()

    # If list is not empty, get the summaries for the ID's
    if listofIDs:
        printQuery(listofIDs)

                ########### Query 2) rterm:great ###########
    # curs = rt.cursor()
    # query = "great"
    # result = curs.set(query.encode("utf-8"))
    #
    # if result != None:
    #     print("\nList of all reviews found using input '" + query + "'")
    #     listofIDs = list()
    #
    #     while result != None:
    #         if(str(result[0].decode("utf-8")) != query):
    #             break
    #
    #         # Only keep track of new IDs! (Replicating ID's consume efficiency)
    #         ReviewID = str(result[1].decode("utf-8"))
    #         if ReviewID not in listofIDs:
    #             listofIDs.append(ReviewID)
    #
    #         result = curs.next()
    #
    # curs.close()
    #
    # # If list is not empty, get the summaries for the ID's
    # if listofIDs:
    #     printQuery(listofIDs)

    return True

# Intersects lists to weed out duplicates and only take overlapped ID's
def intersect(list1, list2, list3):
    tempList = list()

    if list1 and list2: # # Non empty intersect of 2 lists
        tempList =  list(set(list1) & set(list2))
        print("stage 1: ")
        print(tempList)
    elif not list1: # List 1 is empty
        tempList = list2
        print("stage 2: ")
        print(tempList)
    elif not list2: # List 2 is empty
        tempList = list1
        print("stage 3: ")
        print(tempList)
    elif not list1 and not list2: # Both are empty -> return third list
        print("stage 4: ")
        print(tempList)
        return list3

    if not list3: # List 3 is empty
        print("stage 5: ")
        print(tempList)
        return tempList

    else: # Non empty intersect of 2 lists
        print("stage 6: ")
        print(tempList)
        return list(set(tempList) & set(list3))

# Unions lists taking all ID's and removing duplicates
def union(list1, list2, list3):
    final_list = []

    if(list1 != None and list2 != None and list3 != None):
        temp_list = list(set(list1) | set(list2))
        final_list = list(set(temp_list) | set(list3))

    elif(list1 != None and list2 != None and list3 == None):
        final_list = list(set(list1) | set(list2))

    elif(list1 != None and list2 == None and list3 != None):
        final_list = list(set(list1) | set(list3))

    elif(list1 == None and list2 != None and list3 != None):
        final_list = list(set(list3) | set(list2))

    elif(list1 != None and list2 == None and list3 == None):
        final_list = list1

    elif(list1 == None and list2 != None and list3 == None):
        final_list = list2

    elif(list1 == None and list2 == None and list3 != None):
        final_list = list3

    return final_list

# Checks the query for various input types, wild cards and conditions
def checkQuery(query):

    ##### Some notes from building the queries in PT 2 as well as possible breakdown ######
    # All matches are case-insensitive, query has been passed in casted to "lowercase"
    # There is one or more spaces between the conditions.
        # - Parse by spaces, and iterate through to see if it contains anything below?

    # Dates are formatted as yyyy/mm/dd in queries but they are stored as timestamps in the data file
        # Must be converted to timestamp before a search can be performed
        # I'll implement this from my code from project 1

    # You can assume every query has at least one condition on an indexed column,
    # meaning the conditions on price and date can only be used if a condition on review/product terms or review scores is also present.

    dateLo = None
    dateUp = None
    priceLo = None
    priceUp = None
    scoreLo = None
    scoreUp = None
    ptermQueryList = []
    rtermQueryList = []
    scoreQueryList = []

    queryParts = []
    initQuerySplit = query.split()

    for i in initQuerySplit:
        if(i.find(":") > 0):
            first, second = i.split(":")
            queryParts.append(first)
            queryParts.append(":")
            queryParts.append(second)
        elif(i.find("<") > 0):
            first, second = i.split("<")
            queryParts.append(first)
            queryParts.append("<")
            queryParts.append(second)
        elif(i.find(">") > 0):
            first, second = i.split(">")
            queryParts.append(first)
            queryParts.append(">")
            queryParts.append(second)
        else:
            queryParts.append(i)


    i=0
    term = ""
    condition = ""
    amount = ""

    while i < len(queryParts):
        delimiterFound = False

        # Range Conditions
        # Note: to ensure we don't attempt to query out of range, we add "i+1 < len(queryParts)"
        if(i+1 < len(queryParts)):
            if(queryParts[i+1] == "<" or queryParts[i+1] == ">"):
                condition = queryParts[i]
                amount = queryParts[i+2]

                # Set the operator
                lessThanOperator = False
                if(queryParts[i+1] == "<"):
                    lessThanOperator = True

                if(condition == "date"):
                    if(lessThanOperator):
                        dateUp = amount
                    else:
                        dateLo = amount

                elif(condition == "price"):
                    if(lessThanOperator):
                        priceUp = amount
                    else:
                        priceLo = amount

                elif(condition == "score"):
                    if(lessThanOperator):
                        scoreUp = amount
                    else:
                        scoreLo = amount

                else:
                    print("ERROR: Unknown condition: " + condition)
                    break

                # Print the statement, just for debug vvv
                # if(lessThanOperator):
                #     print("SPECIAL: " + condition + " < " + amount)
                # else:
                #     print("SPECIAL: " + condition + " > " + amount)
                # Print the statement, just for debug ^^^

                i+=2
                delimiterFound = True

            # Search only specified tables for the term
            elif(queryParts[i+1] == ":"):
                table = queryParts[i]
                term = queryParts[i+2]

                #DEBUG
                # print("Run a search on " + table + " using the term " + term)

                # ListofIDs = runQuery(table, term)
                # printQuery(ListofIDs)


                # Add the term to the specified table to query
                if(table == "pterm"):
                    ptermQueryList.append(term)
                elif(table == "rterm"):
                    rtermQueryList.append(term)
                elif(table == "score"):
                    scoreQueryList.append(term)
                else:
                    print("ERROR: Unknown table: " + term)
                    break

                i+=2
                delimiterFound = True

        # Search all tables for the term
        if(not delimiterFound):
            term = queryParts[i]

            #DEBUG
            # print("Run a search on ALL tables using the term " + term)

            # Get a list of all review ID's from each table with the key
            # ptermList = runQuery("pterm", term)
            # rtermList = runQuery("rterm", term)
            # scoreList = runQuery("scores", term)

            # We want to search all tables for the term
            ptermQueryList.append(term)
            rtermQueryList.append(term)
            scoreQueryList.append(term)

            # The Code below is moved down
            # ListofIDs = union(ptermList, rtermList, scoreList)
            #
            # # Prints the summary of the common ID's (union) b/t the db's
            # printQuery(ListofIDs)

        i+=1

    # After applying the conditions, and after collecting all of the search terms, then run the query
    outputList = []

    for newTerm in ptermQueryList:
        outputList = outputList + runRangeQuery("pterm", newTerm, dateLo, dateUp, priceLo, priceUp, scoreLo, scoreUp)
    for newTerm in rtermQueryList:
        outputList = outputList + runRangeQuery("rterm", newTerm, dateLo, dateUp, priceLo, priceUp, scoreLo, scoreUp)
    for newTerm in scoreQueryList:
        outputList = outputList + runRangeQuery("score", newTerm, dateLo, dateUp, priceLo, priceUp, scoreLo, scoreUp)

    # Remove duplicates
    outputList = list(dict.fromkeys(outputList))

    # Prints the summary of the common ID's (union) b/t the db's
    printQuery(outputList)





    # if query contains ":"
        # Parse and first half is the db, second half is the key

    # if query contains ":" and " "
        # Parse and first half is the db, remaining terms are key and cond.

    # if query contains "%" (Wildcard only on end of query)
        # Query for partial match

    # if query contains >, < or = and # of " " = 2
        # Ranged query (Price, Date, Score)

    # if query contains >, < or = and # of " " > 2
        # Ranged query + conditions (Price, Date, Score)

# Handles queries and navigation of user input for Part 2
def queryListener():
    print("\nPlease enter a query or change mode, for more detail enter '?'")
    query = customIn("Entry: ")

    if (query == "modeChange"): # Mode has been changed b/t brief or full
        return True

    elif (query == "?"): # Provides more detail on options for Part 2
        print("\nTo change mode: enter 'output=brief' or 'output=full' for a brief or more detailed output")
        print("To run a query: simply enter your query!")
        print("To exit the program, enter 'exit' at any time")
        return True

    else: # Check & run the query!
        checkQuery(query.lower()) # Return checkQuery and make it return T or F depending on state?
        return True


if (__name__ == "__main__"):
    # Initialize
    global outputFlag
    init()

    # Take user input and redirect to sorting file or search queries
    while(not option()):
        pass

    initDB()
    # Process user queries
    while(queryListener()):
        pass
