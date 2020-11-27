from flask import Flask, render_template, flash
from flask import request
from db_connector.db_connector import connect_to_database, execute_query
import requests

app = Flask(__name__)
customername = "NewCustomer"

cart = []

@app.route('/')
@app.route('/home', methods=['POST', 'GET'])
def home():
    db_connection = connect_to_database()
    if request.method =="POST":
        if "ISBN" in request.form:
            ISBN = request.form["ISBN"]
            bookTitle = request.form["title"]
            price = request.form["price"]
            newBook = (ISBN, bookTitle, price)
            cart.append(newBook)
            numberInCart = len(cart)
            for book in cart:
                print(book[1])
            books = execute_query(db_connection, "SELECT bookID, title, cost, yearPublish, quantityInStock FROM books;").fetchall()
            return render_template("home.html", books=books, numberInCart=numberInCart)
        else:
            searchTitle = request.form['searchTitle']
            searchTitle = "%"+searchTitle+"%"
            numberInCart = len(cart)
            books = execute_query(db_connection, "SELECT bookID, title, cost, yearPublish, quantityInStock FROM books WHERE title LIKE %s", ([searchTitle])).fetchall()
            return render_template("home.html", books=books, numberInCart=numberInCart)
    categoryID = request.args.get('categoryID')
    if categoryID:
        books = execute_query(db_connection,"SELECT B.bookID, B.title, B.cost, B.yearPublish, B.quantityInStock, C.categoryName FROM books B "
                              "JOIN bookscategories BC ON B.bookID = BC.bookID "
                              "JOIN categories C ON BC.categoryID = C.categoryID AND C.categoryID =%s ", [categoryID]).fetchall()
    else:
        books = execute_query(db_connection, "SELECT bookID, title, cost, yearPublish, quantityInStock FROM books;").fetchall()
    return render_template("home.html", books=books)


@app.route('/category', methods=['POST', 'GET'])
def category():
    db_connection = connect_to_database()
    numberInCart = len(cart)
    if request.method == "POST":
        newCategory = request.form['newCategory']
        query = "INSERT INTO categories (categoryName) VALUES (%s)"
        execute_query(db_connection, query, [newCategory])

    query = "SELECT categoryID, categoryName FROM categories"
    categories = execute_query(db_connection, query).fetchall()
    return render_template("category.html", categories=categories, numberInCart=numberInCart)


@app.route('/newbook', methods=['POST', 'GET'])
def newbook():
    db_connection = connect_to_database()
    numberInCart = len(cart)
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
                return render_template("newbook.html", book=book, categoryIDs=categoryIDs, allCategories=allCategories, numberInCart=numberInCart)
            else:
                book_not_found = "The book is not in the bookstore. Try again or create the book info into our bookstore below."
                return render_template("newbook.html", error=book_not_found, categoryIDs=categoryIDs, allCategories=allCategories, numberInCart=numberInCart)
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
                return render_template("newbook.html", update=bookUpdated, book=book, categoryIDs=inputCategories, allCategories=allCategories, numberInCart=numberInCart)
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
                return render_template("newbook.html", insert=insertSucess, book=book, categoryIDs=inputCategories, allCategories=allCategories, numberInCart=numberInCart)

    return render_template("newbook.html", allCategories=allCategories, numberInCart=numberInCart)


@app.route('/customerinfo', methods=['POST', 'GET'])
def customerinfo():
    db_connection = connect_to_database()
    numberInCart = len(cart)
    if request.method == "POST":
        # print(request.form) # will see all the request info from the form
        if 'customeremail' in request.form:
            customeremail = request.form['customeremail']
            customer = execute_query(db_connection, "SELECT * FROM customers WHERE email=%s", [customeremail]).fetchall()
            print(customer)
            # If return a matching customer, then update the page
            if customer:
                return render_template("customerinfo.html", customer=customer, numberInCart=numberInCart)
            else:
                error_not_found = "Can't find your Email. Try again or input all your info below to create a new account."
                return render_template("customerinfo.html", error=error_not_found, numberInCart=numberInCart)
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
                    return render_template("customerinfo.html", insert=insert, customer=customer, numberInCart=numberInCart)
                else:
                    query = 'UPDATE customers SET lastname=%s, firstname=%s,address=%s,city=%s,state=%s,postalCode=%s,country=%s WHERE email=%s'
                    data = (lname,fname,address,city,state,postcode,country,email)
                    execute_query(db_connection,query,data)
                    update = "Your Info Updated successfully!"

                    customer = execute_query(db_connection, "SELECT * FROM customers WHERE email=%s",
                                             [email]).fetchall()
                    # flash('Your post has been updated!', 'success')
                    return render_template("customerinfo.html", update=update, customer=customer, numberInCart=numberInCart)

    return render_template("customerinfo.html",numberInCart=numberInCart)


