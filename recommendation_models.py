"""
Recommendation models for recipe recommendation system
"""
import numpy as np
import pandas as pd
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import csr_matrix, vstack, hstack
import pickle
from pathlib import Path

class CollaborativeFilteringModel:
    """SVD-based collaborative filtering"""
    
    def __init__(self, n_factors=50):
        self.n_factors = n_factors
        self.model = TruncatedSVD(n_components=n_factors, random_state=42)
        self.user_factors = None
        self.item_factors = None
        self.user_idx_to_id = None
        self.item_idx_to_id = None
        self.user_id_to_idx = None
        self.item_id_to_idx = None
        self.global_mean = 0
        
    def fit(self, sparse_matrix, id_mappings):
        """Fit the SVD model on sparse matrix"""
        print(f"Training SVD with {self.n_factors} factors on sparse matrix...")
        
        # Store mappings
        self.user_idx_to_id = id_mappings['idx_to_user']
        self.item_idx_to_id = id_mappings['idx_to_recipe']
        self.user_id_to_idx = id_mappings['user_to_idx']
        self.item_id_to_idx = id_mappings['recipe_to_idx']
        
        # Calculate global mean (only non-zero values)
        self.global_mean = sparse_matrix.data.mean()
        
        # Fit SVD on sparse matrix
        self.user_factors = self.model.fit_transform(sparse_matrix)
        self.item_factors = self.model.components_.T
        
        print(f"SVD training completed. User factors: {self.user_factors.shape}, Item factors: {self.item_factors.shape}")
        return self
    
    def predict(self, user_id, item_id):
        """Predict rating for user-item pair"""
        try:
            user_idx = self.user_id_to_idx[user_id]
            item_idx = self.item_id_to_idx[item_id]
            
            prediction = (
                self.global_mean + 
                np.dot(self.user_factors[user_idx], self.item_factors[item_idx])
            )
            
            return np.clip(prediction, 1, 5)
        except (KeyError, IndexError):
            return self.global_mean
    
    def recommend_items(self, user_id, n_recommendations=10, exclude_items=None):
        """Get top N recommendations for a user"""
        try:
            user_idx = self.user_id_to_idx[user_id]
        except KeyError:
            # Cold start - return popular items
            return []
        
        # Calculate predictions for all items
        user_vector = self.user_factors[user_idx]
        predictions = self.global_mean + np.dot(self.item_factors, user_vector)
        
        # Create recommendation list
        recommendations = []
        for idx, score in enumerate(predictions):
            item_id = self.item_idx_to_id[idx]
            if exclude_items and item_id in exclude_items:
                continue
            recommendations.append((item_id, score))
        
        # Sort and return top N
        recommendations.sort(key=lambda x: x[1], reverse=True)
        return recommendations[:n_recommendations]


