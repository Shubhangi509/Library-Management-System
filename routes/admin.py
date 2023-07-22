from flask import Blueprint, g, escape,url_for, session, redirect, render_template, request
from Misc.functions import ago, getUserDetails
from DAO.bookDAO import BookDAO
from DAO.customerDAO import CustomerDAO
from DAO.issuanceDAO import IssuanceDAO
from datetime import datetime, timedelta

admin_view = Blueprint('admin_routes', __name__, template_folder='../templates/admin/', url_prefix='/admin')

@admin_view.before_request
def admin_before_request():
    user = getUserDetails()
    target_route = "admin_login"   
    redirect_url = url_for(target_route)

    if user is None:
        return redirect(redirect_url)
    else: 
        if "userId" not in user or user["userId"] is None:  
            return redirect(redirect_url)
        else:
            if user["userType"]  != 'Admin':  
                return redirect(redirect_url)
            else:
                g.user = user

@admin_view.route("/", methods=['GET'])
def home():
    user = getUserDetails()
    return render_template("admin_home.html",  g=g, user=user)

@admin_view.route("/signout/", methods=['GET'])
def signout():   
    session["userType"] = None
    session["userId"] = None
    session["userName"] = None
    target_route = "admin_login"   
    redirect_url = url_for(target_route)
    return redirect(redirect_url, code=302)

#region book
@admin_view.route('/books/search', methods=['POST'])
def search():
    user = getUserDetails()
    _form = request.form 
    keyword = str(_form.get("keyword"))
    
    if len(keyword)<1:
        return render_template("admin_home.html",g=g, user=user, error="Please enter a keyword!", keyword = escape(keyword))
    
    searchList = BookDAO.search(keyword)
    
    if len(searchList) > 0:
        return render_template("admin_home.html", g=g, user=user, searchList=searchList,  keyword=escape(keyword))

    return render_template("admin_home.html", g=g, user=user, error="No books found!", keyword=escape(keyword))

@admin_view.route('/books/', methods=['GET'])
def books():
    user = getUserDetails()
    mybooks = BookDAO.GetAllBooks()
    return render_template('books/admin_views.html', g=g, books=mybooks, user=user)

@admin_view.route('/books/<string:id>')
def view_book(id):
    user = getUserDetails()
    if id != None:
        book = BookDAO.GetBookById(id)
        if book and len(book) <1:
            return render_template('books/admin_book_view.html', error="No book found!")
        
        return render_template("books/admin_book_view.html", g=g, book=book, user=user)
    
@admin_view.route('/books/add', methods=['GET', 'POST'])
def book_add():
    user = getUserDetails()
    _form = request.form

    if request.method == 'GET':
        return render_template('books/admin_add.html', g=g, user=user)
    else:
        if _form is None:
            return render_template('books/admin_add.html', g=g, user=user, error="Not a valid input!")
        else:
            name = str(_form.get("name"))
            author = str(_form.get("author"))
            about = str(_form.get("about"))
            tags = str(_form.get("tags"))
            total_copy = int(_form.get("total_copy"))
           
            obj = {"name":name,"author":author,"about":about,"tags":tags.split(','),"total_copy":total_copy,"issued_copy":0,"present_copy":total_copy}            
            bookAdded = BookDAO.InsertBook(obj)
            return render_template('books/admin_add.html', g=g, user=user, msg="New Book Added Successfully")     

@admin_view.route('/books/edit/<string:id>', methods=['GET', 'POST'])
def book_edit(id):
    user = getUserDetails()
    _form = request.form
    
    if id != None:
        book = BookDAO.GetBookById(id)
        if book and len(book) <1:
            return render_template('books/admin_edit.html',g=g, user=user, error="No book found!")
        
        if request.method == 'GET':
            return render_template('books/admin_edit.html', g=g, book=book, user=user)
        else:           
            name = str(_form.get("name"))
            author = str(_form.get("author"))
            about = str(_form.get("about"))
            tags = str(_form.get("tags"))
            total_copy = int(_form.get("total_copy")) 

            obj = {"name":name,"author":author,"about":about,"tags":tags.split(','),"total_copy":total_copy,"issued_copy":0,"present_copy":total_copy}            
            book = BookDAO.EditBook(id,obj)
            return render_template("books/admin_edit.html", g=g, book=book, user=user, msg="Book Updated Successfully")
    
    return redirect('/books/')

@admin_view.route('/books/delete/<string:id>', methods=['POST'])
def book_delete(id):
    if id is not None:
        BookDAO.DeleteBook(id)
    
    return redirect('/admin/books/')

