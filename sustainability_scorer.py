"""
Sustainability Scoring for Recipes
"""
import pandas as pd
import numpy as np
from datetime import date

# Carbon footprint data (kg CO2 per kg of ingredient)
CARBON_FOOTPRINT = {
    # High carbon footprint
    'beef': 27.0, 'lamb': 39.2, 'cheese': 13.5, 'pork': 12.1,
    'butter': 11.5, 'chocolate': 19.0, 'coffee': 16.5,
    
    # Medium carbon footprint
    'chicken': 6.9, 'fish': 6.1, 'eggs': 4.8, 'milk': 3.2,
    'rice': 4.0, 'yogurt': 2.2,
    
    # Low carbon footprint
    'vegetables': 2.0, 'fruits': 1.1, 'bread': 1.1,
    'potatoes': 0.9, 'lentils': 0.9, 'beans': 0.8,
    'nuts': 2.3, 'tofu': 2.0, 'pasta': 1.9
}

# Seasonal produce by season
SEASONAL_PRODUCE = {
    'spring': {
        'asparagus', 'strawberries', 'peas', 'artichokes', 'spinach', 
        'radishes', 'rhubarb', 'lettuce', 'carrots', 'new potatoes'
    },
    'summer': {
        'tomatoes', 'corn', 'peaches', 'watermelon', 'zucchini', 
        'berries', 'cucumber', 'peppers', 'eggplant', 'basil'
    },
    'autumn': {
        'apples', 'pumpkin', 'squash', 'sweet potatoes', 'brussels sprouts',
        'pears', 'cranberries', 'mushrooms', 'pomegranate', 'grapes'
    },
    'winter': {
        'citrus', 'kale', 'cabbage', 'potatoes', 'beets',
        'carrots', 'onions', 'turnips', 'leeks', 'parsnips'
    }
}

def get_current_season():
    """Get current season based on month"""
    month = date.today().month
    if month in [3, 4, 5]:
        return 'spring'
    elif month in [6, 7, 8]:
        return 'summer'
    elif month in [9, 10, 11]:
        return 'autumn'
    else:
        return 'winter'

def calculate_carbon_score(ingredients):
    """Calculate carbon footprint score for a recipe"""
    if not ingredients:
        return 50  # Default middle score
    
    total_carbon = 0
    ingredient_count = 0
    
    for ingredient in ingredients:
        ingredient_lower = str(ingredient).lower()
        
        # Check each carbon footprint item
        for item, carbon_value in CARBON_FOOTPRINT.items():
            if item in ingredient_lower:
                total_carbon += carbon_value
                ingredient_count += 1
                break
        else:
            # Default carbon value for unknown ingredients
            total_carbon += 2.0
            ingredient_count += 1
    
    # Calculate average carbon footprint
    avg_carbon = total_carbon / ingredient_count if ingredient_count > 0 else 2.0
    
    # Convert to 0-100 score (lower carbon = higher score)
    # Assuming max carbon is 40 (lamb) and min is 0.8 (beans)
    carbon_score = 100 - ((avg_carbon / 40) * 100)
    carbon_score = max(0, min(100, carbon_score))
    
    return carbon_score

def calculate_seasonality_score(ingredients, season=None):
    """Calculate how seasonal a recipe is"""
    if season is None:
        season = get_current_season()
    
    if not ingredients:
        return 50
    
    seasonal_ingredients = SEASONAL_PRODUCE.get(season, set())
    
    # Count seasonal ingredients
    seasonal_count = 0
    total_produce = 0
    
    for ingredient in ingredients:
        ingredient_lower = str(ingredient).lower()
        
        # Check if it's a produce item
        is_produce = any(produce in ingredient_lower for produce_list in SEASONAL_PRODUCE.values() for produce in produce_list)
        
        if is_produce:
            total_produce += 1
            # Check if it's seasonal
            if any(seasonal in ingredient_lower for seasonal in seasonal_ingredients):
                seasonal_count += 1
    
    # Calculate score
    if total_produce == 0:
        return 50  # No produce, neutral score
    
    seasonality_score = (seasonal_count / total_produce) * 100
    return seasonality_score

def calculate_sustainability_score(recipe):
    """Calculate overall sustainability score for a recipe"""
    ingredients = recipe.get('ingredients', [])
    
    # Get component scores
    carbon_score = calculate_carbon_score(ingredients)
    seasonality_score = calculate_seasonality_score(ingredients)
    
    # Check for plant-based
    is_plant_based = all(
        not any(animal in str(ing).lower() for animal in ['beef', 'lamb', 'pork', 'chicken', 'fish', 'egg', 'milk', 'cheese', 'butter'])
        for ing in ingredients
    )
    
    plant_bonus = 20 if is_plant_based else 0
    
    # Weighted average
    sustainability_score = (
        carbon_score * 0.5 +  # 50% weight on carbon footprint
        seasonality_score * 0.3 +  # 30% weight on seasonality
        plant_bonus * 0.2  # 20% bonus for plant-based
    )
    
    # Classification
    if sustainability_score >= 80:
        category = "Eco Champion"
        badge_class = "eco-excellent"
    elif sustainability_score >= 60:
        category = "Earth Friendly"
        badge_class = "eco-good"
    else:
        category = "Room for Improvement"
        badge_class = "eco-poor"
    
    return {
        'score': sustainability_score,
        'carbon_score': carbon_score,
        'seasonality_score': seasonality_score,
        'is_plant_based': is_plant_based,
        'category': category,
        'badge_class': badge_class
    }

def get_sustainability_tips(recipe, sustainability_data):
    """Get tips to improve recipe sustainability"""
    tips = []
    
    if sustainability_data['carbon_score'] < 60:
        tips.append("💡 Consider replacing high-carbon ingredients like beef or lamb with chicken, fish, or plant proteins")
    
    if sustainability_data['seasonality_score'] < 60:
        season = get_current_season()
        seasonal_items = list(SEASONAL_PRODUCE[season])[:3]
        tips.append(f"🌱 Try adding seasonal ingredients like {', '.join(seasonal_items)}")
    
    if not sustainability_data['is_plant_based']:
        tips.append("🌿 Make it plant-based by using tofu, tempeh, or legumes instead of meat")
    
    # Time-based tip
    if recipe.get('minutes', 0) > 60:
        tips.append("⚡ Consider batch cooking to save energy")
    
    return tips

# Test the module
if __name__ == "__main__":
    # Test recipe
    test_recipe = {
        'name': 'Summer Vegetable Pasta',
        'ingredients': ['tomatoes', 'zucchini', 'basil', 'pasta', 'olive oil', 'garlic'],
        'minutes': 30
    }
    
    result = calculate_sustainability_score(test_recipe)
    print(f"Sustainability Score: {result['score']:.1f}")
    print(f"Category: {result['category']}")
    print(f"Carbon Score: {result['carbon_score']:.1f}")
    print(f"Seasonality Score: {result['seasonality_score']:.1f}")
    print(f"Plant-based: {result['is_plant_based']}")
    
    tips = get_sustainability_tips(test_recipe, result)
    print("\nTips:")
    for tip in tips:
        print(tip)