from flask import Flask, request, render_template, jsonify, session
import pickle
import numpy as np
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this to a secure random key in production

# Database initialization
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  username TEXT UNIQUE NOT NULL,
                  email TEXT UNIQUE NOT NULL,
                  password TEXT NOT NULL)''')
    conn.commit()
    conn.close()

init_db()

# Load pickle files
try:
    with open('classifier.pkl', 'rb') as f:
        model = pickle.load(f)
    with open('fertilizer.pkl', 'rb') as f:
        ferti = pickle.load(f)
    print("Models loaded successfully")
except Exception as e:
    print(f"Error loading pickle files: {e}")
    model, ferti = None, None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = c.fetchone()
    conn.close()
    
    if user and check_password_hash(user[3], password):
        session['user_id'] = user[0]
        return jsonify({"success": True})
    else:
        return jsonify({"success": False, "message": "Invalid username or password"})

@app.route('/signup', methods=['POST'])
def signup():
    username = request.form['username']
    email = request.form['email']
    password = request.form['password']
    
    hashed_password = generate_password_hash(password)
    
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)",
                  (username, email, hashed_password))
        conn.commit()
        return jsonify({"success": True})
    except sqlite3.IntegrityError:
        return jsonify({"success": False, "message": "Username or email already exists"})
    finally:
        conn.close()

@app.route('/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({"success": True})

@app.route('/predict', methods=['POST'])

    

#     

#     return render_template('index.html', result=result)

def predict_fertilizer():
    # Extract form data
    try:
        temp = float(request.form['temperature'])
        humi = float(request.form['humidity'])
        mois = float(request.form['moisture'])
        soil = request.form['soilType']
        crop = request.form['cropType']
        nitro = float(request.form['nitrogen'])
        pota = float(request.form['potassium'])
        phosp = float(request.form['phosphorous'])

        soil_types = ['black', 'clayey', 'loamy', 'red', 'sandy']
        crop_types = ['barley', 'cotton', 'groundNuts', 'maize', 'millets', 'oilSeeds', 'paddy', 'pulses', 'sugarcane', 'tobacco', 'wheat']
            
        soil = soil_types.index(soil)
        crop = crop_types.index(crop)

        input_data = [int(temp), int(humi), int(mois), soil, crop, int(nitro), int(pota), int(phosp)]

        predicted_fertilizer = ferti.classes_[model.predict([input_data])]
                
        return jsonify(success=True, fertilizer=str(predicted_fertilizer))
    
    except Exception as e:
        return jsonify(success=False, message=str(e))

if __name__ == '__main__':
    app.run(debug=True)

if __name__ == "__main__":
    app.run(debug=True)