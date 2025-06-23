"""
Train the recommendation model with improved evaluation metrics
"""
import pandas as pd
import numpy as np
from pathlib import Path
import sys
sys.path.append('.')

from data_preprocessor import DataPreprocessor
from recommendation_models import HybridRecommender
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, mean_absolute_error
from scipy.sparse import csr_matrix, save_npz
import pickle
import warnings
warnings.filterwarnings('ignore')

def calculate_metrics(actual, predicted):
    """Calculate various error metrics"""
    rmse = np.sqrt(mean_squared_error(actual, predicted))
    mae = mean_absolute_error(actual, predicted)
    return rmse, mae

def calculate_map_at_k(recommendations, relevant_items, k=10):
    """Calculate Mean Average Precision at K"""
    if not relevant_items:
        return 0.0
    
    score = 0.0
    num_hits = 0.0
    
    for i, (item_id, _) in enumerate(recommendations[:k]):
        if item_id in relevant_items:
            num_hits += 1.0
            score += num_hits / (i + 1.0)
    
    return score / min(len(relevant_items), k)

def calculate_precision_at_k(recommendations, relevant_items, k=10):
    """Calculate Precision at K"""
    if not recommendations:
        return 0.0
    
    recommended_items = [item_id for item_id, _ in recommendations[:k]]
    hits = len(set(recommended_items) & set(relevant_items))
    return hits / k

def calculate_recall_at_k(recommendations, relevant_items, k=10):
    """Calculate Recall at K"""
    if not relevant_items:
        return 0.0
    
    recommended_items = [item_id for item_id, _ in recommendations[:k]]
    hits = len(set(recommended_items) & set(relevant_items))
    return hits / len(relevant_items)

