from pymongo import MongoClient

class ShowState():
    client = MongoClient("localhost", "27017")
    db = client.Loambot
    showsCollection = db.Shows


    def getAllShows(self):
        for show in self.showsCollection:
            print(show)