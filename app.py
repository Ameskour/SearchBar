from flask import Flask, render_template, request, jsonify
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
import mysql.connector

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    # Establish a connection to the MySQL database
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='espaceo_db_master'
    )

    # Create a cursor object to interact with the database
    cursor = connection.cursor()

    # Define the SQL statement
    query = "SELECT agency_name ,city FROM agenciess"
 
    # Execute the SQL statement
    cursor.execute(query)

    # Fetch all the search results
    search_results = cursor.fetchall()

    # Close the cursor and database connection
    cursor.close()
    connection.close()

    # Perform fuzzy search using the search query (case-insensitive)
    if request.method == 'POST':
        search_query = request.form['search']
        processed_results = process.extract(search_query.lower(), search_results, scorer=fuzz.token_set_ratio, limit=515)
        search_results = [(result, score) for result, score in processed_results if score >= 70]

    # Pagination variables
    results_per_page = 10
    total_results = len(search_results)
    total_pages = (total_results - 1) // results_per_page + 1
    page = request.args.get('page', default=1, type=int)
    start_index = (page - 1) * results_per_page
    end_index = start_index + results_per_page

    # Get the paginated search results
    paginated_results = search_results[start_index:end_index]

    if request.method == 'POST':
        return render_template('search.html', search_results=paginated_results, total_pages=total_pages, current_page=page)
    elif request.method == 'GET':
        return render_template('search.html', search_results=paginated_results, total_pages=total_pages, current_page=page)
    else:
        return "Method not allowed."


@app.route('/suggest', methods=['POST'])
def suggest():
    search_query = request.form['query']

    # Establish a connection to the MySQL database
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='',
        database='espaceo_db_master'
    )

    # Create a cursor object to interact with the database
    cursor = connection.cursor()

    # Define the SQL statement
    query = "SELECT agency_name , city FROM agenciess"

    # Execute the SQL statement
    cursor.execute(query)

    # Fetch all the agency names
    agency_names = [result[0] for result in cursor.fetchall()]

    # Perform fuzzy search using the search query (case-insensitive)
    suggestions = process.extract(search_query.lower(), agency_names, scorer=fuzz.token_set_ratio, limit=10)

    # Close the cursor and database connection
    cursor.close()
    connection.close()

    return jsonify({'suggestions': [suggestion[0] for suggestion in suggestions]})

if __name__ == '__main__':
    app.run(debug=True)