@app.route('/mypayments', methods=['POST', 'GET'])
def mypayments():
    db_connection = connect_to_database()
    numberInCart = len(cart)
    if request.method == "POST":
        # print(request.form) # will see all the request info from the form
        if 'searchPayments' in request.form:
            customeremail = request.form['searchPayments']
            customername = execute_query(db_connection, "SELECT firstName, lastName FROM customers WHERE email=%s", [customeremail]).fetchall()
            query = "SELECT payments.paymentID, customers.firstName, customers.lastName, payments.paymentDate, payments.amount " \
                    "FROM customers INNER JOIN payments ON customers.customerID=payments.customerID AND customers.email=%s"
            payments = execute_query(db_connection, query, [customeremail]).fetchall()

            # If return a matching customer, then update the page
            if payments:
                total = 0
                for payment in payments:
                    total += payment[4]
                return render_template("mypayments.html", payments=payments, total=total, customername=customername, numberInCart=numberInCart)
            else:
                error_not_found = "Can't find your Email. Try again or create a new account on CustomerInfo page."
                return render_template("mypayments.html", error=error_not_found)
    return render_template("mypayments.html", customername="", numberInCart=numberInCart)

@app.route('/makepayment', methods=['POST', 'GET'])
def makepayment():
    db_connection = connect_to_database()
    numberInCart = len(cart)
    if request.method == "POST":
        if 'searchUnPaid' in request.form or ('confirm' in request.form and request.form['confirm'] != 'makepayment'):
        # if request.form['confirm'] != 'makepayment':
            if 'searchUnPaid' in request.form:
                customeremail = request.form['searchUnPaid']
            if 'confirm' in request.form:
                customeremail = request.form['paidBy']
                # Get original Qty, new(input) Qty and index of the books in the table
                originalQty = request.form.getlist('originalQty')
                inputQtys = request.form.getlist('qty')
                index = ''
                for i in range(len(originalQty)):
                    if originalQty[i] != inputQtys[i]:
                        index = i
                # Update the quantity of books if the index is not null
                if index != '':
                    # Get the orderID, bookID and new Qty based on the Index
                    orderID = request.form.getlist('orderID')[index]
                    bookID = request.form.getlist('bookID')[index]
                    inputQty = inputQtys[index]
                    execute_query(db_connection, "UPDATE booksorders SET quantity=%s WHERE orderID=%s AND bookID=%s",
                                  ([inputQty], [orderID], [bookID]))
                # Render the page again
                customerID = request.form['customerID']

            customername = execute_query(db_connection, "SELECT firstName, lastName FROM customers WHERE email=%s", [customeremail]).fetchall()
            queryUnPaid = 'SELECT orders.orderID, customers.firstName, customers.lastName, booksorders.bookID, booksorders.quantity, booksorders.sellingPrice, books.title, customers.customerID FROM orders ' \
                          'JOIN customers ON orders.customerID=customers.customerID ' \
                          'JOIN booksorders ON orders.orderID=booksorders.orderID ' \
                          'JOIN books ON books.bookID=booksorders.bookID WHERE customers.email=%s AND orders.paid=%s;'
            dataUnPaid = ([customeremail], 'FALSE')
            ordersUnPaid = execute_query(db_connection, queryUnPaid, dataUnPaid).fetchall()
            total = 0
            for orderUnPaid in ordersUnPaid:
                total += orderUnPaid[4]*orderUnPaid[5]
            return render_template("makepayment.html", ordersUnPaid=ordersUnPaid, customername=customername, customeremail=customeremail, total=total, numberInCart=numberInCart)
        if request.form['confirm'] == 'makepayment':
            customerID = request.form['customerID']
            amount = request.form['total']
            paymentEmail = request.form['paidBy']
            customerID_makePayment = execute_query(db_connection,"SELECT customerID FROM customers WHERE email=%s", ([paymentEmail])).fetchall()
            if len(customerID_makePayment) == 0:
                execute_query(db_connection, "INSERT INTO payments (paymentDate, amount) VALUES (current_date(), %s)", ([amount]))
            else:
                execute_query(db_connection, "INSERT INTO payments (customerID, paymentDate, amount) VALUES (%s, current_date(), %s)", ([customerID_makePayment], [amount]))
            execute_query(db_connection, "UPDATE orders SET paid='1' WHERE customerID=%s", ([customerID]))
            paid = True
            return render_template("makepayment.html", paid=paid, numberInCart=numberInCart)
    return render_template("makepayment.html", numberInCart=numberInCart)

