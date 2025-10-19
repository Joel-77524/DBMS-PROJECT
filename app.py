from flask import Flask, request, jsonify
from flask_mysqldb import MySQL
from datetime import datetime
from flask_cors import CORS 

app = Flask(__name__)

# --------------------------------------------------------------------------
# CRITICAL FIX: EXPLICIT CORS CONFIGURATION (Kept from original)
# --------------------------------------------------------------------------
CORS(app, resources={r"/api/*": {"origins": [
    "http://127.0.0.1:8080", 
    "http://localhost:8080"
],
"methods": ["GET", "POST", "OPTIONS"],
"allow_headers": ["Content-Type", "Authorization"]
}})

# MySQL Configuration (Assuming the same as your original)
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'Root@2025' # <-- CHANGE THIS to your actual password
app.config['MYSQL_DB'] = 'cinereview_db'
app.config['MYSQL_CURSORCLASS'] = 'DictCursor' 

mysql = MySQL(app)

# --------------------------------------------------------------------------
# FETCH REVIEWS FOR A SPECIFIC MOVIE (Read operation)
# --------------------------------------------------------------------------
# The route now accepts a movie_title as a URL parameter
@app.route('/api/get_reviews/<movie_title>', methods=['GET'])
def get_reviews(movie_title):
    """
    API endpoint to fetch all existing reviews for a specific movie.
    """
    try:
        conn = mysql.connection
        cursor = conn.cursor()
        
        # 💡 UPDATED SQL: Filter by movie_title
        sql = "SELECT reviewer_name, rating, review_text, created_at FROM reviews WHERE movie_title = %s ORDER BY created_at DESC"
        cursor.execute(sql, (movie_title,)) # Pass the movie_title as a parameter
        
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
# SUBMIT REVIEW FOR A SPECIFIC MOVIE (Create operation)
# --------------------------------------------------------------------------
# The route now accepts a movie_title as a URL parameter
@app.route('/api/submit_review/<movie_title>', methods=['POST'])
def submit_review(movie_title):
    """
    API endpoint to receive review data and save it to the database, including movie_title.
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

            # 💡 UPDATED SQL: Insert movie_title along with the review data
            sql = "INSERT INTO reviews (movie_title, reviewer_name, rating, review_text) VALUES (%s, %s, %s, %s)"
            # Pass all four values to the execute method
            cursor.execute(sql, (movie_title, reviewer_name, rating, review_text))

            conn.commit()
            cursor.close()

            return jsonify({'message': f'Review submitted successfully for {movie_title}!'}), 201

        except Exception as e:
            print(f"An error occurred: {e}")
            return jsonify({'error': f'An internal server error occurred: {str(e)}'}), 500

if __name__ == '__main__':
    # Ensure your Flask server is running on the expected port (5000)
    app.run(debug=True, port=5000)