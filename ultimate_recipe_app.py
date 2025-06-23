"""
Ultimate Recipe Recommendation App - Complete Enhanced Version
Features: Multi-diet support, Gamification, Social features, Avatars, Advanced UI
"""
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
import json
import random
from datetime import datetime, date, timedelta
import time
import pickle

# Page Configuration
st.set_page_config(
    page_title="🍳 CulinaryQuest Pro",
    page_icon="🍳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =================== ENHANCED GHIBLI-STYLE CSS ===================
def create_ghibli_css():
    st.markdown("""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Nunito:wght@300;400;600;700;800&family=Fredoka+One:wght@400&display=swap');
        
        .main-header {
            background: linear-gradient(135deg, #a8e6cf 0%, #88d8a3 50%, #7fcdcd 100%);
            padding: 2rem;
            border-radius: 25px;
            text-align: center;
            margin: 1rem 0;
            box-shadow: 0 15px 35px rgba(0,0,0,0.1);
            position: relative;
            overflow: hidden;
        }
        
        .main-header::before {
            content: '🌸✨🍃';
            position: absolute;
            top: 10px;
            right: 20px;
            font-size: 1.5rem;
            animation: float 3s ease-in-out infinite;
        }
        
        .ghibli-card {
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            padding: 1.5rem;
            border-radius: 20px;
            margin: 1rem 0;
            box-shadow: 0 8px 25px rgba(0,0,0,0.1);
            border: 3px solid #a8e6cf;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .ghibli-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 12px 30px rgba(0,0,0,0.15);
        }
        
        .recipe-card {
            background: linear-gradient(135deg, #fff8e1 0%, #f3e5ab 100%);
            padding: 1.5rem;
            border-radius: 15px;
            margin: 0.5rem 0;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            border: 2px solid #dcedc8;
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        
        .recipe-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
            transition: left 0.5s;
        }
        
        .recipe-card:hover::before {
            left: 100%;
        }
        
        .recipe-card:hover {
            transform: translateY(-8px) scale(1.02);
            box-shadow: 0 8px 25px rgba(0,0,0,0.2);
        }
        
        .achievement-badge {
            background: linear-gradient(135deg, #ffd54f 0%, #ffcc02 100%);
            padding: 0.7rem 1.2rem;
            border-radius: 25px;
            margin: 0.3rem;
            display: inline-block;
            box-shadow: 0 4px 10px rgba(0,0,0,0.2);
            font-weight: 600;
            animation: pulse 2s infinite;
        }
        
        .level-progress {
            background: linear-gradient(90deg, #4caf50 0%, #8bc34a 100%);
            height: 25px;
            border-radius: 15px;
            transition: width 1s ease;
            position: relative;
            overflow: hidden;
        }
        
        .level-progress::after {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.3), transparent);
            animation: shine 2s infinite;
        }
        
        .floating-element {
            animation: float 4s ease-in-out infinite;
        }
        
        .pulse-element {
            animation: pulse 2s infinite;
        }
        
        .metric-card {
            background: linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%);
            padding: 1.5rem;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
            border: 2px solid #a5d6a7;
            transition: all 0.3s ease;
        }
        
        .metric-card:hover {
            transform: scale(1.05);
            box-shadow: 0 6px 20px rgba(0,0,0,0.15);
        }
        
        .avatar-selector {
            display: inline-block;
            font-size: 3rem;
            padding: 0.5rem;
            border-radius: 50%;
            margin: 0.3rem;
            cursor: pointer;
            transition: transform 0.3s ease;
            border: 3px solid transparent;
        }
        
        .avatar-selector:hover {
            transform: scale(1.2);
            border-color: #4caf50;
        }
        
        .avatar-selected {
            border-color: #4caf50 !important;
            background: rgba(76, 175, 80, 0.1);
        }
        
        .diet-tag {
            background: linear-gradient(135deg, #e1f5fe 0%, #b3e5fc 100%);
            padding: 0.3rem 0.8rem;
            border-radius: 15px;
            font-size: 0.8rem;
            margin: 0.2rem;
            display: inline-block;
            border: 1px solid #81d4fa;
        }
        
        .sustainability-excellent { border-left: 5px solid #4caf50; }
        .sustainability-good { border-left: 5px solid #8bc34a; }
        .sustainability-moderate { border-left: 5px solid #ff9800; }
        .sustainability-poor { border-left: 5px solid #f44336; }
        
        .leaderboard-item {
            background: linear-gradient(135deg, #f5f5f5 0%, #e0e0e0 100%);
            padding: 1rem;
            border-radius: 10px;
            margin: 0.5rem 0;
            border-left: 4px solid #4caf50;
            transition: all 0.3s ease;
        }
        
        .leaderboard-item:hover {
            transform: translateX(10px);
            box-shadow: 0 4px 15px rgba(0,0,0,0.1);
        }
        
        .challenge-card {
            background: linear-gradient(135deg, #fff3e0 0%, #ffe0b2 100%);
            padding: 1.5rem;
            border-radius: 15px;
            margin: 1rem 0;
            border: 2px solid #ffcc02;
            position: relative;
        }
        
        .challenge-card::after {
            content: '🏆';
            position: absolute;
            top: 10px;
            right: 15px;
            font-size: 1.5rem;
        }
        
        .social-feed-item {
            background: white;
            padding: 1rem;
            border-radius: 10px;
            margin: 0.5rem 0;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            border-left: 3px solid #4caf50;
        }
        
        @keyframes float {
            0%, 100% { transform: translateY(0px); }
            50% { transform: translateY(-15px); }
        }
        
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.05); }
        }
        
        @keyframes shine {
            0% { transform: translateX(-100%); }
            100% { transform: translateX(100%); }
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(20px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .fade-in {
            animation: fadeIn 0.5s ease-out;
        }
        
        .stButton > button {
            background: linear-gradient(135deg, #4caf50 0%, #66bb6a 100%);
            color: white;
            border: none;
            border-radius: 25px;
            padding: 0.5rem 1.5rem;
            font-weight: 600;
            transition: all 0.3s ease;
            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
        }
        
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 15px rgba(0,0,0,0.2);
        }
        
        .sidebar .stSelectbox > div > div {
            background: linear-gradient(135deg, #e8f5e8 0%, #c8e6c9 100%);
            border-radius: 10px;
        }
    </style>
    """, unsafe_allow_html=True)

# =================== ENHANCED DATA MODELS ===================
def init_enhanced_session_state():
    """Initialize enhanced session state with all features"""
    if 'user_profile' not in st.session_state:
        st.session_state.user_profile = {
            'name': 'Chef Explorer',
            'level': 1,
            'xp': 0,
            'total_xp': 0,
            'avatar': '👨‍🍳',
            'join_date': datetime.now().strftime('%Y-%m-%d'),
            
            # Diet and preferences
            'diet_preferences': ['Omnivore'],
            'allergies': [],
            'favorite_cuisines': ['Italian', 'Asian'],
            'cooking_skill': 'Beginner',
            'time_preference': 'Any',
            
            # Gamification
            'cooking_streak': 0,
            'last_cook_date': None,
            'recipes_cooked': 0,
            'recipes_liked': 0,
            'carbon_saved': 0.0,
            'achievements': [],
            'badges': [],
            'challenge_progress': {},
            
            # Social
            'friends': [],
            'following': [],
            'followers': [],
            
            # Collections
            'recipe_collections': {
                'Favorites': [],
                'Want to Try': [],
                'Cooked': []
            },
            
            # Analytics
            'cooking_history': [],
            'rating_history': {},
            'viewed_recipes': [],
            'search_history': []
        }
    
    if 'sample_recipes' not in st.session_state:
        st.session_state.sample_recipes = generate_sample_recipes()
    
    if 'global_leaderboard' not in st.session_state:
        st.session_state.global_leaderboard = generate_sample_leaderboard()
    
    if 'active_challenges' not in st.session_state:
        st.session_state.active_challenges = generate_challenges()
    
    if 'social_feed' not in st.session_state:
        st.session_state.social_feed = generate_social_feed()

def generate_sample_recipes():
    """Generate comprehensive sample recipes for all diets"""
    diets = ['Omnivore', 'Vegetarian', 'Vegan', 'Keto', 'Paleo', 'Mediterranean', 'Gluten-Free', 'Low-Carb', 'High-Protein']
    cuisines = ['Italian', 'Asian', 'Mexican', 'French', 'Indian', 'Mediterranean', 'American', 'Thai', 'Japanese', 'Korean']
    difficulties = ['Beginner', 'Intermediate', 'Advanced']
    
    recipe_names = [
        "Creamy Mushroom Risotto", "Spicy Korean Bibimbap", "Classic Beef Tacos", "Mediterranean Quinoa Bowl",
        "Thai Green Curry", "Italian Carbonara", "Moroccan Tagine", "Japanese Ramen", "Greek Moussaka",
        "Indian Butter Chicken", "French Coq au Vin", "Mexican Enchiladas", "Chinese Kung Pao", "Turkish Kebabs",
        "Spanish Paella", "Lebanese Hummus Bowl", "Ethiopian Injera", "Peruvian Ceviche", "Brazilian Feijoada",
        "German Schnitzel", "Russian Borscht", "Vietnamese Pho", "Argentinian Empanadas", "Jamaican Jerk Chicken",
        "British Fish & Chips", "Australian Meat Pie", "Canadian Poutine", "South African Bobotie", "Kenyan Nyama Choma",
        "Swedish Meatballs", "Polish Pierogi", "Hungarian Goulash", "Czech Svickova", "Austrian Wiener Schnitzel",
        "Swiss Fondue", "Belgian Waffles", "Dutch Stroopwafel", "Portuguese Pastéis", "Danish Smørrebrød",
        "Finnish Salmon Soup", "Norwegian Lutefisk", "Icelandic Lamb Stew", "Irish Shepherd's Pie", "Scottish Haggis",
        "Welsh Rarebit", "Cornish Pasty", "Yorkshire Pudding", "Bangers and Mash", "Bubble and Squeak"
    ]
    
    recipes = []
    for i, name in enumerate(recipe_names):
        recipe = {
            'id': i + 1,
            'name': name,
            'diet': random.choice(diets),
            'cuisine': random.choice(cuisines),
            'difficulty': random.choice(difficulties),
            'prep_time': random.randint(15, 120),
            'cook_time': random.randint(10, 180),
            'total_time': 0,  # Will be calculated
            'servings': random.randint(2, 8),
            'rating': round(random.uniform(3.5, 5.0), 1),
            'calories_per_serving': random.randint(200, 800),
            'protein': random.randint(10, 50),
            'carbs': random.randint(20, 80),
            'fat': random.randint(5, 40),
            'fiber': random.randint(2, 15),
            
            # Sustainability metrics
            'carbon_footprint': round(random.uniform(0.5, 15.0), 2),
            'water_usage': random.randint(100, 5000),
            'seasonality_score': random.randint(40, 100),
            'local_ingredients': random.choice([True, False]),
            
            # Recipe content
            'description': f"A delicious {random.choice(cuisines).lower()} dish that's perfect for any occasion. This {'difficulties'.lower()} recipe brings authentic flavors to your kitchen.",
            'ingredients': generate_recipe_ingredients(random.choice(diets)),
            'instructions': generate_recipe_instructions(),
            'tags': generate_recipe_tags(),
            'chef': f"Chef {random.choice(['Anna', 'Bob', 'Carol', 'David', 'Emma', 'Frank', 'Grace', 'Henry'])}",
            'created_date': (datetime.now() - timedelta(days=random.randint(1, 365))).strftime('%Y-%m-%d'),
            
            # Interaction metrics
            'views': random.randint(50, 5000),
            'likes': random.randint(10, 500),
            'cooked_count': random.randint(5, 200),
            'reviews': random.randint(0, 50)
        }
        recipe['total_time'] = recipe['prep_time'] + recipe['cook_time']
        recipes.append(recipe)
    
    return recipes

def generate_recipe_ingredients(diet):
    """Generate realistic ingredients based on diet type"""
    base_ingredients = {
        'Omnivore': ['chicken breast', 'beef', 'fish', 'eggs', 'milk', 'cheese'],
        'Vegetarian': ['eggs', 'milk', 'cheese', 'yogurt', 'butter'],
        'Vegan': ['tofu', 'tempeh', 'nutritional yeast', 'plant milk'],
        'Keto': ['avocado', 'coconut oil', 'cheese', 'nuts', 'fatty fish'],
        'Paleo': ['grass-fed beef', 'wild salmon', 'sweet potato', 'coconut'],
        'Mediterranean': ['olive oil', 'feta cheese', 'olives', 'tomatoes'],
        'Gluten-Free': ['rice flour', 'quinoa', 'gluten-free oats'],
        'Low-Carb': ['cauliflower', 'zucchini', 'broccoli', 'spinach'],
        'High-Protein': ['protein powder', 'greek yogurt', 'lean meat', 'beans']
    }
    
    common_ingredients = [
        'onion', 'garlic', 'salt', 'pepper', 'olive oil', 'tomatoes',
        'carrots', 'celery', 'herbs', 'spices', 'lemon', 'ginger'
    ]
    
    diet_specific = base_ingredients.get(diet, [])
    ingredients = random.sample(common_ingredients, 6) + random.sample(diet_specific, min(3, len(diet_specific)))
    return ingredients[:8]

def generate_recipe_instructions():
    """Generate sample cooking instructions"""
    instructions = [
        "Prepare all ingredients and mise en place",
        "Heat oil in a large pan over medium heat",
        "Add aromatics and cook until fragrant",
        "Add main ingredients and cook as directed",
        "Season with herbs and spices to taste",
        "Simmer until cooked through and flavors meld",
        "Taste and adjust seasoning as needed",
        "Serve hot and garnish as desired"
    ]
    return instructions

def generate_recipe_tags():
    """Generate relevant recipe tags"""
    tag_options = [
        'quick', 'easy', 'healthy', 'comfort food', 'one-pot', 'family-friendly',
        'date night', 'meal prep', 'budget-friendly', 'seasonal', 'festive',
        'spicy', 'mild', 'creamy', 'crispy', 'fresh', 'hearty'
    ]
    return random.sample(tag_options, random.randint(3, 6))

def generate_sample_leaderboard():
    """Generate sample leaderboard data"""
    chef_names = [
        "Gordon Ramsay Jr", "Julia Child II", "Marco Pierre", "Alice Waters", "Anthony Bourdain",
        "Emeril Lagasse", "Wolfgang Puck", "Daniel Boulud", "Thomas Keller", "Grant Achatz",
        "Ferran Adrià", "Heston Blumenthal", "René Redzepi", "Massimo Bottura", "Alex Atala"
    ]
    
    leaderboard = []
    for i, name in enumerate(chef_names):
        chef = {
            'rank': i + 1,
            'name': name,
            'level': random.randint(15, 50),
            'xp': random.randint(5000, 50000),
            'recipes_cooked': random.randint(100, 1000),
            'carbon_saved': round(random.uniform(50, 500), 1),
            'avatar': random.choice(['👨‍🍳', '👩‍🍳', '🧑‍🍳', '👨‍🍰', '👩‍🍰']),
            'specialty': random.choice(['Italian', 'French', 'Asian', 'Fusion', 'Desserts', 'Healthy'])
        }
        leaderboard.append(chef)
    
    return sorted(leaderboard, key=lambda x: x['xp'], reverse=True)

def generate_challenges():
    """Generate active challenges"""
    challenges = [
        {
            'id': 1,
            'name': 'Sustainable Chef',
            'description': 'Cook 5 low-carbon recipes this week',
            'progress': random.randint(0, 4),
            'target': 5,
            'reward': '100 XP + Eco Badge',
            'expires': (datetime.now() + timedelta(days=4)).strftime('%Y-%m-%d'),
            'type': 'weekly'
        },
        {
            'id': 2,
            'name': 'Global Explorer',
            'description': 'Try recipes from 3 different cuisines',
            'progress': random.randint(0, 2),
            'target': 3,
            'reward': '75 XP + Explorer Badge',
            'expires': (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),
            'type': 'weekly'
        },
        {
            'id': 3,
            'name': 'Healthy Habits',
            'description': 'Cook 10 high-protein recipes',
            'progress': random.randint(2, 8),
            'target': 10,
            'reward': '150 XP + Health Guru Badge',
            'expires': (datetime.now() + timedelta(days=14)).strftime('%Y-%m-%d'),
            'type': 'bi-weekly'
        },
        {
            'id': 4,
            'name': 'Speed Demon',
            'description': 'Cook 3 recipes under 30 minutes',
            'progress': random.randint(0, 2),
            'target': 3,
            'reward': '50 XP + Speed Badge',
            'expires': (datetime.now() + timedelta(days=3)).strftime('%Y-%m-%d'),
            'type': 'daily'
        }
    ]
    return challenges

def generate_social_feed():
    """Generate sample social feed"""
    activities = [
        {
            'user': 'Chef Anna',
            'avatar': '👩‍🍳',
            'action': 'cooked',
            'recipe': 'Spicy Korean Bibimbap',
            'time': '2 hours ago',
            'likes': 12,
            'comments': 3
        },
        {
            'user': 'Sous Bob',
            'avatar': '👨‍🍳',
            'action': 'achieved',
            'achievement': 'Eco Warrior Badge',
            'time': '4 hours ago',
            'likes': 8,
            'comments': 1
        },
        {
            'user': 'Baker Carol',
            'avatar': '👩‍🍰',
            'action': 'shared',
            'recipe': 'Classic Chocolate Soufflé',
            'time': '6 hours ago',
            'likes': 25,
            'comments': 7
        }
    ]
    return activities

# =================== GAMIFICATION SYSTEM ===================
def calculate_level_and_xp():
    """Calculate current level and XP progress"""
    profile = st.session_state.user_profile
    total_xp = profile['total_xp']
    
    # Level calculation: Level = floor(sqrt(total_xp / 100))
    level = int(np.sqrt(total_xp / 100)) + 1
    xp_for_current_level = (level - 1) ** 2 * 100
    xp_for_next_level = level ** 2 * 100
    current_level_xp = total_xp - xp_for_current_level
    xp_needed = xp_for_next_level - xp_for_current_level
    
    return level, current_level_xp, xp_needed

def award_xp(amount, reason):
    """Award XP and check for level ups"""
    profile = st.session_state.user_profile
    old_level = profile['level']
    
    profile['total_xp'] += amount
    new_level, current_xp, xp_needed = calculate_level_and_xp()
    profile['level'] = new_level
    profile['xp'] = current_xp
    
    if new_level > old_level:
        st.balloons()
        st.success(f"🎉 LEVEL UP! You're now Level {new_level}! Keep cooking!")
        
        # Award level-up achievement
        achievement = f"Level {new_level} Chef"
        if achievement not in profile['achievements']:
            profile['achievements'].append(achievement)
    
    st.success(f"🌟 +{amount} XP for {reason}!")

def check_achievements():
    """Check and award achievements"""
    profile = st.session_state.user_profile
    achievements = profile['achievements']
    
    achievement_criteria = {
        'First Love': profile['recipes_liked'] >= 1,
        'Recipe Explorer': profile['recipes_cooked'] >= 5,
        'Social Butterfly': len(profile['friends']) >= 3,
        'Eco Warrior': profile['carbon_saved'] >= 10.0,
        'Streak Master': profile['cooking_streak'] >= 7,
        'Collection Curator': sum(len(col) for col in profile['recipe_collections'].values()) >= 10,
        'Diverse Palate': len(set(profile['favorite_cuisines'])) >= 5,
        'Speed Chef': any(recipe.get('total_time', 60) <= 30 for recipe in profile['cooking_history'][-5:]),
        'Health Guru': sum(1 for recipe in profile['cooking_history'] if recipe.get('calories_per_serving', 500) <= 400) >= 10
    }
    
    new_achievements = []
    for achievement, earned in achievement_criteria.items():
        if earned and achievement not in achievements:
            achievements.append(achievement)
            new_achievements.append(achievement)
    
    if new_achievements:
        for achievement in new_achievements:
            st.success(f"🏆 Achievement Unlocked: {achievement}!")
            award_xp(25, f"earning {achievement} achievement")

# =================== RECIPE RECOMMENDATION ENGINE ===================
def get_personalized_recommendations(diet_filter=None, cuisine_filter=None, max_time=None, n=6):
    """Enhanced recommendation system"""
    recipes = st.session_state.sample_recipes
    profile = st.session_state.user_profile
    
    # Apply filters
    filtered_recipes = recipes.copy()
    
    if diet_filter and diet_filter != 'All':
        filtered_recipes = [r for r in filtered_recipes if r['diet'] == diet_filter]
    
    if cuisine_filter and cuisine_filter != 'All':
        filtered_recipes = [r for r in filtered_recipes if r['cuisine'] == cuisine_filter]
    
    if max_time:
        filtered_recipes = [r for r in filtered_recipes if r['total_time'] <= max_time]
    
    # Apply user preferences
    user_diets = profile['diet_preferences']
    user_cuisines = profile['favorite_cuisines']
    
    # Score recipes based on user preferences
    for recipe in filtered_recipes:
        score = recipe['rating']  # Base score
        
        # Diet preference bonus
        if recipe['diet'] in user_diets:
            score += 1.0
        
        # Cuisine preference bonus
        if recipe['cuisine'] in user_cuisines:
            score += 0.5
        
        # Sustainability bonus
        if recipe['carbon_footprint'] < 5.0:
            score += 0.3
        
        # Difficulty adjustment based on user skill
        skill_levels = {'Beginner': 1, 'Intermediate': 2, 'Advanced': 3}
        user_skill = skill_levels.get(profile['cooking_skill'], 2)
        recipe_difficulty = skill_levels.get(recipe['difficulty'], 2)
        
        if abs(user_skill - recipe_difficulty) <= 1:
            score += 0.2
        
        recipe['recommendation_score'] = score
    
    # Sort by score and return top N
    filtered_recipes.sort(key=lambda x: x['recommendation_score'], reverse=True)
    return filtered_recipes[:n]

# =================== UI COMPONENTS ===================
def display_recipe_card(recipe, show_details_button=True, collection_key=None):
    """Enhanced recipe card with all details"""
    with st.container():
        st.markdown(f"""
        <div class="recipe-card fade-in">
            <h4>🍽️ {recipe['name']}</h4>
            <div style="display: flex; flex-wrap: wrap; gap: 0.5rem; margin: 0.5rem 0;">
                <span class="diet-tag">{recipe['diet']}</span>
                <span class="diet-tag">{recipe['cuisine']}</span>
                <span class="diet-tag">{recipe['difficulty']}</span>
            </div>
            <p><strong>⏱️ Total Time:</strong> {recipe['total_time']} min ({recipe['prep_time']} prep + {recipe['cook_time']} cook)</p>
            <p><strong>👥 Serves:</strong> {recipe['servings']} | <strong>⭐ Rating:</strong> {recipe['rating']}/5</p>
            <p><strong>🔥 Calories:</strong> {recipe['calories_per_serving']} per serving</p>
            <p><strong>🌱 Carbon:</strong> {recipe['carbon_footprint']} kg CO₂</p>
            <p style="font-size: 0.9rem; color: #666;">{recipe['description'][:100]}...</p>
            <p><small>👨‍🍳 by {recipe['chef']} | 👀 {recipe['views']} views | ❤️ {recipe['likes']} likes</small></p>
        </div>
        """, unsafe_allow_html=True)
        
        # Action buttons
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("👁️ View", key=f"view_{recipe['id']}_{collection_key}"):
                st.session_state.selected_recipe = recipe
                st.session_state.show_recipe_detail = True
                
        with col2:
            if st.button("❤️ Like", key=f"like_{recipe['id']}_{collection_key}"):
                profile = st.session_state.user_profile
                profile['recipes_liked'] += 1
                profile['recipe_collections']['Favorites'].append(recipe['id'])
                award_xp(10, "liking a recipe")
                check_achievements()
                st.rerun()
        
        with col3:
            if st.button("🍳 Cook", key=f"cook_{recipe['id']}_{collection_key}"):
                cook_recipe(recipe)
                
        with col4:
            collection_options = list(st.session_state.user_profile['recipe_collections'].keys())
            selected_collection = st.selectbox(
                "Save to", 
                ["Select..."] + collection_options,
                key=f"save_{recipe['id']}_{collection_key}"
            )
            if selected_collection != "Select...":
                save_to_collection(recipe['id'], selected_collection)

def cook_recipe(recipe):
    """Process cooking a recipe"""
    profile = st.session_state.user_profile
    
    # Update cooking streak
    today = datetime.now().date()
    last_cook = profile.get('last_cook_date')
    
    if last_cook:
        last_date = datetime.strptime(last_cook, '%Y-%m-%d').date()
        if today == last_date:
            # Already cooked today
            pass
        elif today == last_date + timedelta(days=1):
            # Consecutive day
            profile['cooking_streak'] += 1
        else:
            # Broke streak
            profile['cooking_streak'] = 1
    else:
        profile['cooking_streak'] = 1
    
    profile['last_cook_date'] = today.strftime('%Y-%m-%d')
    profile['recipes_cooked'] += 1
    profile['carbon_saved'] += max(0, 8.0 - recipe['carbon_footprint'])  # Average meal is ~8kg CO2
    
    # Add to cooking history
    cook_entry = recipe.copy()
    cook_entry['cooked_date'] = today.strftime('%Y-%m-%d')
    profile['cooking_history'].append(cook_entry)
    
    # Add to cooked collection
    if recipe['id'] not in profile['recipe_collections']['Cooked']:
        profile['recipe_collections']['Cooked'].append(recipe['id'])
    
    # Award XP and check achievements
    award_xp(25, f"cooking {recipe['name']}")
    check_achievements()
    
    st.balloons()
    st.success(f"🎉 You cooked {recipe['name']}! Great job!")
    st.rerun()

def save_to_collection(recipe_id, collection_name):
    """Save recipe to a collection"""
    profile = st.session_state.user_profile
    if recipe_id not in profile['recipe_collections'][collection_name]:
        profile['recipe_collections'][collection_name].append(recipe_id)
        st.success(f"Recipe saved to {collection_name}!")
        st.rerun()

def display_recipe_detail(recipe):
    """Display full recipe details"""
    st.markdown(f"""
    <div class="ghibli-card">
        <h2>🍽️ {recipe['name']}</h2>
        <div style="display: flex; flex-wrap: wrap; gap: 0.5rem; margin: 1rem 0;">
            <span class="diet-tag">{recipe['diet']}</span>
            <span class="diet-tag">{recipe['cuisine']}</span>
            <span class="diet-tag">{recipe['difficulty']}</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Recipe info
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown("### 📝 Description")
        st.write(recipe['description'])
        
        st.markdown("### 🛒 Ingredients")
        for i, ingredient in enumerate(recipe['ingredients'], 1):
            st.write(f"{i}. {ingredient}")
        
        st.markdown("### 👩‍🍳 Instructions")
        for i, instruction in enumerate(recipe['instructions'], 1):
            st.write(f"{i}. {instruction}")
        
        st.markdown("### 🏷️ Tags")
        for tag in recipe['tags']:
            st.markdown(f"`{tag}`", unsafe_allow_html=True)
    
    with col2:
        st.markdown("### 📊 Nutrition (per serving)")
        st.metric("Calories", f"{recipe['calories_per_serving']} kcal")
        st.metric("Protein", f"{recipe['protein']} g")
        st.metric("Carbs", f"{recipe['carbs']} g")
        st.metric("Fat", f"{recipe['fat']} g")
        st.metric("Fiber", f"{recipe['fiber']} g")
        
        st.markdown("### 🌍 Sustainability")
        st.metric("Carbon Footprint", f"{recipe['carbon_footprint']} kg CO₂")
        st.metric("Water Usage", f"{recipe['water_usage']} L")
        st.metric("Seasonality Score", f"{recipe['seasonality_score']}/100")
        
        st.markdown("### ⏱️ Time")
        st.metric("Prep Time", f"{recipe['prep_time']} min")
        st.metric("Cook Time", f"{recipe['cook_time']} min")
        st.metric("Total Time", f"{recipe['total_time']} min")
        st.metric("Servings", recipe['servings'])
        
        # Action buttons
        if st.button("🍳 Cook This Recipe!", key="detail_cook"):
            cook_recipe(recipe)
        
        if st.button("❤️ Add to Favorites", key="detail_like"):
            save_to_collection(recipe['id'], 'Favorites')
        
        if st.button("📤 Share Recipe", key="detail_share"):
            st.success("Recipe shared with your friends! 🎉")
    
    if st.button("← Back to Browse"):
        if 'selected_recipe' in st.session_state:
            del st.session_state.selected_recipe
        if 'show_recipe_detail' in st.session_state:
            del st.session_state.show_recipe_detail
        st.rerun()

def display_user_avatar():
    """Display user avatar selection"""
    profile = st.session_state.user_profile
    
    st.markdown("### 🎭 Choose Your Avatar")
    
    avatar_options = [
        '👨‍🍳', '👩‍🍳', '🧑‍🍳', '👨‍🍰', '👩‍🍰', '🧑‍🍰',
        '🍳', '🥘', '🍰', '🍕', '🍜', '🥗', '🍱', '🧄', '🥕', '🥖'
    ]
    
    # Display avatar options in a grid
    cols = st.columns(4)
    for i, avatar in enumerate(avatar_options):
        with cols[i % 4]:
            if st.button(avatar, key=f"avatar_{i}"):
                profile['avatar'] = avatar
                st.success(f"Avatar updated to {avatar}!")
                st.rerun()
    
    # Show current avatar
    st.markdown(f"""
    <div style="text-align: center; margin: 2rem 0;">
        <h3>Your Current Avatar</h3>
        <div style="font-size: 5rem;">{profile['avatar']}</div>
        <p>{profile['name']}</p>
    </div>
    """, unsafe_allow_html=True)

# =================== PAGE FUNCTIONS ===================
def main():
    """Main application"""
    # Initialize session state
    init_enhanced_session_state()
    
    # Create CSS
    create_ghibli_css()
    
    # Main header
    st.markdown(f"""
    <div class="main-header floating-element">
        <h1>🍳 CulinaryQuest Pro</h1>
        <p>Your Ultimate AI-Powered Culinary Adventure with Real Impact!</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check if showing recipe detail
    if st.session_state.get('show_recipe_detail') and 'selected_recipe' in st.session_state:
        display_recipe_detail(st.session_state.selected_recipe)
        return
    
    # Sidebar with user profile
    with st.sidebar:
        profile = st.session_state.user_profile
        level, current_xp, xp_needed = calculate_level_and_xp()
        
        st.markdown(f"""
        <div class="ghibli-card">
            <div style="text-align: center;">
                <div style="font-size: 4rem;">{profile['avatar']}</div>
                <h3>{profile['name']}</h3>
                <p><strong>Level {level} Chef</strong></p>
                <div style="background: #e0e0e0; border-radius: 15px; overflow: hidden; margin: 1rem 0;">
                    <div class="level-progress" style="width: {(current_xp/xp_needed)*100}%"></div>
                </div>
                <p style="font-size: 0.9rem;">{current_xp}/{xp_needed} XP to next level</p>
                <p style="font-size: 0.8rem;">🔥 {profile['cooking_streak']} day streak</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Navigation
        page = st.selectbox("🧭 Navigate", [
            "🏠 Dashboard",
            "🔍 Recipe Discovery", 
            "👥 Social Hub",
            "🏆 Challenges & Leaderboard",
            "📚 My Collections",
            "👤 Profile & Settings",
            "📊 Analytics & Insights"
        ])
    
    # Route to pages
    if page == "🏠 Dashboard":
        dashboard_page()
    elif page == "🔍 Recipe Discovery":
        discovery_page()
    elif page == "👥 Social Hub":
        social_page()
    elif page == "🏆 Challenges & Leaderboard":
        challenges_page()
    elif page == "📚 My Collections":
        collections_page()
    elif page == "👤 Profile & Settings":
        profile_page()
    elif page == "📊 Analytics & Insights":
        analytics_page()

def dashboard_page():
    """Enhanced dashboard with all metrics"""
    profile = st.session_state.user_profile
    
    # Key metrics
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card pulse-element">
            <h2>🔥 {profile['cooking_streak']}</h2>
            <p>Day Streak</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h2>📖 {profile['recipes_cooked']}</h2>
            <p>Recipes Cooked</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h2>❤️ {profile['recipes_liked']}</h2>
            <p>Recipes Liked</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h2>🌱 {profile['carbon_saved']:.1f}</h2>
            <p>kg CO₂ Saved</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col5:
        st.markdown(f"""
        <div class="metric-card">
            <h2>🏆 {len(profile['achievements'])}</h2>
            <p>Achievements</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Personalized recommendations
    st.markdown("## 🌟 Your Personalized Recommendations")
    
    recommendations = get_personalized_recommendations(n=6)
    
    # Display in 2 rows of 3
    for row in range(2):
        cols = st.columns(3)
        for col_idx, recipe in enumerate(recommendations[row*3:(row+1)*3]):
            if col_idx < len(recommendations[row*3:(row+1)*3]):
                with cols[col_idx]:
                    display_recipe_card(recipe, collection_key=f"dash_{row}_{col_idx}")
    
    # Recent achievements
    if profile['achievements']:
        st.markdown("## 🏆 Recent Achievements")
        for achievement in profile['achievements'][-3:]:
            st.markdown(f"""
            <div class="achievement-badge floating-element">
                🏆 {achievement}
            </div>
            """, unsafe_allow_html=True)
    
    # Quick stats chart
    st.markdown("## 📈 Your Cooking Journey")
    
    if profile['cooking_history']:
        # Create cooking frequency chart
        dates = [datetime.strptime(entry['cooked_date'], '%Y-%m-%d') for entry in profile['cooking_history']]
        date_counts = {}
        for date in dates:
            date_str = date.strftime('%Y-%m-%d')
            date_counts[date_str] = date_counts.get(date_str, 0) + 1
        
        if date_counts:
            df = pd.DataFrame(list(date_counts.items()), columns=['Date', 'Recipes'])
            df['Date'] = pd.to_datetime(df['Date'])
            
            fig = px.line(df, x='Date', y='Recipes', 
                         title="Daily Cooking Activity",
                         color_discrete_sequence=['#4caf50'])
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("🌱 Start cooking some recipes to see your journey here!")

def discovery_page():
    """Enhanced recipe discovery with advanced filtering"""
    st.markdown("## 🔍 Discover Amazing Recipes")
    
    # Advanced filters
    with st.expander("🎛️ Advanced Filters", expanded=True):
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            diet_filter = st.selectbox("🥗 Diet Type", 
                                     ['All'] + ['Omnivore', 'Vegetarian', 'Vegan', 'Keto', 'Paleo', 
                                               'Mediterranean', 'Gluten-Free', 'Low-Carb', 'High-Protein'])
        
        with col2:
            cuisine_filter = st.selectbox("🌎 Cuisine", 
                                        ['All'] + ['Italian', 'Asian', 'Mexican', 'French', 'Indian', 
                                                  'Mediterranean', 'American', 'Thai', 'Japanese', 'Korean'])
        
        with col3:
            difficulty_filter = st.selectbox("⚡ Difficulty", 
                                           ['All'] + ['Beginner', 'Intermediate', 'Advanced'])
        
        with col4:
            max_time = st.slider("⏰ Max Total Time (min)", 15, 240, 120)
        
        # Additional filters
        col5, col6, col7, col8 = st.columns(4)
        
        with col5:
            max_calories = st.slider("🔥 Max Calories", 100, 1000, 800)
        
        with col6:
            min_rating = st.slider("⭐ Min Rating", 1.0, 5.0, 3.5, 0.1)
        
        with col7:
            max_carbon = st.slider("🌱 Max Carbon (kg)", 0.5, 20.0, 10.0, 0.5)
        
        with col8:
            show_only_seasonal = st.checkbox("📅 Seasonal Only")
    
    # Get filtered recommendations
    recipes = st.session_state.sample_recipes
    
    # Apply all filters
    filtered_recipes = recipes.copy()
    
    if diet_filter != 'All':
        filtered_recipes = [r for r in filtered_recipes if r['diet'] == diet_filter]
    if cuisine_filter != 'All':
        filtered_recipes = [r for r in filtered_recipes if r['cuisine'] == cuisine_filter]
    if difficulty_filter != 'All':
        filtered_recipes = [r for r in filtered_recipes if r['difficulty'] == difficulty_filter]
    
    filtered_recipes = [r for r in filtered_recipes 
                       if r['total_time'] <= max_time 
                       and r['calories_per_serving'] <= max_calories
                       and r['rating'] >= min_rating
                       and r['carbon_footprint'] <= max_carbon]
    
    if show_only_seasonal:
        filtered_recipes = [r for r in filtered_recipes if r['seasonality_score'] >= 80]
    
    # Sort options
    sort_by = st.selectbox("🔄 Sort by", 
                          ['Recommended', 'Rating', 'Cooking Time', 'Carbon Footprint', 'Calories', 'Newest'])
    
    if sort_by == 'Recommended':
        # Use recommendation score
        for recipe in filtered_recipes:
            recipe['sort_score'] = recipe.get('recommendation_score', recipe['rating'])
        filtered_recipes.sort(key=lambda x: x['sort_score'], reverse=True)
    elif sort_by == 'Rating':
        filtered_recipes.sort(key=lambda x: x['rating'], reverse=True)
    elif sort_by == 'Cooking Time':
        filtered_recipes.sort(key=lambda x: x['total_time'])
    elif sort_by == 'Carbon Footprint':
        filtered_recipes.sort(key=lambda x: x['carbon_footprint'])
    elif sort_by == 'Calories':
        filtered_recipes.sort(key=lambda x: x['calories_per_serving'])
    elif sort_by == 'Newest':
        filtered_recipes.sort(key=lambda x: x['created_date'], reverse=True)
    
    st.markdown(f"### Found {len(filtered_recipes)} recipes matching your criteria")
    
    # Pagination
    recipes_per_page = 9
    total_pages = (len(filtered_recipes) + recipes_per_page - 1) // recipes_per_page
    
    if total_pages > 1:
        page_num = st.selectbox("Page", range(1, total_pages + 1), key="discovery_page")
        start_idx = (page_num - 1) * recipes_per_page
        end_idx = start_idx + recipes_per_page
        page_recipes = filtered_recipes[start_idx:end_idx]
    else:
        page_recipes = filtered_recipes[:recipes_per_page]
    
    # Display recipes in grid
    for i in range(0, len(page_recipes), 3):
        cols = st.columns(3)
        for j, recipe in enumerate(page_recipes[i:i+3]):
            with cols[j]:
                display_recipe_card(recipe, collection_key=f"disc_{i}_{j}")

def social_page():
    """Enhanced social features"""
    st.markdown("## 👥 Social Hub")
    
    tab1, tab2, tab3, tab4 = st.tabs(["🌟 Following", "🔥 Activity Feed", "🏆 Leaderboard", "👫 Friends"])
    
    with tab1:
        profile = st.session_state.user_profile
        
        st.markdown("### 👥 Your Cooking Network")
        
        if profile['friends']:
            for friend in profile['friends']:
                st.markdown(f"""
                <div class="social-feed-item">
                    <h4>{random.choice(['👨‍🍳', '👩‍🍳', '🧑‍🍳'])} {friend}</h4>
                    <p>Level {random.randint(5, 25)} Chef | {random.randint(50, 500)} recipes cooked</p>
                    <p>Latest: Cooked "Spicy Thai Curry" 2 hours ago</p>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info("🌱 Follow some chefs to see their activity here!")
        
        st.markdown("---")
        
        # Discover new chefs
        st.markdown("### 🔍 Discover Amazing Chefs")
        
        suggested_chefs = [
            {"name": "Chef Maria", "specialty": "Italian Cuisine", "level": 15, "followers": 1200},
            {"name": "Chef Kenji", "specialty": "Japanese Fusion", "level": 22, "followers": 850},
            {"name": "Chef Priya", "specialty": "Indian Spices", "level": 18, "followers": 950},
            {"name": "Chef Ahmed", "specialty": "Mediterranean", "level": 20, "followers": 1100}
        ]
        
        for chef in suggested_chefs:
            col1, col2, col3 = st.columns([2, 2, 1])
            
            with col1:
                st.markdown(f"""
                **{random.choice(['👨‍🍳', '👩‍🍳'])} {chef['name']}**  
                {chef['specialty']}
                """)
            
            with col2:
                st.markdown(f"""
                Level {chef['level']} | {chef['followers']} followers  
                Sustainability Score: {random.randint(85, 98)}/100
                """)
            
            with col3:
                if st.button("Follow", key=f"follow_{chef['name']}"):
                    if chef['name'] not in profile['friends']:
                        profile['friends'].append(chef['name'])
                        award_xp(5, f"following {chef['name']}")
                        st.success(f"Now following {chef['name']}!")
                        st.rerun()
    
    with tab2:
        st.markdown("### 🔥 Activity Feed")
        
        feed_items = st.session_state.social_feed
        
        for item in feed_items:
            if item['action'] == 'cooked':
                st.markdown(f"""
                <div class="social-feed-item">
                    <h4>{item['avatar']} {item['user']} cooked {item['recipe']}</h4>
                    <p>{item['time']} | ❤️ {item['likes']} likes | 💬 {item['comments']} comments</p>
                </div>
                """, unsafe_allow_html=True)
            elif item['action'] == 'achieved':
                st.markdown(f"""
                <div class="social-feed-item">
                    <h4>{item['avatar']} {item['user']} earned {item['achievement']}</h4>
                    <p>{item['time']} | ❤️ {item['likes']} likes | 💬 {item['comments']} comments</p>
                </div>
                """, unsafe_allow_html=True)
            elif item['action'] == 'shared':
                st.markdown(f"""
                <div class="social-feed-item">
                    <h4>{item['avatar']} {item['user']} shared {item['recipe']}</h4>
                    <p>{item['time']} | ❤️ {item['likes']} likes | 💬 {item['comments']} comments</p>
                </div>
                """, unsafe_allow_html=True)
    
    with tab3:
        st.markdown("### 🏆 Global Leaderboard")
        
        leaderboard = st.session_state.global_leaderboard
        
        for i, chef in enumerate(leaderboard[:10]):
            rank_emoji = "🥇" if i == 0 else "🥈" if i == 1 else "🥉" if i == 2 else f"{i+1}."
            
            st.markdown(f"""
            <div class="leaderboard-item">
                <h4>{rank_emoji} {chef['avatar']} {chef['name']}</h4>
                <p>Level {chef['level']} | {chef['xp']:,} XP | {chef['recipes_cooked']} recipes</p>
                <p>🌱 {chef['carbon_saved']} kg CO₂ saved | Specialty: {chef['specialty']}</p>
            </div>
            """, unsafe_allow_html=True)
    
    with tab4:
        st.markdown("### 👫 Friends & Community")
        
        # Share your profile
        st.markdown("#### 📤 Share Your Profile")
        if st.button("Generate Share Link"):
            st.success("🔗 Profile link copied! Share with friends: https://culinaryquest.app/chef/explorer")
        
        # Community stats
        st.markdown("#### 📊 Community Impact")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("👥 Active Chefs", "12,847")
        with col2:
            st.metric("🍽️ Recipes Cooked", "1,294,726")
        with col3:
            st.metric("🌱 CO₂ Saved", "45.2 tons")

def challenges_page():
    """Enhanced challenges and achievements"""
    st.markdown("## 🏆 Challenges & Achievements")
    
    tab1, tab2, tab3 = st.tabs(["🎯 Active Challenges", "🏅 Your Achievements", "🎖️ Badge Collection"])
    
    with tab1:
        st.markdown("### 🎯 Your Active Challenges")
        
        challenges = st.session_state.active_challenges
        
        for challenge in challenges:
            progress_percent = (challenge['progress'] / challenge['target']) * 100
            
            st.markdown(f"""
            <div class="challenge-card">
                <h4>{challenge['name']}</h4>
                <p>{challenge['description']}</p>
                <p><strong>Progress:</strong> {challenge['progress']}/{challenge['target']} ({progress_percent:.0f}%)</p>
                <div style="background: #e0e0e0; border-radius: 15px; overflow: hidden; margin: 0.5rem 0;">
                    <div class="level-progress" style="width: {progress_percent}%"></div>
                </div>
                <p><strong>Reward:</strong> {challenge['reward']}</p>
                <p><strong>Expires:</strong> {challenge['expires']}</p>
            </div>
            """, unsafe_allow_html=True)
            
            if challenge['progress'] < challenge['target']:
                if st.button(f"🚀 Work on Challenge", key=f"challenge_{challenge['id']}"):
                    challenge['progress'] += 1
                    if challenge['progress'] >= challenge['target']:
                        st.balloons()
                        award_xp(100, f"completing {challenge['name']} challenge")
                        st.success(f"🎉 Challenge completed! You earned: {challenge['reward']}")
                    else:
                        st.success("Great progress! Keep going!")
                    st.rerun()
        
        # Create new challenge
        st.markdown("---")
        st.markdown("### ➕ Suggest a Challenge")
        
        with st.form("new_challenge"):
            challenge_name = st.text_input("Challenge Name")
            challenge_desc = st.text_area("Description")
            challenge_target = st.number_input("Target", min_value=1, value=5)
            
            if st.form_submit_button("Suggest Challenge"):
                st.success("Thanks for your suggestion! We'll review it for the community.")
    
    with tab2:
        st.markdown("### 🏅 Your Achievements")
        
        profile = st.session_state.user_profile
        all_achievements = [
            "First Love", "Recipe Explorer", "Social Butterfly", "Eco Warrior", 
            "Streak Master", "Collection Curator", "Diverse Palate", "Speed Chef",
            "Health Guru", "Sustainability Champion", "Global Explorer", "Master Chef"
        ]
        
        # Display achievements in grid
        cols = st.columns(3)
        for i, achievement in enumerate(all_achievements):
            with cols[i % 3]:
                if achievement in profile['achievements']:
                    st.markdown(f"""
                    <div class="achievement-badge">
                        🏆 {achievement}
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    st.markdown(f"""
                    <div style="background: #f0f0f0; padding: 0.7rem 1.2rem; border-radius: 25px; margin: 0.3rem; text-align: center; opacity: 0.5;">
                        🔒 {achievement}
                    </div>
                    """, unsafe_allow_html=True)
        
        # Achievement progress
        st.markdown("#### 📈 Achievement Progress")
        achievement_count = len(profile['achievements'])
        total_achievements = len(all_achievements)
        progress = (achievement_count / total_achievements) * 100
        
        st.markdown(f"""
        <div style="margin: 1rem 0;">
            <p><strong>Progress:</strong> {achievement_count}/{total_achievements} ({progress:.0f}%)</p>
            <div style="background: #e0e0e0; border-radius: 15px; overflow: hidden;">
                <div class="level-progress" style="width: {progress}%"></div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    with tab3:
        st.markdown("### 🎖️ Badge Collection")
        
        badge_categories = {
            "🌱 Sustainability": ["Eco Warrior", "Carbon Saver", "Seasonal Expert", "Plant Pioneer"],
            "🍽️ Cooking Skills": ["Speed Chef", "Master Chef", "Technique Expert", "Flavor Master"],
            "👥 Social": ["Social Butterfly", "Community Leader", "Mentor", "Influencer"],
            "🎯 Challenges": ["Challenge Crusher", "Goal Getter", "Persistent", "Achiever"],
            "🌍 Global": ["Global Explorer", "Culture Enthusiast", "Diverse Palate", "World Traveler"]
        }
        
        for category, badges in badge_categories.items():
            st.markdown(f"#### {category}")
            
            cols = st.columns(4)
            for i, badge in enumerate(badges):
                with cols[i % 4]:
                    earned = badge in profile['achievements']
                    if earned:
                        st.markdown(f"""
                        <div class="achievement-badge">
                            🎖️ {badge}
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.markdown(f"""
                        <div style="background: #f0f0f0; padding: 0.5rem; border-radius: 10px; text-align: center; opacity: 0.5;">
                            🔒 {badge}
                        </div>
                        """, unsafe_allow_html=True)

def collections_page():
    """Enhanced recipe collections"""
    st.markdown("## 📚 My Recipe Collections")
    
    profile = st.session_state.user_profile
    recipes = st.session_state.sample_recipes
    
    # Create new collection
    with st.expander("➕ Create New Collection"):
        with st.form("new_collection"):
            collection_name = st.text_input("Collection Name")
            collection_desc = st.text_area("Description (optional)")
            
            if st.form_submit_button("Create Collection"):
                if collection_name and collection_name not in profile['recipe_collections']:
                    profile['recipe_collections'][collection_name] = []
                    st.success(f"Created collection: {collection_name}")
                    st.rerun()
                elif collection_name in profile['recipe_collections']:
                    st.error("Collection already exists!")
    
    # Display collections
    for collection_name, recipe_ids in profile['recipe_collections'].items():
        with st.expander(f"📁 {collection_name} ({len(recipe_ids)} recipes)", expanded=True):
            if recipe_ids:
                collection_recipes = [r for r in recipes if r['id'] in recipe_ids]
                
                # Display recipes in grid
                for i in range(0, len(collection_recipes), 3):
                    cols = st.columns(3)
                    for j, recipe in enumerate(collection_recipes[i:i+3]):
                        if j < len(collection_recipes[i:i+3]):
                            with cols[j]:
                                display_recipe_card(recipe, collection_key=f"coll_{collection_name}_{i}_{j}")
                                
                                # Remove from collection button
                                if st.button(f"🗑️ Remove", key=f"remove_{collection_name}_{recipe['id']}"):
                                    profile['recipe_collections'][collection_name].remove(recipe['id'])
                                    st.success(f"Removed from {collection_name}")
                                    st.rerun()
            else:
                st.info(f"No recipes in {collection_name} yet. Start adding some!")
            
            # Delete collection (except default ones)
            if collection_name not in ['Favorites', 'Want to Try', 'Cooked']:
                if st.button(f"🗑️ Delete {collection_name}", key=f"delete_{collection_name}"):
                    del profile['recipe_collections'][collection_name]
                    st.success(f"Deleted collection: {collection_name}")
                    st.rerun()
    
    # Collection stats
    st.markdown("---")
    st.markdown("### 📊 Collection Statistics")
    
    total_saved = sum(len(recipe_ids) for recipe_ids in profile['recipe_collections'].values())
    unique_saved = len(set().union(*profile['recipe_collections'].values()) if profile['recipe_collections'] else set())
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("📚 Total Saved", total_saved)
    with col2:
        st.metric("🆔 Unique Recipes", unique_saved)
    with col3:
        st.metric("📁 Collections", len(profile['recipe_collections']))

def profile_page():
    """Enhanced profile and settings"""
    st.markdown("## 👤 Profile & Settings")
    
    tab1, tab2, tab3, tab4 = st.tabs(["🎭 Avatar & Profile", "⚙️ Preferences", "📊 Statistics", "💾 Data Export"])
    
    with tab1:
        profile = st.session_state.user_profile
        
        col1, col2 = st.columns([1, 1])
        
        with col1:
            display_user_avatar()
        
        with col2:
            st.markdown("### ✏️ Edit Profile")
            
            with st.form("profile_form"):
                new_name = st.text_input("Chef Name", value=profile['name'])
                
                cooking_skills = ['Beginner', 'Intermediate', 'Advanced', 'Professional']
                new_skill = st.selectbox("Cooking Skill Level", 
                                       cooking_skills,
                                       index=cooking_skills.index(profile['cooking_skill']))
                
                time_preferences = ['Any', 'Quick (≤30 min)', 'Medium (30-60 min)', 'Long (60+ min)']
                new_time_pref = st.selectbox("Preferred Cooking Time",
                                           time_preferences,
                                           index=time_preferences.index(profile['time_preference']))
                
                if st.form_submit_button("💾 Save Profile"):
                    profile['name'] = new_name
                    profile['cooking_skill'] = new_skill
                    profile['time_preference'] = new_time_pref
                    st.success("Profile updated successfully!")
                    st.rerun()
    
    with tab2:
        st.markdown("### 🥗 Dietary Preferences")
        
        diet_options = ['Omnivore', 'Vegetarian', 'Vegan', 'Keto', 'Paleo', 'Mediterranean', 'Gluten-Free', 'Low-Carb', 'High-Protein']
        selected_diets = st.multiselect("Select Your Diets", 
                                       diet_options,
                                       default=profile['diet_preferences'])
        
        st.markdown("### 🚫 Allergies & Restrictions")
        
        allergy_options = ['Nuts', 'Dairy', 'Eggs', 'Soy', 'Shellfish', 'Fish', 'Wheat', 'Sesame']
        selected_allergies = st.multiselect("Food Allergies", 
                                          allergy_options,
                                          default=profile['allergies'])
        
        st.markdown("### 🌍 Favorite Cuisines")
        
        cuisine_options = ['Italian', 'Asian', 'Mexican', 'French', 'Indian', 'Mediterranean', 'American', 'Thai', 'Japanese', 'Korean']
        selected_cuisines = st.multiselect("Favorite Cuisines", 
                                         cuisine_options,
                                         default=profile['favorite_cuisines'])
        
        if st.button("💾 Save Preferences"):
            profile['diet_preferences'] = selected_diets
            profile['allergies'] = selected_allergies
            profile['favorite_cuisines'] = selected_cuisines
            st.success("Preferences updated!")
            st.rerun()
    
    with tab3:
        st.markdown("### 📊 Your Cooking Statistics")
        
        level, current_xp, xp_needed = calculate_level_and_xp()
        
        # Key stats
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("👨‍🍳 Chef Level", level)
        with col2:
            st.metric("⚡ Total XP", f"{profile['total_xp']:,}")
        with col3:
            st.metric("🍽️ Recipes Cooked", profile['recipes_cooked'])
        with col4:
            st.metric("🔥 Best Streak", profile['cooking_streak'])
        
        # Environmental impact
        st.markdown("#### 🌍 Environmental Impact")
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🌱 CO₂ Saved", f"{profile['carbon_saved']:.1f} kg")
        with col2:
            car_km = profile['carbon_saved'] * 4  # 1kg CO2 ≈ 4km driving
            st.metric("🚗 Equivalent Car KM", f"{car_km:.0f} km")
        with col3:
            tree_days = profile['carbon_saved'] * 0.05  # 1 tree absorbs ~20kg/year
            st.metric("🌳 Tree Days", f"{tree_days:.0f} days")
        
        # Activity timeline
        if profile['cooking_history']:
            st.markdown("#### 📈 Cooking Timeline")
            
            # Group by month
            monthly_data = {}
            for entry in profile['cooking_history']:
                month = entry['cooked_date'][:7]  # YYYY-MM
                monthly_data[month] = monthly_data.get(month, 0) + 1
            
            if len(monthly_data) > 1:
                df = pd.DataFrame(list(monthly_data.items()), columns=['Month', 'Recipes'])
                fig = px.bar(df, x='Month', y='Recipes', title="Monthly Cooking Activity")
                st.plotly_chart(fig, use_container_width=True)
    
    with tab4:
        st.markdown("### 💾 Data Export & Import")
        
        # Export profile
        if st.button("📤 Export Profile Data"):
            profile_data = profile.copy()
            profile_json = json.dumps(profile_data, indent=2, default=str)
            
            st.download_button(
                label="⬇️ Download Profile JSON",
                data=profile_json,
                file_name=f"culinary_quest_profile_{datetime.now().strftime('%Y%m%d')}.json",
                mime="application/json"
            )
        
        # Export recipes
        if st.button("📤 Export Liked Recipes"):
            liked_recipe_ids = profile['recipe_collections']['Favorites']
            liked_recipes = [r for r in st.session_state.sample_recipes if r['id'] in liked_recipe_ids]
            
            if liked_recipes:
                df = pd.DataFrame(liked_recipes)
                csv = df.to_csv(index=False)
                
                st.download_button(
                    label="⬇️ Download Recipes CSV",
                    data=csv,
                    file_name=f"favorite_recipes_{datetime.now().strftime('%Y%m%d')}.csv",
                    mime="text/csv"
                )
            else:
                st.info("No favorite recipes to export yet!")
        
        # Reset profile
        st.markdown("---")
        st.markdown("#### ⚠️ Danger Zone")
        
        if st.button("🔄 Reset Profile", type="secondary"):
            if st.button("✅ Confirm Reset", type="primary"):
                # Reset to initial state
                del st.session_state.user_profile
                st.success("Profile reset successfully!")
                st.rerun()

def analytics_page():
    """Enhanced analytics and insights"""
    st.markdown("## 📊 Analytics & Insights")
    
    profile = st.session_state.user_profile
    recipes = st.session_state.sample_recipes
    
    # Overview metrics
    st.markdown("### 📈 Overview")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        st.metric("📅 Days Active", (datetime.now() - datetime.strptime(profile['join_date'], '%Y-%m-%d')).days)
    with col2:
        avg_per_week = profile['recipes_cooked'] / max(1, (datetime.now() - datetime.strptime(profile['join_date'], '%Y-%m-%d')).days / 7)
        st.metric("📊 Avg Recipes/Week", f"{avg_per_week:.1f}")
    with col3:
        completion_rate = len(profile['recipe_collections']['Cooked']) / max(1, len(profile['recipe_collections']['Favorites'])) * 100
        st.metric("✅ Completion Rate", f"{completion_rate:.0f}%")
    with col4:
        if profile['cooking_history']:
            avg_carbon = sum(r['carbon_footprint'] for r in profile['cooking_history']) / len(profile['cooking_history'])
            st.metric("🌱 Avg Carbon/Recipe", f"{avg_carbon:.1f} kg")
        else:
            st.metric("🌱 Avg Carbon/Recipe", "0 kg")
    with col5:
        diversity = len(set(r['cuisine'] for r in profile['cooking_history'] if 'cuisine' in r))
        st.metric("🌍 Cuisine Diversity", diversity)
    
    # Cooking patterns
    if profile['cooking_history']:
        st.markdown("### 📊 Cooking Patterns")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Cuisine distribution
            cuisines = [r['cuisine'] for r in profile['cooking_history']]
            cuisine_counts = pd.Series(cuisines).value_counts()
            
            fig = px.pie(values=cuisine_counts.values, names=cuisine_counts.index, 
                        title="Cuisine Distribution")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            # Difficulty progression
            difficulties = [r['difficulty'] for r in profile['cooking_history']]
            difficulty_counts = pd.Series(difficulties).value_counts()
            
            fig = px.bar(x=difficulty_counts.index, y=difficulty_counts.values,
                        title="Difficulty Level Distribution")
            st.plotly_chart(fig, use_container_width=True)
        
        # Carbon footprint over time
        st.markdown("### 🌱 Environmental Impact Over Time")
        
        if len(profile['cooking_history']) > 1:
            carbon_data = []
            for entry in profile['cooking_history']:
                carbon_data.append({
                    'Date': entry['cooked_date'],
                    'Carbon': entry['carbon_footprint']
                })
            
            df = pd.DataFrame(carbon_data)
            df['Date'] = pd.to_datetime(df['Date'])
            df = df.sort_values('Date')
            df['Cumulative_Saved'] = (8.0 - df['Carbon']).cumsum()  # vs average 8kg meal
            
            fig = px.line(df, x='Date', y='Cumulative_Saved', 
                         title="Cumulative CO₂ Saved vs Average Meals")
            st.plotly_chart(fig, use_container_width=True)
    
    # Recommendations insights
    st.markdown("### 🎯 Recommendation Insights")
    
    # Analyze user preferences vs actual cooking
    if profile['cooking_history']:
        cooked_diets = [r['diet'] for r in profile['cooking_history']]
        preferred_diets = profile['diet_preferences']
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 🥗 Diet Preferences vs Reality")
            diet_comparison = pd.DataFrame({
                'Diet': list(set(cooked_diets + preferred_diets)),
                'Preferred': [1 if diet in preferred_diets else 0 for diet in set(cooked_diets + preferred_diets)],
                'Actually_Cooked': [cooked_diets.count(diet) for diet in set(cooked_diets + preferred_diets)]
            })
            
            fig = px.scatter(diet_comparison, x='Preferred', y='Actually_Cooked', 
                           hover_data=['Diet'], title="Preference vs Reality")
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.markdown("#### ⏰ Cooking Time Analysis")
            cooking_times = [r['total_time'] for r in profile['cooking_history']]
            
            time_categories = []
            for time in cooking_times:
                if time <= 30:
                    time_categories.append('Quick (≤30min)')
                elif time <= 60:
                    time_categories.append('Medium (30-60min)')
                else:
                    time_categories.append('Long (60+min)')
            
            time_counts = pd.Series(time_categories).value_counts()
            fig = px.pie(values=time_counts.values, names=time_counts.index,
                        title="Cooking Time Distribution")
            st.plotly_chart(fig, use_container_width=True)
    
    else:
        st.info("🌱 Start cooking some recipes to see detailed analytics!")

if __name__ == "__main__":
    main()