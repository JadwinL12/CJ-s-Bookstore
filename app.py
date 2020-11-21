from flask import Flask, render_template, flash
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


@app.route('/category', methods=['POST', 'GET'])
def category():
    db_connection = connect_to_database()
    if request.method == "POST":
        newCategory = request.form['newCategory']
        query = "INSERT INTO categories (categoryName) VALUES (%s)"
        execute_query(db_connection, query, [newCategory])

    query = "SELECT categoryID, categoryName FROM categories"
    categories = execute_query(db_connection, query).fetchall()
    return render_template("category.html", categories=categories)


@app.route('/newbook', methods=['POST', 'GET'])
def newbook():
    db_connection = connect_to_database()
    allCategories = execute_query(db_connection, "SELECT categoryID, categoryName FROM categories").fetchall()
    if request.method == "POST":
        # Search ISBN Form.
        if 'searchISBN' in request.form:
            ISBN = request.form['searchISBN']
            book = execute_query(db_connection, "SELECT * FROM books WHERE bookID=%s", [ISBN]).fetchall()
            bookCategories = execute_query(db_connection, "SELECT * FROM bookscategories WHERE bookID=%s", [ISBN]).fetchall()
            categoryIDs = []
            for bookCategory in bookCategories:
                categoryIDs.append(bookCategory[1])
            if book:
                return render_template("newbook.html", book=book, categoryIDs=categoryIDs, allCategories=allCategories)
            else:
                book_not_found = "The book is not in the bookstore. Try again or create the book info into our bookstore below."
                return render_template("newbook.html", error=book_not_found)
        # Input ISBN Form.
        if 'inputISBN' in request.form:
            ISBN = request.form['inputISBN']
            title = request.form['inputTitle']
            cost = request.form['inputCost']
            year = request.form['yearPublish']
            inventory = request.form['inventory']
            inputCategories = request.form.getlist('inputCategory')
            inputCategories = list(map(int, inputCategories))
            book = execute_query(db_connection, "SELECT * FROM books WHERE bookID=%s", [ISBN]).fetchall()
            # If Book existing, update the bookinfo. Else, insert a new book.
            if book:
                # Update books table based on input
                query = 'UPDATE books SET title=%s, cost=%s, yearPublish=%s, quantityInStock=%s WHERE bookID=%s'
                data = (title, cost, year, inventory, ISBN)
                execute_query(db_connection, query, data)

                # Read original categories in booksCategories table based on bookID
                bookCategories = execute_query(db_connection, "SELECT * FROM bookscategories WHERE bookID=%s",
                                        [ISBN]).fetchall()
                originalCategoryIDs = []
                for bookCategory in bookCategories:
                    originalCategoryIDs.append(bookCategory[1])
                # Compare the new Categories and original Categories, insert or delete rows in booksCategories table
                for i in range(1,11):
                    if i in inputCategories and i not in originalCategoryIDs:
                        insertCategoryQuery = "INSERT INTO bookscategories(bookID, categoryID) VALUES (%s,%s)"
                        data = (ISBN, i)
                        execute_query(db_connection, insertCategoryQuery, data)
                    if i not in inputCategories and i in originalCategoryIDs:
                        deleteCategoryQuery = "DELETE FROM bookscategories WHERE bookID=%s and categoryID=%s"
                        data = (ISBN, i)
                        execute_query(db_connection, deleteCategoryQuery, data)

                bookUpdated = "The book info has been updated"
                return render_template("newbook.html", update=bookUpdated, book=book, categoryIDs=inputCategories, allCategories=allCategories)
            else:
                # Insert a new book into books table
                query = 'INSERT INTO books (bookID, title, cost, yearPublish, quantityInStock) ' \
                        'VALUES (%s,%s,%s,%s,%s)'
                data = (ISBN, title, cost, year, inventory)
                execute_query(db_connection, query, data)
                # Insert all selected categories into booksCategories table for a new book
                for i in inputCategories:
                    insertCategoryQuery = "INSERT INTO bookscategories(bookID, categoryID) VALUES (%s,%s)"
                    data = (ISBN, i)
                    execute_query(db_connection, insertCategoryQuery, data)
                book = execute_query(db_connection, "SELECT * FROM books WHERE bookID=%s", [ISBN]).fetchall()
                insertSucess = "New Book added!"
                return render_template("newbook.html", insert=insertSucess, book=book, categoryIDs=inputCategories, allCategories=allCategories)

    return render_template("newbook.html", allCategories=allCategories)


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
                    # flash('Your post has been updated!', 'success')
                    return render_template("customerinfo.html", update=update, customer=customer)

    return render_template("customerinfo.html")


@app.route('/mypayments', methods=['POST', 'GET'])
def mypayments():
    db_connection = connect_to_database()
    if request.method == "POST":
        # print(request.form) # will see all the request info from the form
        if 'searchPayments' in request.form:
            customeremail = request.form['searchPayments']
            customername = execute_query(db_connection, "SELECT firstName, lastName FROM customers WHERE email=%s", [customeremail]).fetchall()
            print(customername[0])
            query = "SELECT payments.paymentID, customers.firstName, customers.lastName, payments.paymentDate, payments.amount " \
                    "FROM customers INNER JOIN payments ON customers.customerID=payments.customerID AND customers.email=%s"
            payments = execute_query(db_connection, query, [customeremail]).fetchall()

            # If return a matching customer, then update the page
            if payments:
                total = 0
                for payment in payments:
                    total += payment[4]
                return render_template("mypayments.html", payments=payments, total=total, customername=customername)
            else:
                error_not_found = "Can't find your Email. Try again or create a new account on CustomerInfo page."
                return render_template("mypayments.html", error=error_not_found)
    return render_template("mypayments.html", customername="")

@app.route('/makepayment')
def makepayment():
    db_connection = connect_to_database()

    return render_template("makepayment.html")

@app.route('/myorders')
def myorders():

    return render_template("myorders.html")

@app.route('/placeorder/<ISBN>', methods=['POST', 'GET'])
def placeorder(ISBN):
    db_connection = connect_to_database()
    query = "SELECT bookID, title, cost, yearPublish, quantityInStock FROM books WHERE bookID=%s;"
    result = execute_query(db_connection, query, [ISBN]).fetchall()
    if request.method == "GET":
        return render_template("placeorder.html", books=result)
    print(result)
    if request.method == "POST":
        # print(request.form) # will see all the request info from the form
        if 'customeremail' in request.form:
            customeremail = request.form['customeremail']
            customer = execute_query(db_connection, "SELECT * FROM customers WHERE email=%s", [customeremail]).fetchall()
            print(customer)
            # If return a matching customer, then update the page
            if customer:
                return render_template("placeorder.html", customer=customer, books=result)
            else:
                error_not_found = "Can't find your Account. Try again or create your account on CustomerInfo page."
                return render_template("placeorder.html", error=error_not_found, books=result)
        # if 'email' in request.form:


    return render_template("placeorder.html", book=result)


if __name__ == '__main__':

    app.run(debug=True)
