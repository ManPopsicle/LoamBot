import DatabaseUtils
import csv
import os
import re
from os import listdir
from os.path import isfile, join

# Initialize connection with local database
dbUtils = DatabaseUtils.DbUtils()
def makeCsv(show):
    
    entries = [['FileName', 'FilePath', 'EpisodeName', 'Index', 'Season', 'EpisodeNumberInSeason', '_ShowId', 'fuckyou']]

    index = 0
    defaultPath = r"D:\Shows\\" + dbUtils.getShowNameFromKeyName(show)
    for path, subdirs, files in os.walk(defaultPath):
        for name in files:
            fullPath = os.path.join(path, name)
            justName = os.path.splitext(name)[0]
            
            #Season
            justSeason = re.search("S..", justName).group()
            justSeasonNum = justSeason.split("S")[1]
            if re.search("00", justSeasonNum) != None:
                justSeasonNum = "0"
            elif re.search("0.", justSeasonNum) != None:
                justSeasonNum = re.search("0.", justSeasonNum).group().split("0")[1]

            #Episode
            justEpisode = re.search("E(\d+)", justName).group()
            justEpisodeNum = justEpisode.split("E")[1]
            if re.search("00", justEpisodeNum) != None:
                justEpisodeNum = "0"
            elif re.search("0.", justEpisodeNum) != None:
                justEpisodeNum = re.search("0.", justEpisodeNum).group().split("0")[1]
            print("season " + justSeasonNum)
            print(justEpisodeNum)
            showId = dbUtils.getShowIdFromKeyName(show)
            print(showId)
            entries.append([justName.encode("utf-8"), fullPath.encode("utf-8"), justName.encode("utf-8"), index, justSeasonNum, justEpisodeNum, showId, justEpisodeNum])
            index+=1

    filename = str(show)+".csv"
    with open(filename, 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerows(entries)


# Helper function for generating a timestamp csv file if it doesn't already exist
# This file will be used to save off a show's current timestamp, season, episode
def makeTimestampCsv(keyList, defaultTimestampPath, defaultTimestampName):
    
    header = ['ShowName', 'EpisodeName', 'Timestamp']
    defaultPath = defaultTimestampPath + defaultTimestampName + ".csv"

    # If the timestamp file already exists, exit
    if(os.path.exists(defaultPath)):
        return

    with open(defaultPath, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(header)
        # Create an entry for each show in the keylist; leave values blank
        for name in keyList:
            csvwriter.writerow([name, "", ""])

