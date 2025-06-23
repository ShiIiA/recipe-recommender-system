import streamlit as st
import csv
import random
from datetime import datetime, date
import ast
import time
from collections import Counter, defaultdict
import json
import os
import math
import pandas as pd

# =============================================================================
# PAGE CONFIGURATION
# =============================================================================
st.set_page_config(
    page_title="🌿 Ghibli Recipe Garden",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# CONSTANTS
# =============================================================================
DATA_DIR = "user_data"
RECIPES_PER_PAGE = 9
MAX_RECIPES_TO_LOAD = 5000

# Create data directory if it doesn't exist
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

# =============================================================================
# SESSION STATE INITIALIZATION
# =============================================================================
def init_session_state():
    """Initialize all session state variables"""
    if 'user_profile' not in st.session_state:
        st.session_state.user_profile = load_user_profile()
    if 'recipe_similarity_cache' not in st.session_state:
        st.session_state.recipe_similarity_cache = {}
    if 'all_recipes' not in st.session_state:
        st.session_state.all_recipes = []
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Home"
    if 'show_favorites_mode' not in st.session_state:
        st.session_state.show_favorites_mode = False

# =============================================================================
# USER PROFILE MANAGEMENT
# =============================================================================
def save_user_profile(profile, user_id="default"):
    """Save user profile to JSON file"""
    try:
        with open(f"{DATA_DIR}/user_{user_id}.json", 'w') as f:
            json.dump(profile, f, indent=2)
    except Exception as e:
        st.warning(f"Could not save profile: {e}")

def load_user_profile(user_id="default"):
    """Load user profile from JSON file"""
    try:
        filepath = f"{DATA_DIR}/user_{user_id}.json"
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                return json.load(f)
    except Exception as e:
        st.warning(f"Could not load profile: {e}")
    
    # Return default profile
    return {
        'liked_recipes': [],
        'viewed_recipes': [],
        'disliked_recipes': [],
        'dietary_restrictions': [],
        'ingredient_preferences': {'loved': [], 'hated': []},
        'badges': [],
        'points': 0,
        'skill_level': 'beginner',
        'cooking_frequency': 'weekly',
        'cuisine_preferences': [],
        'first_visit': True,
        'cooking_history': [],
        'rating_history': {}
    }

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================
def get_current_season():
    """Get current season based on month"""
    month = date.today().month
    if month in [3, 4, 5]:
        return "spring"
    elif month in [6, 7, 8]:
        return "summer"
    elif month in [9, 10, 11]:
        return "autumn"
    else:
        return "winter"

def get_time_of_day():
    """Get time of day based on current hour"""
    hour = datetime.now().hour
    if 5 <= hour < 12:
        return "morning"
    elif 12 <= hour < 18:
        return "afternoon"
    elif 18 <= hour < 22:
        return "evening"
    else:
        return "night"

# =============================================================================
# DATA LOADING AND PROCESSING
# =============================================================================
@st.cache_data
def load_recipe_data():
    """Load recipe data from CSV files"""
    recipes = []
    interactions_data = load_interactions_data()
    
    data_paths = [
        "data/raw/RAW_recipes.csv",
        "RAW_recipes.csv",
        "data/RAW_recipes.csv"
    ]
    
    loaded = False
    
    for data_path in data_paths:
        if load_recipes_from_path(data_path, recipes, interactions_data):
            loaded = True
            st.success(f"✅ Successfully loaded {len(recipes)} recipes")
            break
    
    if not loaded:
        st.error("❌ Could not find recipe files. Please ensure CSV files are in the correct location.")
        return []
    
    return recipes

def load_recipes_from_path(data_path, recipes, interactions_data):
    """Load recipes from a specific path"""
    try:
        with open(data_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for i, row in enumerate(reader):
                if i >= MAX_RECIPES_TO_LOAD:
                    break
                
                recipe = parse_recipe_row(row, i, interactions_data)
                if recipe:
                    recipes.append(recipe)
            
            return True
            
    except FileNotFoundError:
        return False
    except Exception as e:
        st.error(f"Error loading from {data_path}: {e}")
        return False

def parse_recipe_row(row, index, interactions_data):
    """Parse a single recipe row from CSV"""
    try:
        # Parse ingredients
        ingredients = safe_parse_list(row.get('ingredients', '[]'))
        if not ingredients:
            return None
        
        # Parse steps
        steps = safe_parse_list(row.get('steps', '[]'))
        
        # Parse tags
        tags = safe_parse_list(row.get('tags', '[]'))
        
        # Get recipe details
        recipe_id = row.get('recipe_id', row.get('id', str(index)))
        recipe_name = row.get('name', '').strip()
        recipe_description = row.get('description', '').strip()
        
        if not recipe_name:
            return None
        
        # Calculate metrics
        minutes = safe_parse_int(row.get('minutes', 30), 30)
        n_steps = safe_parse_int(row.get('n_steps', len(steps)), len(steps))
        
        avg_rating = calculate_average_rating(str(recipe_id), interactions_data)
        season = determine_recipe_season(recipe_name, recipe_description, ingredients)
        nutrition_score = calculate_nutrition_score(ingredients)
        complexity = classify_recipe_difficulty(ingredients, n_steps, minutes)
        sustainability_score, sustainability_factors = calculate_sustainability_score(season, ingredients)
        
        return {
            'id': recipe_id,
            'name': recipe_name,
            'minutes': minutes,
            'rating': avg_rating,
            'ingredients': ingredients,
            'description': recipe_description,
            'n_steps': n_steps,
            'steps': steps,
            'season': season,
            'nutrition_score': nutrition_score,
            'tags': tags,
            'submitted': row.get('submitted', ''),
            'contributor_id': row.get('contributor_id', ''),
            'n_ingredients': len(ingredients),
            'complexity': complexity,
            'sustainability_score': sustainability_score,
            'sustainability_factors': sustainability_factors
        }
        
    except Exception as e:
        return None

@st.cache_data
def load_interactions_data():
    """Load interaction data from CSV files"""
    interactions = {}
    interaction_paths = [
        "data/raw/RAW_interactions.csv",
        "RAW_interactions.csv",
        "data/RAW_interactions.csv"
    ]
    
    for path in interaction_paths:
        if load_interactions_from_path(path, interactions):
            return interactions
    
    return {}

def load_interactions_from_path(path, interactions):
    """Load interactions from a specific path"""
    try:
        with open(path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                recipe_id = str(row.get('recipe_id', ''))
                rating = safe_parse_float(row.get('rating', 0), 0)
                
                if recipe_id and rating > 0:
                    if recipe_id not in interactions:
                        interactions[recipe_id] = []
                    
                    interactions[recipe_id].append({
                        'rating': rating,
                        'date': row.get('date', ''),
                        'review': row.get('review', '')
                    })
            
            return True
            
    except FileNotFoundError:
        return False
    except Exception as e:
        return False

# =============================================================================
# PARSING UTILITIES
# =============================================================================
def safe_parse_list(value):
    """Safely parse a string representation of a list"""
    try:
        if not value or value == '[]':
            return []
        parsed = ast.literal_eval(value)
        if not isinstance(parsed, list):
            return [str(parsed)]
        return parsed
    except:
        return []

def safe_parse_int(value, default):
    """Safely parse an integer value"""
    try:
        return int(value) if str(value).isdigit() else default
    except:
        return default

def safe_parse_float(value, default):
    """Safely parse a float value"""
    try:
        return float(value)
    except:
        return default

# =============================================================================
# RECIPE ANALYSIS FUNCTIONS
# =============================================================================
def calculate_average_rating(recipe_id, interactions_data):
    """Calculate average rating for a recipe"""
    if recipe_id in interactions_data:
        ratings = [interaction['rating'] for interaction in interactions_data[recipe_id] if interaction['rating'] > 0]
        if ratings:
            return round(sum(ratings) / len(ratings), 1)
    return 3.0

def determine_recipe_season(recipe_name, recipe_description, ingredients):
    """Determine recipe season based on ingredients"""
    combined_text = f"{recipe_name} {recipe_description} {' '.join(str(ing) for ing in ingredients)}".lower()
    
    seasonal_keywords = {
        'spring': ['asparagus', 'spring onion', 'peas', 'artichoke', 'rhubarb', 'lettuce', 'spinach', 'strawberry'],
        'summer': ['tomato', 'zucchini', 'cucumber', 'corn', 'berries', 'melon', 'basil', 'peach'],
        'autumn': ['pumpkin', 'squash', 'apple', 'pear', 'sweet potato', 'brussels sprout', 'cranberry'],
        'winter': ['cabbage', 'kale', 'citrus', 'orange', 'lemon', 'root vegetables', 'ginger']
    }
    
    season_scores = {season: 0 for season in seasonal_keywords}
    
    for season, keywords in seasonal_keywords.items():
        for keyword in keywords:
            if keyword in combined_text:
                season_scores[season] += 1
    
    if all(score == 0 for score in season_scores.values()):
        return get_current_season()
    
    return max(season_scores, key=season_scores.get)

def calculate_nutrition_score(ingredients):
    """Calculate nutrition score based on ingredients"""
    if not ingredients:
        return 2.5
    
    healthy_ingredients = {
        'spinach': 2.0, 'kale': 2.0, 'broccoli': 1.8, 'avocado': 1.9, 'salmon': 1.8,
        'quinoa': 1.8, 'blueberry': 1.8, 'sweet potato': 1.6, 'olive oil': 1.3,
        'tomato': 1.4, 'carrot': 1.5, 'apple': 1.4, 'lemon': 1.3
    }
    
    total_score = 0
    for ingredient in ingredients:
        ingredient_str = str(ingredient).lower().strip()
        matched = False
        for healthy_item, points in healthy_ingredients.items():
            if healthy_item in ingredient_str:
                total_score += points
                matched = True
                break
        if not matched:
            total_score += 0.2
    
    average_score = total_score / len(ingredients)
    final_score = 2.5 + average_score
    return round(max(0, min(5, final_score)), 1)

def classify_recipe_difficulty(ingredients, n_steps, minutes):
    """Classify recipe difficulty"""
    if minutes <= 20 and n_steps <= 4:
        return "Easy"
    elif minutes <= 45 and n_steps <= 8:
        return "Medium"
    else:
        return "Hard"

def calculate_sustainability_score(season, ingredients):
    """Calculate sustainability score"""
    current_season = get_current_season()
    score = 0
    factors = []
    
    if season == current_season:
        score += 3
        factors.append("🌱 Seasonal harmony")
    
    sustainable_ingredients = {
        'spring': ['asparagus', 'peas', 'lettuce', 'spinach'],
        'summer': ['tomato', 'zucchini', 'cucumber', 'berries'],
        'autumn': ['pumpkin', 'squash', 'apple', 'sweet potato'],
        'winter': ['cabbage', 'kale', 'citrus', 'root vegetables']
    }

    ingredient_text = ' '.join(str(ing).lower() for ing in ingredients)
    matches = 0
    
    for ing in sustainable_ingredients.get(current_season, []):
        if ing in ingredient_text:
            matches += 1
    
    if matches >= 2:
        score += 2
        factors.append("🌿 Rich in seasonal ingredients")
    elif matches >= 1:
        score += 1
        factors.append("🍃 Some seasonal ingredients")
    
    return max(0, min(5, score)), factors

def check_dietary_restrictions(ingredients, restrictions):
    """Check if recipe conflicts with dietary restrictions"""
    if not restrictions:
        return False
    
    restriction_keywords = {
        "vegetarian": ["beef", "pork", "lamb", "chicken", "turkey", "duck", "fish", "salmon", "tuna", 
                      "shrimp", "crab", "lobster", "bacon", "ham", "sausage", "meat"],
        "vegan": ["beef", "pork", "lamb", "chicken", "turkey", "duck", "fish", "salmon", "tuna",
                 "shrimp", "crab", "lobster", "seafood", "bacon", "ham", "meat",
                 "milk", "cheese", "butter", "cream", "yogurt", "egg", "honey", "dairy"],
        "gluten_free": ["wheat", "flour", "bread", "pasta", "barley", "rye", "gluten", "soy sauce"],
        "dairy_free": ["milk", "cheese", "butter", "cream", "yogurt", "dairy", "whey", "casein"],
        "nut_free": ["almond", "peanut", "walnut", "pecan", "cashew", "pistachio", "hazelnut", "nuts"],
        "egg_free": ["egg", "eggs", "mayonnaise", "meringue"],
        "soy_free": ["soy", "tofu", "tempeh", "miso", "soy sauce", "edamame"],
        "shellfish_free": ["shrimp", "crab", "lobster", "oyster", "clam", "mussel", "scallop", "shellfish"]
    }
    
    ingredients_text = " ".join(str(ingredients)).lower()
    
    for restriction in restrictions:
        if restriction in restriction_keywords:
            keywords = restriction_keywords[restriction]
            for keyword in keywords:
                if keyword in ingredients_text:
                    return True
    
    return False

# =============================================================================
# USER TRACKING FUNCTIONS
# =============================================================================
def track_recipe_view(recipe_id):
    """Track when a user views a recipe"""
    if recipe_id not in st.session_state.user_profile['viewed_recipes']:
        st.session_state.user_profile['viewed_recipes'].append(recipe_id)
        save_user_profile(st.session_state.user_profile)

def track_recipe_rating(recipe_id, rating):
    """Track when a user rates a recipe"""
    st.session_state.user_profile['rating_history'][str(recipe_id)] = rating
    
    # Update liked/disliked lists
    if rating >= 4 and recipe_id not in st.session_state.user_profile['liked_recipes']:
        st.session_state.user_profile['liked_recipes'].append(recipe_id)
        if recipe_id in st.session_state.user_profile['disliked_recipes']:
            st.session_state.user_profile['disliked_recipes'].remove(recipe_id)
    elif rating <= 2 and recipe_id not in st.session_state.user_profile['disliked_recipes']:
        st.session_state.user_profile['disliked_recipes'].append(recipe_id)
        if recipe_id in st.session_state.user_profile['liked_recipes']:
            st.session_state.user_profile['liked_recipes'].remove(recipe_id)
    
    save_user_profile(st.session_state.user_profile)

def track_recipe_cooked(recipe_id):
    """Track when a user marks a recipe as cooked"""
    if recipe_id not in st.session_state.user_profile['cooking_history']:
        st.session_state.user_profile['cooking_history'].append(recipe_id)
        st.session_state.user_profile['points'] += 20
        save_user_profile(st.session_state.user_profile)

# =============================================================================
# BADGE SYSTEM
# =============================================================================
def check_badges():
    """Check for new badges based on user activity"""
    profile = st.session_state.user_profile
    recipes = st.session_state.get('all_recipes', [])
    new_badges = []
    
    badge_conditions = {
        'nutrition_conscious': {
            'check': lambda: len([r for r in profile['liked_recipes'] 
                                if get_recipe_attribute(r, recipes, 'nutrition_score') >= 4]) >= 3,
            'name': 'Nutrition Conscious',
            'points': 85
        },
        'seasonal_chef': {
            'check': lambda: len([r for r in profile['liked_recipes'] 
                                if get_recipe_attribute(r, recipes, 'season') == get_current_season()]) >= 10,
            'name': 'Seasonal Chef',
            'points': 150
        },
        'quick_cook': {
            'check': lambda: len([r for r in profile.get('cooking_history', []) 
                                if get_recipe_attribute(r, recipes, 'minutes') <= 30]) >= 20,
            'name': 'Quick Cook',
            'points': 120
        },
        'explorer': {
            'check': lambda: len(set([get_recipe_cuisine(r, recipes) 
                                    for r in profile['liked_recipes']])) >= 5,
            'name': 'Explorer',
            'points': 100
        }
    }
    
    for badge_id, badge_info in badge_conditions.items():
        if badge_info['check']() and badge_id not in profile['badges']:
            profile['badges'].append(badge_id)
            profile['points'] += badge_info['points']
            new_badges.append({
                'name': badge_info['name'], 
                'points': badge_info['points'], 
                'id': badge_id
            })
    
    return new_badges

def get_recipe_attribute(recipe_id, recipes, attribute):
    """Get a specific attribute of a recipe"""
    recipe = next((r for r in recipes if r['id'] == recipe_id), None)
    return recipe.get(attribute, 0) if recipe else 0

def get_recipe_cuisine(recipe_id, recipes):
    """Determine cuisine type from recipe tags"""
    recipe = next((r for r in recipes if r['id'] == recipe_id), None)
    if recipe and recipe.get('tags'):
        cuisines = ['italian', 'chinese', 'mexican', 'indian', 'french', 'japanese', 'thai', 'american']
        tags_text = ' '.join(str(tag).lower() for tag in recipe['tags'])
        for cuisine in cuisines:
            if cuisine in tags_text:
                return cuisine
    return 'general'

# =============================================================================
# RECOMMENDATION ENGINE
# =============================================================================
class RecommendationEngine:
    def __init__(self, recipes, user_profile):
        self.recipes = recipes
        self.user_profile = user_profile
        
    def get_user_ingredient_preferences(self):
        """Extract user's preferred ingredients from liked recipes"""
        liked_recipe_ids = self.user_profile.get('liked_recipes', [])
        loved_ingredients = self.user_profile.get('ingredient_preferences', {}).get('loved', [])
        
        preferred_ingredients = set(loved_ingredients)
        
        for recipe in self.recipes:
            if recipe['id'] in liked_recipe_ids:
                for ingredient in recipe.get('ingredients', []):
                    preferred_ingredients.add(str(ingredient).lower().strip())
        
        return preferred_ingredients
    
    def score_recipe_for_user(self, recipe):
        """Score a recipe based on user preferences"""
        score = 0
        explanations = []
        
        # Base score from recipe quality
        rating = recipe.get('rating', 0)
        nutrition = recipe.get('nutrition_score', 2.5)
        sustainability = recipe.get('sustainability_score', 0)
        
        score += (rating * 1.5) + nutrition + (sustainability * 1.5)
        
        # Season bonus
        current_season = get_current_season()
        if recipe.get('season') == current_season:
            score += 4
            explanations.append(f"🌸 Perfect for {current_season} season")
        
        # Sustainability bonus
        if sustainability >= 3:
            score += 2
            explanations.append("🌍 Earth-friendly choice")
        
        # Skill level matching
        skill_mapping = {'beginner': 'Easy', 'intermediate': 'Medium', 'advanced': 'Hard'}
        preferred_difficulty = skill_mapping.get(self.user_profile['skill_level'], 'Medium')
        
        if recipe['complexity'] == preferred_difficulty:
            score += 2
            explanations.append(f"✨ Perfect for your {self.user_profile['skill_level']} level")
        
        # Ingredient preferences
        preferred_ingredients = self.get_user_ingredient_preferences()
        recipe_ingredients = set(str(ing).lower().strip() for ing in recipe.get('ingredients', []))
        
        ingredient_matches = len(preferred_ingredients.intersection(recipe_ingredients))
        if ingredient_matches > 0:
            score += ingredient_matches * 0.7
            explanations.append(f"💚 Features {ingredient_matches} ingredients you love")
        
        # Cooking frequency matching
        cooking_freq = self.user_profile.get('cooking_frequency', 'weekly')
        recipe_time = recipe.get('minutes', 30)
        
        if cooking_freq == 'daily' and recipe_time <= 30:
            score += 2
            explanations.append("⚡ Quick weekday cooking")
        elif cooking_freq == 'weekly' and 30 <= recipe_time <= 60:
            score += 1
            explanations.append("🕰️ Perfect weekend project")
        
        # Bonus for highly nutritious
        if nutrition >= 4.0:
            score += 1
            explanations.append("💫 Highly nutritious")
        
        # Bonus for highly rated
        if rating >= 4.5:
            score += 1
            explanations.append("⭐ Highly rated by community")
        
        return score, explanations
    
    def get_recommendations(self, n_recommendations=10):
        """Get personalized recipe recommendations"""
        scored_recipes = []
        
        viewed_ids = set(self.user_profile.get('viewed_recipes', []))
        liked_ids = set(self.user_profile.get('liked_recipes', []))
        disliked_ids = set(self.user_profile.get('disliked_recipes', []))
        
        for recipe in self.recipes:
            recipe_id = recipe['id']
            
            # Skip already interacted recipes and those with dietary conflicts
            if (recipe_id in viewed_ids or recipe_id in liked_ids or 
                recipe_id in disliked_ids or
                check_dietary_restrictions(recipe['ingredients'], 
                                         self.user_profile.get('dietary_restrictions', []))):
                continue
            
            score, explanations = self.score_recipe_for_user(recipe)
            
            scored_recipes.append({
                'recipe': recipe,
                'score': score,
                'explanations': explanations
            })
        
        # Sort by score and return top N
        scored_recipes.sort(key=lambda x: x['score'], reverse=True)
        return scored_recipes[:n_recommendations]

# =============================================================================
# GOLDEN RECIPE ENGINE
# =============================================================================
class GoldenRecipeEngine:
    def __init__(self, recipes, user_profile):
        self.recipes = recipes
        self.user_profile = user_profile
    
    def find_golden_recipe(self):
        """Find the best recipe of the day for the user"""
        if not self.recipes:
            return None
            
        scored_recipes = []
        current_season = get_current_season()
        
        for recipe in self.recipes:
            score = 0
            golden_reasons = []
            
            # User preference bonus
            if recipe['id'] in self.user_profile.get('liked_recipes', []):
                score += 12
                golden_reasons.append("💫 A recipe close to your heart")
            
            # Seasonal bonus
            if recipe['season'] == current_season:
                score += 6
                golden_reasons.append(f"🌸 Perfect for {current_season}")
            
            # Sustainability bonus
            sustainability = recipe.get('sustainability_score', 0)
            if sustainability >= 4:
                score += 8
                golden_reasons.append("🌍 Exceptional sustainability")
            elif sustainability >= 3:
                score += 5
                golden_reasons.append("🌿 Earth-friendly choice")
            
            # Rating bonus
            if recipe['rating'] >= 4.7:
                score += 6
                golden_reasons.append("⭐ Beloved by the community")
            elif recipe['rating'] >= 4.5:
                score += 4
                golden_reasons.append("✨ Highly rated")
            
            # Nutrition bonus
            nutrition_score = recipe.get('nutrition_score', 2.5)
            if nutrition_score >= 4.5:
                score += 5
                golden_reasons.append("💚 Exceptionally nutritious")
            elif nutrition_score >= 4.0:
                score += 3
                golden_reasons.append("🌱 Very healthy")
            
            # Dietary compatibility bonus
            if not check_dietary_restrictions(recipe['ingredients'], 
                                            self.user_profile.get('dietary_restrictions', [])):
                score += 3
                golden_reasons.append("🕊️ Matches your dietary needs")
            
            if score > 0:
                scored_recipes.append({
                    'recipe': recipe,
                    'score': score,
                    'golden_reasons': golden_reasons
                })
        
        if scored_recipes:
            scored_recipes.sort(key=lambda x: x['score'], reverse=True)
            return scored_recipes[0] if scored_recipes[0]['score'] >= 10 else None
        
        return None

# =============================================================================
# UI COMPONENTS
# =============================================================================
def create_custom_css():
    """Create custom CSS for the app"""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@300;400;600;700&family=Noto+Serif+JP:wght@400;500;700&display=swap');
    
    /* Main container */
    .main {
        padding: 0;
    }
    
    /* Header styles */
    .ghibli-header {
        padding: 3rem 2rem;
        border-radius: 0 0 30px 30px;
        margin: -3rem -3rem 2rem -3rem;
        text-align: center;
        box-shadow: 0 8px 25px rgba(0,0,0,0.1);
    }
    
    /* Recipe card styles */
    .recipe-card {
        background: linear-gradient(145deg, #ffffff 0%, #f8f9fa 100%);
        border: none;
        border-radius: 25px;
        padding: 2rem;
        margin: 1.5rem 0;
        box-shadow: 0 10px 40px rgba(0,0,0,0.08);
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .recipe-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 45px rgba(0,0,0,0.12);
    }
    
    .recipe-title {
        font-size: 1.6rem;
        font-weight: 700;
        margin-bottom: 1rem;
        font-family: 'Noto Serif JP', serif;
    }
    
    .recipe-description {
        font-size: 1rem;
        color: #666;
        line-height: 1.6;
        margin-bottom: 1.5rem;
    }
    
    .recipe-stats {
        display: flex;
        flex-wrap: wrap;
        gap: 0.6rem;
        margin-top: 1rem;
    }
    
    .stat-badge {
        background: rgba(46, 125, 50, 0.1);
        color: #2e7d32;
        padding: 0.4rem 0.8rem;
        border-radius: 20px;
        font-size: 0.9rem;
        font-weight: 600;
        display: inline-flex;
        align-items: center;
        gap: 0.3rem;
    }
    
    .sustainability-badge {
        background: linear-gradient(135deg, #4caf50, #66bb6a);
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 0.5rem 0;
        display: inline-block;
        box-shadow: 0 4px 12px rgba(76, 175, 80, 0.3);
    }
    
    /* Navigation styles */
    .nav-button {
        background: linear-gradient(135deg, #4caf50, #66bb6a);
        color: white;
        border: none;
        padding: 0.8rem 1.5rem;
        border-radius: 25px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s ease;
    }
    
    .nav-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(76, 175, 80, 0.3);
    }
    
    /* Golden recipe styles */
    .golden-recipe-container {
        background: linear-gradient(135deg, #ffd700 0%, #ffb347 50%, #ff8c00 100%);
        border-radius: 25px;
        padding: 2rem;
        margin: 2rem 0;
        box-shadow: 0 15px 50px rgba(255, 215, 0, 0.3);
        border: 3px solid rgba(255, 255, 255, 0.6);
        position: relative;
        overflow: hidden;
    }
    
    .golden-recipe-title {
        color: white;
        font-size: 2rem;
        font-weight: 700;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
        margin: 0 0 1rem 0;
        text-align: center;
    }
    
    .golden-recipe-subtitle {
        color: rgba(255,255,255,0.9);
        font-size: 1.2rem;
        text-align: center;
        margin-bottom: 1.5rem;
        font-style: italic;
    }
    
    /* Badge styles */
    .badge-container {
        background: rgba(255,255,255,0.95);
        padding: 1.5rem;
        border-radius: 20px;
        text-align: center;
        margin: 1rem 0;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    
    /* Metric styles */
    .metric-card {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 4px 15px rgba(0,0,0,0.05);
        border: 1px solid rgba(0,0,0,0.05);
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #2e7d32;
        margin: 0;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #666;
        margin-top: 0.3rem;
    }
    </style>
    """, unsafe_allow_html=True)

def create_header():
    """Create the Ghibli-inspired header"""
    current_season = get_current_season()
    time_of_day = get_time_of_day()
    current_time = datetime.now().strftime("%H:%M")
    current_date = datetime.now().strftime("%B %d, %Y")

    season_styles = {
        "spring": {
            "gradient": "linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 50%, #a5d6a7 100%)",
            "text_color": "#2e7d32",
            "accent": "#4caf50",
            "nature": "🌸🌱"
        },
        "summer": {
            "gradient": "linear-gradient(135deg, #e3f2fd 0%, #90caf9 50%, #42a5f5 100%)",
            "text_color": "#0d47a1",
            "accent": "#1976d2",
            "nature": "🌳🌻"
        },
        "autumn": {
            "gradient": "linear-gradient(135deg, #fff3e0 0%, #ffcc80 50%, #ff9800 100%)",
            "text_color": "#e65100",
            "accent": "#f57c00",
            "nature": "🍂🍄"
        },
        "winter": {
            "gradient": "linear-gradient(135deg, #f3e5f5 0%, #ce93d8 50%, #ba68c8 100%)",
            "text_color": "#4a148c",
            "accent": "#7b1fa2",
            "nature": "❄️🏔️"
        }
    }

    haiku_messages = {
        "spring": {
            "haiku": "Fresh green shoots rise / Earth awakens from deep sleep / Cook with spring's first gifts",
            "wisdom": "In spring's gentle embrace, every sprout tells a story of renewal.",
            "action": "Choose asparagus, tender peas, and young lettuce - spring's precious offerings."
        },
        "summer": {
            "haiku": "Sun-ripened tomatoes / Golden corn dances in heat / Simple becomes feast", 
            "wisdom": "Summer teaches patience through the slow ripening of perfect flavors.",
            "action": "Celebrate tomatoes, zucchini, and berries - summer's abundant gifts."
        },
        "autumn": {
            "haiku": "Leaves fall like recipes / Ancient wisdom fills the air / Harvest time brings peace",
            "wisdom": "Autumn whispers: gather wisely, waste nothing, give thanks for plenty.",
            "action": "Honor squash, apples, and roots - autumn's lasting treasures."
        },
        "winter": {
            "haiku": "Snow blankets the earth / Stored grains hold summer's warmth / Simple soup brings joy",
            "wisdom": "Winter teaches us that the simplest meals warm both body and soul.",
            "action": "Embrace citrus, winter greens, and warming spices - winter's comfort."
        }
    }

    style = season_styles[current_season]
    message = haiku_messages[current_season]

    st.markdown(f"""
    <div class="ghibli-header" style="background: {style['gradient']};">
        <h1 style="font-size: 3rem; color: {style['text_color']}; margin: 0; font-family: 'Noto Serif JP', serif;">
            {style['nature']} Ghibli Recipe Garden {style['nature']}
        </h1>
        <div style="font-size: 1.5rem; color: {style['text_color']}; margin: 1rem 0;">
            {current_time} • {current_date}
        </div>
        <div style="font-size: 1.2rem; color: {style['text_color']}; margin: 1rem 0;">
            {current_season.title()} • {time_of_day.title()}
        </div>
        
        <div style="background: rgba(255,255,255,0.9); padding: 1.5rem; border-radius: 20px; margin: 2rem auto; max-width: 600px;">
            <div style="font-size: 1.1rem; color: {style['text_color']}; font-style: italic; margin-bottom: 1rem;">
                {message['haiku']}
            </div>
            <div style="font-size: 1rem; color: {style['text_color']}; font-weight: 600;">
                {message['wisdom']}
            </div>
            <div style="font-size: 0.9rem; color: {style['text_color']}; margin-top: 0.5rem;">
                {message['action']}
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

def display_recipe_card(recipe, context="main", recommendation_data=None, in_column=False):
    """Display a recipe card with rating functionality"""
    unique_id = f"{context}_{recipe['id']}_{hash(str(recipe))%10000}"
    
    # Recipe header
    st.markdown(f"""
    <div class="recipe-card">
        <div class="recipe-title" style="color: {get_season_color()};">
            {recipe['name']}
        </div>
    """, unsafe_allow_html=True)
    
    # Sustainability badge
    if recipe.get('sustainability_score', 0) >= 3:
        st.markdown(f"""
        <div class="sustainability-badge">
            🌍 Earth Blessing {recipe['sustainability_score']}/5
        </div>
        """, unsafe_allow_html=True)
    
    # Recipe description
    st.markdown(f"""
        <div class="recipe-description">
            {recipe.get('description', 'A delicious recipe to try!')}
        </div>
    """, unsafe_allow_html=True)
    
    # Recipe stats
    st.markdown(f"""
        <div class="recipe-stats">
            <span class="stat-badge">⭐ {recipe['rating']}/5</span>
            <span class="stat-badge">⏰ {recipe['minutes']} min</span>
            <span class="stat-badge">🏆 {recipe['complexity']}</span>
            <span class="stat-badge">🌱 Health: {recipe.get('nutrition_score', 2.5)}/5</span>
            <span class="stat-badge">🍂 {recipe['season'].title()}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Recommendation explanations
    if recommendation_data and recommendation_data.get('explanations'):
        with st.expander("🧚‍♀️ Why this recipe?"):
            for exp in recommendation_data['explanations'][:3]:
                st.write(f"• {exp}")
    
    # Sustainability factors
    if recipe.get('sustainability_factors'):
        with st.expander("🌿 Sustainability"):
            for factor in recipe['sustainability_factors'][:2]:
                st.write(f"• {factor}")
    
    # Rating section - avoid nested columns when already in a column
    if not in_column:
        col1, col2 = st.columns([3, 1])
        
        with col1:
            display_rating_section(recipe, unique_id)
        
        with col2:
            if st.button("🍳 Cooked!", key=f"cooked_{unique_id}"):
                track_recipe_cooked(recipe['id'])
                st.success("Added to cooking history!")
                st.rerun()
    else:
        # If we're already in a column, don't create nested columns
        display_rating_section(recipe, unique_id)
        if st.button("🍳 Cooked!", key=f"cooked_{unique_id}"):
            track_recipe_cooked(recipe['id'])
            st.success("Added to cooking history!")
            st.rerun()
    
    # Recipe details
    with st.expander("📖 Full Recipe"):
        st.markdown(f"**🥬 Ingredients ({len(recipe['ingredients'])}):**")
        for ing in recipe['ingredients']:
            st.write(f"• {ing}")
        
        if recipe.get('steps'):
            st.markdown(f"**📝 Instructions ({len(recipe['steps'])} steps):**")
            for i, step in enumerate(recipe['steps'], 1):
                st.write(f"{i}. {step}")

def display_rating_section(recipe, unique_id):
    """Display the rating section for a recipe"""
    current_rating = st.session_state.user_profile.get('rating_history', {}).get(str(recipe['id']), 0)
    
    if current_rating > 0:
        st.markdown(f"Your rating: {'🍃' * int(current_rating)}{'🍂' * (5 - int(current_rating))} ({current_rating}/5)")
    
    # Create a single row of rating buttons
    rating_container = st.container()
    with rating_container:
        # Use a simple approach without nested columns
        st.write("Rate this recipe:")
        cols = st.columns(5)
        for i in range(5):
            with cols[i]:
                if st.button(f"{'🍃' if i < current_rating else '🍂'}", 
                           key=f"rate_{unique_id}_{i+1}", 
                           help=f"Rate {i+1}/5"):
                    track_recipe_rating(recipe['id'], i+1)
                    new_badges = check_badges()
                    if new_badges:
                        for badge in new_badges:
                            st.success(f"🏆 New badge: {badge['name']} (+{badge['points']} points)")
                    st.rerun()

def get_season_color():
    """Get color based on current season"""
    season_colors = {
        "spring": "#4caf50",
        "summer": "#1976d2",
        "autumn": "#f57c00",
        "winter": "#7b1fa2"
    }
    return season_colors.get(get_current_season(), "#4caf50")

# =============================================================================
# SIDEBAR COMPONENTS
# =============================================================================
def create_sidebar():
    """Create the main sidebar"""
    with st.sidebar:
        st.markdown("# 🌿 Your Garden Profile")
        
        profile = st.session_state.user_profile
        
        # User stats
        col1, col2 = st.columns(2)
        with col1:
            st.metric("🌱 Points", profile['points'])
            st.metric("💚 Loved", len(profile['liked_recipes']))
        with col2:
            st.metric("🍃 Viewed", len(profile['viewed_recipes']))
            st.metric("🍳 Cooked", len(profile.get('cooking_history', [])))
        
        if profile['badges']:
            st.success(f"🏆 {len(profile['badges'])} badges earned!")
        
        st.markdown("---")
        
        # Preferences
        st.markdown("### 🎯 Preferences")
        
        skill_level = st.selectbox(
            "🎓 Skill Level",
            ['beginner', 'intermediate', 'advanced'],
            index=['beginner', 'intermediate', 'advanced'].index(profile['skill_level'])
        )
        
        cooking_frequency = st.selectbox(
            "⏰ Cooking Frequency",
            ['daily', 'weekly', 'monthly'],
            index=['daily', 'weekly', 'monthly'].index(profile['cooking_frequency'])
        )
        
        dietary_options = [
            "vegetarian", "vegan", "gluten_free", "dairy_free", 
            "nut_free", "egg_free", "soy_free", "shellfish_free"
        ]
        
        dietary_restrictions = st.multiselect(
            "🥗 Dietary Restrictions",
            dietary_options,
            default=profile['dietary_restrictions']
        )
        
        # Save changes
        if (skill_level != profile['skill_level'] or 
            cooking_frequency != profile['cooking_frequency'] or 
            set(dietary_restrictions) != set(profile['dietary_restrictions'])):
            
            profile['skill_level'] = skill_level
            profile['cooking_frequency'] = cooking_frequency
            profile['dietary_restrictions'] = dietary_restrictions
            save_user_profile(profile)
            st.success("✅ Preferences updated!")

def create_explore_sidebar():
    """Create sidebar for explore page"""
    with st.sidebar:
        st.markdown("# 🔍 Search Filters")
        
        season_filter = st.selectbox(
            "🌸 Season",
            ['all', 'spring', 'summer', 'autumn', 'winter']
        )
        
        time_filter = st.selectbox(
            "⏰ Cooking Time",
            ['all', 'quick (≤30 min)', 'medium (30-60 min)', 'long (60+ min)']
        )
        
        complexity_filter = st.selectbox(
            "🏆 Difficulty",
            ['all', 'Easy', 'Medium', 'Hard']
        )
        
        rating_filter = st.select_slider(
            "⭐ Minimum Rating",
            options=[0, 1, 2, 3, 4, 4.5],
            value=0
        )
        
        return {
            'season': season_filter,
            'time': time_filter,
            'complexity': complexity_filter,
            'rating': rating_filter
        }

# =============================================================================
# SEARCH AND FILTER FUNCTIONS
# =============================================================================
def apply_filters(recipes, filters):
    """Apply filters to recipe list"""
    filtered = recipes.copy()
    
    # Season filter
    if filters['season'] != 'all':
        filtered = [r for r in filtered if r.get('season') == filters['season']]
    
    # Time filter
    if filters['time'] == 'quick (≤30 min)':
        filtered = [r for r in filtered if r.get('minutes', 30) <= 30]
    elif filters['time'] == 'medium (30-60 min)':
        filtered = [r for r in filtered if 30 < r.get('minutes', 30) <= 60]
    elif filters['time'] == 'long (60+ min)':
        filtered = [r for r in filtered if r.get('minutes', 30) > 60]
    
    # Complexity filter
    if filters['complexity'] != 'all':
        filtered = [r for r in filtered if r.get('complexity') == filters['complexity']]
    
    # Rating filter
    if filters.get('rating', 0) > 0:
        filtered = [r for r in filtered if r.get('rating', 0) >= filters['rating']]
    
    return filtered

def search_recipes(recipes, query):
    """Search recipes by query"""
    if not query:
        return recipes
    
    query_lower = query.lower()
    search_terms = query_lower.split()
    
    results = []
    for recipe in recipes:
        # Search in name
        if any(term in recipe['name'].lower() for term in search_terms):
            results.append(recipe)
            continue
        
        # Search in description
        if any(term in recipe.get('description', '').lower() for term in search_terms):
            results.append(recipe)
            continue
        
        # Search in ingredients
        ingredients_text = ' '.join(str(ing).lower() for ing in recipe.get('ingredients', []))
        if any(term in ingredients_text for term in search_terms):
            results.append(recipe)
            continue
        
        # Search in tags
        tags_text = ' '.join(str(tag).lower() for tag in recipe.get('tags', []))
        if any(term in tags_text for term in search_terms):
            results.append(recipe)
    
    return results

# =============================================================================
# MODEL EVALUATION FUNCTIONS
# =============================================================================
def calculate_rmse(actual, predicted):
    """Calculate Root Mean Square Error"""
    if len(actual) != len(predicted) or len(actual) == 0:
        return None
    
    mse = sum((a - p) ** 2 for a, p in zip(actual, predicted)) / len(actual)
    return math.sqrt(mse)

def calculate_map_at_k(recommended, relevant, k=10):
    """Calculate Mean Average Precision at K"""
    if not relevant:
        return 0.0
    
    relevant_set = set(relevant)
    recommended_k = recommended[:k]
    
    if not recommended_k:
        return 0.0
    
    precision_sum = 0.0
    relevant_count = 0
    
    for i, item in enumerate(recommended_k):
        if item in relevant_set:
            relevant_count += 1
            precision_sum += relevant_count / (i + 1)
    
    if relevant_count == 0:
        return 0.0
    
    return precision_sum / min(len(relevant_set), k)

def evaluate_recommendation_system():
    """Evaluate the recommendation system performance"""
    recipes = st.session_state.get('all_recipes', [])
    profile = st.session_state.user_profile
    
    if not recipes:
        return None, None, None
    
    # Calculate RMSE
    actual_ratings = []
    predicted_ratings = []
    
    engine = RecommendationEngine(recipes, profile)
    
    rating_history = profile.get('rating_history', {})
    if rating_history:
        for recipe_id, actual_rating in rating_history.items():
            recipe = next((r for r in recipes if str(r['id']) == str(recipe_id)), None)
            if recipe:
                predicted_score, _ = engine.score_recipe_for_user(recipe)
                # Normalize score to 1-5 range
                normalized_score = min(5, max(1, (predicted_score / 10) * 5))
                
                actual_ratings.append(actual_rating)
                predicted_ratings.append(normalized_score)
    
    rmse = calculate_rmse(actual_ratings, predicted_ratings) if actual_ratings else None
    
    # Calculate MAP
    liked_recipes = profile.get('liked_recipes', [])
    recommendations = engine.get_recommendations(20)
    recommended_ids = [rec['recipe']['id'] for rec in recommendations]
    
    map_score = calculate_map_at_k(recommended_ids, liked_recipes, k=10)
    
    # Calculate coverage
    all_recipe_ids = [r['id'] for r in recipes]
    viewed_ids = set(profile.get('viewed_recipes', []))
    disliked_ids = set(profile.get('disliked_recipes', []))
    restrictions = profile.get('dietary_restrictions', [])
    
    available_recipes = []
    for recipe in recipes:
        if (recipe['id'] not in viewed_ids and 
            recipe['id'] not in liked_recipes and 
            recipe['id'] not in disliked_ids and
            not check_dietary_restrictions(recipe['ingredients'], restrictions)):
            available_recipes.append(recipe)
    
    coverage = len(available_recipes) / len(all_recipe_ids) if all_recipe_ids else 0
    
    return rmse, map_score, coverage

# =============================================================================
# PAGE FUNCTIONS
# =============================================================================
def home_page():
    """Display the home page"""
    create_sidebar()
    
    profile = st.session_state.user_profile
    recipes = st.session_state.get('all_recipes', [])
    
    if not recipes:
        st.error("❌ No recipes loaded. Please check your data files.")
        return
    
    # Welcome message
    cooking_count = len(profile.get('cooking_history', []))
    if cooking_count == 0:
        st.markdown("""
        ## 🌱 Welcome to your culinary journey!
        
        Discover recipes tailored just for you. Rate recipes with 🍃 leaves and track your cooking adventures!
        """)
    elif cooking_count < 5:
        st.markdown(f"""
        ## 🌿 Great to see you cooking!
        
        You've cooked **{cooking_count}** recipes so far. Keep exploring to discover new flavors!
        """)
    else:
        st.markdown(f"""
        ## 🌳 You're becoming a seasoned chef!
        
        **{cooking_count}** recipes cooked! Your garden is flourishing beautifully.
        """)
    
    # Track recipe views
    for recipe in recipes[:20]:  # Pre-load some views
        track_recipe_view(recipe['id'])
    
    # Golden Recipe
    st.markdown("---")
    st.markdown("## ✨ Today's Golden Recipe")
    
    golden_engine = GoldenRecipeEngine(recipes, profile)
    golden_data = golden_engine.find_golden_recipe()
    
    if golden_data:
        golden_recipe = golden_data['recipe']
        
        st.markdown(f"""
        <div class="golden-recipe-container">
            <div class="golden-recipe-title">🌟 {golden_recipe['name']} 🌟</div>
            <div class="golden-recipe-subtitle">A recipe touched by magic</div>
        </div>
        """, unsafe_allow_html=True)
        
        display_recipe_card(golden_recipe, context="golden", 
                          recommendation_data={'explanations': golden_data['golden_reasons']})
    
    # Personalized Recommendations
    st.markdown("---")
    st.markdown("## 🧚‍♀️ Just for You")
    
    engine = RecommendationEngine(recipes, profile)
    recommendations = engine.get_recommendations(6)
    
    if recommendations:
        st.markdown("Based on your preferences and cooking history:")
        
        # Display in grid
        for i in range(0, len(recommendations), 3):
            cols = st.columns(3)
            for j, rec_data in enumerate(recommendations[i:i+3]):
                with cols[j]:
                    display_recipe_card(rec_data['recipe'], 
                                      context=f"rec_{i}_{j}",
                                      recommendation_data=rec_data,
                                      in_column=True)
    else:
        # Show popular recipes as fallback
        st.info("Rate some recipes to get personalized recommendations!")
        popular = sorted([r for r in recipes if r.get('rating', 0) >= 4.0], 
                        key=lambda x: x.get('rating', 0), reverse=True)[:6]
        
        for i in range(0, len(popular), 3):
            cols = st.columns(3)
            for j, recipe in enumerate(popular[i:i+3]):
                with cols[j]:
                    display_recipe_card(recipe, context=f"pop_{i}_{j}", in_column=True)
    
    # Season highlights
    st.markdown("---")
    st.markdown(f"## 🌸 {get_current_season().title()} Favorites")
    
    seasonal = [r for r in recipes if r.get('season') == get_current_season()][:3]
    
    if seasonal:
        cols = st.columns(3)
        for i, recipe in enumerate(seasonal):
            with cols[i]:
                display_recipe_card(recipe, context=f"season_{i}", in_column=True)

def explore_page():
    """Display the explore page"""
    filters = create_explore_sidebar()
    
    recipes = st.session_state.get('all_recipes', [])
    profile = st.session_state.user_profile
    
    if not recipes:
        st.error("❌ No recipes loaded.")
        return
    
    st.markdown("## 🔍 Discover New Recipes")
    
    # Search bar
    search_query = st.text_input(
        "Search recipes by name, ingredients, or cuisine...",
        placeholder="Try 'pasta', 'chicken', or 'quick dinner'"
    )
    
    # Apply search and filters
    results = recipes
    if search_query:
        results = search_recipes(results, search_query)
    
    results = apply_filters(results, filters)
    
    # Apply dietary restrictions
    if profile.get('dietary_restrictions'):
        results = [r for r in results 
                  if not check_dietary_restrictions(r['ingredients'], 
                                                  profile['dietary_restrictions'])]
    
    st.markdown(f"### Found {len(results)} recipes")
    
    if not results:
        st.info("No recipes match your criteria. Try adjusting filters!")
        return
    
    # Sorting
    sort_option = st.selectbox(
        "Sort by:",
        ['Rating (High to Low)', 'Cooking Time (Short to Long)', 
         'Health Score (High to Low)', 'Sustainability (High to Low)']
    )
    
    if sort_option == 'Rating (High to Low)':
        results.sort(key=lambda x: x.get('rating', 0), reverse=True)
    elif sort_option == 'Cooking Time (Short to Long)':
        results.sort(key=lambda x: x.get('minutes', 999))
    elif sort_option == 'Health Score (High to Low)':
        results.sort(key=lambda x: x.get('nutrition_score', 0), reverse=True)
    elif sort_option == 'Sustainability (High to Low)':
        results.sort(key=lambda x: x.get('sustainability_score', 0), reverse=True)
    
    # Pagination
    total_pages = (len(results) - 1) // RECIPES_PER_PAGE + 1
    page = st.number_input("Page", min_value=1, max_value=total_pages, value=1)
    
    start_idx = (page - 1) * RECIPES_PER_PAGE
    end_idx = start_idx + RECIPES_PER_PAGE
    page_results = results[start_idx:end_idx]
    
    # Display results
    for i in range(0, len(page_results), 3):
        cols = st.columns(3)
        for j, recipe in enumerate(page_results[i:i+3]):
            with cols[j]:
                track_recipe_view(recipe['id'])
                display_recipe_card(recipe, context=f"explore_{page}_{i}_{j}", in_column=True)

def profile_page():
    """Display the profile page"""
    create_sidebar()
    
    profile = st.session_state.user_profile
    recipes = st.session_state.get('all_recipes', [])
    
    st.markdown("## 🌱 Your Cooking Garden")
    
    # Stats overview
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">""" + str(profile['points']) + """</div>
            <div class="metric-label">Garden Points</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">""" + str(len(profile['viewed_recipes'])) + """</div>
            <div class="metric-label">Recipes Explored</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">""" + str(len(profile['liked_recipes'])) + """</div>
            <div class="metric-label">Loved Recipes</div>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-value">""" + str(len(profile.get('cooking_history', []))) + """</div>
            <div class="metric-label">Cooked Recipes</div>
        </div>
        """, unsafe_allow_html=True)
    
    # Badges
    st.markdown("---")
    st.markdown("### 🏆 Your Badges")
    
    if profile['badges']:
        badge_info = {
            'nutrition_conscious': ('Nutrition Conscious', '🥗', 'Loved 3+ healthy recipes'),
            'seasonal_chef': ('Seasonal Chef', '🌸', 'Tried 10+ seasonal recipes'),
            'quick_cook': ('Quick Cook', '⚡', 'Mastered 20+ quick recipes'),
            'explorer': ('Explorer', '🗺️', 'Tried 5+ different cuisines')
        }
        
        cols = st.columns(4)
        for i, badge_id in enumerate(profile['badges']):
            if badge_id in badge_info:
                with cols[i % 4]:
                    name, icon, desc = badge_info[badge_id]
                    st.markdown(f"""
                    <div class="badge-container">
                        <div style="font-size: 3rem;">{icon}</div>
                        <div style="font-weight: 700; margin-top: 0.5rem;">{name}</div>
                        <div style="font-size: 0.8rem; color: #666; margin-top: 0.3rem;">{desc}</div>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.info("🌱 Complete actions to earn beautiful badges!")
    
    # Cooking journey
    st.markdown("---")
    st.markdown("### 📈 Your Cooking Journey")
    
    cooking_history = profile.get('cooking_history', [])
    if cooking_history:
        st.success(f"🌟 You've cooked {len(cooking_history)} recipes! Keep up the amazing work!")
        
        # Show recent cooked recipes
        recent_cooked = cooking_history[-5:]
        cooked_recipes = [r for r in recipes if r['id'] in recent_cooked]
        
        if cooked_recipes:
            st.markdown("**Recently Cooked:**")
            for recipe in cooked_recipes[-3:]:
                with st.expander(f"🌿 {recipe['name']}"):
                    st.write(f"⏰ {recipe['minutes']} minutes | 🏆 {recipe['complexity']} | ⭐ {recipe['rating']}/5")
    else:
        st.info("🌱 Start cooking some recipes to see your journey here!")
    
    # Favorite recipes
    st.markdown("---")
    st.markdown("### 💚 Your Favorite Recipes")
    
    liked_recipes = profile.get('liked_recipes', [])
    if liked_recipes:
        favorite_recipes = [r for r in recipes if r['id'] in liked_recipes][:6]
        
        if favorite_recipes:
            for i in range(0, len(favorite_recipes), 3):
                cols = st.columns(3)
                for j, recipe in enumerate(favorite_recipes[i:i+3]):
                    with cols[j]:
                        display_recipe_card(recipe, context=f"fav_{i}_{j}")
    else:
        st.info("🌱 Rate some recipes with 4+ 🍃 to see your favorites here!")

def analytics_page():
    """Display the analytics page"""
    st.markdown("## 📊 Recipe Garden Analytics")
    
    recipes = st.session_state.get('all_recipes', [])
    profile = st.session_state.user_profile
    
    if not recipes:
        st.error("❌ No data available for analytics.")
        return
    
    # Dataset overview
    st.markdown("### 📈 Dataset Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("📚 Total Recipes", len(recipes))
    
    with col2:
        avg_rating = sum(r.get('rating', 0) for r in recipes) / len(recipes)
        st.metric("⭐ Avg Rating", f"{avg_rating:.1f}/5")
    
    with col3:
        avg_time = sum(r.get('minutes', 30) for r in recipes) / len(recipes)
        st.metric("⏰ Avg Time", f"{avg_time:.0f} min")
    
    with col4:
        avg_nutrition = sum(r.get('nutrition_score', 2.5) for r in recipes) / len(recipes)
        st.metric("🌱 Avg Health", f"{avg_nutrition:.1f}/5")
    
    # Distribution analysis
    st.markdown("---")
    st.markdown("### 🎯 Recipe Distribution")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**🏆 Difficulty Distribution:**")
        complexity_counts = Counter(r.get('complexity', 'Medium') for r in recipes)
        for complexity, count in complexity_counts.items():
            percentage = (count / len(recipes)) * 100
            st.write(f"• {complexity}: {count} ({percentage:.1f}%)")
    
    with col2:
        st.markdown("**🌸 Seasonal Distribution:**")
        season_counts = Counter(r.get('season', 'summer') for r in recipes)
        for season, count in season_counts.items():
            percentage = (count / len(recipes)) * 100
            st.write(f"• {season.title()}: {count} ({percentage:.1f}%)")
    
    # Time distribution
    st.markdown("---")
    st.markdown("### ⏰ Cooking Time Distribution")
    
    time_ranges = {
        "Quick (≤20 min)": len([r for r in recipes if r.get('minutes', 30) <= 20]),
        "Medium (21-45 min)": len([r for r in recipes if 20 < r.get('minutes', 30) <= 45]),
        "Long (46-90 min)": len([r for r in recipes if 45 < r.get('minutes', 30) <= 90]),
        "Very Long (>90 min)": len([r for r in recipes if r.get('minutes', 30) > 90])
    }
    
    for range_name, count in time_ranges.items():
        percentage = (count / len(recipes)) * 100
        st.write(f"• {range_name}: {count} ({percentage:.1f}%)")
    
    # Model evaluation
    st.markdown("---")
    st.markdown("### 🤖 Recommendation System Performance")
    
    with st.spinner("🔮 Evaluating recommendation system..."):
        rmse, map_score, coverage = evaluate_recommendation_system()
    
    if rmse is not None:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("📏 RMSE", f"{rmse:.3f}", help="Root Mean Square Error - lower is better")
        
        with col2:
            st.metric("🎯 MAP@10", f"{map_score:.3f}", help="Mean Average Precision - higher is better")
        
        with col3:
            st.metric("🌍 Coverage", f"{coverage:.1%}", help="Percentage of recommendable recipes")
        
        # Performance insights
        st.markdown("---")
        st.markdown("### 🔍 Performance Insights")
        
        if rmse < 1.0:
            st.success("🌟 Excellent rating prediction accuracy!")
        elif rmse < 1.5:
            st.info("🌿 Good rating prediction performance.")
        else:
            st.warning("🌱 Rating predictions could be improved with more data.")
        
        if map_score > 0.3:
            st.success("🎯 Excellent recommendation relevance!")
        elif map_score > 0.1:
            st.info("👍 Good recommendation quality.")
        else:
            st.warning("📈 Recommendations need more personalization.")
    else:
        st.info("🌱 Rate more recipes to see detailed performance metrics!")
    
    # User engagement stats
    if profile.get('rating_history'):
        st.markdown("---")
        st.markdown("### 👤 Your Engagement Statistics")
        
        ratings = list(profile['rating_history'].values())
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            avg_user_rating = sum(ratings) / len(ratings)
            st.metric("🍃 Your Avg Rating", f"{avg_user_rating:.1f}/5")
        
        with col2:
            st.metric("📊 Recipes Rated", len(ratings))
        
        with col3:
            engagement_rate = len(ratings) / len(profile['viewed_recipes']) if profile['viewed_recipes'] else 0
            st.metric("💚 Engagement Rate", f"{engagement_rate:.1%}")

# =============================================================================
# MAIN APPLICATION
# =============================================================================
def main():
    """Main application entry point"""
    # Initialize session state
    init_session_state()
    
    # Create custom CSS
    create_custom_css()
    
    # Create header
    create_header()
    
    # Load data if not loaded
    if not st.session_state.all_recipes:
        with st.spinner("🌱 Loading your recipe garden..."):
            recipes = load_recipe_data()
            if recipes:
                st.session_state.all_recipes = recipes
    
    # Navigation
    st.markdown("---")
    
    # Create navigation buttons
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🏠 Home", key="nav_home", use_container_width=True):
            st.session_state.current_page = "Home"
    
    with col2:
        if st.button("🔍 Explore", key="nav_explore", use_container_width=True):
            st.session_state.current_page = "Explore"
    
    with col3:
        if st.button("👤 Profile", key="nav_profile", use_container_width=True):
            st.session_state.current_page = "Profile"
    
    with col4:
        if st.button("📊 Analytics", key="nav_analytics", use_container_width=True):
            st.session_state.current_page = "Analytics"
    
    st.markdown("---")
    
    # Route to appropriate page
    if st.session_state.current_page == "Home":
        home_page()
    elif st.session_state.current_page == "Explore":
        explore_page()
    elif st.session_state.current_page == "Profile":
        profile_page()
    elif st.session_state.current_page == "Analytics":
        analytics_page()
    
    # Footer
    st.markdown("---")
    st.markdown("""
    <div style="text-align: center; color: #666; padding: 2rem;">
        <p>🌿 Ghibli Recipe Garden • Made with love and sustainability in mind 🌿</p>
        <p style="font-size: 0.8rem;">© 2024 • Discover the magic of seasonal cooking</p>
    </div>
    """, unsafe_allow_html=True)

# =============================================================================
# RUN APPLICATION
# =============================================================================
if __name__ == "__main__":
    main()