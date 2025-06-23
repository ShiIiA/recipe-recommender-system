"""
Data preprocessing module for recipe recommendation system - Fixed version
"""
import pandas as pd
import numpy as np
import ast
import json
from datetime import datetime
import pickle
from pathlib import Path
from scipy.sparse import csr_matrix, save_npz
from sklearn.preprocessing import LabelEncoder

class DataPreprocessor:
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.recipes_df = None
        self.interactions_df = None
        self.users_df = None
        self.user_encoder = LabelEncoder()
        self.recipe_encoder = LabelEncoder()
        
    def load_data(self, max_recipes=20000, min_interactions_per_user=5):
        """Load all data files with constraints"""
        print("Loading recipe data...")
        # Try multiple paths
        recipe_paths = [
            self.data_dir / "raw" / "RAW_recipes.csv",
            self.data_dir / "RAW_recipes.csv",
            "RAW_recipes.csv"
        ]
        
        for path in recipe_paths:
            if Path(path).exists():
                self.recipes_df = pd.read_csv(path, nrows=max_recipes)
                print(f"Loaded {len(self.recipes_df)} recipes from {path}")
                break
        
        print("Loading interaction data...")
        interaction_paths = [
            self.data_dir / "raw" / "RAW_interactions.csv",
            self.data_dir / "RAW_interactions.csv",
            "RAW_interactions.csv"
        ]
        
        for path in interaction_paths:
            if Path(path).exists():
                # Load all interactions first
                temp_interactions = pd.read_csv(path)
                
                # Filter to only include recipes we have
                recipe_ids = set(self.recipes_df['id'].values)
                temp_interactions = temp_interactions[temp_interactions['recipe_id'].isin(recipe_ids)]
                
                # Filter users with minimum interactions
                user_counts = temp_interactions['user_id'].value_counts()
                active_users = user_counts[user_counts >= min_interactions_per_user].index
                
                # Limit to top active users to manage matrix size
                top_users = user_counts.head(10000).index  # Top 10k users
                self.interactions_df = temp_interactions[temp_interactions['user_id'].isin(top_users)]
                
                print(f"Loaded {len(self.interactions_df)} interactions from {(self.interactions_df['user_id'].nunique())} users")
                break
    
    def parse_list_column(self, value):
        """Safely parse string representation of lists"""
        if pd.isna(value) or value == '':
            return []
        try:
            return ast.literal_eval(value)
        except:
            return []
    
    def preprocess_recipes(self):
        """Clean and process recipe data"""
        print("Preprocessing recipes...")
        
        # Parse list columns
        self.recipes_df['ingredients'] = self.recipes_df['ingredients'].apply(self.parse_list_column)
        self.recipes_df['tags'] = self.recipes_df['tags'].apply(self.parse_list_column)
        self.recipes_df['steps'] = self.recipes_df['steps'].apply(self.parse_list_column)
        self.recipes_df['nutrition'] = self.recipes_df['nutrition'].apply(self.parse_list_column)
        
        # Extract nutrition values
        nutrition_cols = ['calories', 'total_fat', 'sugar', 'sodium', 'protein', 'saturated_fat', 'carbohydrates']
        for i, col in enumerate(nutrition_cols):
            self.recipes_df[col] = self.recipes_df['nutrition'].apply(
                lambda x: float(x[i]) if len(x) > i else 0
            )
        
        # Create features
        self.recipes_df['n_ingredients'] = self.recipes_df['ingredients'].apply(len)
        self.recipes_df['n_steps'] = self.recipes_df['steps'].apply(len)
        
        # Categorize cooking time
        self.recipes_df['time_category'] = pd.cut(
            self.recipes_df['minutes'],
            bins=[0, 20, 45, 90, 1440, float('inf')],
            labels=['very_quick', 'quick', 'medium', 'long', 'very_long']
        )
        
        # Extract main categories from tags
        self.recipes_df['is_vegetarian'] = self.recipes_df['tags'].apply(
            lambda tags: any('vegetarian' in str(tag).lower() for tag in tags)
        )
        self.recipes_df['is_vegan'] = self.recipes_df['tags'].apply(
            lambda tags: any('vegan' in str(tag).lower() for tag in tags)
        )
        self.recipes_df['is_healthy'] = self.recipes_df['tags'].apply(
            lambda tags: any(word in str(tags).lower() for word in ['healthy', 'low-fat', 'low-calorie'])
        )
        
        # Calculate health score (0-100)
        self.recipes_df['health_score'] = self._calculate_health_score()
        
        # Remove invalid recipes
        self.recipes_df = self.recipes_df[
            (self.recipes_df['n_ingredients'] > 0) & 
            (self.recipes_df['n_steps'] > 0) &
            (self.recipes_df['minutes'] > 0) &
            (self.recipes_df['minutes'] < 1440)  # Less than 24 hours
        ]
        
        # Ensure we only keep recipes that have interactions
        interacted_recipes = set(self.interactions_df['recipe_id'].unique())
        self.recipes_df = self.recipes_df[self.recipes_df['id'].isin(interacted_recipes)]
        
        print(f"Preprocessed {len(self.recipes_df)} valid recipes")
        return self.recipes_df
    
    def _calculate_health_score(self):
        """Calculate health score based on nutrition info"""
        scores = pd.DataFrame()
        
        # Lower calories is better (normalized)
        scores['calorie_score'] = 100 - (self.recipes_df['calories'].clip(0, 1000) / 10)
        
        # Lower fat is better
        scores['fat_score'] = 100 - self.recipes_df['total_fat'].clip(0, 100)
        
        # Lower sugar is better
        scores['sugar_score'] = 100 - self.recipes_df['sugar'].clip(0, 100)
        
        # Higher protein is better
        scores['protein_score'] = self.recipes_df['protein'].clip(0, 100)
        
        # Calculate weighted average
        health_score = (
            scores['calorie_score'] * 0.3 +
            scores['fat_score'] * 0.2 +
            scores['sugar_score'] * 0.2 +
            scores['protein_score'] * 0.3
        )
        
        return health_score.clip(0, 100)
    
    def preprocess_interactions(self):
        """Clean and process interaction data"""
        print("Preprocessing interactions...")
        
        # Convert date to datetime
        self.interactions_df['date'] = pd.to_datetime(self.interactions_df['date'])
        
        # Remove invalid ratings
        self.interactions_df = self.interactions_df[
            (self.interactions_df['rating'] >= 1) & 
            (self.interactions_df['rating'] <= 5)
        ]
        
        # Only keep interactions for recipes we have
        valid_recipes = set(self.recipes_df['id'].values)
        self.interactions_df = self.interactions_df[
            self.interactions_df['recipe_id'].isin(valid_recipes)
        ]
        
        # Add time-based features
        self.interactions_df['year'] = self.interactions_df['date'].dt.year
        self.interactions_df['month'] = self.interactions_df['date'].dt.month
        self.interactions_df['season'] = self.interactions_df['month'].apply(self._get_season)
        
        print(f"Preprocessed {len(self.interactions_df)} valid interactions")
        print(f"Users: {self.interactions_df['user_id'].nunique()}")
        print(f"Recipes: {self.interactions_df['recipe_id'].nunique()}")
        
        return self.interactions_df
    
    def _get_season(self, month):
        """Get season from month"""
        if month in [3, 4, 5]:
            return 'spring'
        elif month in [6, 7, 8]:
            return 'summer'
        elif month in [9, 10, 11]:
            return 'autumn'
        else:
            return 'winter'
    
    def create_user_item_matrix(self):
        """Create sparse user-item interaction matrix"""
        print("Creating sparse user-item matrix...")
        
        # Encode user and recipe IDs to continuous integers
        self.interactions_df['user_idx'] = self.user_encoder.fit_transform(self.interactions_df['user_id'])
        self.interactions_df['recipe_idx'] = self.recipe_encoder.fit_transform(self.interactions_df['recipe_id'])
        
        # Create sparse matrix
        n_users = self.interactions_df['user_idx'].nunique()
        n_recipes = self.interactions_df['recipe_idx'].nunique()
        
        print(f"Matrix dimensions: {n_users} users x {n_recipes} recipes")
        
        # Create sparse matrix using COO format
        sparse_matrix = csr_matrix(
            (self.interactions_df['rating'].values,
             (self.interactions_df['user_idx'].values,
              self.interactions_df['recipe_idx'].values)),
            shape=(n_users, n_recipes)
        )
        
        print(f"Created sparse matrix with {sparse_matrix.nnz} non-zero entries")
        print(f"Sparsity: {1 - sparse_matrix.nnz / (n_users * n_recipes):.2%}")
        
        return sparse_matrix
    
    def save_processed_data(self, output_dir="processed_data"):
        """Save processed data"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Save as pickle for faster loading
        self.recipes_df.to_pickle(output_path / "recipes_processed.pkl")
        self.interactions_df.to_pickle(output_path / "interactions_processed.pkl")
        
        # Save encoders
        with open(output_path / "user_encoder.pkl", 'wb') as f:
            pickle.dump(self.user_encoder, f)
        with open(output_path / "recipe_encoder.pkl", 'wb') as f:
            pickle.dump(self.recipe_encoder, f)
        
        # Save ID mappings
        user_mapping = dict(zip(self.user_encoder.classes_, self.user_encoder.transform(self.user_encoder.classes_)))
        recipe_mapping = dict(zip(self.recipe_encoder.classes_, self.recipe_encoder.transform(self.recipe_encoder.classes_)))
        
        with open(output_path / "id_mappings.pkl", 'wb') as f:
            pickle.dump({
                'user_to_idx': user_mapping,
                'recipe_to_idx': recipe_mapping,
                'idx_to_user': {v: k for k, v in user_mapping.items()},
                'idx_to_recipe': {v: k for k, v in recipe_mapping.items()}
            }, f)
        
        # Save recipe features for content-based filtering
        recipe_features = self._extract_recipe_features()
        with open(output_path / "recipe_features.pkl", 'wb') as f:
            pickle.dump(recipe_features, f)
        
        print(f"Saved processed data to {output_path}")
    
    def _extract_recipe_features(self):
        """Extract features for content-based filtering"""
        features = {}
        
        for idx, row in self.recipes_df.iterrows():
            features[row['id']] = {
                'ingredients': row['ingredients'],
                'tags': row['tags'],
                'time_category': row['time_category'],
                'health_score': row['health_score'],
                'n_ingredients': row['n_ingredients'],
                'n_steps': row['n_steps'],
                'is_vegetarian': row['is_vegetarian'],
                'is_vegan': row['is_vegan'],
                'is_healthy': row['is_healthy'],
                'calories': row['calories'],
                'protein': row['protein']
            }
        
        return features

# Usage
if __name__ == "__main__":
    preprocessor = DataPreprocessor()
    preprocessor.load_data(max_recipes=20000, min_interactions_per_user=5)
    preprocessor.preprocess_recipes()
    preprocessor.preprocess_interactions()
    matrix = preprocessor.create_user_item_matrix()
    preprocessor.save_processed_data()