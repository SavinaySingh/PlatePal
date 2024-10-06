import pickle
from collections import Counter
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from rapidfuzz import fuzz

class RestaurantProductMatcher:
    def __init__(self, restaurant_ingredients_path, product_catalogue_path):
        # Load restaurant-ingredient matching
        self.restaurant_ingredients = pickle.load(open(restaurant_ingredients_path, 'rb'))
        # Load Product Catalogue
        self.product_catalogue = pickle.load(open(product_catalogue_path, 'rb'))
        # Initialize scoring weights
        self.weights = {
            'freq': 0.4,    # Weight for frequency score
            'cosine': 0.4,  # Weight for cosine similarity score
            'fuzzy': 0.2    # Weight for fuzzy match score
        }
        self.cosine_similarity_scores = {}
        self.fuzzy_similarity_scores = {}
        self.combined_similarity_scores = {}

    # Function to compute fuzzy match score between two sets of strings
    @staticmethod
    def fuzzy_match_score(ingredient, category):
        return fuzz.partial_ratio(ingredient.lower(), category.lower()) / 100  # Normalize to 0-1

    # Convert restaurant ingredients and categories into a TF-IDF vector space
    def calculate_cosine_similarity(self):
        vectorizer = TfidfVectorizer().fit(self.product_catalogue + list(ingredient for rest in self.restaurant_ingredients.values() for ingredient in rest))

        # Prepare the catalogue vectors
        catalogue_vectors = vectorizer.transform(self.product_catalogue)

        for rest_name, ingredients in self.restaurant_ingredients.items():
            ingredient_text = ' '.join(ingredients)
            rest_vector = vectorizer.transform([ingredient_text])

            # Calculate cosine similarity
            scores = cosine_similarity(rest_vector, catalogue_vectors)[0]
            self.cosine_similarity_scores[rest_name] = dict(zip(self.product_catalogue, scores))

    # Combine fuzzy match with cosine similarity
    def fuzzy_cosine_similarity(self):
        for rest_name, ingredients in self.restaurant_ingredients.items():
            self.fuzzy_similarity_scores[rest_name] = {}
            for category in self.product_catalogue:
                # For each ingredient in the restaurant, find its best fuzzy match in the category
                fuzzy_scores = [self.fuzzy_match_score(ingredient, category) for ingredient in ingredients]
                # Calculate a weighted similarity score using fuzzy matching
                avg_fuzzy_score = np.mean(fuzzy_scores) if fuzzy_scores else 0
                self.fuzzy_similarity_scores[rest_name][category] = avg_fuzzy_score

    # Function to compute final score based on frequency, cosine, and fuzzy scores
    def compute_final_score(self, restaurant, category, freq, cosine_score, fuzzy_score):
        freq_score = freq.get(category, 0) / sum(freq.values()) if sum(freq.values()) > 0 else 0  # Normalize frequency score
        return (self.weights['freq'] * freq_score + 
                self.weights['cosine'] * cosine_score + 
                self.weights['fuzzy'] * fuzzy_score)

    # Method to compute combined similarity scores
    def compute_combined_scores(self):
        for restaurant in self.restaurant_ingredients:
            self.combined_similarity_scores[restaurant] = {}
            # Get the frequency counts for the current restaurant
            freq = Counter(self.restaurant_ingredients[restaurant])
            
            for category in self.product_catalogue:
                cosine_score = self.cosine_similarity_scores[restaurant].get(category, 0)
                fuzzy_score = self.fuzzy_similarity_scores[restaurant].get(category, 0)

                # Compute final score considering frequency, cosine, and fuzzy scores
                final_score = self.compute_final_score(restaurant, category, freq, cosine_score, fuzzy_score)
                
                self.combined_similarity_scores[restaurant][category] = final_score

    def get_top_recommendations(self, restaurant_name, top_n=10):
        if restaurant_name not in self.combined_similarity_scores:
            return f"No data available for restaurant: {restaurant_name}"

        recommendations = self.combined_similarity_scores[restaurant_name]
        sorted_recommendations = sorted(recommendations.items(), key=lambda x: -x[1])

        # Prepare output with explanations
        output = []
        for category, score in sorted_recommendations[:top_n]:
            # Generate explanations
            ingredient_connection = self.get_ingredient_connections(restaurant_name, category)
            output.append({
                'Product': category,
                'Score': score,
                'Ingredient Connection': ingredient_connection
            })

        return output

    def get_ingredient_connections(self, restaurant_name, category):
        # Fetch the ingredients for the restaurant
        ingredients = self.restaurant_ingredients[restaurant_name]
        connections = []

        # Find which ingredients connect to the category
        for ingredient in ingredients:
            if self.fuzzy_match_score(ingredient, category) > 0.8:  # You can adjust the threshold
                connections.append(ingredient)

        return connections


# Usage
if __name__ == "__main__":
    matcher = RestaurantProductMatcher('./pickle_files/restaurant_ingredients.pkl', './pickle_files/product_catalogue.pkl')
    
    # Step 1: Calculate cosine similarity
    matcher.calculate_cosine_similarity()
    
    # Step 2: Fuzzy matching scores
    matcher.fuzzy_cosine_similarity()
    
    # Step 3: Combine similarity scores
    matcher.compute_combined_scores()
    
    # Get restaurant name from user input
    restaurant_name = input("Enter the restaurant name for product recommendations: ")
    
    # Get top recommendations
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
            
