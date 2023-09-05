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
        for show in self.showsCollection.find():
            showEntry = [show['ShowName'], show['KeyName']]
            showList.append(showEntry)
        return showList


    # Updates a show manually
    # Parameters: 
    #   curEp: VLC-extracted episode name
    #   curTime: VLC-extracted timestamp of show
    def saveShowEntry(self, curEp, curTime):

        # First find the name of the collection based on the user's KeyName input
        collectionName = self.showsCollection.find_one(
            {"KeyName": self.CurrentShow})['ShowCollection'].collection
        
        # Return the entire collection by searching for it based on its name
        queriedCollection = self.db[collectionName]
        curEpisodeId = queriedCollection.find_one({'FileName' : curEp})

        show = self.showsCollection.find_one_and_update(
            {"KeyName": self.CurrentShow}, 
            {'$set': {"CurrentEpisode": curEpisodeId, "CurrentTime": curTime}})
                

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
    #   name: Playlist name
    def getCurrentEpisodeIndex(self, playlistName):
        index = 0
        result = self.showsCollection.find_one(
            {"KeyName": playlistName})
        if(result != None):
            result = self.showsCollection.find_one(
                {"KeyName": playlistName})['CurrentEpisode']
            index = result['Index']
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
        
        # Iterate through the entire Shows collection
        for show in self.showsCollection.find():
            # Search through the individual Show_Data collection for that episode name
            collection =  show['ShowCollection'].collection
            if collection == "":
                continue
            # Now searching in the individual collection
            queriedCollection = self.db[collection]
            # Locate the ShowId of the episode
            showId = queriedCollection.find_one(
                {'EpisodeName':episodeName})
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
    #   name: Playlist name
    def getShowIdFromKeyName(self, playlistName):
        
        return self.showsCollection.find_one(
            {"KeyName": playlistName})['_id']

    
    # Produces a list of file paths to be fed into the VLC MediaListPlayer object
    # by querying the database to find the correct show's collection of episodes
    # Parameters:
    #   playlistName: The KeyName value of the show in question
    def buildPlaylist(self, playlistName):
        # First find the name of the collection based on the user's KeyName input
        collectionName = self.showsCollection.find_one(
            {"KeyName": playlistName})['ShowCollection'].collection
        
        # Return the entire collection by searching for it based on its name
        queriedCollection = self.db[collectionName]

        # Get all the episodes
        episodeList = queriedCollection.find({})
        filePathList = []

        # Find the file path of every single episode and compile it into one list
        for episode in episodeList:
            filePathList.append(episode['FilePath'])
        return filePathList
        
# {
#     'data': 
#     {
#         '_STATISTICS_WRITING_APP': "mkvmerge v48.0.0 ('Fortress Around Your Heart') 64-bit", 
#         'NUMBER_OF_FRAMES': 35766, 'BPS': 2597630, 
#         'filename': 'The Boondocks (2005) - S01E01 - The Garden Party (1080p HMAX WEB-DL x265 YOGI).mkv', 
#         '_STATISTICS_TAGS': 'BPS DURATION NUMBER_OF_FRAMES NUMBER_OF_BYTES', 
#         'NUMBER_OF_BYTES': 387498873, 
#         'DURATION': '00:19:53.392000000', 
#         'title': 'The Boondocks (2005) - S01E01', 
#         '_STATISTICS_WRITING_DATE_UTC': '2020-07-01 23:01:48'}, 
#     0: {
#         'Chroma location': 'Left', 
#         'Codec': 'MPEG-H Part2/HEVC (H.265) (hevc)', 
#         'Frame rate': 29.970628, 
#         'Decoded format': '', 
#         'Buffer dimensions': '1920x1080', 
#         'Orientation': 'Top left', 
#         'Type': 'Video', 
#         'Video resolution': '1920x1080'}, 
#     1: {
#         'Codec': 'A52 Audio (aka AC3) (a52 )', 
#         'Channels': 'Stereo', 
#         'Bits per sample': 32, 
#         'Sample rate': '48000 Hz', 
#         'Language': 'English', 
#         'Type': 'Audio'}, 
#     2: {
#         'Type': 'Subtitle', 
#         'Codec': 'Text subtitles with various tags (subt)', 
#         'Language': 'English', 'Description': 'English'}, 
#     3: {
#         'Type': 'Subtitle', 
#         'Codec': 'Text subtitles with various tags (subt)', 
#         'Language': 'English', 
#         'Description': 'English [SDH]'}
# }