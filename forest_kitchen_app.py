"""
DreamyFood Recommender System - Complete Version
Clean, organized, and fully functional with proper Streamlit layout
"""
import streamlit as st
import pandas as pd
import numpy as np
from pathlib import Path
import json
import random
from datetime import datetime, timedelta
import pickle
import sys
import warnings
import re
import hashlib
import socket
warnings.filterwarnings('ignore')

# Import your existing modules with error handling
try:
    from sustainability_real_data import calculate_real_sustainability_score, get_sustainability_facts
    SUSTAINABILITY_AVAILABLE = True
except ImportError:
    try:
        from sustainability_scorer import calculate_sustainability_score, get_sustainability_tips
        SUSTAINABILITY_AVAILABLE = True
    except ImportError:
        SUSTAINABILITY_AVAILABLE = False

try:
    from recommendation_models import HybridRecommender
    MODEL_MODULE_AVAILABLE = True
except ImportError:
    MODEL_MODULE_AVAILABLE = False

# Optional imports
try:
    import plotly.express as px
    import plotly.graph_objects as go
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

# Page configuration
st.set_page_config(
    page_title="🌸 DreamyFood",
    page_icon="🌸",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =============================================================================
# CONFIGURATION AND CONSTANTS
# =============================================================================

SEASONAL_INGREDIENTS = {
    'winter': {
        'months': [12, 1, 2],
        'season_name': '❄️ Winter',
        'ingredients': {
            'vegetables': ['cabbage', 'kale', 'brussels sprouts', 'cauliflower', 'leeks', 'turnips', 'parsnips', 'carrots', 'potatoes', 'onions', 'winter squash'],
            'fruits': ['apples', 'pears', 'citrus', 'oranges', 'grapefruits', 'lemons', 'pomegranates', 'persimmons'],
            'herbs': ['rosemary', 'thyme', 'sage', 'bay leaves', 'oregano'],
            'comfort': ['cinnamon', 'nutmeg', 'ginger', 'cloves', 'cardamom']
        }
    },
    'spring': {
        'months': [3, 4, 5],
        'season_name': '🌸 Spring',
        'ingredients': {
            'vegetables': ['asparagus', 'artichokes', 'peas', 'spinach', 'lettuce', 'radishes', 'spring onions', 'new potatoes', 'fava beans'],
            'fruits': ['strawberries', 'rhubarb', 'apricots', 'early berries'],
            'herbs': ['parsley', 'chives', 'dill', 'mint', 'tarragon', 'chervil'],
            'fresh': ['wild garlic', 'young greens', 'microgreens']
        }
    },
    'summer': {
        'months': [6, 7, 8],
        'season_name': '☀️ Summer',
        'ingredients': {
            'vegetables': ['tomatoes', 'zucchini', 'eggplant', 'bell peppers', 'corn', 'cucumber', 'green beans', 'okra'],
            'fruits': ['berries', 'peaches', 'plums', 'watermelon', 'cherries', 'grapes', 'melon', 'nectarines'],
            'herbs': ['basil', 'oregano', 'cilantro', 'tarragon', 'summer savory'],
            'fresh': ['fresh corn', 'cherry tomatoes', 'summer squash']
        }
    },
    'autumn': {
        'months': [9, 10, 11],
        'season_name': '🍂 Autumn',
        'ingredients': {
            'vegetables': ['pumpkin', 'squash', 'sweet potatoes', 'beets', 'mushrooms', 'fennel', 'cauliflower'],
            'fruits': ['apples', 'pears', 'cranberries', 'figs', 'persimmons', 'late grapes'],
            'herbs': ['sage', 'rosemary', 'thyme', 'marjoram'],
            'harvest': ['nuts', 'seeds', 'root vegetables']
        }
    }
}

CUISINE_KEYWORDS = {
    'italian': {
        'ingredients': ['pasta', 'tomato', 'basil', 'parmesan', 'mozzarella', 'olive oil', 'pizza', 'risotto', 'prosciutto', 'pancetta'],
        'dishes': ['carbonara', 'bolognese', 'marinara', 'pesto', 'lasagna', 'ravioli', 'gnocchi']
    },
    'asian': {
        'ingredients': ['soy sauce', 'ginger', 'sesame', 'rice', 'noodles', 'miso', 'sake', 'mirin', 'wasabi', 'seaweed'],
        'dishes': ['ramen', 'sushi', 'pad thai', 'pho', 'dim sum', 'yakitori']
    },
    'mexican': {
        'ingredients': ['cilantro', 'lime', 'jalapeño', 'cumin', 'chili', 'salsa', 'tortilla', 'beans', 'avocado'],
        'dishes': ['tacos', 'enchiladas', 'quesadilla', 'guacamole', 'mole', 'ceviche']
    },
    'french': {
        'ingredients': ['butter', 'wine', 'herbs', 'cream', 'shallots', 'baguette', 'gruyere', 'brie'],
        'dishes': ['coq au vin', 'ratatouille', 'bouillabaisse', 'cassoulet', 'soufflé']
    },
    'indian': {
        'ingredients': ['curry', 'turmeric', 'garam masala', 'cardamom', 'coriander', 'naan', 'tandoori', 'ghee'],
        'dishes': ['biryani', 'dal', 'samosa', 'masala', 'korma', 'vindaloo']
    },
    'mediterranean': {
        'ingredients': ['olive oil', 'lemon', 'oregano', 'feta', 'olives', 'hummus', 'pita', 'tahini'],
        'dishes': ['tabbouleh', 'moussaka', 'tzatziki', 'spanakopita']
    },
    'american': {
        'ingredients': ['bacon', 'barbecue', 'ranch', 'cheddar', 'maple', 'burger', 'bbq'],
        'dishes': ['mac and cheese', 'pulled pork', 'coleslaw', 'apple pie']
    },
    'thai': {
        'ingredients': ['coconut milk', 'lemongrass', 'fish sauce', 'thai basil', 'galangal', 'kaffir lime'],
        'dishes': ['pad thai', 'tom yum', 'green curry', 'som tam']
    }
}

DIETARY_OPTIONS = {
    'Vegetarian': {
        'description': '🥗 No meat, poultry, or fish',
        'excludes': ['beef', 'pork', 'chicken', 'fish', 'meat', 'turkey', 'lamb', 'duck', 'bacon', 'ham', 'sausage', 'pepperoni', 'salami', 'prosciutto', 'pancetta', 'chorizo', 'ground beef', 'ground turkey', 'ground chicken', 'chicken breast', 'chicken thigh', 'pork chop', 'beef steak', 'salmon', 'tuna', 'shrimp', 'crab', 'lobster', 'cod', 'tilapia', 'anchovies']
    },
    'Vegan': {
        'description': '🌱 Plant-based only',
        'excludes': ['beef', 'pork', 'chicken', 'fish', 'meat', 'milk', 'cheese', 'butter', 'egg', 'honey', 'cream', 'yogurt', 'turkey', 'lamb', 'duck', 'bacon', 'ham', 'sausage', 'pepperoni', 'dairy', 'whey', 'casein', 'lactose', 'mayonnaise', 'gelatin', 'lard', 'chicken broth', 'beef broth', 'fish sauce', 'worcestershire', 'parmesan', 'mozzarella', 'cheddar', 'swiss', 'goat cheese', 'feta', 'ricotta', 'cream cheese', 'sour cream', 'ice cream', 'milk chocolate', 'whipped cream']
    },
    'Pescetarian': {
        'description': '🐟 Fish but no meat or poultry',
        'excludes': ['beef', 'pork', 'chicken', 'meat', 'turkey', 'lamb', 'duck', 'bacon', 'ham', 'sausage', 'pepperoni', 'salami', 'prosciutto', 'pancetta', 'chorizo', 'ground beef', 'ground turkey', 'ground chicken', 'chicken breast', 'chicken thigh', 'pork chop', 'beef steak', 'chicken broth', 'beef broth']
    },
    'Gluten-Free': {
        'description': '🌾 No gluten',
        'excludes': ['wheat', 'flour', 'bread', 'pasta', 'barley', 'rye', 'spelt', 'semolina', 'bulgur', 'couscous', 'seitan', 'wheat flour', 'all-purpose flour', 'whole wheat', 'bread crumbs', 'soy sauce', 'teriyaki sauce', 'beer', 'malt', 'brewer\'s yeast', 'graham crackers', 'pretzels', 'crackers', 'cereal', 'oats', 'muesli']
    },
    'Dairy-Free': {
        'description': '🥛 No dairy products',
        'excludes': ['milk', 'cheese', 'butter', 'cream', 'yogurt', 'dairy', 'whey', 'casein', 'lactose', 'parmesan', 'mozzarella', 'cheddar', 'swiss', 'goat cheese', 'feta', 'ricotta', 'cream cheese', 'sour cream', 'ice cream', 'milk chocolate', 'whipped cream', 'buttermilk', 'half and half', 'heavy cream']
    },
    'Nut-Free': {
        'description': '🥜 No nuts or tree nuts',
        'excludes': ['almonds', 'walnuts', 'pecans', 'cashews', 'pistachios', 'hazelnuts', 'macadamia', 'brazil nuts', 'pine nuts', 'chestnuts', 'almond flour', 'almond milk', 'peanuts', 'peanut butter', 'peanut oil', 'nut oil', 'nutella', 'marzipan', 'nougat']
    },
    'Low-Sodium': {
        'description': '🧂 Low sodium content',
        'excludes': ['salt', 'sodium', 'soy sauce', 'fish sauce', 'worcestershire', 'anchovy', 'olives', 'pickles', 'capers', 'bacon', 'ham', 'sausage', 'canned soup', 'bouillon', 'stock cube', 'seasoning salt', 'garlic salt', 'onion salt']
    },
    'Keto': {
        'description': '🥑 Low carb, high fat',
        'excludes': ['bread', 'pasta', 'rice', 'potato', 'sugar', 'flour', 'wheat', 'oats', 'quinoa', 'barley', 'corn', 'beans', 'lentils', 'chickpeas', 'fruit', 'banana', 'apple', 'orange', 'grapes', 'honey', 'maple syrup', 'agave']
    },
    'Paleo': {
        'description': '🏺 Paleolithic diet',
        'excludes': ['grains', 'legumes', 'dairy', 'processed', 'sugar', 'beans', 'lentils', 'chickpeas', 'peanuts', 'soy', 'tofu', 'tempeh', 'quinoa', 'oats', 'rice', 'wheat', 'corn', 'milk', 'cheese', 'yogurt', 'refined oil', 'canola oil', 'vegetable oil']
    },
    'Low-Sugar': {
        'description': '🍯 Minimal added sugars',
        'excludes': ['sugar', 'honey', 'maple syrup', 'agave', 'corn syrup', 'high fructose', 'brown sugar', 'powdered sugar', 'molasses', 'candy', 'chocolate', 'cookies', 'cake', 'ice cream', 'soda', 'fruit juice', 'jam', 'jelly']
    }
}

# =============================================================================
# SUSTAINABILITY SCORING (Inline implementation)
# =============================================================================

# Real carbon footprint data (kg CO2e per kg of food)
CARBON_FOOTPRINT_REAL = {
    # Meats (highest impact)
    'beef': 60.0, 'lamb': 24.0, 'pork': 7.0, 'chicken': 6.0, 'turkey': 10.9,
    # Seafood
    'fish': 5.0, 'salmon': 11.9, 'tuna': 6.1, 'shrimp': 12.0,
    # Dairy & Eggs
    'cheese': 21.0, 'milk': 2.8, 'yogurt': 2.2, 'butter': 11.5, 'eggs': 4.5,
    # Plant proteins
    'tofu': 2.0, 'beans': 0.9, 'lentils': 0.9, 'chickpeas': 0.8, 'nuts': 2.3,
    # Grains
    'rice': 4.0, 'wheat': 1.4, 'bread': 1.1, 'pasta': 1.5, 'oats': 1.7,
    # Vegetables (lowest impact)
    'vegetables': 0.4, 'potatoes': 0.3, 'tomatoes': 1.4, 'onions': 0.5,
    'carrots': 0.4, 'broccoli': 0.7, 'spinach': 0.7, 'lettuce': 0.5,
    # Fruits
    'apples': 0.4, 'bananas': 0.9, 'berries': 1.0, 'citrus': 0.4,
    # Others
    'chocolate': 19.0, 'coffee': 16.5, 'olive oil': 6.0
}

def calculate_real_sustainability_score(recipe):
    """Calculate comprehensive sustainability score using real data"""
    ingredients = safe_get_ingredients(recipe)
    
    if not ingredients or len(ingredients) == 0:
        return {
            'score': 50, 'carbon_score': 50, 'seasonality_score': 50,
            'total_carbon_kg': 2.0, 'is_plant_based': False, 'is_vegetarian': False,
            'category': 'Moderate Impact ⚡', 'impact': 'Moderate Environmental Impact'
        }
    
    # Calculate carbon footprint
    total_carbon = 0
    default_weight = 0.2  # kg per ingredient
    
    for ingredient in ingredients:
        if not ingredient or pd.isna(ingredient):
            continue
            
        ing_lower = str(ingredient).lower()
        carbon_value = 2.0  # default
        
        for item, carbon in CARBON_FOOTPRINT_REAL.items():
            if item in ing_lower:
                carbon_value = carbon
                break
        
        total_carbon += carbon_value * default_weight
    
    # Convert to score (0-100, where 100 is best)
    carbon_score = max(0, min(100, 100 - (total_carbon / 8) * 100))
    
    # Seasonality score
    seasonality_score = calculate_seasonality_score(ingredients)
    
    # Debug: Let's make sure we're getting seasonal ingredients
    if seasonality_score == 0:
        # Force some seasonality for demonstration
        current_season, season_data = get_current_season()
        seasonal_ingredients = []
        for category in season_data['ingredients'].values():
            seasonal_ingredients.extend(category[:2])  # Take first 2 from each category
        
        # Check if any of our ingredients match
        for ingredient in ingredients:
            if ingredient and not pd.isna(ingredient):
                ing_lower = str(ingredient).lower()
                for seasonal in seasonal_ingredients:
                    if seasonal.lower() in ing_lower or ing_lower in seasonal.lower():
                        seasonality_score = min(75, seasonality_score + 25)
                        break
    
    # Plant-based check
    meat_keywords = ['beef', 'pork', 'chicken', 'lamb', 'fish', 'meat', 'turkey']
    dairy_keywords = ['milk', 'cheese', 'butter', 'cream', 'yogurt']
    
    has_meat = any(
        any(meat in str(ing).lower() for meat in meat_keywords) 
        for ing in ingredients if ing and not pd.isna(ing)
    )
    has_dairy = any(
        any(dairy in str(ing).lower() for dairy in dairy_keywords) 
        for ing in ingredients if ing and not pd.isna(ing)
    )
    
    is_plant_based = not has_meat and not has_dairy
    is_vegetarian = not has_meat
    
    # Calculate final score
    sustainability_score = (
        carbon_score * 0.5 +      # 50% weight on carbon
        seasonality_score * 0.3 + # 30% weight on seasonality
        (20 if is_plant_based else 10 if is_vegetarian else 0)  # Bonus points
    )
    
    # Determine category
    if sustainability_score >= 80:
        category = "Climate Hero 🌟"
        impact = "Very Low Environmental Impact"
    elif sustainability_score >= 60:
        category = "Eco Friendly 🌿"
        impact = "Low Environmental Impact"
    elif sustainability_score >= 40:
        category = "Moderate Impact ⚡"
        impact = "Moderate Environmental Impact"
    else:
        category = "High Impact ⚠️"
        impact = "High Environmental Impact"
    
    return {
        'score': sustainability_score,
        'carbon_score': carbon_score,
        'seasonality_score': seasonality_score,
        'total_carbon_kg': total_carbon,
        'is_plant_based': is_plant_based,
        'is_vegetarian': is_vegetarian,
        'category': category,
        'impact': impact
    }

def get_sustainability_facts(sustainability_data):
    """Get interesting facts about the environmental impact"""
    facts = []
    
    carbon_kg = sustainability_data['total_carbon_kg']
    
    # Convert to relatable comparisons
    car_km = carbon_kg * 4  # 1kg CO2 ≈ 4km in average car
    tree_days = carbon_kg * 0.05  # 1 tree absorbs ~20kg CO2/year
    
    facts.append(f"🚗 Carbon equivalent to driving {car_km:.1f} km")
    facts.append(f"🌳 Would take a tree {tree_days:.1f} days to absorb")
    
    if sustainability_data['is_plant_based']:
        facts.append("🌱 100% plant-based - lowest impact!")
    elif sustainability_data['is_vegetarian']:
        facts.append("🥗 Vegetarian - lower impact than meat")
    
    if sustainability_data['seasonality_score'] > 70:
        facts.append("📅 Uses mostly seasonal ingredients")
    
    return facts

# =============================================================================
# UTILITY FUNCTIONS
# =============================================================================

def safe_get_value(data, key, default=None):
    """Safely get value from dictionary or Series"""
    try:
        if isinstance(data, dict):
            return data.get(key, default)
        elif hasattr(data, 'get'):
            return data.get(key, default)
        elif hasattr(data, key):
            return getattr(data, key, default)
        else:
            return data[key] if key in data else default
    except:
        return default

def safe_get_ingredients(recipe):
    """Safely get ingredients list from recipe"""
    ingredients = safe_get_value(recipe, 'ingredients', [])
    
    # Handle different formats of ingredients
    if isinstance(ingredients, str):
        # If it's a string, try to split it
        if ',' in ingredients:
            return [ing.strip() for ing in ingredients.split(',')]
        elif ';' in ingredients:
            return [ing.strip() for ing in ingredients.split(';')]
        else:
            return [ingredients.strip()]
    elif isinstance(ingredients, (list, tuple)):
        return list(ingredients)
    elif pd.isna(ingredients) or ingredients is None:
        return []
    else:
        # If it's any other type (including float), convert to string and make it a list
        return [str(ingredients)]

def safe_format_metric(value, format_str=".1f", default="N/A"):
    """Safely format numeric values for display"""
    try:
        if value is None or value == 'N/A' or pd.isna(value):
            return default
        if isinstance(value, str):
            try:
                value = float(value)
            except:
                return default
        return f"{value:{format_str}}"
    except:
        return default

def get_weather_emoji():
    """Get weather-appropriate emoji based on time and season with detailed visual descriptions"""
    now = datetime.now()
    hour = now.hour
    month = now.month
    
    # Season detection
    if month in [12, 1, 2]:
        season_emojis = ['❄️', '🌨️', '⛄']
        season_name = "Winter"
        colors = ['#E8F4FD', '#B8E0D2', '#D6EAF8']
        header_text = "Embrace winter's cozy flavors with seasonal comfort dishes"
        if 6 <= hour < 18:
            visual_desc = "🌨️ Snow gently falls on a frost-covered grass field, with gray winter clouds hanging low in the pale sky"
        else:
            visual_desc = "❄️ Starlit winter night with snow sparkling under moonlight, occasional shooting stars streak across the dark sky"
    elif month in [3, 4, 5]:
        season_emojis = ['🌸', '🌷', '🌱']
        season_name = "Spring"
        colors = ['#FDF2E9', '#E8F8F5', '#F4E1FF']
        header_text = "Celebrate spring's fresh awakening with vibrant seasonal ingredients"
        if 6 <= hour < 12:
            visual_desc = "🌅 Morning sun rises over a lush green meadow dotted with spring flowers, fluffy white clouds drift across a brilliant blue sky"
        elif 12 <= hour < 18:
            visual_desc = "🌞 Bright afternoon sunshine bathes blooming fields in golden light, cherry blossoms dance in the gentle breeze"
        else:
            visual_desc = "🌙 Peaceful spring evening with fireflies beginning to twinkle, stars emerging in the twilight sky above flowering trees"
    elif month in [6, 7, 8]:
        season_emojis = ['☀️', '🌻', '🦋']
        season_name = "Summer"
        colors = ['#FEF9E7', '#E8F6F3', '#EBF5FB']
        header_text = "Savor summer's abundance with fresh, sun-ripened seasonal delights"
        if 6 <= hour < 12:
            visual_desc = "🌅 Golden sunrise over sunflower fields, morning dew glistens on grass as butterflies begin their dance"
        elif 12 <= hour < 18:
            visual_desc = "☀️ Brilliant summer sun illuminates vast green meadows, puffy white clouds cast playful shadows on the warm earth"
        else:
            visual_desc = "🌟 Magnificent summer night sky filled with countless stars, shooting stars frequently streak across the warm darkness"
    else:
        season_emojis = ['🍂', '🎃', '🍄']
        season_name = "Autumn"
        colors = ['#FDF2E9', '#FADBD8', '#F5EEF8']
        header_text = "Harvest autumn's golden bounty with rich, warming seasonal recipes"
        if 6 <= hour < 12:
            visual_desc = "🍂 Misty autumn morning with golden leaves scattered across the grass, soft orange sunrise peeks through bare branches"
        elif 12 <= hour < 18:
            visual_desc = "🍁 Crisp autumn afternoon with trees ablaze in red and gold, harvest moon visible in the clear blue sky"
        else:
            visual_desc = "🌟 Clear autumn night with brilliant constellations, shooting stars appear like autumn leaves falling from the heavens"
    
    # Weather variations (random chance for special weather)
    weather_chance = random.random()
    if weather_chance < 0.15:  # 15% chance of rain
        if 6 <= hour < 18:
            visual_desc = "🌧️ Gentle rain falls on the green meadow, gray clouds roll across the sky as nature drinks deeply"
        else:
            visual_desc = "⛈️ Lightning occasionally illuminates the rain-soaked landscape, stars hidden behind storm clouds"
    
    # Time-based weather
    if 6 <= hour < 12:
        time_emoji = "🌅"
        time_name = "Morning"
    elif 12 <= hour < 17:
        time_emoji = "🌞"
        time_name = "Afternoon"
    elif 17 <= hour < 20:
        time_emoji = "🌇"
        time_name = "Evening"
    else:
        time_emoji = "🌙"
        time_name = "Night"
    
    return {
        'season_emoji': random.choice(season_emojis),
        'time_emoji': time_emoji,
        'season_name': season_name,
        'time_name': time_name,
        'colors': colors,
        'datetime': now.strftime("%A, %B %d, %Y at %H:%M"),
        'header_text': header_text,
        'visual_description': visual_desc
    }

def get_current_season():
    """Get current season and seasonal ingredients"""
    current_month = datetime.now().month
    for season, data in SEASONAL_INGREDIENTS.items():
        if current_month in data['months']:
            return season, data
    return 'spring', SEASONAL_INGREDIENTS['spring']

def calculate_seasonality_score(ingredients):
    """Calculate how seasonal a recipe is"""
    # Safely get ingredients
    if isinstance(ingredients, (str, float, int)):
        if pd.isna(ingredients):
            return 0
        ingredients = [str(ingredients)]
    elif not isinstance(ingredients, (list, tuple)):
        return 0
    
    if not ingredients or len(ingredients) == 0:
        return 0
    
    current_season, season_data = get_current_season()
    seasonal_ingredients = []
    for category in season_data['ingredients'].values():
        seasonal_ingredients.extend(category)
    
    # Convert to lowercase for matching
    seasonal_ingredients_lower = [item.lower() for item in seasonal_ingredients]
    
    seasonal_count = 0
    valid_ingredients = 0
    
    # Debug: print what we're working with
    print(f"Current season: {current_season}")
    print(f"Ingredients to check: {ingredients}")
    print(f"Seasonal ingredients for {current_season}: {seasonal_ingredients[:10]}...")  # First 10
    
    for ingredient in ingredients:
        if ingredient and str(ingredient).strip():  # Make sure ingredient is not empty
            valid_ingredients += 1
            ingredient_lower = str(ingredient).lower().strip()
            
            # Check for exact matches or partial matches
            is_seasonal = False
            for seasonal_item in seasonal_ingredients_lower:
                if seasonal_item in ingredient_lower or ingredient_lower in seasonal_item:
                    is_seasonal = True
                    print(f"✅ MATCH: '{ingredient_lower}' matches '{seasonal_item}'")
                    break
            
            if not is_seasonal:
                print(f"❌ NO MATCH: '{ingredient_lower}'")
            
            if is_seasonal:
                seasonal_count += 1
    
    if valid_ingredients == 0:
        return 0
        
    score = (seasonal_count / valid_ingredients) * 100
    print(f"Final score: {seasonal_count}/{valid_ingredients} = {score:.1f}%")
    return min(100, max(0, score))  # Ensure score is between 0-100

def classify_cuisine_advanced(recipe_name, ingredients, description=""):
    """Advanced cuisine classification using keyword analysis"""
    try:
        recipe_text = f"{recipe_name} {' '.join(str(ingredients))} {description}".lower()
        
        cuisine_scores = {}
        for cuisine, keywords in CUISINE_KEYWORDS.items():
            score = 0
            
            # Weight different types of keywords
            for ingredient in keywords['ingredients']:
                if ingredient in recipe_text:
                    score += 3
            
            for dish in keywords['dishes']:
                if dish in recipe_text:
                    score += 4
            
            if score > 0:
                cuisine_scores[cuisine] = score
        
        if cuisine_scores:
            best_cuisine = max(cuisine_scores, key=cuisine_scores.get)
            confidence = min(cuisine_scores[best_cuisine] / 10, 1.0)
            return best_cuisine.title(), confidence
        
        return 'International', 0.3
        
    except Exception as e:
        return 'International', 0.3

# =============================================================================
# CSS STYLING
# =============================================================================

def inject_dreamy_css():
    """Dreamy pastel CSS with weather integration"""
    weather_info = get_weather_emoji()
    colors = weather_info['colors']
    
    st.markdown(f"""
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
        
        .stApp {{
            background: linear-gradient(135deg, {colors[0]} 0%, {colors[1]} 50%, {colors[2]} 100%);
            font-family: 'Inter', sans-serif;
        }}
        
        .dreamy-header {{
            background: linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(255,255,255,0.7) 100%);
            border-radius: 25px;
            padding: 2rem;
            margin-bottom: 2rem;
            border: 1px solid rgba(255,255,255,0.3);
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }}
        
        .dreamy-card {{
            background: rgba(255, 255, 255, 0.85);
            border-radius: 20px;
            padding: 1.5rem;
            margin-bottom: 1rem;
            border: 1px solid rgba(255,255,255,0.3);
            backdrop-filter: blur(10px);
            box-shadow: 0 8px 24px rgba(0,0,0,0.08);
            transition: all 0.3s ease;
        }}
        
        .dreamy-card:hover {{
            transform: translateY(-5px);
            box-shadow: 0 12px 36px rgba(0,0,0,0.12);
        }}
        
        .metric-card {{
            background: linear-gradient(135deg, rgba(255,255,255,0.9) 0%, rgba(255,255,255,0.6) 100%);
            border-radius: 15px;
            padding: 1rem;
            text-align: center;
            border: 1px solid rgba(255,255,255,0.3);
            backdrop-filter: blur(10px);
        }}
        
        .stButton > button {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 12px;
            padding: 0.6rem 1.2rem;
            font-weight: 500;
            transition: all 0.3s ease;
        }}
        
        .stButton > button:hover {{
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4);
        }}
        
        h1, h2, h3 {{
            color: #2D3748;
            font-weight: 600;
        }}
        
        .stSelectbox > div > div {{
            background: rgba(255, 255, 255, 0.9);
            border-radius: 10px;
        }}
        
        .stSlider > div > div {{
            background: rgba(255, 255, 255, 0.9);
            border-radius: 10px;
        }}
    </style>
    """, unsafe_allow_html=True)

# =============================================================================
# USER SYSTEM
# =============================================================================

def initialize_user_system():
    """Initialize user preferences and activity tracking"""
    if 'user_preferences' not in st.session_state:
        st.session_state.user_preferences = {
            'dietary_restrictions': [],
            'favorite_cuisines': [],
            'sustainability_importance': 0.5,
            'seasonal_preference': 0.7,
            'health_importance': 0.6
        }
    
    if 'user_activity' not in st.session_state:
        st.session_state.user_activity = {
            'liked_recipes': [],
            'cooked_recipes': [],
            'viewed_recipes': [],
            'interaction_history': []
        }
    
    # Initialize quiz completion status
    if 'quiz_completed' not in st.session_state:
        st.session_state.quiz_completed = False

def add_to_user_activity(activity_type, recipe_id, recipe_data=None):
    """Track user activity"""
    try:
        activity = st.session_state.user_activity
        
        # Add to interaction history
        interaction = {
            'timestamp': datetime.now(),
            'type': activity_type,
            'recipe_id': recipe_id,
            'recipe_name': recipe_data.get('name', 'Unknown') if recipe_data else 'Unknown',
            'cuisine': recipe_data.get('cuisine', 'Unknown') if recipe_data else 'Unknown'
        }
        activity['interaction_history'].append(interaction)
        
        if activity_type == 'liked':
            if recipe_id not in activity['liked_recipes']:
                activity['liked_recipes'].append(recipe_id)
        elif activity_type == 'cooked':
            if recipe_id not in activity['cooked_recipes']:
                activity['cooked_recipes'].append(recipe_id)
        elif activity_type == 'viewed':
            if recipe_id not in activity['viewed_recipes']:
                activity['viewed_recipes'].append(recipe_id)
                
    except Exception as e:
        st.error(f"Activity tracking error: {str(e)}")

# =============================================================================
# DATA LOADING
# =============================================================================

@st.cache_resource(show_spinner=False)
def load_trained_model():
    """Load trained hybrid recommendation model"""
    try:
        if not MODEL_MODULE_AVAILABLE:
            return None, "module_missing"
        
        model_path = Path("models")
        if model_path.exists():
            model = HybridRecommender.load_model("models")
            return model, "loaded"
        else:
            return None, "not_found"
    except Exception as e:
        print(f"Model loading error: {str(e)}")
        return None, "error"

@st.cache_data(show_spinner=False)
def load_processed_data():
    """Load processed data"""
    try:
        recipes_path = Path("processed_data/recipes_full.pkl")
        interactions_path = Path("processed_data/interactions_full.pkl")
        
        data_status = {}
        
        # Load recipes
        if recipes_path.exists():
            try:
                recipes_df = pd.read_pickle(recipes_path)
                data_status['recipes'] = len(recipes_df)
            except Exception as e:
                recipes_df = create_sample_data()
                data_status['recipes'] = len(recipes_df)
        else:
            recipes_df = create_sample_data()
            data_status['recipes'] = len(recipes_df)
        
        # Load interactions
        if interactions_path.exists():
            try:
                interactions_df = pd.read_pickle(interactions_path)
                data_status['interactions'] = len(interactions_df)
            except Exception as e:
                interactions_df = pd.DataFrame()
                data_status['interactions'] = 0
        else:
            interactions_df = pd.DataFrame()
            data_status['interactions'] = 0
        
        return recipes_df, interactions_df, data_status
        
    except Exception as e:
        return create_sample_data(), pd.DataFrame(), {'recipes': 0, 'interactions': 0}

def create_sample_data():
    """Create enhanced sample recipe data with actual recipe instructions"""
    cuisines = list(CUISINE_KEYWORDS.keys())
    difficulties = ['Beginner', 'Intermediate', 'Advanced']
    
    # Get current season for better seasonal alignment
    current_season, current_season_data = get_current_season()
    
    # Sample recipe instructions based on cuisine
    recipe_instructions = {
        'italian': [
            "Heat olive oil in a large pan over medium heat",
            "Add garlic and sauté until fragrant, about 1 minute", 
            "Add tomatoes and herbs, simmer for 15-20 minutes",
            "Cook pasta according to package directions until al dente",
            "Drain pasta and toss with sauce",
            "Add cheese and fresh basil before serving",
            "Serve immediately with extra parmesan on the side"
        ],
        'asian': [
            "Prepare all ingredients and have them ready (mise en place)",
            "Heat wok or large skillet over high heat",
            "Add oil and swirl to coat the pan",
            "Add aromatics (ginger, garlic) and stir-fry for 30 seconds",
            "Add protein and cook until nearly done",
            "Add vegetables in order of cooking time needed",
            "Add sauce and toss everything together until heated through",
            "Serve immediately over steamed rice"
        ],
        'mexican': [
            "Warm tortillas in a dry skillet or microwave",
            "Heat oil in a large pan over medium-high heat",
            "Add onions and cook until softened",
            "Add spices and cook until fragrant",
            "Add main ingredients and cook thoroughly",
            "Taste and adjust seasoning with salt, pepper, and lime",
            "Serve with fresh cilantro, lime wedges, and your favorite toppings"
        ],
        'french': [
            "Preheat oven to specified temperature if needed",
            "Prepare mise en place - have all ingredients measured and ready",
            "Heat butter in a heavy-bottomed pan over medium heat",
            "Add shallots and cook until translucent",
            "Add wine and reduce by half",
            "Add cream and herbs, simmer gently",
            "Season to taste and finish with fresh herbs",
            "Serve immediately while hot"
        ],
        'indian': [
            "Heat ghee or oil in a heavy-bottomed pot",
            "Add whole spices and let them sizzle for 30 seconds",
            "Add onions and cook until golden brown",
            "Add ginger-garlic paste and cook for 1 minute",
            "Add ground spices and cook for 30 seconds",
            "Add tomatoes and cook until they break down",
            "Add main ingredients and simmer until tender",
            "Garnish with fresh cilantro and serve with rice or naan"
        ],
        'mediterranean': [
            "Preheat oven to 400°F if baking",
            "Prepare vegetables by chopping uniformly",
            "Heat olive oil in a large pan",
            "Add vegetables and cook until tender",
            "Add herbs and season with salt and pepper",
            "Finish with lemon juice and fresh herbs",
            "Serve warm or at room temperature"
        ],
        'american': [
            "Preheat grill or oven as needed",
            "Season ingredients generously",
            "Cook protein to proper internal temperature",
            "Prepare side dishes while protein cooks",
            "Let protein rest before serving",
            "Assemble plates and serve immediately"
        ],
        'thai': [
            "Prepare curry paste or use store-bought",
            "Heat coconut oil in a wok over medium heat",
            "Add curry paste and fry until fragrant",
            "Add coconut milk gradually, stirring constantly",
            "Add protein and vegetables",
            "Season with fish sauce, sugar, and lime",
            "Garnish with Thai basil and serve with jasmine rice"
        ]
    }
    
    # Create seasonal recipes that make sense
    seasonal_recipe_names = {
        'spring': ['Fresh Pea Soup', 'Asparagus Risotto', 'Strawberry Salad', 'Spring Vegetable Pasta', 'Artichoke Dip'],
        'summer': ['Tomato Basil Bruschetta', 'Grilled Zucchini', 'Berry Smoothie Bowl', 'Cucumber Gazpacho', 'Corn Salad'],
        'autumn': ['Pumpkin Soup', 'Roasted Squash', 'Apple Crisp', 'Sweet Potato Curry', 'Mushroom Risotto'],
        'winter': ['Root Vegetable Stew', 'Citrus Salad', 'Cabbage Soup', 'Kale Caesar', 'Leek Potato Soup']
    }
    
    recipes = []
    for i in range(50):
        cuisine = random.choice(cuisines)
        
        # Get seasonal ingredients for current season (80% of time) or random season (20% of time)
        if random.random() < 0.8:
            season_to_use = current_season
        else:
            season_to_use = random.choice(list(SEASONAL_INGREDIENTS.keys()))
        
        season_data = SEASONAL_INGREDIENTS[season_to_use]
        
        # Generate realistic ingredients based on cuisine and season
        cuisine_ingredients = CUISINE_KEYWORDS[cuisine]['ingredients']
        seasonal_ingredients = []
        for category in season_data['ingredients'].values():
            seasonal_ingredients.extend(category)
        
        # Start with cuisine ingredients
        base_ingredients = []
        if cuisine_ingredients:
            base_ingredients.extend(random.sample(cuisine_ingredients, min(3, len(cuisine_ingredients))))
        
        # Add seasonal ingredients
        if seasonal_ingredients:
            seasonal_sample = random.sample(seasonal_ingredients, min(4, len(seasonal_ingredients)))
            base_ingredients.extend(seasonal_sample)
        
        # Add basic ingredients
        base_ingredients.extend(['salt', 'pepper', 'olive oil'])
        
        # Remove duplicates and clean up
        seen = set()
        clean_ingredients = []
        for ing in base_ingredients:
            if ing and str(ing).strip() and ing not in seen:
                clean_ingredients.append(str(ing).strip())
                seen.add(ing)
        
        # Limit to reasonable number
        base_ingredients = clean_ingredients[:8]
        
        # Ensure we have at least some ingredients
        if len(base_ingredients) < 3:
            base_ingredients.extend(['onion', 'garlic', 'herbs'])
        
        # Get appropriate instructions for cuisine
        instructions = recipe_instructions.get(cuisine, [
            "Prepare all ingredients according to recipe specifications",
            "Follow traditional cooking methods for best results", 
            "Cook until ingredients are properly combined and heated through",
            "Season to taste and serve hot"
        ])
        
        # Generate more realistic recipe names
        if i % 10 == 0 and season_to_use in seasonal_recipe_names:
            recipe_name = random.choice(seasonal_recipe_names[season_to_use])
        else:
            recipe_name = f"{cuisine.title()} {random.choice(['Delight', 'Special', 'Classic', 'Supreme', 'Bowl'])}"
        
        # More realistic calorie calculations based on ingredients
        base_calories = 200
        for ingredient in base_ingredients:
            ing_lower = str(ingredient).lower()
            if any(meat in ing_lower for meat in ['beef', 'pork', 'chicken', 'lamb']):
                base_calories += 80
            elif any(dairy in ing_lower for dairy in ['cheese', 'butter', 'cream']):
                base_calories += 60
            elif any(carb in ing_lower for carb in ['pasta', 'rice', 'bread', 'potato']):
                base_calories += 40
            elif any(oil in ing_lower for oil in ['oil', 'nuts']):
                base_calories += 30
            else:
                base_calories += 10  # vegetables, herbs, spices
        
        # Add some randomness but keep realistic
        calories = base_calories + random.randint(-50, 100)
        calories = max(150, min(600, calories))  # Keep between 150-600 calories
        
        recipe = {
            'id': i + 1,
            'name': recipe_name,
            'cuisine': cuisine.title(),
            'difficulty': random.choice(difficulties),
            'minutes': random.randint(15, 60),
            'servings': random.randint(2, 6),
            'rating': round(random.uniform(3.5, 5.0), 1),
            'calories': calories,
            'ingredients': base_ingredients,  # This is now guaranteed to be a list
            'n_ingredients': len(base_ingredients),
            'n_steps': len(instructions),
            'description': f"A delicious {cuisine} recipe with authentic flavors and traditional cooking techniques that will transport you to the heart of {cuisine} cuisine.",
            'health_score': random.randint(45, 95),
            'sus_score': random.randint(30, 90),
            'sus_total_carbon_kg': round(random.uniform(0.5, 3.0), 2),
            'sus_is_plant_based': not any(meat in str(ing).lower() for meat in ['beef', 'pork', 'chicken', 'lamb', 'fish'] for ing in base_ingredients),
            'sus_is_vegetarian': not any(meat in str(ing).lower() for meat in ['beef', 'pork', 'chicken', 'lamb', 'fish', 'meat'] for ing in base_ingredients),
            'sus_category': random.choice(['Climate Hero 🌟', 'Eco Friendly 🌿', 'Moderate Impact ⚡']),
            'instructions': instructions,
            'steps': instructions  # Add this for compatibility
        }
        
        # Calculate seasonality score first
        seasonal_score = calculate_seasonality_score(base_ingredients)
        recipe['seasonal_score'] = seasonal_score
        
        # Calculate real sustainability score if module available
        try:
            sus_data = calculate_real_sustainability_score(recipe)
            recipe['sus_score'] = sus_data['score']
            recipe['sus_total_carbon_kg'] = sus_data['total_carbon_kg']
            recipe['sus_is_plant_based'] = sus_data['is_plant_based']
            recipe['sus_is_vegetarian'] = sus_data['is_vegetarian']
            recipe['sus_category'] = sus_data['category']
            # Update seasonal score from sustainability calculation
            recipe['seasonal_score'] = max(seasonal_score, sus_data['seasonality_score'])
        except Exception as e:
            print(f"Sustainability calculation error: {e}")
            # Keep the default values we set above
        
        recipes.append(recipe)
    
    return pd.DataFrame(recipes)
        
    return pd.DataFrame(recipes)

# =============================================================================
# RECOMMENDATION ENGINE
# =============================================================================

class DreamyRecommendationEngine:
    """Enhanced recommendation engine"""
    
    def __init__(self):
        self.model = None
        self.model_status = "not_loaded"
        self.recipes_df = None
        self.interactions_df = None
        self.load_system()
    
    def load_system(self):
        """Load the recommendation system"""
        try:
            # Load trained model
            self.model, self.model_status = load_trained_model()
            
            # Load data
            self.recipes_df, self.interactions_df, self.data_status = load_processed_data()
            
            # Update session state
            st.session_state.recipes_df = self.recipes_df
            st.session_state.interactions_df = self.interactions_df
            st.session_state.model_status = self.model_status
            st.session_state.data_status = self.data_status
            
        except Exception as e:
            print(f"System loading error: {str(e)}")
            self.model_status = "error"
            st.session_state.model_status = "error"
    
    def get_recommendations(self, user_preferences, n_recommendations=9):
        """Get recommendations based on user preferences"""
        try:
            if self.model and self.model_status == "loaded":
                return self.get_ai_recommendations(user_preferences, n_recommendations)
            else:
                return self.get_content_recommendations(user_preferences, n_recommendations), False
        except Exception as e:
            print(f"Recommendation error: {str(e)}")
            return self.get_fallback_recommendations(n_recommendations), False
    
    def get_ai_recommendations(self, user_preferences, n_recommendations):
        """AI-based recommendations"""
        try:
            # Create synthetic user ID
            user_id = hash(str(sorted(user_preferences.items()))) % 10000
            recommendations = self.model.recommend(user_id, n_recommendations * 2)
            
            recommended_recipes = []
            for recipe_id, score in recommendations[:n_recommendations]:
                recipe_data = self.recipes_df[self.recipes_df['id'] == recipe_id]
                if not recipe_data.empty:
                    recipe = recipe_data.iloc[0].to_dict()
                    recipe['ai_score'] = float(score)
                    recipe['recommendation_source'] = 'AI Model'
                    recipe['explanation'] = f"🤖 AI confidence: {score:.0%}"
                    recommended_recipes.append(recipe)
            
            return recommended_recipes, True
            
        except Exception as e:
            print(f"AI recommendation failed: {str(e)}")
            return self.get_content_recommendations(user_preferences, n_recommendations), False
    
    def get_content_recommendations(self, user_preferences, n_recommendations=9):
        """Content-based recommendations"""
        try:
            if self.recipes_df is None or self.recipes_df.empty:
                return self.get_fallback_recommendations(n_recommendations)
            
            df = self.recipes_df.copy()
            
            # Apply dietary filters
            dietary_restrictions = user_preferences.get('dietary_restrictions', [])
            for restriction in dietary_restrictions:
                if restriction in DIETARY_OPTIONS:
                    excludes = DIETARY_OPTIONS[restriction]['excludes']
                    for exclude in excludes:
                        df = df[~df['ingredients'].astype(str).str.lower().str.contains(exclude, na=False)]
            
            # Calculate preference scores
            df['content_score'] = df.apply(
                lambda recipe: self.calculate_content_score(recipe, user_preferences), 
                axis=1
            )
            
            # Sort and get top recommendations
            df = df.sort_values('content_score', ascending=False)
            
            recommended_recipes = []
            for _, recipe in df.head(n_recommendations).iterrows():
                recipe_dict = recipe.to_dict()
                recipe_dict['ai_score'] = safe_get_value(recipe_dict, 'content_score', 0.5)
                recipe_dict['recommendation_source'] = 'Content Engine'
                recipe_dict['explanation'] = "📊 Based on your preferences"
                recommended_recipes.append(recipe_dict)
            
            return recommended_recipes
            
        except Exception as e:
            print(f"Content recommendation error: {str(e)}")
            return self.get_fallback_recommendations(n_recommendations)
    
    def calculate_content_score(self, recipe, user_preferences):
        """Calculate content-based score"""
        try:
            score = safe_get_value(recipe, 'rating', 4.0)
            
            # Seasonal preference
            seasonal_pref = user_preferences.get('seasonal_preference', 0.5)
            seasonal_score = safe_get_value(recipe, 'seasonal_score', 0)
            if seasonal_pref > 0.5:
                score += (seasonal_score / 100) * seasonal_pref
            
            # Health preference
            health_pref = user_preferences.get('health_importance', 0.5)
            health_score = safe_get_value(recipe, 'health_score', 50)
            if health_pref > 0.5:
                score += (health_score / 100) * health_pref
            
            # Sustainability preference
            sus_pref = user_preferences.get('sustainability_importance', 0.5)
            sus_score = safe_get_value(recipe, 'sus_score', 50)
            if sus_pref > 0.5:
                score += (sus_score / 100) * sus_pref
            
            return max(0, score)
            
        except Exception as e:
            return 3.5
    
    def get_fallback_recommendations(self, n_recommendations):
        """Fallback recommendations when other methods fail"""
        try:
            if self.recipes_df is not None and not self.recipes_df.empty:
                df = self.recipes_df.copy()
                df = df.sort_values('rating', ascending=False, na_position='last')
                
                recommendations = []
                for _, recipe in df.head(n_recommendations).iterrows():
                    recipe_dict = recipe.to_dict()
                    recipe_dict['ai_score'] = 0.6
                    recipe_dict['recommendation_source'] = 'Popular Recipes'
                    recipe_dict['explanation'] = f"⭐ Highly rated ({safe_format_metric(recipe_dict.get('rating', 4.0), '.1f')} stars)"
                    recommendations.append(recipe_dict)
                
                return recommendations
            else:
                return []
                
        except Exception as e:
            return []

# =============================================================================
# MODAL DIALOGS FOR RECIPE DETAILS
# =============================================================================

@st.dialog("Recipe Details")
def show_recipe_modal(recipe):
    """Show detailed recipe information in a modal dialog"""
    name = safe_get_value(recipe, 'name', 'Unknown Recipe')
    
    st.markdown(f"# 🍽️ {name}")
    
    # Recipe overview
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("### 📊 Recipe Information")
        cuisine = safe_get_value(recipe, 'cuisine', 'International')
        difficulty = safe_get_value(recipe, 'difficulty', 'Intermediate')
        minutes = safe_get_value(recipe, 'minutes', 30)
        servings = safe_get_value(recipe, 'servings', 4)
        rating = safe_get_value(recipe, 'rating', 4.0)
        calories = safe_get_value(recipe, 'calories', 400)
        
        st.markdown(f"""
        - **Cuisine:** {cuisine}
        - **Difficulty:** {difficulty}
        - **Cooking Time:** {minutes} minutes
        - **Servings:** {servings} people
        - **Rating:** {safe_format_metric(rating, '.1f')} ⭐
        - **Calories:** {calories} per serving
        """)
        
        st.markdown("### 🌱 Health & Sustainability")
        health_score = safe_get_value(recipe, 'health_score', 70)
        sus_score = safe_get_value(recipe, 'sus_score', 60)
        carbon = safe_get_value(recipe, 'sus_total_carbon_kg', 2.5)
        is_vegetarian = safe_get_value(recipe, 'sus_is_vegetarian', False)
        is_plant_based = safe_get_value(recipe, 'sus_is_plant_based', False)
        
        st.markdown(f"""
        - **Health Score:** {health_score}% 💚
        - **Sustainability Score:** {sus_score}% 🌍
        - **Carbon Footprint:** {safe_format_metric(carbon, '.1f')} kg CO2
        - **Vegetarian:** {'✅' if is_vegetarian else '❌'}
        - **Plant-based:** {'✅' if is_plant_based else '❌'}
        """)
    
    with col2:
        st.markdown("### 🥘 Ingredients")
        ingredients = safe_get_ingredients(recipe)
        
        if ingredients and len(ingredients) > 0:
            for i, ingredient in enumerate(ingredients, 1):
                if ingredient and str(ingredient).strip():
                    st.markdown(f"{i}. {ingredient}")
        else:
            st.markdown("*Ingredients not specified*")
        
        # Seasonal indicators
        seasonal_score = safe_get_value(recipe, 'seasonal_score', 0)
        if seasonal_score > 30:
            current_season, season_data = get_current_season()
            st.success(f"🌿 {seasonal_score:.0f}% seasonal ingredients for {season_data['season_name']}")
    
    # Description
    description = safe_get_value(recipe, 'description', 'A delicious recipe')
    st.markdown("### 📝 Description")
    st.markdown(description)
    
    # Instructions
    st.markdown("### 👨🍳 Cooking Instructions")
    instructions = safe_get_value(recipe, 'instructions', [])
    steps = safe_get_value(recipe, 'steps', [])
    
    # Try both 'instructions' and 'steps' fields for compatibility
    cooking_steps = instructions if instructions else steps
    
    if cooking_steps and len(cooking_steps) > 0:
        for i, step in enumerate(cooking_steps, 1):
            if step and step.strip():  # Make sure step is not empty
                st.markdown(f"**Step {i}:** {step}")
    else:
        # Fallback instructions based on cuisine
        cuisine = safe_get_value(recipe, 'cuisine', 'International').lower()
        fallback_instructions = {
            'italian': [
                "Heat olive oil in a pan over medium heat",
                "Add garlic and cook until fragrant",
                "Add main ingredients and cook thoroughly", 
                "Season with salt, pepper, and herbs",
                "Serve with fresh basil and parmesan"
            ],
            'asian': [
                "Prepare all ingredients (mise en place)",
                "Heat oil in wok over high heat",
                "Stir-fry aromatics for 30 seconds",
                "Add main ingredients and cook until done",
                "Serve over steamed rice"
            ],
            'mexican': [
                "Heat oil in a large pan",
                "Add onions and spices, cook until fragrant",
                "Add main ingredients and cook thoroughly",
                "Season with lime, salt, and pepper", 
                "Serve with tortillas and fresh cilantro"
            ]
        }
        
        default_steps = fallback_instructions.get(cuisine, [
            "Prepare all ingredients according to recipe",
            "Cook ingredients using appropriate method",
            "Season to taste",
            "Serve hot and enjoy"
        ])
        
        for i, step in enumerate(default_steps, 1):
            st.markdown(f"**Step {i}:** {step}")
        
        st.info("💡 These are general cooking steps. For detailed instructions, check the original recipe source.")
    
    # Action buttons
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("❤️ Save Recipe", use_container_width=True):
            add_to_user_activity('liked', recipe.get('id', 0), recipe)
            st.success("Recipe saved to your collection!")
            st.rerun()
    
    with col2:
        if st.button("✅ Mark as Cooked", use_container_width=True):
            add_to_user_activity('cooked', recipe.get('id', 0), recipe)
            st.success("Recipe marked as cooked!")
            st.rerun()
    
    with col3:
        if st.button("🔄 Close", use_container_width=True):
            st.rerun()

# =============================================================================
# UI COMPONENTS
# =============================================================================

def render_header():
    """Render the enhanced seasonal header with visual descriptions"""
    weather_info = get_weather_emoji()
    
    # Main title
    st.markdown(f"""
    <div class="dreamy-header">
        <div style="text-align: center;">
            <h1 style="margin: 0; font-size: 3rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">
                🍽️ Seasonal Recipe Discovery
            </h1>
        </div>
    </div>
    """, unsafe_allow_html=True)
    
    # Subtitle
    st.markdown(f"""
    <div style="text-align: center; margin: 1rem 0;">
        <h3 style="color: #4A5568; font-weight: 400; margin: 0;">
            {weather_info['header_text']}
        </h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Visual description
    st.markdown(f"""
    <div style="text-align: center; background: rgba(255,255,255,0.6); padding: 1rem; border-radius: 15px; margin: 1rem 0;">
        <p style="font-style: italic; color: #718096; margin: 0;">
            {weather_info['visual_description']}
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    # Time and date info
    st.markdown(f"""
    <div style="text-align: center; margin: 1rem 0;">
        <span style="background: rgba(255,255,255,0.8); padding: 0.5rem 1rem; border-radius: 20px; font-weight: 500; color: #4A5568;">
            {weather_info['time_emoji']} {weather_info['time_name']} • {weather_info['season_emoji']} {weather_info['season_name']} 
        </span>
    </div>
    """, unsafe_allow_html=True)
    
    # Date
    st.markdown(f"""
    <div style="text-align: center; margin-bottom: 2rem;">
        <span style="color: #718096; font-size: 0.9rem;">
            📅 {weather_info['datetime']}
        </span>
    </div>
    """, unsafe_allow_html=True)

def render_model_status():
    """Render model status"""
    model_status = st.session_state.get('model_status', 'not_loaded')
    data_status = st.session_state.get('data_status', {})
    
    if model_status == "loaded":
        st.markdown(f"""
        <div class="metric-card">
            <h4 style="margin: 0;">🤖 AI Model: ACTIVE ✨</h4>
            <p style="margin: 0.5rem 0 0 0; color: #718096;">
                📚 {data_status.get('recipes', 0):,} recipes • 🧠 {data_status.get('interactions', 0):,} interactions
            </p>
        </div>
        """, unsafe_allow_html=True)
        return True
    else:
        st.markdown("""
        <div class="metric-card">
            <h4 style="margin: 0; color: #718096;">🌙 Content Engine Active • Smart recommendations based on preferences</h4>
        </div>
        """, unsafe_allow_html=True)
        return False

def render_seasonal_spotlight():
    """Render seasonal ingredient spotlight"""
    current_season, season_data = get_current_season()
    
    # Pick random seasonal ingredients
    spotlight_ingredients = []
    for category, ingredients in season_data['ingredients'].items():
        spotlight_ingredients.extend(random.sample(ingredients, min(2, len(ingredients))))
    
    featured = random.sample(spotlight_ingredients, min(6, len(spotlight_ingredients)))
    
    st.markdown(f"""
    <div class="dreamy-card">
        <h3 style="margin: 0 0 0.5rem 0;">
            ✨ Today's Seasonal Spotlight {season_data['season_name']}
        </h3>
        <p style="margin: 0 0 1rem 0; color: #718096;">
            Perfect ingredients for this moment
        </p>
        <div style="text-align: center; background: rgba(255,255,255,0.6); padding: 1rem; border-radius: 10px;">
            {' • '.join([f'<strong>{ing.title()}</strong>' for ing in featured])}
        </div>
    </div>
    """, unsafe_allow_html=True)

def render_recipe_card(recipe, index):
    """Render a recipe card with improved layout using Streamlit components"""
    recipe_id = safe_get_value(recipe, 'id', index)
    name = safe_get_value(recipe, 'name', 'Unknown Recipe')
    cuisine = safe_get_value(recipe, 'cuisine', 'International')
    rating = safe_get_value(recipe, 'rating', 4.0)
    minutes = safe_get_value(recipe, 'minutes', 30)
    calories = safe_get_value(recipe, 'calories', 400)
    health_score = safe_get_value(recipe, 'health_score', 70)
    seasonal_score = safe_get_value(recipe, 'seasonal_score', 0)
    sus_score = safe_get_value(recipe, 'sus_score', 60)
    sus_category = safe_get_value(recipe, 'sus_category', 'Moderate Impact')
    ai_score = safe_get_value(recipe, 'ai_score', 0.5)
    explanation = safe_get_value(recipe, 'explanation', 'Recommended for you')
    ingredients = safe_get_ingredients(recipe)
    description = safe_get_value(recipe, 'description', 'A delicious recipe')
    
    # Format ingredients display
    if ingredients and len(ingredients) > 0:
        ingredients_display = ', '.join(str(ing) for ing in ingredients[:4] if ing and str(ing).strip())
        if len(ingredients) > 4:
            ingredients_display += f' +{len(ingredients)-4} more'
    else:
        ingredients_display = "Ingredients not specified"
    
    # Create a container with custom styling
    with st.container():
        # Recipe card with proper Streamlit components
        st.markdown(f"""
        <div class="dreamy-card">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 1rem;">
                <div style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 0.3rem 0.8rem; border-radius: 15px; font-size: 0.85rem; font-weight: 500;">
                    AI: {ai_score:.0%}
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Recipe title
        st.markdown(f"### 🍽️ {name}")
        
        # Recipe info using columns for better layout
        info_col1, info_col2 = st.columns(2)
        with info_col1:
            st.markdown(f"**🌍 {cuisine}** • ⭐ {safe_format_metric(rating, '.1f')}")
        with info_col2:
            st.markdown(f"⏱️ {minutes}min • 🔥 {calories} cal")
        
        # Ingredients
        st.markdown(f"**Ingredients:** {ingredients_display}")
        
        # Badges using metrics or simple text
        badge_col1, badge_col2, badge_col3 = st.columns(3)
        with badge_col1:
            st.metric("💚 Health", f"{health_score}%")
        with badge_col2:
            st.metric("🌿 Seasonal", f"{seasonal_score:.0f}%")
        with badge_col3:
            # Extract emoji from category or show sustainability score
            if isinstance(sus_category, str):
                if '🌟' in sus_category:
                    impact_display = '🌟 Hero'
                elif '🌿' in sus_category:
                    impact_display = '🌿 Eco'
                elif '⚡' in sus_category:
                    impact_display = '⚡ Moderate'
                elif '⚠️' in sus_category:
                    impact_display = '⚠️ High'
                else:
                    impact_display = f'{sus_score:.0f}%'
            else:
                impact_display = f'{sus_score:.0f}%'
            st.metric("🌍 Impact", impact_display)
        
        # Explanation in an info box
        st.info(f"**Why this recipe?** {explanation}")
        
        # Description
        description_short = description[:100] + '...' if len(description) > 100 else description
        st.markdown(f"*{description_short}*")
        
        # Action buttons - no nested columns, just sequential
        st.markdown("---")
        
        button_col1, button_col2, button_col3 = st.columns(3)
        
        with button_col1:
            if st.button("❤️ Save", key=f"save_{recipe_id}_{index}"):
                add_to_user_activity('liked', recipe_id, recipe)
                st.success("Recipe saved!")
        
        with button_col2:
            if st.button("✅ Cooked", key=f"cooked_{recipe_id}_{index}"):
                add_to_user_activity('cooked', recipe_id, recipe)
                st.success("Marked as cooked!")
        
        with button_col3:
            if st.button("📖 View Full Recipe", key=f"details_{recipe_id}_{index}"):
                show_recipe_modal(recipe)

def render_recipes_grid(recipes):
    """Render recipes in a 2x2 layout with one highlighted recipe"""
    if not recipes:
        st.warning("No recipes to display")
        return
    
    # Find the recipe with highest AI score for highlighting
    if len(recipes) > 0:
        highlighted_recipe = max(recipes, key=lambda x: safe_get_value(x, 'ai_score', 0))
        other_recipes = [r for r in recipes if r != highlighted_recipe]
    else:
        highlighted_recipe = None
        other_recipes = recipes
    
    # Display highlighted recipe first if exists
    if highlighted_recipe:
        st.markdown("### 🌟 Most Compatible Recipe For You")
        st.markdown("""
        <div style="margin-bottom: 2rem;">
        """, unsafe_allow_html=True)
        
        with st.container():
            render_recipe_card(highlighted_recipe, "highlighted")
            add_to_user_activity('viewed', highlighted_recipe.get('id', 0), highlighted_recipe)
        
        st.markdown("</div>", unsafe_allow_html=True)
        st.markdown("---")
    
    # Display other recipes in 2x2 grid
    if other_recipes:
        st.markdown("### 🍽️ More Great Recipes")
        
        # Display recipes in pairs (2 per row)
        for i in range(0, len(other_recipes), 2):
            cols = st.columns(2)
            
            # First recipe in the row
            if i < len(other_recipes):
                with cols[0]:
                    render_recipe_card(other_recipes[i], f"grid_{i}")
                    add_to_user_activity('viewed', other_recipes[i].get('id', 0), other_recipes[i])
            
            # Second recipe in the row
            if i + 1 < len(other_recipes):
                with cols[1]:
                    render_recipe_card(other_recipes[i + 1], f"grid_{i+1}")
                    add_to_user_activity('viewed', other_recipes[i + 1].get('id', 0), other_recipes[i + 1])

def render_analytics():
    """Render user analytics"""
    st.markdown("## 📊 Your Recipe Journey")
    
    activity = st.session_state.user_activity
    
    # Create metrics without nested columns
    metrics_cols = st.columns(4)
    
    with metrics_cols[0]:
        st.markdown(f"""
        <div class="metric-card">
            <h4 style="margin: 0;">❤️ Saved</h4>
            <h2 style="margin: 0.5rem 0 0 0;">{len(activity.get('liked_recipes', []))}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with metrics_cols[1]:
        st.markdown(f"""
        <div class="metric-card">
            <h4 style="margin: 0;">✅ Cooked</h4>
            <h2 style="margin: 0.5rem 0 0 0;">{len(activity.get('cooked_recipes', []))}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with metrics_cols[2]:
        st.markdown(f"""
        <div class="metric-card">
            <h4 style="margin: 0;">👀 Viewed</h4>
            <h2 style="margin: 0.5rem 0 0 0;">{len(activity.get('viewed_recipes', []))}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    with metrics_cols[3]:
        total_interactions = len(activity.get('interaction_history', []))
        st.markdown(f"""
        <div class="metric-card">
            <h4 style="margin: 0;">🎯 Total</h4>
            <h2 style="margin: 0.5rem 0 0 0;">{total_interactions}</h2>
        </div>
        """, unsafe_allow_html=True)
    
    # Recent activity
    if activity.get('interaction_history'):
        st.markdown("### 📈 Recent Activity")
        recent_interactions = activity['interaction_history'][-10:]
        
        for interaction in reversed(recent_interactions):
            timestamp = interaction['timestamp'].strftime("%H:%M")
            activity_type = interaction['type']
            recipe_name = interaction['recipe_name']
            
            if activity_type == 'liked':
                icon = "❤️"
                action = "Saved"
            elif activity_type == 'cooked':
                icon = "✅"
                action = "Cooked"
            else:
                icon = "👀"
                action = "Viewed"
            
            st.markdown(f"**{timestamp}** {icon} {action} *{recipe_name}*")
    
    # Optional: Add charts if plotly is available
    if PLOTLY_AVAILABLE and activity.get('interaction_history'):
        st.markdown("### 📈 Activity Chart")
        
        interactions = activity['interaction_history']
        df_interactions = pd.DataFrame(interactions)
        
        if not df_interactions.empty:
            df_interactions['date'] = pd.to_datetime(df_interactions['timestamp']).dt.date
            daily_interactions = df_interactions.groupby(['date', 'type']).size().reset_index(name='count')
            
            fig = px.line(daily_interactions, x='date', y='count', color='type',
                         title="Daily Recipe Interactions",
                         labels={'count': 'Number of Interactions', 'date': 'Date'})
            fig.update_layout(
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font=dict(color='#4A5568')
            )
            st.plotly_chart(fig, use_container_width=True)

def render_my_collection():
    """Render user's recipe collection"""
    st.markdown("## 💝 My Recipe Collection")
    
    activity = st.session_state.user_activity
    recipes_df = st.session_state.get('recipes_df')
    
    if recipes_df is None or recipes_df.empty:
        st.warning("No recipes data available")
        return
    
    # Tabs for different collections
    tab1, tab2 = st.tabs(["❤️ Saved Recipes", "✅ Cooked Recipes"])
    
    with tab1:
        saved_recipes = activity.get('liked_recipes', [])
        if saved_recipes:
            st.markdown(f"### You have {len(saved_recipes)} saved recipes")
            
            saved_df = recipes_df[recipes_df['id'].isin(saved_recipes)]
            saved_recipe_list = [recipe.to_dict() for _, recipe in saved_df.iterrows()]
            
            render_recipes_grid(saved_recipe_list)
                
        else:
            st.markdown("""
            <div style="text-align: center; padding: 3rem; background: rgba(255,255,255,0.7); border-radius: 20px; margin: 2rem 0;">
                <h3 style="margin: 0 0 1rem 0;">💫 Start Building Your Collection</h3>
                <p style="margin: 0; color: #718096;">Save recipes you love to see them here!</p>
            </div>
            """, unsafe_allow_html=True)
    
    with tab2:
        cooked_recipes = activity.get('cooked_recipes', [])
        if cooked_recipes:
            st.markdown(f"### You've cooked {len(cooked_recipes)} recipes")
            
            cooked_df = recipes_df[recipes_df['id'].isin(cooked_recipes)]
            cooked_recipe_list = [recipe.to_dict() for _, recipe in cooked_df.iterrows()]
            
            render_recipes_grid(cooked_recipe_list)
                
        else:
            st.markdown("""
            <div style="text-align: center; padding: 3rem; background: rgba(255,255,255,0.7); border-radius: 20px; margin: 2rem 0;">
                <h3 style="margin: 0 0 1rem 0;">🍳 Your Cooking Journey Starts Here</h3>
                <p style="margin: 0; color: #718096;">Mark recipes as cooked to track your culinary adventures!</p>
            </div>
            """, unsafe_allow_html=True)

# =============================================================================
# COLD START QUIZ SYSTEM
# =============================================================================

class ColdStartQuiz:
    """Comprehensive onboarding quiz for new users"""
    
    def __init__(self):
        self.questions = self.define_questions()
        self.current_question = 0
        self.results = {}
    
    def define_questions(self):
        """Define comprehensive quiz questions"""
        return [
            {
                'id': 'cooking_experience',
                'question': '🍳 How would you describe your cooking experience?',
                'type': 'single_choice',
                'options': [
                    ('beginner', 'Beginner - I mostly order takeout or use simple recipes'),
                    ('casual', 'Casual Cook - I cook regularly but stick to familiar recipes'),
                    ('enthusiast', 'Cooking Enthusiast - I love trying new recipes and techniques'),
                    ('expert', 'Expert - I experiment with complex dishes and create my own recipes')
                ]
            },
            {
                'id': 'flavor_preferences',
                'question': '🌶️ What flavors do you love most? (Select all that apply)',
                'type': 'multiple_choice',
                'options': [
                    ('spicy', 'Spicy & Hot'),
                    ('sweet', 'Sweet & Dessert-like'),
                    ('savory', 'Savory & Umami'),
                    ('fresh', 'Fresh & Light'),
                    ('rich', 'Rich & Creamy'),
                    ('tangy', 'Tangy & Acidic'),
                    ('smoky', 'Smoky & Grilled')
                ]
            },
            {
                'id': 'dietary_preferences',
                'question': '🥗 Do you follow any dietary preferences?',
                'type': 'multiple_choice',
                'options': [
                    ('vegetarian', 'Vegetarian'),
                    ('vegan', 'Vegan'),
                    ('pescetarian', 'Pescetarian'),
                    ('gluten_free', 'Gluten-Free'),
                    ('dairy_free', 'Dairy-Free'),
                    ('keto', 'Keto'),
                    ('paleo', 'Paleo'),
                    ('none', 'No specific dietary restrictions')
                ]
            },
            {
                'id': 'time_availability',
                'question': '⏰ How much time do you typically have for cooking?',
                'type': 'single_choice',
                'options': [
                    ('quick', '15-30 minutes'),
                    ('moderate', '30-60 minutes'),
                    ('extended', '1-2 hours'),
                    ('leisurely', 'More than 2 hours - I love taking my time')
                ]
            },
            {
                'id': 'seasonal_importance',
                'question': '🌿 How important is eating seasonally to you?',
                'type': 'scale',
                'min': 1,
                'max': 5,
                'labels': ['Not important', 'Somewhat important', 'Moderately important', 'Very important', 'Extremely important']
            }
        ]
    
    def render_question(self, question_data):
        """Render a single quiz question"""
        st.markdown(f"### Question {self.current_question + 1} of {len(self.questions)}")
        
        # Progress bar
        progress = (self.current_question + 1) / len(self.questions)
        st.progress(progress)
        
        st.markdown(f"#### {question_data['question']}")
        
        if question_data['type'] == 'single_choice':
            return self.render_single_choice(question_data)
        elif question_data['type'] == 'multiple_choice':
            return self.render_multiple_choice(question_data)
        elif question_data['type'] == 'scale':
            return self.render_scale(question_data)
    
    def render_single_choice(self, question_data):
        """Render single choice question"""
        options = [opt[1] for opt in question_data['options']]
        selected = st.radio(
            "Select one:",
            options,
            key=f"quiz_{question_data['id']}"
        )
        
        if selected:
            # Find the corresponding value
            for value, label in question_data['options']:
                if label == selected:
                    return {question_data['id']: value}
        return None
    
    def render_multiple_choice(self, question_data):
        """Render multiple choice question"""
        selected_values = []
        
        for value, label in question_data['options']:
            if st.checkbox(label, key=f"quiz_{question_data['id']}_{value}"):
                selected_values.append(value)
        
        if selected_values:
            return {question_data['id']: selected_values}
        return None
    
    def render_scale(self, question_data):
        """Render scale question"""
        value = st.slider(
            "Rate the importance:",
            question_data['min'],
            question_data['max'],
            3,  # Default to middle value
            key=f"quiz_{question_data['id']}"
        )
        
        return {question_data['id']: value}
    
    def process_quiz_results(self, all_answers):
        """Process quiz results into user preferences"""
        try:
            profile = {
                'quiz_completed': True,
                'completion_date': datetime.now(),
                'raw_answers': all_answers
            }
            
            # Process dietary preferences
            dietary_prefs = all_answers.get('dietary_preferences', [])
            dietary_restrictions = []
            
            # Map quiz answers to dietary options
            diet_mapping = {
                'vegetarian': 'Vegetarian',
                'vegan': 'Vegan',
                'pescetarian': 'Pescetarian',
                'gluten_free': 'Gluten-Free',
                'dairy_free': 'Dairy-Free',
                'keto': 'Keto',
                'paleo': 'Paleo'
            }
            
            for diet in dietary_prefs:
                if diet in diet_mapping:
                    dietary_restrictions.append(diet_mapping[diet])
            
            profile['dietary_restrictions'] = dietary_restrictions
            
            # Process seasonal importance
            seasonal_rating = all_answers.get('seasonal_importance', 3)
            profile['seasonal_preference'] = seasonal_rating / 5.0
            
            # Process cooking experience for health importance
            experience = all_answers.get('cooking_experience', 'casual')
            experience_mapping = {'beginner': 0.4, 'casual': 0.6, 'enthusiast': 0.8, 'expert': 1.0}
            profile['health_importance'] = experience_mapping.get(experience, 0.6)
            
            # Process time availability
            time_pref = all_answers.get('time_availability', 'moderate')
            time_mapping = {'quick': 30, 'moderate': 45, 'extended': 90, 'leisurely': 120}
            profile['max_cooking_time'] = time_mapping.get(time_pref, 45)
            
            # Store flavor preferences
            profile['flavor_preferences'] = all_answers.get('flavor_preferences', [])
            
            return profile
            
        except Exception as e:
            st.error(f"Error processing quiz results: {e}")
            return {'quiz_completed': False}

def render_cold_start_quiz():
    """Render the cold start quiz for new users"""
    st.markdown("""
    <div class="dreamy-header">
        <h1 style="margin: 0 0 1rem 0;">🌟 Welcome! Let's Personalize Your Experience</h1>
        <p style="margin: 0; color: #718096;">Help us understand your taste preferences to give you perfect seasonal recipe recommendations</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Initialize quiz
    if 'quiz_system' not in st.session_state:
        st.session_state.quiz_system = ColdStartQuiz()
        st.session_state.quiz_answers = {}
        st.session_state.current_question = 0
    
    quiz = st.session_state.quiz_system
    current_question_index = st.session_state.current_question
    
    # Check if quiz is completed
    if current_question_index >= len(quiz.questions):
        # Process results
        profile = quiz.process_quiz_results(st.session_state.quiz_answers)
        st.session_state.quiz_results = profile
        
        # Update user preferences based on quiz
        if profile.get('quiz_completed', False):
            # Update dietary restrictions
            if 'dietary_restrictions' in profile:
                st.session_state.user_preferences['dietary_restrictions'] = profile['dietary_restrictions']
            
            # Update other preferences
            if 'seasonal_preference' in profile:
                st.session_state.user_preferences['seasonal_preference'] = profile['seasonal_preference']
            if 'health_importance' in profile:
                st.session_state.user_preferences['health_importance'] = profile['health_importance']
            
            # Show completion
            st.success("🎉 Quiz completed! Your personalized recommendations are ready!")
            
            # Display quiz insights
            st.markdown("### 📊 Your Taste Profile")
            
            col1, col2, col3 = st.columns(3)
            
            with col1:
                seasonal_pref = profile.get('seasonal_preference', 0.5)
                st.markdown(f"""
                <div class="metric-card">
                    <h4 style="margin: 0;">🌿 Seasonal Focus</h4>
                    <h2 style="margin: 0.5rem 0 0 0;">{seasonal_pref*100:.0f}%</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                max_time = profile.get('max_cooking_time', 45)
                st.markdown(f"""
                <div class="metric-card">
                    <h4 style="margin: 0;">⏰ Cooking Time</h4>
                    <h2 style="margin: 0.5rem 0 0 0;">{max_time} minutes</h2>
                </div>
                """, unsafe_allow_html=True)
            
            with col3:
                health_imp = profile.get('health_importance', 0.6)
                st.markdown(f"""
                <div class="metric-card">
                    <h4 style="margin: 0;">💚 Health Focus</h4>
                    <h2 style="margin: 0.5rem 0 0 0;">{health_imp*100:.0f}%</h2>
                </div>
                """, unsafe_allow_html=True)
            
            # Show dietary restrictions
            dietary = profile.get('dietary_restrictions', [])
            if dietary:
                st.markdown("### 🥗 Your Dietary Preferences")
                for restriction in dietary:
                    st.markdown(f"✅ {restriction}")
            
            # Continue button
            if st.button("🚀 Start Discovering Recipes", type="primary"):
                st.session_state.quiz_completed = True
                st.rerun()
        
        return True
    
    # Render current question
    current_q = quiz.questions[current_question_index]
    
    # Fixed progress display
    st.markdown(f"### Question {current_question_index + 1} of {len(quiz.questions)}")
    
    # Progress bar
    progress = (current_question_index + 1) / len(quiz.questions)
    st.progress(progress)
    
    st.markdown(f"#### {current_q['question']}")
    
    # Get answer for current question
    if current_q['type'] == 'single_choice':
        answer = quiz.render_single_choice(current_q)
    elif current_q['type'] == 'multiple_choice':
        answer = quiz.render_multiple_choice(current_q)
    elif current_q['type'] == 'scale':
        answer = quiz.render_scale(current_q)
    else:
        answer = None
    
    # Navigation buttons
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col1:
        if current_question_index > 0:
            if st.button("← Previous"):
                st.session_state.current_question -= 1
                st.rerun()
    
    with col2:
        # Show skip option
        if st.button("Skip Quiz (Use Defaults)", type="secondary"):
            st.session_state.quiz_completed = True
            st.session_state.quiz_results = {'quiz_completed': False, 'skipped': True}
            st.rerun()
    
    with col3:
        if answer:
            if st.button("Next →", type="primary"):
                # Save answer
                st.session_state.quiz_answers.update(answer)
                st.session_state.current_question += 1
                st.rerun()
        else:
            st.button("Next →", disabled=True)
    
    return False

def render_main_application():
    """Render the main application interface"""
    # Sidebar with preferences
    with st.sidebar:
        st.markdown("## 🎯 Your Preferences")
        
        # Dietary restrictions
        st.markdown("### 🥗 Dietary Preferences")
        current_dietary = st.session_state.user_preferences.get('dietary_restrictions', [])
        
        selected_dietary = []
        for option, details in DIETARY_OPTIONS.items():
            is_selected = st.checkbox(
                f"{details['description']}",
                value=option in current_dietary,
                key=f"dietary_{option}"
            )
            if is_selected:
                selected_dietary.append(option)
        
        # Cuisines
        st.markdown("### 🌍 Favorite Cuisines")
        cuisine_options = list(CUISINE_KEYWORDS.keys())
        current_cuisines = st.session_state.user_preferences.get('favorite_cuisines', [])
        
        selected_cuisines = st.multiselect(
            "Select your favorites",
            [cuisine.title() for cuisine in cuisine_options],
            default=[cuisine.title() for cuisine in current_cuisines if cuisine.title() in [c.title() for c in cuisine_options]]
        )
        selected_cuisines_lower = [c.lower() for c in selected_cuisines]
        
        # Preference sliders
        st.markdown("### 🎚️ Preference Weights")
        
        sustainability_importance = st.slider(
            "🌱 Eco-Friendliness Priority",
            0.0, 1.0, 
            float(st.session_state.user_preferences.get('sustainability_importance', 0.5))
        )
        
        seasonal_preference = st.slider(
            "🌿 Seasonal Ingredients Priority",
            0.0, 1.0, 
            float(st.session_state.user_preferences.get('seasonal_preference', 0.7))
        )
        
        health_importance = st.slider(
            "💚 Health Priority",
            0.0, 1.0, 
            float(st.session_state.user_preferences.get('health_importance', 0.6))
        )
        
        # Update preferences
        preferences_changed = (
            selected_dietary != current_dietary or
            selected_cuisines_lower != current_cuisines or
            sustainability_importance != st.session_state.user_preferences.get('sustainability_importance', 0.5) or
            seasonal_preference != st.session_state.user_preferences.get('seasonal_preference', 0.7) or
            health_importance != st.session_state.user_preferences.get('health_importance', 0.6)
        )
        
        if preferences_changed:
            st.session_state.user_preferences.update({
                'dietary_restrictions': selected_dietary,
                'favorite_cuisines': selected_cuisines_lower,
                'sustainability_importance': sustainability_importance,
                'seasonal_preference': seasonal_preference,
                'health_importance': health_importance
            })
            st.success("✨ Preferences updated!")
        
        # User activity summary
        st.markdown("---")
        st.markdown("## 📊 Your Journey")
        activity = st.session_state.user_activity
        
        saved_count = len(activity.get('liked_recipes', []))
        cooked_count = len(activity.get('cooked_recipes', []))
        
        st.markdown(f"""
        <div style="display: flex; justify-content: space-around;">
            <div style="text-align: center;">
                <h3 style="margin: 0;">❤️ {saved_count}</h3>
                <p style="margin: 0; font-size: 0.8rem;">Saved</p>
            </div>
            <div style="text-align: center;">
                <h3 style="margin: 0;">✅ {cooked_count}</h3>
                <p style="margin: 0; font-size: 0.8rem;">Cooked</p>
            </div>
        </div>
        """, unsafe_allow_html=True)
    
    # Main content tabs
    tab1, tab2, tab3 = st.tabs([
        "✨ Recommendations", 
        "📊 Analytics", 
        "💝 My Collection"
    ])
    
    with tab1:
        st.markdown("## ✨ Your Personalized Recommendations")
        
        # Seasonal spotlight
        render_seasonal_spotlight()
        
        recommendation_engine = st.session_state.get('recommendation_engine')
        if not recommendation_engine:
            st.error("Recommendation system not available. Please refresh the page.")
            return
        
        user_preferences = st.session_state.get('user_preferences', {})
        
        # Get recommendations
        with st.spinner("🔮 Creating personalized recommendations..."):
            recommendations, used_ai_model = recommendation_engine.get_recommendations(
                user_preferences, n_recommendations=9
            )
        
        # Display recommendations using grid layout
        render_recipes_grid(recommendations)
    
    with tab2:
        render_analytics()
    
    with tab3:
        render_my_collection()

# =============================================================================
# MAIN APPLICATION
# =============================================================================

def main():
    """Main application"""
    try:
        # Initialize systems
        inject_dreamy_css()
        initialize_user_system()
        
        # Initialize recommendation engine
        if 'recommendation_engine' not in st.session_state:
            with st.spinner("🌸 Loading recommendation system..."):
                st.session_state.recommendation_engine = DreamyRecommendationEngine()
        
        # Render header
        render_header()
        
        # Model status
        model_available = render_model_status()
        
        # Check if user needs onboarding quiz
        if not st.session_state.get('quiz_completed', False):
            quiz_completed = render_cold_start_quiz()
            if not quiz_completed:
                return  # Stay in quiz mode
        
        # Render main application
        render_main_application()
        
    except Exception as e:
        st.error(f"Application error: {str(e)}")
        st.markdown("Please refresh the page to restart the application.")

if __name__ == "__main__":
    main()