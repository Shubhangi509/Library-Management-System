from flask import current_app
from functools import wraps
import hashlib, binascii
from flask import session,redirect
import timeago, datetime
   
def ago(date):
    """
        Calculate a '3 hours ago' type string from a python datetime.
    """
    now = datetime.datetime.now() + datetime.timedelta(seconds = 60 * 3.4)

    return (timeago.format(date, now)) # will print x secs/hours/minutes ago

def getUserDetails():
    if "userId" not in session or session["userId"] is None:
        return None
    else:        
        return { "userType" : session['userType'], "userId": session['userId'] , "userName" : session['userName']}        

def find_matching_customer(customerId, customers):
    for customer in customers:
        if str(customer['_id']) == customerId:
            return customer
    return None

def find_matching_book(bookId, books):
    for book in books:
        if str(book['_id']) == bookId:
            return book
    return None