class ContentBasedModel:
    """Content-based filtering using recipe features"""
    
    def __init__(self):
        # Don't use lambda in tokenizer - use a regular function or None
        self.tfidf_ingredients = TfidfVectorizer(max_features=1000, lowercase=True)
        self.tfidf_tags = TfidfVectorizer(max_features=500, lowercase=True)
        self.recipe_features = None
        self.feature_matrix = None
        self.recipe_ids = None
        
    def _tokenize_list(self, x):
        """Tokenizer function for TfidfVectorizer"""
        if isinstance(x, list):
            return [str(item).lower() for item in x]
        return [str(x).lower()]
        
    def fit(self, recipes_df):
        """Build content-based model"""
        print("Building content-based model...")
        
        self.recipe_ids = recipes_df['id'].tolist()
        
        # Process ingredients - convert list to string for TfidfVectorizer
        ingredients_text = recipes_df['ingredients'].apply(lambda x: ' '.join([str(i).lower() for i in x]))
        ingredients_features = self.tfidf_ingredients.fit_transform(ingredients_text)
        
        # Process tags - convert list to string for TfidfVectorizer
        tags_text = recipes_df['tags'].apply(lambda x: ' '.join([str(t).lower() for t in x]))
        tags_features = self.tfidf_tags.fit_transform(tags_text)
        
        # Numerical features
        numerical_features = recipes_df[[
            'n_ingredients', 'n_steps', 'minutes', 
            'health_score', 'calories', 'protein'
        ]].values
        
        # Normalize numerical features
        numerical_features = (numerical_features - numerical_features.mean(axis=0)) / (numerical_features.std(axis=0) + 1e-8)
        
        # Combine all features
        self.feature_matrix = hstack([
            ingredients_features,
            tags_features,
            csr_matrix(numerical_features)
        ])
        
        print(f"Built feature matrix with shape: {self.feature_matrix.shape}")
        return self
    
    def get_similar_items(self, item_id, n_similar=10):
        """Find similar recipes"""
        try:
            item_idx = self.recipe_ids.index(item_id)
        except ValueError:
            return []
        
        # Calculate similarities
        item_vector = self.feature_matrix[item_idx]
        similarities = cosine_similarity(item_vector, self.feature_matrix).flatten()
        
        # Get top similar items
        similar_indices = similarities.argsort()[::-1][1:n_similar+1]  # Exclude self
        
        similar_items = []
        for idx in similar_indices:
            similar_items.append((self.recipe_ids[idx], similarities[idx]))
        
        return similar_items
    
    def recommend_based_on_profile(self, liked_items, n_recommendations=10):
        """Recommend based on user's liked items"""
        if not liked_items:
            return []
        
        # Get indices of liked items
        liked_indices = []
        for item_id in liked_items:
            try:
                idx = self.recipe_ids.index(item_id)
                liked_indices.append(idx)
            except ValueError:
                continue
        
        if not liked_indices:
            return []
        
        # Create user profile as average of liked items
        user_profile = self.feature_matrix[liked_indices].mean(axis=0)
        
        # Convert to numpy array if it's a matrix
        if hasattr(user_profile, 'A1'):
            user_profile = np.asarray(user_profile).reshape(1, -1)
        else:
            user_profile = np.asarray(user_profile).reshape(1, -1)
        
        # Calculate similarities to all items
        similarities = cosine_similarity(user_profile, self.feature_matrix).flatten()
        
        # Get recommendations
        recommendations = []
        for idx, (recipe_id, score) in enumerate(zip(self.recipe_ids, similarities)):
            if recipe_id not in liked_items:
                recommendations.append((recipe_id, score))
        
        recommendations.sort(key=lambda x: x[1], reverse=True)
        return recommendations[:n_recommendations]


