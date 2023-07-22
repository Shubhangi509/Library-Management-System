from flask import Flask, g, escape, session, redirect, render_template, request,url_for
from pymongo.mongo_client import MongoClient
from Misc.functions import ago, getUserDetails, find_matching_customer, find_matching_book

app = Flask(__name__)
app.secret_key = '#$ab9&^BB00_.'

# Create a new client and connect to the server
uri = "mongodb+srv://Shubhangi509:BKFSu7asnkqhoiXn@library.as5cucm.mongodb.net/Library"
client = MongoClient(uri)
db = client.Library

#Import DataAccess
from DAO.adminDAO import AdminDAO
from DAO.customerDAO import CustomerDAO
from DAO.bookDAO import BookDAO
from DAO.issuanceDAO import IssuanceDAO

#Registering DB
AdminDAO.db = db
CustomerDAO.db = db
BookDAO.db = db
IssuanceDAO.db = db

# Registering blueprints
from routes.admin import admin_view
from routes.customer import customer_view

# Registering custom functions to be used within templates
app.jinja_env.globals.update(str=str)

app.register_blueprint(admin_view)
app.register_blueprint(customer_view)


@app.route("/", methods=['GET'])
def login():
    user = getUserDetails()
    if user is None:
        return render_template("shared/login.html",error=""); 
    else:
        if "userId" not in user or user["userId"] is None:  
            return render_template("shared/login.html",error="");
        
        if user['userType'] == "Admin":
            redirect_url = url_for("admin_routes.home")
            return redirect(redirect_url)
        else:
            redirect_url = url_for("customer_routes.home")
            return redirect(redirect_url) 

@app.route("/admin-login", methods=['GET','POST'])
def admin_login():
    user = getUserDetails()
    if user is None:
        return render_template("shared/admin_login.html",error=""); 
    else:
        if "userId" not in user or user["userId"] is None:  
            return render_template("shared/admin_login.html",error="");
        
        if user['userType'] == "Admin":
            redirect_url = url_for("admin_routes.home")
            return redirect(redirect_url)
        else:
            redirect_url = url_for("customer_routes.home")
            return redirect(redirect_url) 

@app.route("/signin",methods=['POST'])
def signin():
	if request.method == 'POST':
		_form = request.form 
		user = str(_form.get("user"))
		username = str(_form.get("username"))
		password = str(_form.get("password"))

		if user == "Admin":
			curUrl = "shared/admin_login.html"
		else:
			curUrl = "shared/login.html"

		if len(username)<1 or len(password)<1:
			return render_template(curUrl, error="Username and password are required")

		d = CustomerDAO.CheckLogin(username, password, user)
		if d:
			session['userType'] = user
			session['userId'] = str(d["_id"])  # Convert ObjectId to string
			session['userName'] = str(d["name"])
			
			if user == "Admin":
				return redirect("/admin")
			else:
				return redirect("/customer")
		else:
			return render_template(curUrl, error="Username or password incorrect")

@app.errorhandler(404)
def page_not_found(e):
    # You can return a custom error page
    return render_template('shared/404.html'), 404

if __name__ == "__main__":
    app.run(debug=True)