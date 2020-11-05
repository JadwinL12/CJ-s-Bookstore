from flask import Flask, render_template
from flask import request
from db_connector.db_connector import connect_to_database, execute_query

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


@app.route('/newcustomer', methods=['POST', 'GET'])
def newcustomer():
    db_connection = connect_to_database()
    # if request.method == 'GET':
    #     query = 'SELECT id,
    if request.method == "POST":
        fname = request.form['fname']
        lname = request.form['lname']
        email = request.form['email']
        address = request.form['address']
        city = request.form['city']
        state = request.form['state']
        postcode = request.form['postcode']
        country = request.form['country']

        query = "SELECT email from customers where email=%s"
        result = execute_query(db_connection,query,[email]).fetchall()
        print(result[0])
        print([email])
        # If the email not exsist yet, then allow t
        if result[0][0] == email:
            error = "Email existing, try again!"
            return render_template("newcustomer.html", error=error)
        else:
            query = 'INSERT INTO customers (firstName, lastName, email, address, city, state, postalCode, country) ' \
                    'VALUES (%s,%s,%s,%s,%s,%s,%s,%s)'
            data = (fname, lname, email, address, city, state, postcode, country)
            print(data)
            execute_query(db_connection,query,data)
    # query = "SELECT email FROM customers"
    # result = execute_query(db_connection,query).fetchall()
    # # print(result)
    return render_template("newcustomer.html")

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
