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

# Format file data for splitting data into db_load formatted
def formatDBdata(fileName):
    subprocess.call(["./break.pl", fileName])

# Format file name to a database type (.txt -> .idx)
# rw.idx, pt.idx, rt.idx, and sc.idx
def formatDBname(fileName):
    if (fileName == "sorted_pterms.txt"):
        return "Index/pt.idx"
    elif (fileName == "sorted_rterms.txt"):
            return "Index/rt.idx"
    elif (fileName == "reviews.txt"):
            return "Index/rw.idx"
    elif (fileName == "sorted_scores.txt"):
            return "Index/sc.idx"
    else:
        print("ERROR: Cannot format the file " + fileName)

# Takes the sorted files and creates a database using db_load
def createIndex(fileName):

    # Format the name of the database as well as the sorted data
    formatDBdata(fileName)
    dbName = formatDBname(fileName)
    fileName = "formatted_" + fileName

    # DB Type: Hash
    if fileName == "formatted_reviews.txt":
        bashCommand = "db_load -T -f Formatted/" +  fileName +  " -t hash " + dbName
        process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)

        # Find a way to handle errors in python not in terminal
        output, error = process.communicate()

    # DB Type: B+-Tree
    else:
        bashCommand = "db_load -T -f Formatted/" +  fileName +  " -t btree " + dbName
        process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)

        # Find a way to handle errors in python not in terminal
        output, error = process.communicate()

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
        bashCommand = 'sort -u RawData/' +  fileName[i] + " -o " + "Sorted/sorted_" + fileName[i]
        process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)

        # Find a way to handle errors in python not in terminal
        output, error = process.communicate()
        fileName[i] = "sorted_" + fileName[i]

    # Create the index files for all the sorted data
    for file in fileName:
        createIndex(file)
    print("\nAll the files have been sorted and indexed!")

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
        return False

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

if (__name__ == "__main__"):
    # Initialize
    init()

    # Take user input and redirect to sorting file or queries
    process = input("Option Selected: ")
    while(not option(process)):
        process = input("Option Selected: ")
        pass
