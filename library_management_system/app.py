from flask import Flask,render_template,request,redirect,url_for,flash, session
from flask_sqlalchemy import SQLAlchemy
import datetime
from flask_migrate import Migrate

app=Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:psql@localhost/library'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.secret_key = 'your_secret_key_here'
db = SQLAlchemy(app)
migrate = Migrate(app, db)
# Dummy data for users and books (replace with your database)

class registration(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    firstname = db.Column(db.String(80))
    lastname = db.Column(db.String(80))
    email = db.Column(db.String(120))
    password = db.Column(db.String(80))


class Book(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    author = db.Column(db.String(100), nullable=False)

# Member model
class Member(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)


# Transaction model
class Transaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    book_id = db.Column(db.Integer, db.ForeignKey('book.id'), nullable=False)
    member_id = db.Column(db.Integer, db.ForeignKey('member.id'), nullable=False)
    registration_id = db.Column(db.Integer, db.ForeignKey('registration.id'), nullable=False)
    due_date = db.Column(db.Date, nullable=False)

    # Define relationships
    book = db.relationship('Book', backref='transactions')
    member = db.relationship('Member', backref='transactions')
    registration = db.relationship('registration', backref='transactions')

# Define the home page
@app.route('/')
def index():
    return render_template('front_page.html')

# User registration page
@app.route("/user_login",methods=["GET", "POST"])
def user_login():
    if request.method=="POST":
        email=request.form.get('email')
        password=request.form.get('password')
        facebook=registration.query.filter_by(email=email).first()
        if  facebook and facebook.password==password:
            return render_template("user_navbar.html")
        else:
            error_message="Email and password dose note match"
            return render_template("user_login.html")
    return render_template("user_login.html")



@app.route("/signin",methods=["GET", "POST"])
def signin():
    if request.method == "POST":
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        email = request.form.get("email")
        password = request.form.get("password")
        new_login=registration(firstname = firstname,lastname=lastname
            ,email=email,password=password)
        db.session.add(new_login)
        db.session.commit()
        return render_template("user_login.html")
    return render_template("user_registration.html")


@app.route("/admin_login",methods=["GET", "POST"])
def admin_login():
    if request.method=="POST":
        email=request.form.get('email')
        password=request.form.get('password')
        facebook=registration.query.filter_by(email=email).first()
        if  facebook and facebook.password==password:
            return render_template("admin_navbar.html")
        else:
            error_message="Email and password dose note match"
            return render_template("admin_login.html")
    return render_template("admin_login.html")


@app.route("/admin_signin",methods=["GET", "POST"])
def admin_signin():
    if request.method == "POST":
        firstname = request.form.get('firstname')
        lastname = request.form.get('lastname')
        email = request.form.get("email")
        password = request.form.get("password")
        new_login=registration(firstname = firstname,lastname=lastname
            ,email=email,password=password)
        db.session.add(new_login)
        db.session.commit()
        return render_template("admin_login.html")
    return render_template("admin_register.html")

@app.route('/user_navbar',methods=["GET", "POST"])
def user_navbar():
    return render_template('user_navbar.html')


@app.route('/dashboard',methods=["GET", "POST"])
def dashboard():
    total_books = 100
    available_books = 80
    issued_books = 15
    overdue_books = 5

    return render_template("dashboard.html",
                            total_books=total_books,
                            available_books=available_books,
                            issued_books=issued_books,
                            overdue_books=overdue_books)

@app.route('/borrow_book', methods=["GET", "POST"])
def borrow_book():
    if request.method == "POST":
        # Check if there are available books to borrow
        if 'total_books' in session and session['total_books'] > 0:
            borrowed_book = request.form.get('book_name')

            # Decrease the total_books count by 1 when a user borrows a book
            session['total_books'] -= 1

            session['borrowed_book'] = borrowed_book

            return redirect(url_for('borrow_confirmation'))
        else:
            flash("Sorry, there are no available books to borrow.")
    
    return render_template("borrow_book.html")

@app.route('/borrow_confirmation', methods=["GET", "POST"])
def borrow_confirmation():
    borrowed_book = session.get('borrowed_book')

    return render_template("borrow_confirmation.html", borrowed_book=borrowed_book)


@app.route('/book_search', methods=['GET', 'POST'])
def book_search():
    if request.method == 'POST':
        search_query = request.form.get('search_query')
        
        # Search books in the database based on the query
        matching_books = Book.query.filter(
            (Book.title.ilike(f"%{search_query}%")) | (Book.author.ilike(f"%{search_query}%"))
        ).all()
        
        return render_template('book_search.html', books=matching_books, search_query=search_query)
    
    return render_template('book_search.html', books=None, search_query=None)

@app.route('/admin_navbar',methods=["GET", "POST"])
def admin_navbar():
    return render_template('admin_navbar.html')

@app.route('/add_book', methods=['GET','POST'])
def add_book():
    title = request.form.get("title")
    author = request.form.get("author")
    
    if title and author:
        new_book = Book(title=title, author=author)
        db.session.add(new_book)
        db.session.commit()

        # books = Book.query.all()
    return render_template("addbook.html")

@app.route('/add_member', methods=['GET','POST'])
def add_member():

    name = request.form.get("name")
    email = request.form.get("email")
    
    if name and email:
        new_member = Member(name=name, email=email)
        db.session.add(new_member)
        db.session.commit()
        members=Member.query.all()
    return render_template("addmember.html",members=members)

@app.route('/view_dates', methods=['GET', 'POST'])
def view_dates():
    if request.method == 'POST':
        member_id = request.form.get('member_id')

        # Retrieve transactions for the given member where due_date is in the future
        transactions = Transaction.query.filter(
            (Transaction.member_id == member_id) & (Transaction.due_date > datetime.date.today())
        ).all()

        transaction_details = []

        for transaction in transactions:
            book = Book.query.get(transaction.book_id)
            member = Member.query.get(transaction.member_id)

            if book and member:
                transaction_detail = {
                    'book_title': book.title,
                    'book_author': book.author,
                    'book_due_date': transaction.due_date,
                    'member_name': member.name,
                }
                transaction_details.append(transaction_detail)

        return render_template('view_dates.html', transaction_details=transaction_details, member_id=member_id)

    return render_template('view_dates.html')


@app.route('/return_book', methods=['GET', 'POST'])
def return_book():
    if request.method == 'POST':
        # Get the user's input, e.g., book ID and member ID
        book_id = request.form.get('book_id')
        member_id = request.form.get('member_id')

        # Implement the logic to retrieve the due date
        # For example, you can use SQLAlchemy to query your database
        # Replace 'Transaction' with your actual model name
        transaction = Transaction.query.filter_by(book_id=book_id, member_id=member_id).first()

        if transaction:
            # Retrieve the due date from the transaction
            return_date = transaction.due_date.strftime('%Y-%m-%d')  # Format the date as needed
            flash(f'Book is due on: {return_date}', 'info')
        else:
            flash('Book not found or not issued to this member', 'error')

        return redirect('/return_book')

    return render_template('return_book.html', return_date=None)

@app.route('/book_update', methods=['GET', 'POST'])
def book_update():
    if request.method == 'POST':
        # Get data from the form (e.g., book ID and updated information)
        book_id = request.form.get('book_id')
        updated_title = request.form.get('updated_title')
        updated_author = request.form.get('updated_author')

        # Perform the book update logic here (e.g., update book details in the database)
        # Replace this with your actual book update logic

        # Redirect to a relevant page (e.g., back to the book details or dashboard)
        return redirect(url_for('dashboard'))

    # If it's a GET request, render the book update form
    return render_template('book_update.html')


@app.route('/view_orders')
def view_orders():
    # Retrieve orders data from the database (replace with your data retrieval logic)
    orders = [
        {'order_id': 1, 'book_title': 'Book 1', 'member_name': 'Member A', 'order_date': '2023-09-20'},
        {'order_id': 2, 'book_title': 'Book 2', 'member_name': 'Member B', 'order_date': '2023-09-21'},
    ]

    return render_template('view_orders.html', orders=orders)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
 