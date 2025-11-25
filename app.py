from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# temporary storage (before connecting to database)
users = []

@app.route('/')
def home():
    return redirect(url_for('login'))

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # check if user already exists
        for u in users:
            if u['email'] == email:
                return "Email already registered. Try logging in."

        users.append({'email': email, 'password': password})
        return redirect(url_for('login'))

    return render_template('signup.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        for u in users:
            if u['email'] == email and u['password'] == password:
                return f"Welcome, {email}! Login successful."
        return "Invalid email or password."

    return render_template('login.html')


if __name__ == '__main__':
    app.run(debug=True)

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        trip_type = request.form['trip_type']
        from_country = request.form['from_country']
        to_country = request.form['to_country']
        depart_date = request.form['depart_date']
        return_date = request.form['return_date']
        travellers = request.form['travellers']

        print(trip_type, from_country, to_country, depart_date, return_date, travellers)
        return "Search data received!"

    return render_template('search.html')

