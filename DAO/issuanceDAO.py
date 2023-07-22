from pymongo.mongo_client import MongoClient
from bson import ObjectId
from datetime import datetime, timedelta


class IssuanceDAO():
    db:any
    
    def GetAllIssues():
        issued_books_list = list(IssuanceDAO.db.Issuance.find().sort("issueDate", -1))
        for document in issued_books_list:
            document["formattedIssueDate"] = document["issueDate"].strftime("%d-%m-%Y")
            document["formattedFineDate"] = document["fineDate"].strftime("%d-%m-%Y")
            
            if document['returnDate'] != None:
                document["formattedReturnDate"] = document['returnDate'].strftime("%d-%m-%Y")

            date_diff = datetime.now() - document["fineDate"]
            days_diff = date_diff.days                
            document["fineMultiplier"] = days_diff
            document["fineAmount"] = int(document['fineAmount'])
        
        return issued_books_list
    
    def GetIssueById(_id):
        return IssuanceDAO.db.Issuance.find_one({"_id":ObjectId(_id)})
    
    def IssueBook(obj):
        return IssuanceDAO.db.Issuance.insert_one(obj)
    
    def ReturnIssuedBook(_id, obj):
        return IssuanceDAO.db.Issuance.find_one_and_update( {"_id": ObjectId(_id)}, {"$set": obj}, return_document=True)

    def IncreaseIssueCount(_id):
        book = IssuanceDAO.db.Issuance.find_one({"_id":ObjectId(_id)})
        msg=""
        if book["present_copy"] > 0:
            msg = "Success"
            IssuanceDAO.db.Issuance.find_one_and_update({"_id": ObjectId(_id)},{"$set": { "issued_copy": int(book["issued_copy"]) + 1, "present_copy": int(book["present_copy"]) - 1  }})
        else:
            msg = "No book available"
            
        return {msg:msg}
            
    def DecreaseIssueCount(_id):
        book = IssuanceDAO.db.Issuance.find_one({"_id":ObjectId(_id)})
        IssuanceDAO.db.Issuance.find_one_and_update({"_id": ObjectId(_id)},{"$set": { "issued_copy": int(book["issued_copy"]) - 1, "present_copy": int(book["present_copy"]) + 1  }})
