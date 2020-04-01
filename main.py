#!/usr/bin/python
from bsddb3 import db
import datetime
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

# Return a date object from a user inputted date
def formatDate(date):
    Year, Month, Day = date.split("/")
    timestamp = datetime.datetime(int(Year), int(Month), int(Day), 0, 0).timestamp()
    return timestamp

# Runs a query on the hash database and prints the returned data
def printQuery(listofIDs):
    # Flag for queries - True is Full, False is brief
    global outputFlag, rw

    # Invalid query
    if listofIDs is None or not listofIDs:
        return print("\nNo products or reviews meet all the criteria!")

    for ID in listofIDs:

        # Point cursor to the provided ID in the reviews database
        curs = rw.cursor()
        result = curs.set(ID.encode("utf-8"))
        curs.close()

        # If the ID exists -> get data!
        if (result != None):
            value = result[1].decode("utf-8")
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
        return None

# Given no specified database to check, check all!
def checkAllDB(query):
    ptermList = runQuery("pterm", query)
    rtermList = runQuery("rterm", query)
    scoreList = []

    # Merge the list of ID's from all 3 databases
    return union(ptermList, rtermList, scoreList)

# Runs a basic query on the B+-Tree database's given a specific key and database
def runQuery(database, query):
    global pt, rt, sc

    db = determineDB(database)
    if (db is None):
        return # Provided db name is not valid

    curs = db.cursor()
    listofIDs = list()

    # Bool values used to control query type (Regular or Ranged)
    score = False
    greaterThan = False

    # Check for wildcard
    if (query.find("%") > 0):
        result = curs.set_range(query.encode("utf-8"))

    # Check if its a range search with score
    elif db == sc:
        condition, key = query.split()
        score = True
        greaterThan = False

        if condition == ">":
            greaterThan = True
            start = str( int(key) + 1 )
            end = curs.last()
            result = curs.set_range(start.encode("utf-8"))
        else:
            end = curs.set_range(key.encode("utf-8"))
            result = curs.first()

    # Regular search
    else:
        result = curs.set(query.encode("utf-8"))

    if (result != None): # Regular Query

        while result != None:

            # Break for regular query
            if((str(result[0].decode("utf-8")) != query) and not score):
                break

            # Break for range query
            if (score and not greaterThan): # data < key
                num = result[0].decode("utf-8").split(".")
                if result == end:
                    break

            # Break for range query
            elif score and greaterThan: # data > key
                if result == end:
                    ReviewID = str(result[1].decode("utf-8"))
                    ReviewID = ReviewID.replace('\r', '')
                    if ReviewID not in listofIDs:
                        listofIDs.append(ReviewID)
                    break

            # Only keep track of new IDs! (Not sure if we should do this)
            ReviewID = str(result[1].decode("utf-8"))
            ReviewID = ReviewID.replace('\r', '')

            if ReviewID not in listofIDs:
                listofIDs.append(ReviewID)

            result = curs.next()

    curs.close()
    return listofIDs

# Runs queries to find results that match the ranges provided (Date and Price)
def hashQuery(type, userKey, listofIDs):
    global outputFlag, rw

    # Invalid query with the B+- Trees
    if listofIDs is None or not listofIDs:
        print("hashQuery: No ID's to query")
        return

    DatePriceFlag = False # True for Date; False for Price
    condition, key = userKey.split()
    greaterThan = False

    if condition == ">":
        greaterThan = True

    if type == "date":
        DatePriceFlag = True
        timestamp = formatDate(key) # Gets timestamp

    elif type == "price":
        range = key
        DatePriceFlag = False

    finalListofIDs = []

    # Iterate through ID's and save which ones are within range
    for ID in listofIDs:

        # Point cursor to the provided ID in the reviews database
        curs = rw.cursor()
        result = curs.set(ID.encode("utf-8"))
        curs.close()

        # If the ID exists -> get data!
        if (result != None):

            value = result[1].decode("utf-8")
            value = value.split(",")

            if DatePriceFlag: # True -> Date Search
                for i in value:
                    line = str(i.replace('\r', ''))

                    # IF: len 10 digits (len of epoch time now) && all digits
                    if (line.isdigit() and len(line) <= 10 and len(line) > 4):

                        # Review data passes check -> Save ID
                        pulledData = int(str(line))
                        keyRange = int(timestamp)

                        if (greaterThan) and (pulledData > keyRange):
                            finalListofIDs.append(ID)
                            break

                        elif not greaterThan and (pulledData < keyRange):
                            finalListofIDs.append(ID)
                            break

            elif not  DatePriceFlag: # False -> Price Search
                for i in value:
                    line = i.replace('\r', '')
                    index = len(line) - 3 # Where the "." is expected

                    if (index > 0) and (line.find(".", index) != -1):
                        parse = i.split(".", 1)

                        # IF: len > 0.00 && len after period (00) equals && 3rd index from last is decimal .00
                        if (len(line) >= 4) and (len(parse[1]) == 2) and (i[len(line) - 3] == "."):

                            # Review data passes check -> Save ID
                            pulledData = float(str(line))
                            keyRange = float(range)

                            if (greaterThan) and (pulledData > keyRange):
                                finalListofIDs.append(ID)
                                break

                            elif not greaterThan and (pulledData < keyRange):
                                finalListofIDs.append(ID)
                                break

        else:
            print("ERROR: hashQuery")

    return finalListofIDs

