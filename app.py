from flask import Flask, render_template, request, redirect, session
import sqlite3

app = Flask(__name__)

app.secret_key = 'your_secret_key'

def get_db_connection():
    conn = sqlite3.connect('users.db')
    conn.row_factory = sqlite3.Row
    return conn

# Create DB if not exists
def init_db():
    conn = sqlite3.connect('repair.db')
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS bookings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            phone TEXT,
            device TEXT,
            issue TEXT,
            address TEXT,
            time TEXT
        )
    ''')
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return render_template('index.html')




@app.route('/book', methods=['GET', 'POST'])
def book_repair():
    if request.method == 'POST':
        name = request.form['name']
        phone = request.form['phone']
        device = request.form['device']
        issue = request.form['issue']
        address = request.form['address']
        time = request.form['time']

        conn = sqlite3.connect('repair.db')
        c = conn.cursor()
        c.execute("INSERT INTO bookings (name, phone, device, issue, address, time) VALUES (?, ?, ?, ?, ?, ?)",
                  (name, phone, device, issue, address, time))
        conn.commit()
        conn.close()

        return redirect('/confirmation')

    return render_template('book_repair.html')

@app.route('/confirmation')
def confirmation():
    return render_template('confirmation.html')

@app.route('/view_bookings')
def view_bookings():
    conn = sqlite3.connect('repair.db')
    c = conn.cursor()
    c.execute("SELECT * FROM bookings ORDER BY time ASC")
    bookings = c.fetchall()
    conn.close()
    return render_template('view_bookings.html', bookings=bookings)

# @app.route('/login', methods=['GET', 'POST'])
# def login():
#     if request.method == 'POST':
#         username = request.form['username']
#         password = request.form['password']

#         # Simple static login (you can connect to DB later)
#         if username == 'Deepika' and password == 'deepu@7396':
#             session['admin'] = True
#             return redirect('/admin_dashboard')
#         else:
#             return render_template('login.html', error='Invalid Credentials')

#     return render_template('login.html')

# @app.route('/admin_dashboard')
# def admin_dashboard():
#     if not session.get('admin'):
#         return redirect('/login')
#     return render_template('admin_dashboard.html')  # Your admin HTML


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
                           (name, email, password))
            conn.commit()
        except:
            return render_template('register.html', error='Email already exists!')
        finally:
            conn.close()

        return redirect('/customer_login')

    return render_template('register.html')



@app.route('/customer_login', methods=['GET', 'POST'])
def customer_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE email=? AND password=?", (email, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            session['user_id'] = user['id']
            session['user_name'] = user['name']
            return redirect('/')  # ✅ Redirect to index page
        else:
            return render_template('customer_login.html', error='Invalid credentials')

    return render_template('customer_login.html')


@app.route('/home')
def home():
    return render_template('index.html')


@app.route('/logout')
def logout():
    session.pop('admin', None)
    return redirect('/')

@app.route('/my_bookings', methods=['GET', 'POST'])
def my_bookings():
    bookings = []
    phone = ""

    if request.method == 'POST':
        phone = request.form['phone']
        conn = sqlite3.connect('repair.db')
        c = conn.cursor()
        c.execute("SELECT * FROM bookings WHERE phone = ?", (phone,))
        bookings = c.fetchall()
        conn.close()

    return render_template('my_bookings.html', bookings=bookings, phone=phone)

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')

@app.route('/thankyou')
def thankyou():
    return render_template('thankyou.html')


if __name__ == '__main__':
    app.run(debug=True)
