"""
Real Sustainability Scoring with Actual Environmental Data
Sources: 
- Poore & Nemecek (2018) - Science journal
- EPA data
- FAO statistics
"""

import pandas as pd
import numpy as np
from datetime import date

# Real carbon footprint data (kg CO2e per kg of food)
# Source: Poore & Nemecek (2018), "Reducing food's environmental impacts"
CARBON_FOOTPRINT_REAL = {
    # Meats (highest impact)
    'beef': 60.0,
    'lamb': 24.0,
    'mutton': 24.0,
    'pork': 7.0,
    'poultry': 6.0,
    'chicken': 6.0,
    'turkey': 10.9,
    'duck': 8.0,
    
    # Seafood
    'fish': 5.0,
    'salmon': 11.9,
    'tuna': 6.1,
    'shrimp': 12.0,
    'prawns': 12.0,
    'crab': 11.0,
    'lobster': 20.0,
    
    # Dairy & Eggs
    'cheese': 21.0,
    'milk': 2.8,
    'yogurt': 2.2,
    'butter': 11.5,
    'cream': 5.5,
    'eggs': 4.5,
    'egg': 4.5,
    
    # Plant proteins
    'tofu': 2.0,
    'tempeh': 2.5,
    'beans': 0.9,
    'lentils': 0.9,
    'chickpeas': 0.8,
    'peas': 0.9,
    'nuts': 2.3,
    'almonds': 2.3,
    'walnuts': 2.3,
    
    # Grains
    'rice': 4.0,
    'wheat': 1.4,
    'bread': 1.1,
    'pasta': 1.5,
    'oats': 1.7,
    'quinoa': 1.5,
    
    # Vegetables (lowest impact)
    'vegetables': 0.4,
    'potatoes': 0.3,
    'tomatoes': 1.4,
    'onions': 0.5,
    'carrots': 0.4,
    'broccoli': 0.7,
    'spinach': 0.7,
    'lettuce': 0.5,
    'cabbage': 0.5,
    
    # Fruits
    'apples': 0.4,
    'bananas': 0.9,
    'berries': 1.0,
    'citrus': 0.4,
    'grapes': 1.0,
    'avocado': 2.5,
    
    # Others
    'chocolate': 19.0,
    'coffee': 16.5,
    'sugar': 3.0,
    'oil': 3.5,
    'olive oil': 6.0
}

# Water usage data (liters per kg)
WATER_FOOTPRINT = {
    'beef': 15415,
    'pork': 5988,
    'chicken': 4325,
    'eggs': 3265,
    'milk': 1020,
    'cheese': 5060,
    'rice': 2497,
    'wheat': 1827,
    'vegetables': 322,
    'fruits': 962,
    'nuts': 9063,
    'chocolate': 17196
}

# Seasonal produce by month (Northern Hemisphere)
SEASONAL_CALENDAR = {
    1: ['cabbage', 'kale', 'leeks', 'brussels sprouts', 'cauliflower', 'citrus'],
    2: ['cabbage', 'kale', 'leeks', 'brussels sprouts', 'cauliflower', 'citrus'],
    3: ['broccoli', 'lettuce', 'peas', 'spinach', 'artichokes', 'asparagus'],
    4: ['asparagus', 'peas', 'lettuce', 'spinach', 'strawberries', 'rhubarb'],
    5: ['asparagus', 'strawberries', 'peas', 'lettuce', 'spinach', 'cherries'],
    6: ['strawberries', 'cherries', 'blueberries', 'tomatoes', 'cucumber', 'zucchini'],
    7: ['tomatoes', 'corn', 'berries', 'peaches', 'cucumber', 'zucchini', 'beans'],
    8: ['tomatoes', 'corn', 'berries', 'peaches', 'peppers', 'eggplant', 'melons'],
    9: ['apples', 'pears', 'grapes', 'tomatoes', 'peppers', 'eggplant', 'squash'],
    10: ['apples', 'pumpkin', 'squash', 'sweet potatoes', 'brussels sprouts', 'cranberries'],
    11: ['squash', 'pumpkin', 'sweet potatoes', 'brussels sprouts', 'cranberries', 'kale'],
    12: ['cabbage', 'kale', 'brussels sprouts', 'leeks', 'citrus', 'pomegranate']
}

