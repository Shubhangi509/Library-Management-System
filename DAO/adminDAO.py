from pymongo.mongo_client import MongoClient

class AdminDAO():
    db:any
  
    def CheckLogin(username, password):     
        return AdminDAO.db.User.find_one({"username": username, "password":password, "type":"admin"})
