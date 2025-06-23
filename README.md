# recipe-recommender-system
Personalized recipe recommendation system using Food.com dataset

Overview
DreamyFood is an innovative recipe recommendation system that combines artificial intelligence with environmental consciousness to help users discover delicious, seasonal recipes. Our app creates a magical cooking experience while promoting sustainable food choices.

Mission
Empower home cooks to make environmentally conscious food choices through personalized, seasonal recipe recommendations that reduce carbon footprint and celebrate local ingredients.

Key Features

Smart Recommendations

AI-Powered Engine: Advanced hybrid recommendation system combining collaborative and content-based filtering
Cold-Start Onboarding: Interactive 5-question quiz for instant personalization
Real-Time Adaptation: System learns from user interactions and preferences
Contextual Suggestions: Weather and time-aware recommendations

Sustainability Intelligence

Real Environmental Data: Carbon footprint calculations based on Poore & Nemecek (2018) research
Seasonal Awareness: Promotes ingredients that are currently in season
Plant-Based Detection: Automatic identification and promotion of sustainable options
Impact Visualization: Relatable environmental comparisons (car miles, tree absorption days)

Gamified Experience

Achievement System: Unlock badges for sustainable cooking milestones
Progress Tracking: Visual progress bars for weekly challenges
Recipe Collection: Save and organize favorite recipes
Cooking History: Track culinary journey with statistics

Design

Seasonal Themes: Dynamic weather-aware headers and color schemes
Responsive Layout: Perfect experience on desktop and mobile
Micro-Interactions: Delightful animations and feedback


Quick Start
Prerequisites

Python 3.8 or higher
pip package manager
Git

Installation

Clone the Repository
bashgit clone https://github.com/ShiIiA/recipe-recommender-system.git
cd recipe-recommender-system

Create Virtual Environment (Recommended)
bashpython -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate

Install Dependencies
bashpip install -r requirements.txt

Run the Application
bashstreamlit run app.py

Open Your Browser
Navigate to http://localhost:8501 to start discovering recipes!


Project Architecture
recipe-recommender-system/
├── app.py                      # Main Streamlit application
├── sustainability_real_data.py # Environmental impact calculations
├── sustainability_scorer.py    # Alternative sustainability scoring
├── requirements.txt            # Python dependencies
├── data/                       # Data files and exploration
│   ├── exploration.ipynb       # EDA notebook
│   ├── raw_recipes.csv         # Raw recipe dataset
│   └── processed_recipes.pkl   # Processed recipe data
├── models/                     # Trained recommendation models
│   ├── hybrid_recommender.pkl  # Main AI model
│   └── model_metrics.json      # Performance metrics
├── screenshots/               # Application screenshots
├── docs/                       # Additional documentation
└── tests/                      # Unit tests

Core Components
1. Recommendation Engine
pythonclass DreamyRecommendationEngine:
    - AI Model Integration
    - Content-based Filtering  
    - Preference Learning
    - Real-time Adaptation

Features:

Hybrid approach combining multiple recommendation strategies
Handles cold-start problem with intelligent onboarding
Learns from user behavior (likes, cooks, views)
Fallback mechanisms for robust performance

2. Sustainability Module
pythondef calculate_real_sustainability_score(recipe):
    - Carbon Footprint Analysis
    - Water Usage Calculation
    - Seasonal Ingredient Scoring
    - Plant-based Classification
Data Sources:

Carbon Data: Poore & Nemecek (2018) Science journal
Seasonal Data: USDA agricultural calendars
Water Usage: Water Footprint Network data

3. User Interface
pythondef render_dreamy_interface():
    - Seasonal Theme Engine
    - Interactive Recipe Cards
    - Modal Recipe Details
    - Progress Visualization
Design Philosophy:

Biomimicry: Colors and patterns inspired by nature
Seasonal Adaptation: UI changes with weather and time
Micro-interactions: Smooth animations and transitions
Accessibility: High contrast and semantic markup


Sustainability Features
Environmental Impact Metrics
MetricDescriptionData SourceCarbon Footprintkg CO2e per kg of ingredientPoore & Nemecek (2018)Water UsageLiters per kg of ingredientWater Footprint NetworkSeasonality Score% of seasonal ingredientsUSDA Seasonal CalendarTransportation ImpactLocal vs. imported ingredientsRegional Agricultural Data

Sustainability Categories

 Climate Hero (80-100%): Very low environmental impact
 Eco Friendly (60-79%): Low environmental impact
 Moderate Impact (40-59%): Moderate environmental impact
 High Impact (0-39%): High environmental impact