def calculate_real_carbon_score(ingredients):
    """Calculate actual carbon footprint score based on scientific data"""
    if not ingredients:
        return 50, 0, []
    
    total_carbon = 0
    carbon_breakdown = []
    ingredient_weights = []
    
    # Estimate 200g per ingredient (can be refined)
    default_weight = 0.2  # kg
    
    for ingredient in ingredients:
        ing_lower = str(ingredient).lower()
        carbon_value = 0
        matched_item = None
        
        # Find best match for carbon data
        for item, carbon in CARBON_FOOTPRINT_REAL.items():
            if item in ing_lower:
                carbon_value = carbon
                matched_item = item
                break
        
        # Default values by category
        if carbon_value == 0:
            if any(meat in ing_lower for meat in ['meat', 'steak', 'roast']):
                carbon_value = 20.0  # Generic meat
                matched_item = 'meat'
            elif any(veg in ing_lower for veg in ['vegetable', 'veggie', 'salad']):
                carbon_value = 0.5  # Generic vegetable
                matched_item = 'vegetable'
            else:
                carbon_value = 2.0  # Generic food
                matched_item = 'other'
        
        ingredient_carbon = carbon_value * default_weight
        total_carbon += ingredient_carbon
        carbon_breakdown.append({
            'ingredient': ingredient,
            'matched': matched_item,
            'carbon_per_kg': carbon_value,
            'total_carbon': ingredient_carbon
        })
    
    # Convert to score (0-100, where 100 is best)
    # Assuming a meal with 10kg CO2e is very bad, 0.5kg is very good
    carbon_score = max(0, min(100, 100 - (total_carbon / 10) * 100))
    
    return carbon_score, total_carbon, carbon_breakdown

def calculate_water_score(ingredients):
    """Calculate water footprint score"""
    if not ingredients:
        return 50
    
    total_water = 0
    default_weight = 0.2  # kg
    
    for ingredient in ingredients:
        ing_lower = str(ingredient).lower()
        water_value = 500  # Default
        
        for item, water in WATER_FOOTPRINT.items():
            if item in ing_lower:
                water_value = water
                break
        
        total_water += water_value * default_weight
    
    # Convert to score (15000L is bad, 500L is good for a meal)
    water_score = max(0, min(100, 100 - (total_water / 15000) * 100))
    
    return water_score

def is_currently_seasonal(ingredient):
    """Check if ingredient is currently in season"""
    current_month = date.today().month
    seasonal_items = SEASONAL_CALENDAR.get(current_month, [])
    
    ing_lower = str(ingredient).lower()
    return any(seasonal in ing_lower for seasonal in seasonal_items)

def calculate_real_sustainability_score(recipe):
    """Calculate comprehensive sustainability score using real data"""
    ingredients = recipe.get('ingredients', [])
    
    # Get component scores
    carbon_score, total_carbon, carbon_breakdown = calculate_real_carbon_score(ingredients)
    water_score = calculate_water_score(ingredients)
    
    # Seasonality
    seasonal_count = sum(1 for ing in ingredients if is_currently_seasonal(ing))
    seasonality_score = (seasonal_count / len(ingredients) * 100) if ingredients else 50
    
    # Plant-based bonus
    meat_keywords = ['beef', 'pork', 'chicken', 'lamb', 'fish', 'meat', 'turkey', 'duck']
    dairy_keywords = ['milk', 'cheese', 'butter', 'cream', 'yogurt']
    
    has_meat = any(
        any(meat in str(ing).lower() for meat in meat_keywords)
        for ing in ingredients
    )
    has_dairy = any(
        any(dairy in str(ing).lower() for dairy in dairy_keywords)
        for ing in ingredients
    )
    
    is_plant_based = not has_meat and not has_dairy
    is_vegetarian = not has_meat
    
    # Calculate final score
    sustainability_score = (
        carbon_score * 0.5 +      # 50% weight on carbon
        water_score * 0.2 +       # 20% weight on water
        seasonality_score * 0.2 + # 20% weight on seasonality
        (10 if is_plant_based else 5 if is_vegetarian else 0)  # Bonus points
    )
    
    # Determine category
    if sustainability_score >= 80:
        category = "Climate Hero 🌟"
        badge_class = "eco-excellent"
        impact = "Very Low Environmental Impact"
    elif sustainability_score >= 60:
        category = "Eco Friendly 🌿"
        badge_class = "eco-good"
        impact = "Low Environmental Impact"
    elif sustainability_score >= 40:
        category = "Moderate Impact ⚡"
        badge_class = "eco-moderate"
        impact = "Moderate Environmental Impact"
    else:
        category = "High Impact ⚠️"
        badge_class = "eco-poor"
        impact = "High Environmental Impact"
    
    return {
        'score': sustainability_score,
        'carbon_score': carbon_score,
        'water_score': water_score,
        'seasonality_score': seasonality_score,
        'total_carbon_kg': total_carbon,
        'is_plant_based': is_plant_based,
        'is_vegetarian': is_vegetarian,
        'category': category,
        'badge_class': badge_class,
        'impact': impact,
        'carbon_breakdown': carbon_breakdown
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