class HybridRecommender:
    """Hybrid model combining collaborative and content-based approaches"""
    
    def __init__(self, cf_weight=0.6, cb_weight=0.4):
        self.cf_model = CollaborativeFilteringModel()
        self.cb_model = ContentBasedModel()
        self.cf_weight = cf_weight
        self.cb_weight = cb_weight
        self.recipes_df = None
        self.interactions_df = None
        self.id_mappings = None
        
    def fit(self, recipes_df, interactions_df, sparse_matrix, id_mappings):
        """Train both models"""
        print("Training hybrid recommender...")
        
        self.recipes_df = recipes_df
        self.interactions_df = interactions_df
        self.id_mappings = id_mappings
        
        # Train collaborative filtering on sparse matrix
        self.cf_model.fit(sparse_matrix, id_mappings)
        
        # Train content-based
        self.cb_model.fit(recipes_df)
        
        print("Hybrid recommender training completed")
        return self
    
    def recommend(self, user_id, n_recommendations=10):
        """Get hybrid recommendations"""
        # Get user's interaction history
        user_interactions = self.interactions_df[self.interactions_df['user_id'] == user_id]
        rated_items = set(user_interactions['recipe_id'].tolist())
        liked_items = user_interactions[user_interactions['rating'] >= 4]['recipe_id'].tolist()
        
        # Get collaborative filtering recommendations
        cf_recs = self.cf_model.recommend_items(user_id, n_recommendations * 3, rated_items)
        cf_scores = {item_id: score for item_id, score in cf_recs}
        
        # Get content-based recommendations
        cb_recs = self.cb_model.recommend_based_on_profile(liked_items, n_recommendations * 3)
        cb_scores = {item_id: score for item_id, score in cb_recs}
        
        # Combine scores
        all_items = set(cf_scores.keys()) | set(cb_scores.keys())
        hybrid_scores = {}
        
        for item_id in all_items:
            cf_score = cf_scores.get(item_id, 0)
            cb_score = cb_scores.get(item_id, 0)
            
            # Normalize scores
            cf_score_norm = cf_score / 5.0 if cf_score > 0 else 0
            cb_score_norm = cb_score if cb_score > 0 else 0
            
            # Weighted combination
            hybrid_score = (self.cf_weight * cf_score_norm + self.cb_weight * cb_score_norm)
            
            if item_id not in rated_items:
                hybrid_scores[item_id] = hybrid_score
        
        # Sort and return top N
        recommendations = sorted(hybrid_scores.items(), key=lambda x: x[1], reverse=True)
        return recommendations[:n_recommendations]
    
    def save_model(self, path="models"):
        """Save trained models"""
        model_path = Path(path)
        model_path.mkdir(exist_ok=True)
        
        # Save components separately to avoid pickle issues
        import joblib
        
        # Save the main model data
        model_data = {
            'cf_weight': self.cf_weight,
            'cb_weight': self.cb_weight,
            'id_mappings': self.id_mappings
        }
        
        with open(model_path / "model_config.pkl", 'wb') as f:
            pickle.dump(model_data, f)
        
        # Save CF model
        cf_data = {
            'user_factors': self.cf_model.user_factors,
            'item_factors': self.cf_model.item_factors,
            'user_idx_to_id': self.cf_model.user_idx_to_id,
            'item_idx_to_id': self.cf_model.item_idx_to_id,
            'user_id_to_idx': self.cf_model.user_id_to_idx,
            'item_id_to_idx': self.cf_model.item_id_to_idx,
            'global_mean': self.cf_model.global_mean,
            'n_factors': self.cf_model.n_factors
        }
        
        with open(model_path / "cf_model.pkl", 'wb') as f:
            pickle.dump(cf_data, f)
        
        # Save CB model components
        cb_data = {
            'recipe_ids': self.cb_model.recipe_ids,
            'feature_matrix': self.cb_model.feature_matrix
        }
        
        with open(model_path / "cb_model.pkl", 'wb') as f:
            pickle.dump(cb_data, f)
        
        # Save TfidfVectorizers separately using joblib
        joblib.dump(self.cb_model.tfidf_ingredients, model_path / "tfidf_ingredients.pkl")
        joblib.dump(self.cb_model.tfidf_tags, model_path / "tfidf_tags.pkl")
        
        print(f"Model saved to {model_path}")
    
    @classmethod
    def load_model(cls, path="models"):
        """Load trained model"""
        import joblib
        model_path = Path(path)
        
        # Load config
        with open(model_path / "model_config.pkl", 'rb') as f:
            model_data = pickle.load(f)
        
        # Create recommender
        recommender = cls()
        recommender.cf_weight = model_data['cf_weight']
        recommender.cb_weight = model_data['cb_weight']
        recommender.id_mappings = model_data.get('id_mappings')
        
        # Load CF model
        with open(model_path / "cf_model.pkl", 'rb') as f:
            cf_data = pickle.load(f)
        
        recommender.cf_model.user_factors = cf_data['user_factors']
        recommender.cf_model.item_factors = cf_data['item_factors']
        recommender.cf_model.user_idx_to_id = cf_data['user_idx_to_id']
        recommender.cf_model.item_idx_to_id = cf_data['item_idx_to_id']
        recommender.cf_model.user_id_to_idx = cf_data['user_id_to_idx']
        recommender.cf_model.item_id_to_idx = cf_data['item_id_to_idx']
        recommender.cf_model.global_mean = cf_data['global_mean']
        recommender.cf_model.n_factors = cf_data['n_factors']
        
        # Load CB model
        with open(model_path / "cb_model.pkl", 'rb') as f:
            cb_data = pickle.load(f)
        
        recommender.cb_model.recipe_ids = cb_data['recipe_ids']
        recommender.cb_model.feature_matrix = cb_data['feature_matrix']
        
        # Load TfidfVectorizers
        recommender.cb_model.tfidf_ingredients = joblib.load(model_path / "tfidf_ingredients.pkl")
        recommender.cb_model.tfidf_tags = joblib.load(model_path / "tfidf_tags.pkl")
        
        return recommender