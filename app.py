from flask import Flask, request, jsonify, render_template, session, redirect, url_for, flash
from pymongo import MongoClient
from datetime import datetime
from bson import ObjectId
import os
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size
app.secret_key = 'your-secret-key-here'  # Add this for session handling

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# MongoDB connection
client = MongoClient('mongodb://localhost:27017/')
db = client['interestsDB']  # Changed from travel_plans to interestsDB
users_collection = db['users']  # This is the main collection for user profiles
plans_collection = db['plans']

# Allowed file extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Landing Page (Default)
@app.route("/")
def index():
    if "email" in session:
        return redirect(url_for("new"))  # If logged in, go to new.html
    return render_template("index.html")  # Show landing page

# Ensure user is logged in before accessing protected pages
@app.route("/check_auth")
def check_auth():
    if "email" not in session:
        return redirect(url_for("login"))
    
    # Check if user has completed profile and interests
    user = users_collection.find_one({"email": session["email"]})
    if not user.get("name"):  # If profile not completed
        return redirect(url_for("profile"))
    if not user.get("interests"):  # If interests not selected
        return redirect(url_for("interests"))
    return redirect(url_for("new"))

# Login Page
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        user = users_collection.find_one({"email": email})
        if user and check_password_hash(user["password"], password):
            session["email"] = email
            session["username"] = user["username"]
            
            # Check if user needs to complete profile or interests
            if not user.get("name"):  # If profile not completed
                return redirect(url_for("profile"))
            if not user.get("interests"):  # If interests not selected
                return redirect(url_for("interests"))
            return redirect(url_for("new"))  # If everything is complete

        flash("Invalid credentials, try again.", "error")
        return redirect(url_for("login"))

    return render_template("login.html")

# Signup Page
@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        email = request.form.get("email")
        password = request.form.get("password")

        # Check if user already exists
        if users_collection.find_one({"email": email}):
            flash("User already exists. Try logging in.", "error")
            return redirect(url_for("login"))

        # Create new user with the structure matching your sample
        hashed_password = generate_password_hash(password)
        new_user = {
            "email": email,
            "username": username,
            "password": hashed_password,
            "interests": [],
            "birthday": None,
            "destination": "",
            "languages": [],
            "name": "",
            "nationality": "",
            "preference": "",
            "profilePhoto": "",
            "tripType": ""
        }
        
        users_collection.insert_one(new_user)

        # Store session
        session["email"] = email
        session["username"] = username

        return redirect(url_for("profile"))  # After signup, go to profile setup

    return render_template("signup.html")

# Profile Setup Page (Only for new users after signup)
@app.route("/profile", methods=["GET", "POST"])
def profile():
    if "email" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        # Handle profile photo upload
        profile_photo_url = ""
        if 'profilePhoto' in request.files:
            file = request.files['profilePhoto']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filename = f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{filename}"
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                profile_photo_url = f"/static/uploads/{filename}"

        # Update user profile
        update_data = {
            "name": request.form.get("name"),
            "nationality": request.form.get("nationality"),
            "birthday": request.form.get("birthday"),
            "gender": request.form.get("gender"),
            "tripType": request.form.get("tripType"),
            "destination": request.form.get("destination"),
            "languages": request.form.getlist("languages[]")  # Get all values for languages[]
        }
        
        # Clean up empty strings from languages array
        update_data["languages"] = [lang.strip() for lang in update_data["languages"] if lang.strip()]
        
        if profile_photo_url:
            update_data["profilePhoto"] = profile_photo_url

        print("Updating user with data:", update_data)  # Debug print

        users_collection.update_one(
            {"email": session["email"]},
            {"$set": update_data}
        )

        return redirect(url_for("interests"))

    user = users_collection.find_one({"email": session["email"]}, {"_id": 0})
    return render_template("profile.html", user=user)

# Interests Selection Page (Only for new users after profile setup)
@app.route("/interests", methods=["GET", "POST"])
def interests():
    if "email" not in session:
        return redirect(url_for("login"))

    if request.method == "POST":
        data = request.get_json()
        if not data or "interests" not in data:
            return jsonify({"error": "No interests received"}), 400

        # Update user's interests
        users_collection.update_one(
            {"email": session["email"]},
            {"$set": {"interests": data["interests"]}}
        )

        # Return success with redirect URL
        return jsonify({
            "success": True,
            "redirect": url_for("new")
        })

    return render_template("interests.html")

# Main Page (new.html)
@app.route("/new")
def new():
    if "email" not in session:
        return redirect(url_for("login"))
    
    # Get user data
    user = users_collection.find_one({"email": session["email"]})
    
    # Fetch all plans from MongoDB
    plans = list(plans_collection.find())
    # Convert ObjectId to string for JSON serialization
    for plan in plans:
        plan['_id'] = str(plan['_id'])
    return render_template('new.html', plans=plans, user=user)

# Logout
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("index"))

@app.route('/plan/<plan_id>')
def plan_detail(plan_id):
    try:
        plan = plans_collection.find_one({'_id': ObjectId(plan_id)})
        if plan:
            plan['_id'] = str(plan['_id'])
            return render_template('plan_detail.html', plan=plan)
        return "Plan not found", 404
    except Exception as e:
        return str(e), 400

