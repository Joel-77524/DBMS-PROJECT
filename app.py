from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
from datetime import datetime
from flask_cors import CORS 

app = Flask(__name__)

# --------------------------------------------------------------------------
# CRITICAL FIX: EXPLICIT CORS CONFIGURATION
# --------------------------------------------------------------------------
# This explicitly allows the common local development origins (127.0.0.1:8080 and localhost:8080)
# and lists the allowed methods and headers, which helps bypass strict browser validation issues.
CORS(app, resources={r"/api/*": {"origins": [
    "http://127.0.0.1:8080", 
    "http://localhost:8080"
],
"methods": ["GET", "POST", "OPTIONS"],
"allow_headers": ["Content-Type", "Authorization"]
}})

# MySQL Configuration
app.config['MYSQL_HOST'] = 'localhost'      # Your MySQL server host
app.config['MYSQL_USER'] = 'root'           # Your MySQL username
app.config['MYSQL_PASSWORD'] = 'Root12345' # <-- CHANGE THIS to your actual password
app.config['MYSQL_DB'] = 'cinereview_db'    # The database name
# Returns rows as dictionaries
app.config['MYSQL_CURSORCLASS'] = 'DictCursor' 

mysql = MySQL(app)

# --------------------------------------------------------------------------
# FETCH ALL REVIEWS (Read operation)
# --------------------------------------------------------------------------
@app.route('/api/get_reviews', methods=['GET'])
def get_reviews():
    """
    API endpoint to fetch all existing reviews from the database.
    """
    try:
        conn = mysql.connection
        cursor = conn.cursor()
        
        sql = "SELECT reviewer_name, rating, review_text, created_at FROM reviews ORDER BY created_at DESC"
        cursor.execute(sql)
        
        reviews = cursor.fetchall()
        cursor.close()

        # Convert datetime objects to string format for JSON serialization
        for review in reviews:
            if isinstance(review.get('created_at'), datetime):
                review['created_at'] = review['created_at'].strftime("%Y-%m-%d")

        return jsonify(reviews), 200

    except Exception as e:
        print(f"Error fetching reviews: {e}")
        return jsonify({'error': f'Failed to retrieve data from database: {str(e)}'}), 500


# --------------------------------------------------------------------------
# SUBMIT REVIEW (Create operation)
# --------------------------------------------------------------------------
@app.route('/api/submit_review', methods=['POST'])
def submit_review():
    """
    API endpoint to receive review data from the frontend and save it to the database.
    """
    if request.method == 'POST':
        try:
            data = request.get_json()
            
            reviewer_name = data.get('reviewer_name')
            rating = data.get('rating')
            review_text = data.get('review_text')

            if not all([reviewer_name, rating, review_text]):
                return jsonify({'error': 'Missing required fields (Name, Rating, Text)'}), 400

            try:
                rating = int(rating)
                if not 1 <= rating <= 5:
                    raise ValueError
            except ValueError:
                return jsonify({'error': 'Rating must be an integer between 1 and 5'}), 400

            conn = mysql.connection
            cursor = conn.cursor()

            sql = "INSERT INTO reviews (reviewer_name, rating, review_text) VALUES (%s, %s, %s)"
            cursor.execute(sql, (reviewer_name, rating, review_text))

            conn.commit()
            cursor.close()

            return jsonify({'message': 'Review submitted successfully!'}), 201

        except Exception as e:
            print(f"An error occurred: {e}")
            return jsonify({'error': f'An internal server error occurred: {str(e)}'}), 500

if __name__ == '__main__':
    # Ensure your Flask server is running on the expected port (5000)
    app.run(debug=True, port=5000)