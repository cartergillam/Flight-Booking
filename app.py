from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from pymongo.mongo_client import MongoClient
import certifi
from dotenv import load_dotenv
import os

load_dotenv()  # Load environment variables from .env file

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Set a secret key for session management

# Setting up MongoDB
uri = os.getenv("MONGODB_URI")  # Get MongoDB URI from environment variable

# Create a new client and connect to the server
client = MongoClient(uri, tlsCAFile=certifi.where())
db = client["user_database"]
users_collection = db["users"]
bookings_collection = db["bookings"]

@app.route('/', methods=['GET', 'POST'])
def flightSearch():
    user = None
    email = None
    flight_details = None

    if session:
        email = session['user_email']
        user = users_collection.find_one({"email": email})

        if request.method == 'POST':
            flight_type = request.form['flightType']
            from_city = request.form['from']
            to_city = request.form['to']

            # Create mock flight details
            flight_details = {
                'flight_type': flight_type,
                'from': from_city,
                'to': to_city
            }
            session['trip_type'] = flight_type
            session['from'] = from_city
            session['to'] = to_city

    
    return render_template('flightSearch.html', user=user, email=email, flight_details=flight_details)


# Profile Management route
@app.route('/profile/<email>', methods=['GET', 'POST'])
def profile(email):
    user = users_collection.find_one({"email": email})
    error_message = None
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'Save Changes':
            first_name = request.form['firstName']
            last_name = request.form['lastName']
            new_email = request.form['email']
            password = request.form['password']
            confirm_password = request.form['confirmPass']
            if not first_name or not last_name or not new_email or not password or not confirm_password:
                error_message = "All fields must be filled."
            elif password != confirm_password:
                error_message = "Passwords do not match."
            else:
                error_message = ""
                update_fields = {
                    "firstName": first_name,
                    "lastName": last_name,
                    "email": new_email,
                    "password": password
                }
                users_collection.update_one({"email": email}, {"$set": update_fields})
                return redirect(url_for('profile', email=new_email))
        elif action == 'Discard Changes':
            return redirect(url_for('flightSearch'))
    return render_template('profile.html', user=user, email=email, error_message=error_message)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':

        # Get form data
        firstName = request.form['firstName']
        lastName = request.form['lastName']
        email = request.form['email']
        password = request.form['password']
        confirmPass = request.form['confirmPass']

        #Check if fields are empty 
        if not firstName or not lastName or not email or not password or not confirmPass:
            return render_template('register.html', errorMessage="Fill out all fields")

        #Check if passwords match
        if password != confirmPass:
            return render_template('register.html', errorMessage="Passwords do not match")

        # Check if the username already exists in the database
        existing_user = users_collection.find_one({"email": email})
        if existing_user:
            return render_template('register.html', errorMessage="email already registered")

        
        # Store user details in the database
        users_collection.insert_one({
            "firstName": firstName,
            "lastName": lastName,
            "email": email,
            "password": password
        })
        # Redirect to login page
        return redirect(url_for('login'))

        
    return render_template('register.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        user_email = request.form['email']
        user_password = request.form['password']

        db_user = users_collection.find_one({"email": user_email})

        # Checks if the entered email is registered with a user in the database 
        if db_user is None:
            return render_template('login.html', errorMessage="The provided email is not registered")
        else:
            if db_user['password'] == user_password:
                session['user_email'] = user_email
                return redirect(url_for('flightSearch'))
            else:
                return render_template('login.html', errorMessage="Email and password does not match")
    return render_template('login.html')

@app.route('/seat-selection', methods=['GET'])
def seat_selection():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    user = users_collection.find_one({"email": session['user_email']})
    trip_type = session.get('trip_type', 'one_way')
    from_city = session.get('from', 'Unknown')
    to_city = session.get('to', 'Unknown')
    return render_template('seat-selection.html', user=user, trip_type=trip_type, from_city=from_city, to_city=to_city)

@app.route('/get-trip-info', methods=['GET'])
def get_trip_info():
    if 'user_email' not in session:
        return jsonify({"error": "User not logged in"}), 401
    user = users_collection.find_one({"email": session['user_email']})
    trip_type = session.get('trip_type', 'one_way')
    return jsonify({
        "isRoundTrip": trip_type == 'round_trip',
        "passengerName": f"{user['firstName']} {user['lastName']}",
        "tripType": trip_type
    })

@app.route('/save-seat-selection', methods=['POST'])
def save_seat_selection():
    if 'user_email' not in session:
        return jsonify({"success": False, "error": "User not logged in"}), 401
    data = request.json
    booking = {
        "user_email": session['user_email'],
        "departureSeat": data['departureSeat'],
        "returnSeat": data.get('returnSeat'),
        "trip_type": session.get('trip_type', 'one_way'),
        "to_city": session.get('to'),
        "from_city": session.get('from')
    }
    bookings_collection.insert_one(booking)
    return jsonify({"success": True, "userEmail": session['user_email']})


@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('flightSearch'))


@app.route('/clear-bookings')
def clear_bookings():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    user_email = session['user_email']
    bookings_collection.delete_many({"user_email": user_email})
    return redirect(url_for('profile', email=user_email))

@app.route('/booking-history')
def booking_history():
    if 'user_email' not in session:
        return redirect(url_for('login'))
    
    user_email = session['user_email']
    bookings = bookings_collection.find({"user_email": user_email})
    return render_template('booking-history.html', bookings=bookings)

if __name__ == "__main__":
    app.run(debug=True) # pragma: no cover