@app.route('/api/plans', methods=['POST'])
def create_plan_api():
    try:
        # Handle image upload or URL
        image_type = request.form.get('image_type')
        if image_type == 'file':
            if 'image_file' not in request.files:
                return jsonify({'success': False, 'error': 'No file uploaded'}), 400
            
            file = request.files['image_file']
            if file.filename == '':
                return jsonify({'success': False, 'error': 'No file selected'}), 400
            
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                # Add timestamp to filename to make it unique
                filename = f"{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}_{filename}"
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                image_url = f"/static/uploads/{filename}"
            else:
                return jsonify({'success': False, 'error': 'Invalid file type'}), 400
        else:
            image_url = request.form.get('image_url')
            if not image_url:
                return jsonify({'success': False, 'error': 'No image URL provided'}), 400

        # Create plan with either uploaded file path or URL
        plan = {
            'image_url': image_url,
            'name': request.form.get('name'),
            'location': request.form.get('location'),
            'start_date': request.form.get('start_date'),
            'end_date': request.form.get('end_date'),
            'description': request.form.get('description'),
            'created_at': datetime.utcnow(),
            'participants': []
        }
        
        result = plans_collection.insert_one(plan)
        return jsonify({'success': True, 'id': str(result.inserted_id)}), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/search')
def search():
    if 'email' not in session:
        return redirect(url_for('login'))
    
    user = users_collection.find_one({'email': session['email']})
    if not user:
        return redirect(url_for('login'))
    
    # Fetch all plans for initial display
    plans = list(plans_collection.find())
    # Convert ObjectId to string for JSON serialization
    for plan in plans:
        plan['_id'] = str(plan['_id'])
        
    return render_template('search.html', user=user, plans=plans)

@app.route('/view_profile')
def view_profile():
    if "email" not in session:
        return redirect(url_for("login"))
    user = users_collection.find_one({"email": session["email"]})
    if user:
        return render_template('demoprofile.html', user=user)
    return redirect(url_for("login"))

@app.route('/update_bio', methods=['POST'])
def update_bio():
    if "email" not in session:
        return jsonify({"success": False, "error": "Not logged in"}), 401
    
    try:
        data = request.get_json()
        bio = data.get('bio', '').strip()
        
        users_collection.update_one(
            {"email": session["email"]},
            {"$set": {"bio": bio}}
        )
        
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 400

@app.route('/create_plan')
def create_plan_page():
    if "email" not in session:
        return redirect(url_for("login"))
    return render_template('create_plan.html')

@app.route('/find_matches', methods=['POST'])
def find_matches():
    print("Received request to /find_matches")  # Debug print
    
    # Check if user is logged in
    if not session.get('email'):
        return jsonify({
            "error": "Authentication required",
            "message": "Please log in to find matches",
            "code": "AUTH_REQUIRED"
        }), 401

    try:
        data = request.get_json()
        print("Raw request data:", request.data)  # Debug print
        print("Parsed JSON data:", data)  # Debug print
        
        if not data:
            return jsonify({
                "error": "Invalid request",
                "message": "No data received",
                "code": "INVALID_REQUEST"
            }), 400

        # Extract search criteria
        destination = data.get("destination")
        num_people = int(data.get("numPeople", 1))
        gender = data.get("gender", "all")  # Changed from sex to gender
        age_range = data.get("ageRange", {"min": 18, "max": 25})

        if not destination:
            return jsonify({
                "error": "Missing parameter",
                "message": "Destination is required",
                "code": "MISSING_DESTINATION"
            }), 400

        print(f"Processing request - destination: {destination}, people: {num_people}, gender: {gender}, age range: {age_range}")

        # Build the query
        query = {
            "email": {"$ne": session["email"]},  # Exclude current user
            "destination": destination  # Match exact destination
        }
        
        # Handle gender preference matching
        if gender and gender != "all":
            query["gender"] = gender  # Direct match on gender field

        # Add age range filter if provided
        if age_range:
            # Calculate age range dates
            today = datetime.utcnow()
            max_birth_year = today.year - age_range["min"]
            min_birth_year = today.year - age_range["max"]
            
            # Convert birthday string to datetime for comparison
            query["$expr"] = {
                "$and": [
                    {"$gte": [{"$year": {"$dateFromString": {"dateString": "$birthday"}}}, min_birth_year]},
                    {"$lte": [{"$year": {"$dateFromString": {"dateString": "$birthday"}}}, max_birth_year]}
                ]
            }

        print("MongoDB query:", query)  # Debug print

        # Execute query and get results
        matched_users = list(users_collection.find(
            query,
            {
                "_id": 0,
                "name": 1,
                "nationality": 1,
                "profilePhoto": 1,
                "birthday": 1,
                "languages": 1,
                "interests": 1,
                "tripType": 1,
                "destination": 1,
                "gender": 1,  # Add gender field to projection
                "email": 1  # Also include email for user filtering
            }
        ).limit(num_people))
        
        print(f"Found {len(matched_users)} matches")  # Debug print
        print("Matched users:", matched_users)  # Debug print

        if not matched_users:
            return jsonify({
                "matches": [],
                "message": "No matches found for your criteria",
                "code": "NO_MATCHES"
            })

        return jsonify({
            "matches": matched_users,
            "message": f"Found {len(matched_users)} potential travel companions",
            "code": "SUCCESS"
        })
        
    except Exception as e:
        print(f"Error in find_matches: {str(e)}")  # Debug print
        import traceback
        print("Traceback:", traceback.format_exc())  # Print full traceback
        return jsonify({
            "error": "Server error",
            "message": str(e),
            "code": "SERVER_ERROR"
        }), 500

# Example of how to retrieve a user's data
@app.route('/user/<username>', methods=['GET'])
def get_user(username):
    user = users_collection.find_one({'username': username}, {'password': 0})  # Exclude password
    if user:
        return jsonify(user)
    return {'error': 'User not found'}, 404

if __name__ == '__main__':
    app.run(debug=True) 