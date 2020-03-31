#!/usr/bin/python
from bsddb3 import db
import subprocess

# # Format file data for splitting data into db_load formatted
# def formatDBdata(fileName):
#     subprocess.call(["./filebreak.pl", fileName])

# Format file name to a database type (.txt -> .idx)
def formatDBname(fileName):
    if (fileName == "pterms.txt"):
        return "Index/pt.idx"
    elif (fileName == "rterms.txt"):
            return "Index/rt.idx"
    elif (fileName == "reviews.txt"):
            return "Index/rw.idx"
    elif (fileName == "scores.txt"):
            return "Index/sc.idx"
    else:
        print("ERROR: Cannot format the file " + fileName)

# Takes the sorted files and creates a database using db_load
def createIndex(fileName):

    # Format the name of the database as well as the sorted data
    dbName = formatDBname(fileName)

    # DB Type: Hash
    if fileName == "reviews.txt":
        subprocess.call(["./filebreak.pl", fileName])
        fileName = "formatted_" + fileName
        bashCommand = "db_load -T -f Formatted/" +  fileName +  " -t hash " + dbName
        process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)

        # Find a way to handle errors in python not in terminal
        output, error = process.communicate()

        T4 = subprocess.Popen(["db_dump", "-p", "-f", "Dump/review.txt", "Index/rw.idx"])

        # Try the method below but duplicate=0 (Still produce the tripples? )

    # DB Type: B+-Tree
    else:
        # bashCommand = "db_load -T -f Formatted/" +  fileName +  " -t btree " + dbName
        # process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
        # # Find a way to handle errors in python not in terminal
        # output, error = process.communicate()
        file = fileName.split(".")
        Path = "RawData/" + fileName
        DumpPath = "Dump/" + fileName

        T1 = subprocess.Popen(['cat', Path], stdout=subprocess.PIPE, universal_newlines=True)
        T2 = subprocess.Popen(["sort", "-u"], stdin=T1.stdout, stdout=subprocess.PIPE)
        T3 = subprocess.Popen(["./break.pl"], stdin=T2.stdout, stdout=subprocess.PIPE)
        T4 = subprocess.Popen(["db_load", "-c", "duplicates=1", "-T", "-t", "btree", dbName], stdin=T3.stdout, stdout=subprocess.PIPE)
        T4.wait()
        T5 = subprocess.Popen(["db_dump", "-p", "-f", DumpPath, dbName])



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
    #sortAllFiles()
    fileName = ["scores.txt", "pterms.txt", "rterms.txt", "reviews.txt"]
    for file in fileName:
        createIndex(file)
    print("\nAll the files have been sorted and indexed!")