@admin_view.route('/books/issue/', methods=['GET','POST'])
def book_issue():
    user = getUserDetails()
    customers = list(CustomerDAO.GetAllCustomer())
    books = list(BookDAO.GetAllBooks())
    issues = list(IssuanceDAO.GetAllIssues())
    
    if request.method == 'GET':
        return render_template('books/admin_issue.html',g=g, user=user,customers = list(customers),books=books,issues=issues )
    else:
        _form = request.form
        bookId = _form.get("bookId")
        customerId = _form.get("customerId")
        issueDate = _form.get("issueDate")
        returnDate = _form.get("returnDate")
        
        if bookId is None or customerId is None:
            return render_template('books/admin_issue.html',g=g, user=user,customers = list(customers),books=books,issues=issues,error="All fields are required" )
        else:        
            issueDate = datetime.strptime(issueDate, "%Y-%m-%dT%H:%M")
            returnDate = datetime.strptime(returnDate, "%Y-%m-%dT%H:%M")
            obj = {"bookId":bookId,"customerId":customerId,"issueDate":issueDate,"fineDate":returnDate,"returnDate":None,"fineAmount":0}
            issuedBook = IssuanceDAO.IssueBook(obj)    
            return render_template('books/admin_issue.html',g=g, user=user,customers = list(customers),books=books,issues=issues,msg="New Book Issued Successfully" )
      
@admin_view.route('/books/remove/<string:id>', methods=['POST'])
def book_remove(id):
    user = getUserDetails()
    customers = list(CustomerDAO.GetAllCustomer())
    books = list(BookDAO.GetAllBooks())
    issues = list(IssuanceDAO.GetAllIssues())
    
    if id is None:
        return render_template('books/admin_issue.html',g=g, user=user,customers = list(customers),books=books,issues=issues,error="Not a valid input!")
    else:
        issueData = IssuanceDAO.GetIssueById(id)        
        date_diff = datetime.now() - issueData["fineDate"]
        days_diff = date_diff.days  
        obj = {"returnDate":datetime.now(), "fineAmount": 0 }
        if int(days_diff) > 0:
            obj["fineAmount"] = days_diff * 50
        returnedBook = IssuanceDAO.ReturnIssuedBook(id, obj) 
        return render_template('books/customer_add.html',g=g, user=user,customers = list(customers),books=books,issues=issues, msg="Book Returned Successfully")     

      
#endregion book

#region users
@admin_view.route('/users/', methods=['GET'])
def users():
    user = getUserDetails()
    customers = CustomerDAO.GetAllCustomer()
    return render_template('users/admin_views.html', g=g, user=user, customers=customers)

@admin_view.route('/users/<string:id>', methods=['GET'])
def view_users(id):
    user = getUserDetails()
    if id != None:
        customer = CustomerDAO.GetCustomerById(id)
       
        if customer and len(customer) <1:
            return render_template('users/admin_user_view.html', error="No Customer found!")
        
        return render_template('users/admin_user_view.html', g=g, user=user, customer=customer)
   
@admin_view.route('/users/add', methods=['GET', 'POST'])
def user_add():
    user = getUserDetails()
    _form = request.form

    if request.method == 'GET':
        return render_template('users/admin_add.html', g=g, user=user)
    else:
        if _form is None:
            return render_template('users/admin_add.html', g=g, user=user, error="Not a valid input!")
        else:
            name = str(_form.get("name"))
            email = str(_form.get("email"))
            username = str(_form.get("username"))
            password = str(_form.get("password"))
           
            obj = {"name":name,"email":email,"username":username,"password":password,"type":"customer"}            
            customerAdded = CustomerDAO.InsertCustomer(obj)
            return render_template('users/admin_add.html', g=g, user=user, msg="New Customer Added Successfully")     

@admin_view.route('/users/edit/<string:id>', methods=['GET', 'POST'])
def user_edit(id):
    user = getUserDetails()
    _form = request.form
    
    if id != None:
        customer = CustomerDAO.GetCustomerById(id)
        if customer and len(customer) <1:
            return render_template('users/admin_edit.html',g=g, user=user, error="No book found!")
        
        if request.method == 'GET':
            return render_template('users/admin_edit.html', g=g, user=user, customer=customer)
        else:           
            name = str(_form.get("name"))
            email = str(_form.get("email"))
            username = str(_form.get("username"))
            password = str(_form.get("password"))
           
            obj = {"name":name,"email":email,"username":username,"password":password,"type":"customer"}            
            customer = CustomerDAO.EditCustomer(id,obj)
            return render_template("users/admin_edit.html", g=g, user=user, customer=customer, msg="Customer Details Updated Successfully")
    
    return redirect('/books/')

@admin_view.route('/users/delete/<string:id>', methods=['POST'])
def user_delete(id):
    if id is not None:
        CustomerDAO.DeleteCustomer(id)
    
    return redirect('/admin/users/')

#endregion users


    