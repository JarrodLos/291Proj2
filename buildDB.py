#!/usr/bin/python
from bsddb3 import db
import subprocess

# Format file data for splitting data into db_load formatted
def formatDBdata(fileName):
    subprocess.call(["./break.pl", fileName])

# Format file name to a database type (.txt -> .idx)
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

if (__name__ == "__main__"):
    sortAllFiles()
    print("\nAll the files have been sorted and indexed!")
