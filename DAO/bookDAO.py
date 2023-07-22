from pymongo.mongo_client import MongoClient
from bson import ObjectId
from datetime import datetime, timedelta

class BookDAO():
    db:any
    
    def search(keyword):
        query = {
            "$or": [
                {"name": {"$regex": keyword, "$options": "i"}},
                {"author": {"$regex": keyword, "$options": "i"}},
                {"about": {"$regex": keyword, "$options": "i"}},
                {"tags": {"$regex": keyword, "$options": "i"}},
            ]
        }    
        
        results = BookDAO.db.Book.find(query)
        return list(results)
    
    def GetAllBooks():   
        return BookDAO.db.Book.find()    
    
    def GetBookById(_id):   
        return BookDAO.db.Book.find_one({"_id":ObjectId(_id)})
    
    def InsertBook(book):
        return BookDAO.db.Book.insert_one(book)
    
    def EditBook(_id,book):
        return BookDAO.db.Book.find_one_and_update( {"_id": ObjectId(_id)},{"$set": book},return_document=True)
    
    def DeleteBook(_id):
        return BookDAO.db.Book.find_one_and_delete({"_id":ObjectId(_id)})
    
    def GetAllBooksByCustomerId(_id):
        customerData = BookDAO.db.User.find_one({"_id":ObjectId(_id)})    
        allbooks = BookDAO.db.Book.find()
        currentlyIssued = BookDAO.db.Issuance.find({"customerId":_id, 'returnDate': None})
        matching_data = {'customerData':customerData,'books':[]}
        
        issued_books_list = list(currentlyIssued)
        for book in allbooks:
            book["isIssued"] = 0

            for issued_book in issued_books_list:
                if issued_book["bookId"] == str(book["_id"]):
                    book["isIssued"] = 1
                    book["issueId"] = str(issued_book["_id"])
            
            matching_data["books"].append(book)
                  
        return matching_data
    
    def GetBooksByCustomerId(_id):
        customerData = BookDAO.db.User.find_one({"_id":ObjectId(_id)})    
        currentlyIssued = BookDAO.db.Issuance.find({"customerId":_id, 'returnDate': None})
        matching_data = {'customerData':customerData,'books':[]}
        for document in currentlyIssued:
            bookId = str(document['bookId'])
            bookData = BookDAO.db.Book.find_one({"_id":ObjectId(bookId)})
            if bookData:
                bookData["issueDate"] = document['issueDate']
                bookData["formattedIssueDate"] = bookData["issueDate"].strftime("%d-%m-%Y")
                bookData["fineDate"] = document["fineDate"]
                bookData["formattedFineDate"] = bookData["fineDate"].strftime("%d-%m-%Y")

                date_diff = datetime.now() - document["fineDate"]
                days_diff = date_diff.days                
                bookData["fineMultiplier"] = days_diff

                bookData["returnDate"] = document['returnDate']
                bookData["fineAmount"] = int(document['fineAmount'])

                matching_data["books"].append(bookData)
        
        return matching_data
    
    

     