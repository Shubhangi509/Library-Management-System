from flask import Blueprint, g, escape,url_for, session, redirect, render_template, request
from Misc.functions import ago, getUserDetails
from DAO.bookDAO import BookDAO
from DAO.customerDAO import CustomerDAO
from DAO.issuanceDAO import IssuanceDAO

from datetime import datetime, timedelta

customer_view = Blueprint('customer_routes', __name__, template_folder='../templates/customer/', url_prefix='/customer')

@customer_view.before_request
def Customer_before_request():
    user = getUserDetails()
    target_route = "login"   
    redirect_url = url_for(target_route)
    
    if user is None:
        redirect(redirect_url)
    else: 
        if "userId" not in user or user["userId"] is None:  
            redirect(redirect_url)
        else:
            if user["userType"] != 'Customer':  
                return redirect(redirect_url)
            else:
                g.user = user

@customer_view.route("/", methods=['GET'])
def home():
    user = getUserDetails()
    return render_template("customer_home.html",  g=g, user=user)

@customer_view.route("/signout/", methods=['GET'])
def signout():   
    session["userType"] = None
    session["userId"] = None
    session["userName"] = None
    target_route = "login"   
    redirect_url = url_for(target_route)
    return redirect(redirect_url, code=302)

#region book
@customer_view.route('/books/search', methods=['POST'])
def search():
    user = getUserDetails()
    _form = request.form 
    keyword = str(_form.get("keyword"))
    
    if len(keyword)<1:
        return render_template("customer_home.html",g=g, user=user, error="Please enter a keyword!", keyword=escape(keyword))
    
    searchList = BookDAO.search(keyword)
    
    if len(searchList) > 0:
        return render_template("customer_home.html", g=g, user=user, searchList=searchList,  keyword=escape(keyword))

    return render_template("customer_home.html", g=g, user=user, error="No books found!", keyword=escape(keyword))

@customer_view.route('/books/', methods=['GET'])
def books():
    user = getUserDetails()
    mybooks = BookDAO.GetBooksByCustomerId(str(user['userId']))    
    return render_template('books/customer_views.html', g=g, books=mybooks["books"], user=user)

@customer_view.route('/books/<string:id>')
def view_book(id):
    user = getUserDetails()
    if id != None:
        book = BookDAO.GetBookById(id)
        if book and len(book) <1:
            return render_template('books/customer_book_view.html', error="No book found!")
        
        return render_template("books/customer_book_view.html", g=g, book=book, user=user)

@customer_view.route('/books/add/', methods=['GET'])
def book_add_show():
    user = getUserDetails()
    books = BookDAO.GetAllBooksByCustomerId(str(user['userId']))    
    return render_template('books/customer_add.html', g=g, user=user, books=books["books"])
        
@customer_view.route('/books/add/<string:id>', methods=['POST'])
def book_add(id):
    user = getUserDetails()

    if id is None:
        books = BookDAO.GetAllBooksByCustomerId(str(user['userId']))    
        return render_template('books/customer_add.html', g=g, user=user, books=books["books"], error="Not a valid input!")
    else:
        obj = {"bookId":id,"customerId":user['userId'],"issueDate":datetime.now(),"fineDate":datetime.now() + timedelta(days=7),"returnDate":None,"fineAmount":0}
        issuedBook = IssuanceDAO.IssueBook(obj)    
        books = BookDAO.GetAllBooksByCustomerId(str(user['userId']))    
        return render_template('books/customer_add.html', g=g, user=user, books=books["books"], msg="New Book Issued Successfully")     

@customer_view.route('/books/remove/<string:id>', methods=['POST'])
def book_remove(id):
    user = getUserDetails()

    if id is None:
        books = BookDAO.GetAllBooksByCustomerId(str(user['userId']))    
        return render_template('books/customer_add.html',  g=g, user=user, books=books["books"],  error="Not a valid input!")
    else:
        issueData = IssuanceDAO.GetIssueById(id)
        
        date_diff = datetime.now() - issueData["fineDate"]
        days_diff = date_diff.days  
        obj = {"returnDate":datetime.now(), "fineAmount": 0 }
        if int(days_diff) > 0:
            obj["fineAmount"] = days_diff * 50

        returnedBook = IssuanceDAO.ReturnIssuedBook(id, obj) 
        books = BookDAO.GetAllBooksByCustomerId(str(user['userId']))    
        return render_template('books/customer_add.html',  g=g, user=user, books=books["books"],  msg="Book Returned Successfully")     


#endregion book

#region users
#endregion users
