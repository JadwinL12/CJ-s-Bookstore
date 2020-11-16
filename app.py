from flask import Flask, render_template
from flask import request
from db_connector.db_connector import connect_to_database, execute_query
import requests

app = Flask(__name__)
customername = "NewCustomer"


@app.route('/')
@app.route('/home')
def home():
    db_connection = connect_to_database()
    query = "SELECT bookID, title, cost, yearPublish, quantityInStock FROM books;"
    result = execute_query(db_connection, query).fetchall()
    # print(result)
    return render_template("home.html", books=result, customername=customername)


@app.route('/newbook', methods=['POST', 'GET'])
def newbook():
    db_connection = connect_to_database()
    if request.method == "POST":
        if 'ISBN' in request.form:
            ISBN = request.form['ISBN']
            book = execute_query(db_connection, "SELECT * FROM books WHERE bookID=%s", [ISBN]).fetchall()
            if book:
                return render_template("newbook.html", book=book)
            else:
                book_not_found = "The book is not in the bookstore. Try again or create the book info into our bookstore below."
                return render_template("newbook.html", error=book_not_found)
        if 'inputISBN' in request.form:
            ISBN = request.form['inputISBN']
            title = request.form['inputTitle']
            cost = request.form['inputCost']
            year = request.form['yearPublish']
            inventory = request.form['inventory']
            book = execute_query(db_connection, "SELECT * FROM books WHERE bookID=%s", [ISBN]).fetchall()
            if book:
                book_exist = "The book is already in our bookstore."
                return render_template("newbook.html", error=book_exist, book=book)
            else:
                query = 'INSERT INTO books (bookID, title, cost, yearPublish, quantityInStock) ' \
                        'VALUES (%s,%s,%s,%s,%s)'
                data = (ISBN, title, cost, year, inventory)
                execute_query(db_connection, query, data)
                insertSucess = "New Book added!"
                return render_template("newbook.html", insert=insertSucess, book=book)


    # ISBNS = execute_query(db_connection, "SELECT bookID FROM books").fetchall()
    # print(ISBNS)
    # booknotfound = "The book can't be found with the provided ISBN. Try again."
    # book = "http://openlibrary.org/search.json?q=" + "9780358004417"
    # x = requests.get(book)
    # print(x.content)
    return render_template("newbook.html")


@app.route('/customerinfo', methods=['POST', 'GET'])
def customerinfo():
    db_connection = connect_to_database()
    if request.method == "POST":
        # print(request.form) # will see all the request info from the form
        if 'customeremail' in request.form:
            customeremail = request.form['customeremail']
            customer = execute_query(db_connection, "SELECT * FROM customers WHERE email=%s", [customeremail]).fetchall()
            print(customer)
            # If return a matching customer, then update the page
            if customer:
                return render_template("customerinfo.html", customer=customer)
            else:
                error_not_found = "Can't find your Email. Try again or input all your info below to create a new account."
                return render_template("customerinfo.html", error=error_not_found)
        # if customer didn't search email
        if 'email' in request.form:
            fname = request.form['fname']
            lname = request.form['lname']
            email = request.form['email']
            address = request.form['address']
            city = request.form['city']
            state = request.form['state']
            postcode = request.form['postcode']
            country = request.form['country']
            # All these can't be null
            if fname and lname and email and address and postcode:
                query = "SELECT email from customers where email=%s"
                result = execute_query(db_connection, query, [email]).fetchall()
                update = ""
                insert = ""
                if result==():
                    print("Test")
                # If the email already exist, then update the info
                length = len(result)
                if len(result)==0:
                    query = 'INSERT INTO customers (firstName, lastName, email, address, city, state, postalCode, country) ' \
                        'VALUES (%s,%s,%s,%s,%s,%s,%s,%s)'
                    data = (fname, lname, email, address, city, state, postcode, country)
                    print(data)
                    execute_query(db_connection,query,data)
                    insert = "Your Info Created successfully!"
                    customer = execute_query(db_connection, "SELECT * FROM customers WHERE email=%s",
                                             [email]).fetchall()
                    return render_template("customerinfo.html", insert=insert, customer=customer)
                else:
                    query = 'UPDATE customers SET lastname=%s, firstname=%s,address=%s,city=%s,state=%s,postalCode=%s,country=%s WHERE email=%s'
                    data = (lname,fname,address,city,state,postcode,country,email)
                    execute_query(db_connection,query,data)
                    update = "Your Info Updated successfully!"
                    customer = execute_query(db_connection, "SELECT * FROM customers WHERE email=%s",
                                             [email]).fetchall()
                    return render_template("customerinfo.html", update=update, customer=customer)

    return render_template("customerinfo.html")

@app.route('/mypayments')
def mypayments():

    return render_template("mypayments.html")

@app.route('/makepayment')
def makepayment():

    return render_template("makepayment.html")

@app.route('/myorders')
def myorders():

    return render_template("myorders.html")

@app.route('/placeorder')
def placeorder():
    return render_template("placeorder.html")


if __name__ == '__main__':

    app.run(debug=True)
