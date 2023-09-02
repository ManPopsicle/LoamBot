import ShowState
import csv
import os
import re
from os import listdir
from os.path import isfile, join

# Initialize connection with local database
ShowStates = ShowState.ShowState()
def makeCsv(show):
    
    entries = [['FileName', 'FilePath', 'EpisodeName', 'Index', 'Season', 'EpisodeNumberInSeason', 'fuckyou']]

    index = 0
    defaultPath = r"D:\Shows\\" + ShowStates.convertToTitle(show)
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
            if(re.search("E...", justName) != None):
                justEpisode = re.search("E...", justName).group()
            else:
                justEpisode = re.search("E..", justName).group()
            justEpisodeNum = justEpisode.split("E")[1]
            if re.search("0.", justEpisodeNum) != None:
                justEpisodeNum = re.search("0.", justEpisodeNum).group().split("0")[1]
            print("season " + justSeasonNum)
            print(justEpisodeNum)
            entries.append([justName, fullPath, justName, index, justSeasonNum, justEpisodeNum, justEpisodeNum])
            index+=1

    filename = str(show)+".csv"
    with open(filename, 'w') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerows(entries)


makeCsv("spongebob")