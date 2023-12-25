from pymongo import MongoClient, ReturnDocument
from bson.objectid import ObjectId

import os

class DbUtils():
    client = MongoClient("localhost", 27017)
    db = client.Loambot
    showsCollection = db.Shows
    CurrentShow = ""            # This should be a KeyName, not a ShowName value
    keyList = []
    

    # Builds list of shows for PaginationView to create a command out of
    def buildShowList(self):
        showList = []
        for show in self.showsCollection.find().sort("KeyName"):
            showEntry = [show['ShowName'], show['KeyName']]
            showList.append(showEntry)
        return showList
    
        

    # Builds list of shows for PaginationView to create a command out of
    def buildEpisodeList(self, playlistName):
        episodeList = []
        collectionName = self.showsCollection.find_one(
            {"KeyName": playlistName})['ShowsCollection'].collection
        
        queriedCollection = self.db[collectionName]
        for episode in queriedCollection.find({}):
            episodeEntry = [episode['EpisodeName'], episode['Index']]
            episodeList.append(episodeEntry)

        return episodeList


    # Updates a show manually
    # Parameters: 
    #   curEp: VLC-extracted episode name
    #   curTime: VLC-extracted timestamp of show
    def saveShowEntry(self, curEp, curTime):

        # First find the name of the collection based on the user's KeyName input
        collectionName = self.showsCollection.find_one(
            {"KeyName": self.CurrentShow})['ShowsCollection'].collection
        
        # Return the entire collection by searching for it based on its name
        show = self.showsCollection.find_one_and_update(
            {"KeyName": self.CurrentShow}, 
            {'$set': {"CurrentEpisode": curEp, "CurrentTime": curTime}})

                

    # Finds the last played episode's filename
    # Parameters:
    #   name: Playlist name (Don't use actual name)
    def getCurrentEpisode(self, playlistName):
        return self.showsCollection.find_one(
            {"KeyName": playlistName})['CurrentEpisode']
    
    
    # Finds the last played episode's previous time
    # Parameters:
    #   name: Playlist name (Don't use actual name)
    def getSeekTime(self, playlistName):

        result =  self.showsCollection.find_one(
            {"KeyName": playlistName})['CurrentTime']
        return result
    
    
    # Based on playlist name, find that show's current episode index
    # This is really just used when a new playlist is loaded and the savestate needs to be loaded
    # Parameters:
    #   episodeName: Episode name
    def getCurrentEpisodeIndex(self):
        index = 0
        episodeName = self.showsCollection.find_one(
            {"KeyName": self.CurrentShow})['CurrentEpisode']
        collectionName = self.showsCollection.find_one(
            {"KeyName": self.CurrentShow})['ShowsCollection'].collection
        if(collectionName != None):
            queriedCollection = self.db[collectionName]

            showId = queriedCollection.find_one(
                {'EpisodeName':episodeName})
            if (showId != None):
                index = queriedCollection.find_one(
                    {'EpisodeName':episodeName})['Index']
        return index


    # Gets the playlist's name using the show's name
    # Parameters:
    #   name: Show name
    def getKeyNameFromShowName(self, showName):
            
        result =  self.showsCollection.find_one(
            {"ShowName": showName})['KeyName']
        return result
    
    
    # Gets the playlist's name using episode name
    # This should really only be used on bot restart, when VLC is already up and playing something
    # This way, it can retrieve the current show dynamically on startup
    # Parameters:
    #   name: Show name (retrieved from VLC.info())
    def getKeyNameFromEpisodeName(self, episodeName):
        
        # Iterate through the entire Shows collection to search each show's episode collection
        for show in self.showsCollection.find():
            # Retrieve next show's name in the database
            collection =  show['ShowsCollection'].collection
            if collection == "":
                continue
            # Now searching in the show's individual collection
            queriedCollection = self.db[collection]
            # Locate the ShowId of the episode
            showId = queriedCollection.find_one(
                {'EpisodeName':episodeName})
            # Episode found; save off the ShowId
            if (showId != None):
                showId = queriedCollection.find_one(
                    {'EpisodeName':episodeName})['_ShowId']
            # Go back to the Show collection and get the KeyName based on the found ShowId
            result = self.showsCollection.find_one({'_id': ObjectId(showId)})
            # If found, return the KeyName
            if result:
                result = self.showsCollection.find_one({'_id': ObjectId(showId)})['KeyName']
                return result
        
        # If no results found, return None
        return None
        
    
    # Gets the show's name using the playlistName
    # Parameters:
    #   name: Playlist name
    def getShowNameFromKeyName(self, playlistName):
        
        return self.showsCollection.find_one(
            {"KeyName": playlistName})['ShowName']
    
    
    # Gets the show's name using the playlistName
    # Parameters:
    #   playlistName: Playlist name
    def getShowIdFromKeyName(self, playlistName):
        
        return self.showsCollection.find_one(
            {"KeyName": playlistName})['_id']

    
    # Gets the index of an episode based on a season and episode number
    # Parameters:
    #   playlistName: Playlist name
    #   seasonNum: Season number
    #   episodeNum: Episode number
    def getIndexFromSeasonAndEpisode(self, playlistName, seasonNum, episodeNum):
        
        # Find the correct episode collection
        collectionName = self.showsCollection.find_one(
            {"KeyName": playlistName})['ShowsCollection'].collection
        queriedCollection = self.db[collectionName]
        
        print(collectionName + " " + seasonNum + " " + episodeNum)
        episode = queriedCollection.find_one(
            {"$and": [{'Season': int(seasonNum)}, {'EpisodeNumberInSeason': int(episodeNum)}] }, {'Index': 1})
        print(episode['Index'])
        return episode['Index']



    
    # Produces a list of file paths to be fed into the VLC MediaListPlayer object
    # by querying the database to find the correct show's collection of episodes
    # Parameters:
    #   playlistName: The KeyName value of the show in question
    def buildPlaylist(self, playlistName):
        # First find the name of the collection based on the user's KeyName input
        collectionName = self.showsCollection.find_one(
            {"KeyName": playlistName})['ShowsCollection'].collection
        
        # Return the entire collection by searching for it based on its name
        queriedCollection = self.db[collectionName]

        # Get all the episodes
        episodeList = queriedCollection.find({})
        filePathList = []

        # Find the file path of every single episode and compile it into one list
        for episode in episodeList:
            filePathList.append(episode['FilePath'])
        return filePathList
