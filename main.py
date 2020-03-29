#!/usr/bin/python
from bsddb3 import db
import subprocess

# Initial print of commands to guide the user through the program
def init():
    print("\nPlease select one of the following options:")
    print("\nA) To sort and index a single file")
    print("B) To sort and index all files")
    print("C) To retrieve data")
    print("D) To exit\n")

# Format file name to a database type (.txt -> .db)
def formatFileName(fileName):
    newName = fileName.split(".")
    return newName[0] + ".db"

def createIndex(fileName):

    DB_File = formatFileName(fileName) # removes .txt -> "fileName.db"
    database = db.DB()
    database.set_flags(db.DB_DUP)

    # DB Type: Hash
    if fileName == "reviews.txt":
        print("create Hash")

    # DB Type: B+-Tree
    else:
        print("create b+")
# Sorts an individual file provided its file name and it is in the directory
def sortFile():
    fileName = input("\nFile name you would like sorted and indexed: ")

    # Sort all files except reviews (pterms, rterms and scores)
    if (fileName != reviews.txt):
        bashCommand = "sort -u " +  fileName + " -o " + "sorted_" + fileName
        process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)

        # Find a way to handle errors in python not in terminal
        output, error = process.communicate()
        print("The file " + fileName + " was sorted and saved as sorted_" + fileName)
        fileName = "sorted_" + fileName

    # Create index
    createIndex(fileName)
    print("The file " + file + " was indexed accordingly")

# Sorts all the files expected for the group 2 project (pterms, rterms and scores)
def sortAllFiles():
    fileName = ["scores.txt", "pterms.txt", "rterms.txt", "reviews.txt"]

    # Sort all files except reviews (pterms, rterms and scores)
    for i in range(0, 3):
        # The sort command sent to terminal (Linux)
        bashCommand = "sort -u " +  fileName[i] + " -o " + "sorted_" + fileName[i]
        process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)

        # Find a way to handle errors in python not in terminal
        output, error = process.communicate()
        print("The file " + fileName[i] + " was sorted and saved as sorted_" + fileName[i])
        # fileName[i] = "sorted_" + fileName[i]

    for file in fileName:
        createIndex(fileName)
        print("The file " + file + " was indexed accordingly")

# Handles the navigation of the program from user input
def option(selectedProcess):
    if (selectedProcess.lower() == "a"): # Sort a single file
        sortFile()
        init()
        return False

    # Expects files: reviews.txt, scores.txt, rterms.txt, pterms.txt
    elif (selectedProcess.lower() == "b"): # Sort all files (provided they are formatted)
        sortAllFiles()
        init()
        return True

    # Part 2: Data queries
    elif (selectedProcess.lower() == "c"):
        # Data queries
        return True

    elif (selectedProcess.lower() == "d"):
        print("Exiting program...")
        exit()

    else:
        print("\nERROR: Entry " + selectedProcess + " is not a valid option, please try again\n")
        return False


# DB_File = "fruit.db"
# database = db.DB() # handle for Berkeley DB database
#
# # Do we want to allow duplicates? (This cmd allows dups.)
# database.set_flags(db.DB_DUP)
#
# # The arguments correspond to (fileName, database name within the file for multiple
# # databases, database type, flag to create database)
# database.open(DB_File ,None, db.DB_HASH, db.DB_CREATE)
# # database.open(DB_File ,None, db.DB_BTREE, db.DB_CREATE)
#
# curs = database.cursor()

# # Hash index on reviews.txt with review id as keys and the full review record as data
# DB_File = "reviews.db"
# database = db.DB()
# database.set_flags(db.DB_DUP)
# database.open(DB_File ,None, db.DB_HASH, db.DB_CREATE)
#
# # B+-tree index on pterms.txt with terms as keys and review ids as data
# DB_File = "pterms.db"
# database = db.DB()
# database.set_flags(db.DB_DUP)
# database.open(DB_File ,None, db.DB_BTREE, db.DB_CREATE)
#
# #  B+-tree index on rterms.txt with terms as keys and review ids as data
# DB_File = "rterms.db"
# database = db.DB()
# database.set_flags(db.DB_DUP)
# database.open(DB_File ,None, db.DB_BTREE, db.DB_CREATE)
#
# # B+-tree index on scores.txt with scores as keys and review ids as data
# DB_File = "scores.db"
# database = db.DB()
# database.set_flags(db.DB_DUP)
# database.open(DB_File ,None, db.DB_BTREE, db.DB_CREATE)


if (__name__ == "__main__"):
    # Initialize and login
    global connection, cursor, currUser
    init()

    # Take user input and redirect to sorting file or queries
    process = input("Option Selected: ")
    while(not option(process)):
        process = input("Option Selected: ")
        pass
