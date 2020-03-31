#!/usr/bin/python
from bsddb3 import db
import subprocess

# Initial print of commands to guide the user through the program
def init():
    global outputFlag
    print("\nPlease select one of the following options:")
    print("A) To sort and index all files")
    print("B) To retrieve data")
    print("C) To exit\n")

    # Flag for queries - True is Full, False is brief
    outputFlag = False;

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
    global outputFlag

    myInput = input(prompt)
    if (myInput == "output=brief"):
        outputFlag = False
        print("The output format has been changed to: Brief")
        return "modeChange"

    elif (myInput == "output=full"):
        print(outputFlag)
        print("The output format has been changed to: Full")
        return "modeChange"

    elif (myInput == "exit"):
        print("\nExiting program...")
        exit()

    else:
        return myInput


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


    print("\nDeconstructed Query:")
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
                    # do date search ############
                    pass
                elif(condition == "price"):
                    pass
                    # do price search ############
                elif(condition == "score"):
                    pass
                    # do score search ############
                else:
                    print("ERROR: Unknown query condition.")
                    break

                # Print the statement
                if(lessThanOperator):
                    print("SPECIAL: " + condition + " < " + amount)
                else:
                    print("SPECIAL: " + condition + " > " + amount)

                i+=2
                delimiterFound = True

            elif(queryParts[i+1] == ":"):
                table = queryParts[i]
                term = queryParts[i+2]

                # Search only specified tables for the term ############
                print("Table: " + table + " - Term: " + term)

                i+=2
                delimiterFound = True

        if(not delimiterFound):
            # Search all tables for the term ############
            print(queryParts[i])

        i+=1

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

    return True # Change this, it was giving bugs with no return

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

    # Eventually change this, but for now just loop through each time
    return True

if (__name__ == "__main__"):
    # Initialize
    global outputFlag
    init()

    # Take user input and redirect to sorting file or search queries
    while(not option()):
        pass

    # Process user queries
    while(queryListener()):
        pass
