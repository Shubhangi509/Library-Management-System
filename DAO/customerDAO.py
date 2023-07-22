from pymongo.mongo_client import MongoClient
from bson import ObjectId
import datetime

class CustomerDAO():
    db:any
        
    def CheckLogin(username, password, type):       
        return CustomerDAO.db.User.find_one({"username": username, "password": password, "type":type})
    
    def GetAllCustomer():
        return CustomerDAO.db.User.find({"type":"Customer"})
    
    def GetCustomerById(_id):
        return CustomerDAO.db.User.find_one({"_id":ObjectId(_id)})
    
    def InsertCustomer(book):
        return CustomerDAO.db.User.insert_one(book)
    
    def EditCustomer(_id,book):
        return CustomerDAO.db.User.find_one_and_update( {"_id": ObjectId(_id)},{"$set": book},return_document=True)
    
    def DeleteCustomer(_id):
        return CustomerDAO.db.User.find_one_and_delete({"_id":ObjectId(_id)})