def evaluate_model_comprehensive(recommender, test_interactions, train_interactions, id_mappings, k=10):
    """Comprehensive model evaluation"""
    print("\nPerforming comprehensive model evaluation...")
    
    # Get users who have both train and test data
    test_users = set(test_interactions['user_id'].unique())
    train_users = set(train_interactions['user_id'].unique())
    common_users = list(test_users & train_users)
    
    # Also require users to have enough test interactions
    valid_test_users = []
    for user_id in common_users:
        user_test_count = len(test_interactions[test_interactions['user_id'] == user_id])
        if user_test_count >= 2:  # At least 2 test items
            valid_test_users.append(user_id)
    
    print(f"Found {len(valid_test_users)} users with sufficient test data")
    
    # Sample from valid users
    sample_size = min(500, len(valid_test_users))
    sampled_users = np.random.choice(valid_test_users, sample_size, replace=False)
    
    print(f"Evaluating on {sample_size} users...")
    
    # Metrics storage
    rmse_scores = []
    mae_scores = []
    precision_scores = []
    recall_scores = []
    map_scores = []
    
    valid_users = 0
    
    for user_id in sampled_users:
        # Get user's test interactions
        user_test = test_interactions[test_interactions['user_id'] == user_id]
        
        if len(user_test) < 2:  # Need at least 2 test items
            continue
        
        # Get user's training interactions (to exclude from recommendations)
        user_train = train_interactions[train_interactions['user_id'] == user_id]
        trained_items = set(user_train['recipe_id'].values)
        
        # 1. Rating Prediction Evaluation
        actual_ratings = []
        predicted_ratings = []
        
        for _, row in user_test.iterrows():
            actual_rating = row['rating']
            try:
                # Get prediction
                pred_rating = recommender.cf_model.predict(user_id, row['recipe_id'])
                actual_ratings.append(actual_rating)
                predicted_ratings.append(pred_rating)
            except:
                # If prediction fails, use global mean
                actual_ratings.append(actual_rating)
                predicted_ratings.append(recommender.cf_model.global_mean)
        
        if actual_ratings:
            rmse, mae = calculate_metrics(actual_ratings, predicted_ratings)
            rmse_scores.append(rmse)
            mae_scores.append(mae)
        
        # 2. Ranking Evaluation
        # Get items the user liked in test set (4+ stars)
        liked_test_items = set(user_test[user_test['rating'] >= 4]['recipe_id'].values)
        
        if liked_test_items:
            try:
                # Get recommendations (excluding training items)
                recommendations = recommender.recommend(user_id, n_recommendations=k*2)
                
                # Filter out items already seen in training
                filtered_recs = [(item_id, score) for item_id, score in recommendations 
                                if item_id not in trained_items][:k]
                
                if filtered_recs:
                    # Calculate metrics
                    precision = calculate_precision_at_k(filtered_recs, liked_test_items, k)
                    recall = calculate_recall_at_k(filtered_recs, liked_test_items, k)
                    map_score = calculate_map_at_k(filtered_recs, liked_test_items, k)
                    
                    precision_scores.append(precision)
                    recall_scores.append(recall)
                    map_scores.append(map_score)
                    
                    valid_users += 1
            except Exception as e:
                continue
    
    # Calculate average metrics
    results = {
        'rmse': np.mean(rmse_scores) if rmse_scores else 0,
        'mae': np.mean(mae_scores) if mae_scores else 0,
        'precision@k': np.mean(precision_scores) if precision_scores else 0,
        'recall@k': np.mean(recall_scores) if recall_scores else 0,
        'map@k': np.mean(map_scores) if map_scores else 0,
        'valid_users': valid_users,
        'total_evaluated': len(sampled_users)
    }
    
    # Print detailed results
    print("\n" + "="*50)
    print("EVALUATION RESULTS")
    print("="*50)
    print(f"Users evaluated: {valid_users}/{len(sampled_users)}")
    print(f"\nRating Prediction Metrics:")
    print(f"  RMSE: {results['rmse']:.3f}")
    print(f"  MAE:  {results['mae']:.3f}")
    print(f"\nRanking Metrics (k={k}):")
    print(f"  Precision@{k}: {results['precision@k']:.3f}")
    print(f"  Recall@{k}:    {results['recall@k']:.3f}")
    print(f"  MAP@{k}:       {results['map@k']:.3f}")
    print("="*50)
    
    # Sanity checks
    if results['rmse'] < 0.5:
        print("\n⚠️  WARNING: RMSE seems unusually low. Possible data leakage.")
    if results['precision@k'] == 0 and valid_users > 0:
        print("⚠️  WARNING: Precision@k is 0. Check recommendation logic.")
    
    return results

