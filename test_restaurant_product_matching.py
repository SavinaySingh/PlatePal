import unittest
from unittest.mock import patch, MagicMock
import numpy as np
from restaurant_product_matching import RestaurantProductMatcher
import pickle
from collections import Counter

class TestRestaurantProductMatcher(unittest.TestCase):

    def setUp(self):
        # Sample data for testing
        self.mock_restaurant_ingredients = {
            'Restaurant A': ['chicken', 'lettuce', 'tomato'],
            'Restaurant B': ['beef', 'cheese', 'bread']
        }
        
        self.mock_product_catalogue = ['Chicken Salad', 'Beef Burger', 'Lettuce Wrap', 'Tomato Soup', 'Cheese Sandwich']
        
        # Save mock data to pickle files
        with open('mock_restaurant_ingredients.pkl', 'wb') as f:
            pickle.dump(self.mock_restaurant_ingredients, f)
        with open('mock_product_catalogue.pkl', 'wb') as f:
            pickle.dump(self.mock_product_catalogue, f)
        
        # Initialize the matcher with mock data
        self.matcher = RestaurantProductMatcher('mock_restaurant_ingredients.pkl', 'mock_product_catalogue.pkl')

    def test_fuzzy_match_score(self):
        score = self.matcher.fuzzy_match_score('chicken', 'Chicken Salad')
        self.assertGreater(score, 0.8, "Fuzzy match score should be high for similar strings")
        
        score = self.matcher.fuzzy_match_score('beef', 'Chicken Salad')
        self.assertLess(score, 0.5, "Fuzzy match score should be low for dissimilar strings")

    def test_calculate_cosine_similarity(self):
        self.matcher.calculate_cosine_similarity()
        self.assertIn('Restaurant A', self.matcher.cosine_similarity_scores)
        self.assertIn('Restaurant B', self.matcher.cosine_similarity_scores)
        self.assertEqual(len(self.matcher.cosine_similarity_scores['Restaurant A']), len(self.mock_product_catalogue), "Cosine similarity scores should match the product catalogue length")

    def test_fuzzy_cosine_similarity(self):
        self.matcher.fuzzy_cosine_similarity()
        self.assertIn('Restaurant A', self.matcher.fuzzy_similarity_scores)
        self.assertIn('Restaurant B', self.matcher.fuzzy_similarity_scores)
        self.assertEqual(len(self.matcher.fuzzy_similarity_scores['Restaurant A']), len(self.mock_product_catalogue), "Fuzzy similarity scores should match the product catalogue length")

    def test_compute_final_score(self):
        freq = Counter(self.mock_restaurant_ingredients['Restaurant A'])
        cosine_score = 0.7
        fuzzy_score = 0.9
        final_score = self.matcher.compute_final_score('Restaurant A', 'Chicken Salad', freq, cosine_score, fuzzy_score)
        self.assertGreater(final_score, 0, "Final score should be a positive value")

    def test_get_top_recommendations(self):
        self.matcher.calculate_cosine_similarity()
        self.matcher.fuzzy_cosine_similarity()
        self.matcher.compute_combined_scores()
        
        recommendations = self.matcher.get_top_recommendations('Restaurant A', top_n=2)
        self.assertIsInstance(recommendations, list, "Recommendations should be a list")
        self.assertGreater(len(recommendations), 0, "There should be recommendations for Restaurant A")

    def tearDown(self):
        import osa
        # Clean up mock files
        os.remove('mock_restaurant_ingredients.pkl')
        os.remove('mock_product_catalogue.pkl')

if __name__ == '__main__':
    unittest.main()