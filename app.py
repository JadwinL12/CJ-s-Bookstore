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


@app.route('/signup')
def signup():
    return render_template("signup.html")


@app.route('/login')
def login():
    return render_template("login.html")


@app.route('/cart')
def cart():
    return render_template("cart.html")


if __name__ == '__main__':
    app.run(debug=True)
