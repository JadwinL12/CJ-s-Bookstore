from flask import Flask, render_template
from db_connector.db_connector import connect_to_database, execute_query

app = Flask(__name__)


@app.route('/')
@app.route('/home')
def home():
    db_connection = connect_to_database()
    query = "SELECT bookID, title, cost, yearPublish, quantityInStock FROM books;"
    result = execute_query(db_connection, query).fetchall()
    # print(result)
    return render_template("home.html", books=result)


@app.route('/newcustomer')
def newcustomer():
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