Impact Visualization
Your Recipe's Impact:
🚗 Carbon equivalent to driving 2.4 km
🌳 Would take a tree 0.8 days to absorb
💧 Water usage: 45 liters
📅 75% seasonal ingredients

Gamification System

Achievement Badges
BadgeRequirementReward🌱 Plant PioneerCook 5 plant-based recipesUnlock advanced plant-based recipes🌿 Seasonal SageUse 90% seasonal ingredients in a weekSeasonal recipe collection♻️ Eco ChampionAchieve 10 "Climate Hero" recipesSustainability tips library👨‍🍳 Culinary ExplorerTry 5 different cuisinesInternational recipe unlock🔥 Streak MasterCook daily for 7 daysPremium recipe features

Progress Tracking

Weekly Challenges: "Cook 3 vegetarian dinners this week"
Monthly Goals: "Reduce carbon footprint by 20%"
Seasonal Quests: "Try 10 autumn ingredients"
Skill Progression: Beginner → Intermediate → Expert → Master Chef


Technical Implementation
 Technology Stack
ComponentTechnologyPurposeFrontendStreamlitInteractive web applicationData ProcessingPandas, NumPyRecipe and user data manipulationVisualizationPlotlyInteractive charts and graphsStylingCustom CSSDreamy aesthetic and animationsState ManagementStreamlit Session StateUser preferences and activityRecommendationsScikit-learnMachine learning algorithms

Recommendation Algorithm
pythondef get_recommendations(user_preferences, n_recommendations=9):
    """
    Hybrid recommendation approach:
    1. Content-based filtering (50% weight)
    2. Collaborative filtering (30% weight)  
    3. Sustainability boost (20% weight)
    """
    
    # Content-based score
    content_score = calculate_content_similarity(user_profile, recipes)
    
    # Collaborative score (if available)
    collaborative_score = get_collaborative_recommendations(user_id)
    
    # Sustainability bonus
    sustainability_bonus = apply_eco_preference_boost(user_preferences)
    
    # Weighted combination
    final_score = (
        content_score * 0.5 + 
        collaborative_score * 0.3 + 
        sustainability_bonus * 0.2
    )
    
    return top_n_recipes(final_score, n_recommendations)
 Sustainability Scoring Algorithm
pythondef calculate_sustainability_score(recipe):
    """
    Multi-factor sustainability assessment:
    - Carbon footprint (50% weight)
    - Water usage (20% weight)
    - Seasonality (20% weight)
    - Plant-based bonus (10% weight)
    """
    
    carbon_score = calculate_carbon_impact(recipe.ingredients)
    water_score = calculate_water_usage(recipe.ingredients)
    seasonal_score = calculate_seasonality(recipe.ingredients)
    plant_bonus = check_plant_based(recipe.ingredients)
    
    return weighted_average([
        (carbon_score, 0.5),
        (water_score, 0.2), 
        (seasonal_score, 0.2),
        (plant_bonus, 0.1)
    ])

 User Experience Flow
 1. Onboarding Journey
mermaidgraph LR
    A[Welcome] --> B[Quiz: Cooking Experience]
    B --> C[Quiz: Flavor Preferences]
    C --> D[Quiz: Dietary Restrictions]
    D --> E[Quiz: Time Availability]
    E --> F[Quiz: Sustainability Importance]
    F --> G[Personalized Dashboard]
 2. Recipe Discovery
mermaidgraph LR
    A[Seasonal Header] --> B[Recommended Recipes]
    B --> C[Recipe Details Modal]
    C --> D[Save/Cook Actions]
    D --> E[Updated Preferences]
    E --> F[Improved Recommendations]
 3. Progress Tracking
mermaidgraph LR
    A[Cooking Activity] --> B[Sustainability Metrics]
    B --> C[Achievement Progress]
    C --> D[Badge Unlocks]
    D --> E[Social Sharing]


 Data Science Approach
 Dataset Information


Model Performance




License
This project is licensed under the MIT License - see the LICENSE file for details.
MIT License

Copyright (c) 2024 DreamyFood Contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

Acknowledgments
Research & Data

Poore & Nemecek (2018): "Reducing food's environmental impacts through producers and consumers" - Science Journal
Water Footprint Network: Global water usage data
USDA: Seasonal produce calendars and nutritional data
FAO: Food and Agriculture Organization sustainability metrics

Design Inspiration

Studio Ghibli Films: Visual aesthetics and natural themes
Material Design: Google's design principles
Figma Community: UI/UX design patterns and components

Technology Used

Streamlit: Amazing web app framework
Plotly: Interactive visualization library
Pandas: Data manipulation and analysis
Scikit-learn: Machine learning algorithms
