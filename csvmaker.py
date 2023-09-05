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
            if re.search("0.", justEpisodeNum) != None:
                justEpisodeNum = re.search("0.", justEpisodeNum).group().split("0")[1]
            print("season " + justSeasonNum)
            print(justEpisodeNum)
            showId = dbUtils.getShowIdFromKeyName(show)
            print(showId)
            entries.append([justName, fullPath, justName, index, justSeasonNum, justEpisodeNum, showId, justEpisodeNum])
            index+=1

    filename = str(show)+".csv"
    with open(filename, 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerows(entries)


makeCsv("boondocks")