@app.route('/myorders', methods=['POST', 'GET'])
def myorders():
    db_connection = connect_to_database()
    numberInCart = len(cart)
    if request.method == "POST":
        customeremail = request.form['searchOrders']
        query = "SELECT orders.orderID, books.bookID, customers.firstName, customers.lastName, books.title, booksorders.quantity, orders.paid FROM customers " \
                "LEFT JOIN orders ON customers.customerID = orders.customerID " \
                "LEFT JOIN booksorders ON booksorders.orderID = orders.orderID " \
                "LEFT JOIN books ON books.bookID = booksorders.bookID  WHERE customers.email=%s"
        orders = execute_query(db_connection, query, ([customeremail])).fetchall()
        return render_template("myorders.html", orders=orders,numberInCart=numberInCart)
    return render_template("myorders.html",numberInCart=numberInCart)

@app.route('/placeorder', defaults={"ISBN": None}, methods=['POST', 'GET'])
@app.route('/placeorder/<ISBN>', methods=['POST', 'GET'])
def placeorder(ISBN):
    db_connection = connect_to_database()
    numberInCart = len(cart)
    if request.method == "GET":
        if ISBN:
            query = "SELECT bookID, title, cost, yearPublish, quantityInStock FROM books WHERE bookID=%s;"
            result = execute_query(db_connection, query, [ISBN]).fetchall()
            return render_template("placeorder.html", books=result,numberInCart=numberInCart)
        else:
            return render_template("placeorder.html",numberInCart=numberInCart)
    if request.method == "POST":
        if ('customeremail' in request.form) and (request.form['customeremail'] != ""):
            print(request.form)
            db_connection = connect_to_database()
            customeremail = request.form['customeremail']
            if 'book' in request.form:
                bookID = request.form.getlist('book')
                quantity = request.form.getlist('qty')
                sellingPrice = request.form.getlist('price')
                customer = execute_query(db_connection, "SELECT * FROM customers WHERE email=%s", [customeremail]).fetchall()
                customerID = customer[0][0]
                # If return a matching customer, then update the page
                if customerID:
                    execute_query(db_connection, "INSERT INTO orders (`customerID`, `paid`) VALUES (%s, %s)", ([customerID], 0))
                    order = execute_query(db_connection, "SELECT LAST_INSERT_ID();")
                    orderID = order.fetchall()[0][0]
                    for i in range(0, len(bookID)):
                        execute_query(db_connection, "INSERT INTO booksorders (`bookID`, `orderID`, `quantity`, `sellingPrice`) VALUES (%s, %s, %s, %s)", (bookID[i], orderID, quantity[i], sellingPrice[i]))
                    cart.clear()
                    return render_template("placeorder.html",numberInCart=numberInCart)
                else:
                    error_not_found = "Can't find your Account. Try again or create your account on CustomerInfo page."
                    return render_template("placeorder.html", error=error_not_found,numberInCart=numberInCart)
            else:
                error_not_found = "There is no book in your cart. Please add a book and try again."
                return render_template("placeorder.html", error=error_not_found, numberInCart=numberInCart)
        else:
            error_not_found = "Can't find your Account. Try again or create your account on CustomerInfo page."
            return render_template("placeorder.html", error=error_not_found,numberInCart=numberInCart)


@app.route('/placeorder2', methods=['POST', 'GET'])
def placeorder2():
    if request.method == "GET":
        userCart = cart
        numberInCart = len(cart)
        return render_template("placeorder.html", books=userCart, numberInCart=numberInCart)


if __name__ == '__main__':

    app.run(debug=True)
