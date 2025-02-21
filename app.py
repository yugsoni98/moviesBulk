from flask import Flask, jsonify, request, render_template
from pymongo import MongoClient
import pandas as pd
import io
import base64
import json
from datetime import datetime
import ast
app = Flask(__name__)

# MongoDB connection
MONGO_URI = "mongodb://localhost:27017/"
client = MongoClient(MONGO_URI)
db = client.flaskproject
collection = db.moviesData



def parse_languages(x):
    try:
        return [lang.strip() for lang in ast.literal_eval(x)]
    except Exception as e:
        return []

@app.route('/')
def home():
    return render_template("index.html")

@app.route('/moviesCRM')
def movies_crm():
    return render_template('moviesCRM.html')

@app.route('/upload', methods=['POST'])
def upload_file():
    try:

        data = request.json
        if not data or 'filename' not in data or 'content' not in data:
            return jsonify({"error": "Invalid input"}), 400

        file_content = base64.b64decode(data['content'])
        
        try:
            df = pd.read_csv(io.BytesIO(file_content))
        except Exception as e:
            return jsonify({"error": f"Invalid file: {str(e)}"}), 400
        
        required_columns = [
            "budget", "homepage", "original_language", "original_title", "overview",
            "release_date", "revenue", "runtime", "status", "title", "vote_average",
            "vote_count", "production_company_id", "genre_id", "languages"
        ]
        
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            return jsonify({"error": f"Missing Data: {missing_columns}"}), 400
        
        df["release_date"] = pd.to_datetime(df["release_date"], errors="coerce")  
        df["release_date"] = df["release_date"].dt.strftime("%Y-%m-%d")  
        
        df["languages"] = df["languages"].fillna("[]").apply(parse_languages)

        df = df.where(pd.notnull(df), None)
        movies = df.to_dict(orient="records")

        if movies:
            collection.insert_many(movies)

        return jsonify({"message": "File uploaded successfully", "records_inserted": len(movies)})
    
    except Exception as e:
        return jsonify({"error": str(e), "message": "Something went wrong."}), 500
    
@app.route('/movies', methods=['GET'])
def get_movies():
    try:
        page = int(request.args.get('page', 1))
        limit = int(request.args.get('limit', 10))
        skip = (page - 1) * limit

        year = request.args.get('year')  
        language = request.args.get('language')  

        sort_by = request.args.get('sort_by', 'release_date')  
        order = request.args.get('order', 'desc') 

        query = {}

        if year:
            query["release_date"] = {
                "$regex": f"^{year}-" 
            }
        if language:
            query["languages"] = {"$regex": language, "$options": "i"}

        sort_field = "release_date" if sort_by == "release_date" else "vote_average"
        sort_order = -1 if order == "desc" else 1 
        print("query", query)

        movies = list(
            collection.find(query, {"_id": 0})  
            .sort(sort_field, sort_order)
            .skip(skip)
            .limit(limit)
        )

        for movie in movies:
            if isinstance(movie.get("languages"), str): 
                movie["languages"] = eval(movie["languages"]) if "[" in movie["languages"] else [movie["languages"]]
            print(movie)
            for key, value in movie.items():
                if isinstance(value, list):
                    continue
                if pd.isna(value):
                    movie[key] = None




        total_records = collection.count_documents(query)
        print(f'Total Records: {total_records}')  

        return jsonify({
            "total_records": total_records,
            "current_page": page,
            "total_pages": (total_records + limit - 1) // limit,
            "movies": movies
        })

    except Exception as e:
        print(f'Error: {str(e)}')  
        return jsonify({"error": str(e), "message": "Something went wrong."}), 500


if __name__ == '__main__':
    app.run(debug=True)