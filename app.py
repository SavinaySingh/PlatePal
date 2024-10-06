from flask import Flask, render_template, request
import pickle
from collections import Counter
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from rapidfuzz import fuzz
from restaurant_product_matching import RestaurantProductMatcher

app = Flask(__name__)

matcher = RestaurantProductMatcher('./pickle_files/restaurant_ingredients.pkl', './pickle_files/product_catalogue.pkl')
matcher.calculate_cosine_similarity()
matcher.fuzzy_cosine_similarity()
matcher.compute_combined_scores()


@app.route('/', methods=['GET', 'POST'])
def index():
    recommendations = None
    if request.method == 'POST':
        restaurant_name = request.form['restaurant_name']
        recommendations = matcher.get_top_recommendations(restaurant_name)
    
        # Display results
        if isinstance(recommendations, str):
            print(recommendations)
        else:
            for recommendation in recommendations:
                print(f"Product: {recommendation['Product']}")
                print(f"Score: {recommendation['Score']:.2f}")
                print(f"Ingredient Connection: {', '.join(recommendation['Ingredient Connection'])}")
                print("\n---\n")
    return render_template('index.html', recommendations=recommendations)

if __name__ == '__main__':
    app.run(debug=True)