# Intersects lists to weed out duplicates and only take overlapped ID's
def intersect(list1, list2):
    tempList = list()

    if not list1: # List 1 is empty -> Return List 2
        return list2

    elif not list2:  # List 2 is empty -> Return List 1
        return list1

    else: # Return the intersect of both lists
        return list(set(list1) & set(list2))

# Unions lists taking all ID's and removing duplicates
def union(list1, list2, list3):
    temp_list = list(set(list1) | set(list2))
    final_list = list(set(temp_list) | set(list3))
    return final_list

# Parse a query into a list
def parseQuery(query):

    list = query.split()
    queryParts = []

    for i in list:
        GreaterIndex = i.find("<")
        LesserIndex = i.find(">")

        # Database provided format
        if (i.find(":") > 0):
            first, second = i.split(":")
            queryParts.append(first)
            queryParts.append(":")
            queryParts.append(second)

        # Greater than format
        elif (GreaterIndex >= 0):
            if (GreaterIndex > 0):
                first, second = i.split("<")
                queryParts.append(first)
                queryParts.append("<")

                if second != '': # Case where {score<, 10}
                    queryParts.append(second)
            else:
                if (len(i) > 1): # Case where {score, <10}

                    first, second = i.split("<")
                    queryParts.append("<")
                    queryParts.append(second)

                else: # Case where {score, <, 10}
                    queryParts.append("<")

        # Less than format
        elif (LesserIndex >= 0):
            if (LesserIndex > 0):
                first, second = i.split(">")
                queryParts.append(first)
                queryParts.append(">")

                if second != '': # Case where {score>, 10}
                    queryParts.append(second)
            else:
                if (len(i) > 1): # Case where {score, >10}

                    first, second = i.split(">")
                    queryParts.append(">")
                    queryParts.append(second)

                else: # Case where {score, >, 10}
                    queryParts.append(">")

        # Regular value
        else:
            queryParts.append(i)

    return queryParts

# Checks the query for various input types, wild cards and conditions
def checkQuery(query):

    parsedQuery = parseQuery(query)
    specialConds = [":", ">", "<"]
    specialWords = ["date", "price"]

    i = 0

    rangeQuery = [] # Pull out and save the hash query here
    ListofIds = []  # Pull out and save the intersect of IDs here

    # Process one term at a time and group together as neccessary
    # B+- Tree queries
    while i < len(parsedQuery):

        word = parsedQuery[i]
        tempListofIDs = []

        # Word is not a special condition or reserved word
        if (word not in specialConds) and  (word not in specialWords):

            if (i == 0): # First term in query

                # Guitar
                if (len(parsedQuery) == 1):
                    tempListofIDs = checkAllDB(word)
                    i += 1

                # Ex. Guitar score < 200
                elif (parsedQuery[i+1] not in specialConds):
                    tempListofIDs = checkAllDB(word)
                    i += 1

                # Ex. pterm:guitar OR score<10
                elif (parsedQuery[i+1] in specialConds):
                    first = parsedQuery[i]
                    last = parsedQuery[i+ 2]
                    cond = parsedQuery[i+1]
                    i += 3

                    if (cond == ":"): # db:term
                        tempListofIDs = runQuery(first, last)

                    else: # Score >, < #
                        key = cond + " " + last
                        tempListofIDs = runQuery(first, key)


            else: # Not the first term

                if (i != (len(parsedQuery) - 1)): # Not the Last term

                    # Ex. something Guitar something
                    if (parsedQuery[i+1] not in specialConds):
                        tempListofIDs = checkAllDB(word)
                        i += 1

                    # something, score, <, something, OR something, db, :, term
                    else:
                        first = parsedQuery[i]
                        last = parsedQuery[i+ 2]
                        cond = parsedQuery[i+1]
                        i += 3

                        if (cond == ":"): # db:term
                            tempListofIDs = runQuery(first, last)

                        else: # Score >, < #
                            key = cond + " " + last
                            tempListofIDs = runQuery(first, key)

                else: # last term -> Ex. [price, <, 200, guitar]
                    tempListofIDs = checkAllDB(word)

        else: # Reserved words

            if (word in specialWords):
                rangeQuery.append(parsedQuery[i])
                rangeQuery.append(parsedQuery[i + 1])
                rangeQuery.append(parsedQuery[i + 2])
                i += 3

            else:
                i += 1

        # Merge the results under instection
        if not ListofIds:
            ListofIds = tempListofIDs
        else:
            ListofIds = intersect(ListofIds, tempListofIDs)

    # If no special ranges provided, print & return
    if not rangeQuery:
        printQuery(ListofIds)
        return

    FinalListofIds = []
    i = 0

    # Fetch the data associated with the ID's and check the range queries
    while i < len(rangeQuery):

        # Pull data
        tempListofIDs = []
        first = rangeQuery[i]
        last = rangeQuery[i+ 2]
        cond = rangeQuery[i+1]
        i += 3

        # Format for query and get the list of ID's
        key = cond + " " + last
        tempListofIDs = hashQuery(first, key, ListofIds)

        # Merge the results under instection
        if not FinalListofIds:
            FinalListofIds = tempListofIDs
        else:
            FinalListofIds = list(set(FinalListofIds) & set(tempListofIDs))

    printQuery(FinalListofIds)

    return

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
        # checkQuery(query.lower())
        checkQuery(query.lower())
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