def main():
    print("="*50)
    print("Recipe Recommendation System - Model Training")
    print("="*50)
    
    # Step 1: Preprocess data
    print("\n1. Preprocessing data...")
    preprocessor = DataPreprocessor()
    
    # Load data with constraints
    preprocessor.load_data(
        max_recipes=20000,
        min_interactions_per_user=5
    )
    
    if preprocessor.recipes_df is None or preprocessor.interactions_df is None:
        print("ERROR: Could not load data files!")
        return
    
    recipes_df = preprocessor.preprocess_recipes()
    interactions_df = preprocessor.preprocess_interactions()
    
    # Step 2: Create sparse user-item matrix
    print("\n2. Creating sparse user-item matrix...")
    sparse_matrix = preprocessor.create_user_item_matrix()
    
    # Save processed data
    Path("processed_data").mkdir(exist_ok=True)
    preprocessor.save_processed_data()
    
    # Load ID mappings
    with open("processed_data/id_mappings.pkl", 'rb') as f:
        id_mappings = pickle.load(f)
    
    # Step 3: Split data for evaluation
    print("\n3. Splitting data for evaluation...")
    
    # Better approach: User-based split to ensure users appear in both sets
    # First, find users with enough interactions
    user_interaction_counts = interactions_df['user_id'].value_counts()
    users_with_enough_data = user_interaction_counts[user_interaction_counts >= 10].index
    
    print(f"Users with 10+ interactions: {len(users_with_enough_data)}")
    
    # Filter to only these users
    filtered_interactions = interactions_df[interactions_df['user_id'].isin(users_with_enough_data)]
    
    # For each user, split their interactions 80/20
    train_interactions = []
    test_interactions = []
    
    for user_id in users_with_enough_data:
        user_data = filtered_interactions[filtered_interactions['user_id'] == user_id]
        
        # Shuffle user's interactions
        user_data_shuffled = user_data.sample(frac=1, random_state=42)
        
        # Split 80/20
        split_point = int(len(user_data_shuffled) * 0.8)
        train_interactions.append(user_data_shuffled.iloc[:split_point])
        test_interactions.append(user_data_shuffled.iloc[split_point:])
    
    # Combine all users' data
    train_interactions = pd.concat(train_interactions, ignore_index=True)
    test_interactions = pd.concat(test_interactions, ignore_index=True)
    
    print(f"Train interactions: {len(train_interactions)}")
    print(f"Test interactions: {len(test_interactions)}")
    print(f"Users in train: {train_interactions['user_id'].nunique()}")
    print(f"Users in test: {test_interactions['user_id'].nunique()}")
    
    # Verify overlap
    test_users = set(test_interactions['user_id'].unique())
    train_users = set(train_interactions['user_id'].unique())
    common_users = test_users & train_users
    print(f"Common users between train and test: {len(common_users)}")
    
    # Create training sparse matrix
    train_sparse = csr_matrix(
        (train_interactions['rating'].values,
         (train_interactions['user_idx'].values,
          train_interactions['recipe_idx'].values)),
        shape=sparse_matrix.shape
    )
    
    # Step 4: Train hybrid model
    print("\n4. Training hybrid recommender...")
    recommender = HybridRecommender(cf_weight=0.7, cb_weight=0.3)
    recommender.fit(recipes_df, train_interactions, train_sparse, id_mappings)
    
    # Step 5: Comprehensive evaluation
    print("\n5. Evaluating model...")
    evaluation_results = evaluate_model_comprehensive(
        recommender, 
        test_interactions,
        train_interactions,
        id_mappings,
        k=10
    )
    
    # Step 6: Save everything
    print("\n6. Saving processed data and models...")
    
    recipes_df.to_pickle("processed_data/recipes_full.pkl")
    interactions_df.to_pickle("processed_data/interactions_full.pkl")
    save_npz("processed_data/user_item_sparse.npz", sparse_matrix)
    
    # Save evaluation results
    with open("processed_data/evaluation_results.pkl", 'wb') as f:
        pickle.dump(evaluation_results, f)
    
    recommender.save_model()
    
    # Step 7: Test recommendations
    print("\n7. Sample recommendations...")
    
    # Get a user with many interactions
    user_counts = train_interactions['user_id'].value_counts()
    test_user_id = user_counts.head(1).index[0]
    
    print(f"\nTesting with user {test_user_id}:")
    user_train_data = train_interactions[train_interactions['user_id'] == test_user_id]
    print(f"- Training ratings: {len(user_train_data)}")
    print(f"- Average rating given: {user_train_data['rating'].mean():.2f}")
    
    # Show some liked recipes
    liked_recipes = user_train_data[user_train_data['rating'] >= 4].head(3)
    print("\nUser's liked recipes in training:")
    for _, row in liked_recipes.iterrows():
        recipe = recipes_df[recipes_df['id'] == row['recipe_id']].iloc[0]
        print(f"  • {recipe['name']} (rated {row['rating']})")
    
    # Get recommendations
    print(f"\nTop 5 recommendations:")
    recommendations = recommender.recommend(test_user_id, n_recommendations=5)
    
    for i, (recipe_id, score) in enumerate(recommendations, 1):
        recipe = recipes_df[recipes_df['id'] == recipe_id].iloc[0]
        print(f"{i}. {recipe['name']} (Score: {score:.3f})")
        print(f"   Time: {recipe['minutes']} min | Health: {recipe['health_score']:.1f}")

if __name__ == "__main__":
    main()