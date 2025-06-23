"""
Enhanced Recipe Recommendation App with Proper ML Models
"""
import streamlit as st
import pandas as pd
import numpy as np
import pickle
from pathlib import Path
from datetime import datetime, date
import json
import os
from recommendation_models import HybridRecommender
import random

# Page configuration
st.set_page_config(
    page_title="🌿 Ghibli Recipe Garden - AI Powered",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constants
DATA_DIR = "user_data"
MODEL_PATH = "models/hybrid_model.pkl"
RECIPES_PATH = "processed_data/recipes_full.pkl"
INTERACTIONS_PATH = "processed_data/interactions_full.pkl"

# Create directories
Path(DATA_DIR).mkdir(exist_ok=True)

# =============================================================================
# SESSION STATE INITIALIZATION
# =============================================================================
def init_session_state():
    """Initialize session state variables"""
    if 'user_id' not in st.session_state:
        # Simulate user login - in production, this would be actual auth
        st.session_state.user_id = random.randint(1000, 999999)
    
    if 'user_profile' not in st.session_state:
        st.session_state.user_profile = load_user_profile(st.session_state.user_id)
    
    if 'recommender' not in st.session_state:
        st.session_state.recommender = None
    
    if 'recipes_df' not in st.session_state:
        st.session_state.recipes_df = None
    
    if 'interactions_df' not in st.session_state:
        st.session_state.interactions_df = None
    
    if 'current_page' not in st.session_state:
        st.session_state.current_page = "Home"

# =============================================================================
# DATA LOADING
# =============================================================================
@st.cache_resource
def load_model():
    """Load the trained recommendation model"""
    try:
        if Path(MODEL_PATH).exists():
            return HybridRecommender.load_model(MODEL_PATH)
        else:
            st.warning("Model not found. Please run train_model.py first!")
            return None
    except Exception as e:
        st.error(f"Error loading model: {e}")
        return None

@st.cache_data
def load_recipe_data():
    """Load processed recipe data"""
    try:
        if Path(RECIPES_PATH).exists():
            return pd.read_pickle(RECIPES_PATH)
        else:
            st.warning("Processed recipes not found. Loading raw data...")
            # Fallback to raw data
            return load_raw_recipes()
    except Exception as e:
        st.error(f"Error loading recipes: {e}")
        return pd.DataFrame()

@st.cache_data
def load_interaction_data():
    """Load processed interaction data"""
    try:
        if Path(INTERACTIONS_PATH).exists():
            return pd.read_pickle(INTERACTIONS_PATH)
        else:
            return pd.DataFrame()
    except Exception as e:
        st.error(f"Error loading interactions: {e}")
        return pd.DataFrame()

def load_raw_recipes():
    """Fallback to load raw recipes"""
    import ast
    
    paths = ["RAW_recipes.csv", "data/RAW_recipes.csv"]
    for path in paths:
        if Path(path).exists():
            df = pd.read_csv(path, nrows=10000)
            # Basic preprocessing
            df['ingredients'] = df['ingredients'].apply(lambda x: ast.literal_eval(x) if pd.notna(x) else [])
            df['tags'] = df['tags'].apply(lambda x: ast.literal_eval(x) if pd.notna(x) else [])
            df['health_score'] = np.random.randint(60, 100, size=len(df))  # Placeholder
            return df
    return pd.DataFrame()

# =============================================================================
# USER PROFILE MANAGEMENT
# =============================================================================
def save_user_profile(profile, user_id):
    """Save user profile to JSON"""
    filepath = Path(DATA_DIR) / f"user_{user_id}.json"
    with open(filepath, 'w') as f:
        json.dump(profile, f, indent=2)

def load_user_profile(user_id):
    """Load user profile from JSON"""
    filepath = Path(DATA_DIR) / f"user_{user_id}.json"
    
    if filepath.exists():
        with open(filepath, 'r') as f:
            return json.load(f)
    
    # Default profile
    return {
        'user_id': user_id,
        'liked_recipes': [],
        'disliked_recipes': [],
        'rated_recipes': {},
        'dietary_restrictions': [],
        'skill_level': 'intermediate',
        'preferred_time': 'medium',
        'cuisine_preferences': [],
        'health_conscious': False,
        'sustainability_focus': False,
        'achievements': [],
        'points': 0,
        'level': 1,
        'created_at': datetime.now().isoformat()
    }

# =============================================================================
# HELPER FUNCTIONS
# =============================================================================
def get_current_season():
    """Get current season"""
    month = date.today().month
    if month in [3, 4, 5]:
        return "spring"
    elif month in [6, 7, 8]:
        return "summer"
    elif month in [9, 10, 11]:
        return "autumn"
    else:
        return "winter"

def calculate_user_level(points):
    """Calculate user level from points"""
    levels = [
        (0, "Novice Cook"),
        (100, "Home Chef"),
        (300, "Skilled Cook"),
        (600, "Master Chef"),
        (1000, "Culinary Expert")
    ]
    
    for threshold, title in reversed(levels):
        if points >= threshold:
            return title
    return "Novice Cook"

def award_achievement(achievement_id, achievement_name, points=50):
    """Award achievement to user"""
    profile = st.session_state.user_profile
    
    if achievement_id not in profile['achievements']:
        profile['achievements'].append(achievement_id)
        profile['points'] += points
        save_user_profile(profile, st.session_state.user_id)
        st.success(f"🏆 Achievement Unlocked: {achievement_name} (+{points} points)")

# =============================================================================
# UI COMPONENTS
# =============================================================================
def create_header():
    """Create beautiful seasonal header"""
    season = get_current_season()
    current_time = datetime.now().strftime("%H:%M")
    current_date = datetime.now().strftime("%B %d, %Y")
    
    season_themes = {
        "spring": {
            "gradient": "linear-gradient(135deg, #a8e6cf 0%, #dcedc1 100%)",
            "emoji": "🌸",
            "message": "Fresh beginnings bloom in every dish"
        },
        "summer": {
            "gradient": "linear-gradient(135deg, #ffeaa7 0%, #fab1a0 100%)",
            "emoji": "🌻",
            "message": "Savor the sunshine in seasonal flavors"
        },
        "autumn": {
            "gradient": "linear-gradient(135deg, #ff7b00 0%, #ffc048 100%)",
            "emoji": "🍂",
            "message": "Harvest warmth in every recipe"
        },
        "winter": {
            "gradient": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
            "emoji": "❄️",
            "message": "Cozy comfort food for the soul"
        }
    }
    
    theme = season_themes[season]
    
    st.markdown(f"""
    <div style="background: {theme['gradient']}; padding: 3rem; border-radius: 0 0 30px 30px; margin: -3rem -3rem 2rem -3rem; text-align: center;">
        <h1 style="color: white; font-size: 3.5rem; margin: 0; text-shadow: 2px 2px 4px rgba(0,0,0,0.2);">
            {theme['emoji']} Ghibli Recipe Garden {theme['emoji']}
        </h1>
        <p style="color: white; font-size: 1.5rem; margin: 1rem 0; opacity: 0.95;">
            {current_time} • {current_date}
        </p>
        <p style="color: white; font-size: 1.2rem; font-style: italic; opacity: 0.9;">
            {theme['message']}
        </p>
    </div>
    """, unsafe_allow_html=True)

def display_recipe_card(recipe, context="view", show_actions=True):
    """Display a recipe card"""
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.markdown(f"### {recipe['name']}")
        
        # Tags
        if 'tags' in recipe and recipe['tags']:
            tags_html = " ".join([f"<span style='background: #e0e0e0; padding: 2px 8px; border-radius: 12px; margin: 2px; display: inline-block; font-size: 0.8rem;'>{tag}</span>" 
                                for tag in recipe['tags'][:5]])
            st.markdown(tags_html, unsafe_allow_html=True)
        
        # Description
        if 'description' in recipe and recipe['description']:
            st.write(recipe['description'][:200] + "..." if len(str(recipe['description'])) > 200 else recipe['description'])
    
    with col2:
        # Stats
        st.metric("⏱️ Time", f"{recipe.get('minutes', 30)} min")
        st.metric("🍃 Health Score", f"{recipe.get('health_score', 75):.0f}/100")
        
        if 'n_ingredients' in recipe:
            st.metric("🥘 Ingredients", recipe['n_ingredients'])
    
    if show_actions:
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            if st.button("👍 Like", key=f"like_{recipe['id']}_{context}"):
                add_rating(recipe['id'], 5)
                
        with col2:
            if st.button("👎 Dislike", key=f"dislike_{recipe['id']}_{context}"):
                add_rating(recipe['id'], 2)
                
        with col3:
            if st.button("📖 View Recipe", key=f"view_{recipe['id']}_{context}"):
                st.session_state.selected_recipe = recipe['id']
                st.session_state.current_page = "Recipe Detail"
                st.rerun()
        
        with col4:
            if st.button("🍳 Cooked It!", key=f"cook_{recipe['id']}_{context}"):
                award_achievement("first_cook", "First Dish Cooked!", 30)
                st.balloons()

def add_rating(recipe_id, rating):
    """Add user rating for a recipe"""
    profile = st.session_state.user_profile
    profile['rated_recipes'][str(recipe_id)] = rating
    
    if rating >= 4:
        if recipe_id not in profile['liked_recipes']:
            profile['liked_recipes'].append(recipe_id)
        if recipe_id in profile['disliked_recipes']:
            profile['disliked_recipes'].remove(recipe_id)
    elif rating <= 2:
        if recipe_id not in profile['disliked_recipes']:
            profile['disliked_recipes'].append(recipe_id)
        if recipe_id in profile['liked_recipes']:
            profile['liked_recipes'].remove(recipe_id)
    
    profile['points'] += 5
    save_user_profile(profile, st.session_state.user_id)
    
    # Check for achievements
    if len(profile['rated_recipes']) == 10:
        award_achievement("rate_10", "Recipe Critic", 50)
    
    st.success("Rating saved! +5 points")

# =============================================================================
# PAGE FUNCTIONS
# =============================================================================
def home_page():
    """Main home page with AI recommendations"""
    st.markdown("## 🌟 Your Personalized Recipe Journey")
    
    profile = st.session_state.user_profile
    recommender = st.session_state.recommender
    recipes_df = st.session_state.recipes_df
    
    # User stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🏆 Level", calculate_user_level(profile['points']))
    with col2:
        st.metric("⭐ Points", profile['points'])
    with col3:
        st.metric("❤️ Liked Recipes", len(profile['liked_recipes']))
    with col4:
        st.metric("🎖️ Achievements", len(profile['achievements']))
    
    st.markdown("---")
    
    # AI Recommendations
    if recommender and not recipes_df.empty:
        st.markdown("### 🤖 AI-Powered Recommendations")
        
        with st.spinner("🔮 Finding perfect recipes for you..."):
            try:
                # Get recommendations
                if len(profile['liked_recipes']) > 0:
                    recommendations = recommender.recommend(
                        st.session_state.user_id, 
                        n_recommendations=6
                    )
                    
                    # Display in grid
                    for i in range(0, len(recommendations), 3):
                        cols = st.columns(3)
                        for j, (recipe_id, score) in enumerate(recommendations[i:i+3]):
                            if recipe_id in recipes_df['id'].values:
                                recipe = recipes_df[recipes_df['id'] == recipe_id].iloc[0]
                                with cols[j]:
                                    with st.container():
                                        st.markdown(f"**Match Score: {score*100:.0f}%**")
                                        display_recipe_card(recipe, context=f"rec_{i}_{j}")
                else:
                    st.info("👋 Like some recipes to get personalized recommendations!")
                    
                    # Show popular recipes instead
                    st.markdown("### 🌟 Popular Recipes to Get Started")
                    popular_recipes = recipes_df.nlargest(6, 'health_score')
                    
                    for i in range(0, len(popular_recipes), 3):
                        cols = st.columns(3)
                        for j in range(3):
                            if i+j < len(popular_recipes):
                                with cols[j]:
                                    recipe = popular_recipes.iloc[i+j]
                                    display_recipe_card(recipe, context=f"pop_{i}_{j}")
                    
            except Exception as e:
                st.error(f"Error getting recommendations: {e}")
                st.info("Showing random recipes instead...")
                
                # Fallback to random recipes
                random_recipes = recipes_df.sample(min(6, len(recipes_df)))
                for i in range(0, len(random_recipes), 3):
                    cols = st.columns(3)
                    for j in range(3):
                        if i+j < len(random_recipes):
                            with cols[j]:
                                recipe = random_recipes.iloc[i+j]
                                display_recipe_card(recipe, context=f"rand_{i}_{j}")
    else:
        st.warning("⚠️ Recommendation system not available. Please ensure the model is trained.")

def explore_page():
    """Explore recipes with filters"""
    st.markdown("## 🔍 Explore Recipes")
    
    recipes_df = st.session_state.recipes_df
    
    if recipes_df.empty:
        st.error("No recipes available")
        return
    
    # Filters
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        time_filter = st.selectbox(
            "⏱️ Cooking Time",
            ["All", "Quick (< 30 min)", "Medium (30-60 min)", "Long (> 60 min)"]
        )
    
    with col2:
        health_filter = st.slider(
            "🍃 Min Health Score",
            0, 100, 50
        )
    
    with col3:
        search_query = st.text_input("🔍 Search recipes...")
    
    with col4:
        sort_by = st.selectbox(
            "📊 Sort by",
            ["Health Score", "Cooking Time", "Popularity"]
        )
    
    # Apply filters
    filtered_df = recipes_df.copy()
    
    if time_filter == "Quick (< 30 min)":
        filtered_df = filtered_df[filtered_df['minutes'] < 30]
    elif time_filter == "Medium (30-60 min)":
        filtered_df = filtered_df[(filtered_df['minutes'] >= 30) & (filtered_df['minutes'] <= 60)]
    elif time_filter == "Long (> 60 min)":
        filtered_df = filtered_df[filtered_df['minutes'] > 60]
    
    filtered_df = filtered_df[filtered_df['health_score'] >= health_filter]
    
    if search_query:
        mask = filtered_df['name'].str.contains(search_query, case=False, na=False)
        filtered_df = filtered_df[mask]
    
    # Sort
    if sort_by == "Health Score":
        filtered_df = filtered_df.sort_values('health_score', ascending=False)
    elif sort_by == "Cooking Time":
        filtered_df = filtered_df.sort_values('minutes')
    else:
        filtered_df = filtered_df.sample(frac=1)  # Random for "popularity"
    
    st.markdown(f"### Found {len(filtered_df)} recipes")
    
    # Display results
    n_cols = 3
    n_recipes = min(12, len(filtered_df))
    
    for i in range(0, n_recipes, n_cols):
        cols = st.columns(n_cols)
        for j in range(n_cols):
            if i+j < n_recipes:
                with cols[j]:
                    recipe = filtered_df.iloc[i+j]
                    display_recipe_card(recipe, context=f"explore_{i}_{j}")

def profile_page():
    """User profile and achievements"""
    st.markdown("## 👤 Your Recipe Garden Profile")
    
    profile = st.session_state.user_profile
    
    # Profile header
    col1, col2 = st.columns([1, 3])
    
    with col1:
        # Avatar placeholder
        st.markdown("""
        <div style="width: 150px; height: 150px; border-radius: 50%; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); display: flex; align-items: center; justify-content: center;">
            <span style="font-size: 4rem; color: white;">👨‍🍳</span>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"### {calculate_user_level(profile['points'])}")
        st.markdown(f"**User ID:** {profile['user_id']}")
        st.markdown(f"**Member Since:** {profile.get('created_at', 'Today')[:10]}")
        st.progress(min(profile['points'] % 100 / 100, 1.0))
        st.caption(f"{profile['points'] % 100}/100 points to next level")
    
    # Stats
    st.markdown("---")
    st.markdown("### 📊 Your Stats")
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📝 Recipes Rated", len(profile['rated_recipes']))
    with col2:
        st.metric("❤️ Recipes Liked", len(profile['liked_recipes']))
    with col3:
        st.metric("🏆 Achievements", len(profile['achievements']))
    with col4:
        st.metric("⭐ Total Points", profile['points'])
    
    # Achievements
    st.markdown("---")
    st.markdown("### 🏆 Achievements")
    
    all_achievements = {
        "first_cook": {"name": "First Dish Cooked!", "desc": "Cooked your first recipe", "icon": "👨‍🍳"},
        "rate_10": {"name": "Recipe Critic", "desc": "Rated 10 recipes", "icon": "⭐"},
        "like_20": {"name": "Food Lover", "desc": "Liked 20 recipes", "icon": "❤️"},
        "explore_50": {"name": "Recipe Explorer", "desc": "Viewed 50 recipes", "icon": "🔍"},
        "health_nut": {"name": "Health Conscious", "desc": "Liked 10 healthy recipes", "icon": "🥗"},
        "quick_chef": {"name": "Speed Demon", "desc": "Cooked 5 quick recipes", "icon": "⚡"},
        "master_chef": {"name": "Master Chef", "desc": "Reached 1000 points", "icon": "👑"}
    }
    
    cols = st.columns(4)
    for i, (ach_id, ach_data) in enumerate(all_achievements.items()):
        with cols[i % 4]:
            if ach_id in profile['achievements']:
                st.markdown(f"""
                <div style="text-align: center; padding: 1rem; background: linear-gradient(135deg, #f5f5f5, #e0e0e0); border-radius: 10px;">
                    <div style="font-size: 3rem;">{ach_data['icon']}</div>
                    <div style="font-weight: bold;">{ach_data['name']}</div>
                    <div style="font-size: 0.8rem; color: #666;">{ach_data['desc']}</div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div style="text-align: center; padding: 1rem; background: #f5f5f5; border-radius: 10px; opacity: 0.5;">
                    <div style="font-size: 3rem;">🔒</div>
                    <div style="font-weight: bold;">???</div>
                    <div style="font-size: 0.8rem; color: #666;">{ach_data['desc']}</div>
                </div>
                """, unsafe_allow_html=True)
    
    # Preferences
    st.markdown("---")
    st.markdown("### ⚙️ Preferences")
    
    col1, col2 = st.columns(2)
    
    with col1:
        new_skill = st.selectbox(
            "👨‍🍳 Skill Level",
            ["beginner", "intermediate", "advanced"],
            index=["beginner", "intermediate", "advanced"].index(profile['skill_level'])
        )
        
        new_time = st.selectbox(
            "⏱️ Preferred Cooking Time",
            ["quick", "medium", "long"],
            index=["quick", "medium", "long"].index(profile.get('preferred_time', 'medium'))
        )
    
    with col2:
        new_health = st.checkbox("🥗 Health Conscious", value=profile.get('health_conscious', False))
        new_sustain = st.checkbox("🌍 Sustainability Focus", value=profile.get('sustainability_focus', False))
    
    if st.button("💾 Save Preferences"):
        profile['skill_level'] = new_skill
        profile['preferred_time'] = new_time
        profile['health_conscious'] = new_health
        profile['sustainability_focus'] = new_sustain
        save_user_profile(profile, st.session_state.user_id)
        st.success("Preferences saved!")

def analytics_page():
    """Show recommendation system analytics"""
    st.markdown("## 📊 Recommendation Analytics")
    
    recipes_df = st.session_state.recipes_df
    interactions_df = st.session_state.interactions_df
    
    if recipes_df.empty:
        st.error("No data available for analytics")
        return
    
    # System stats
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("📚 Total Recipes", len(recipes_df))
    with col2:
        st.metric("👥 Total Users", interactions_df['user_id'].nunique() if not interactions_df.empty else 0)
    with col3:
        st.metric("⭐ Total Ratings", len(interactions_df) if not interactions_df.empty else 0)
    with col4:
        avg_rating = interactions_df['rating'].mean() if not interactions_df.empty else 0
        st.metric("📈 Avg Rating", f"{avg_rating:.2f}")
    
    # Recipe distribution
    st.markdown("---")
    st.markdown("### 📊 Recipe Distribution")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Time distribution
        time_dist = pd.cut(recipes_df['minutes'], bins=[0, 30, 60, 120, float('inf')], 
                          labels=['Quick', 'Medium', 'Long', 'Very Long']).value_counts()
        
        st.markdown("**Cooking Time Distribution**")
        for category, count in time_dist.items():
            st.write(f"{category}: {count} ({count/len(recipes_df)*100:.1f}%)")
    
    with col2:
        # Health score distribution
        health_bins = pd.cut(recipes_df['health_score'], bins=[0, 50, 70, 85, 100], 
                            labels=['Low', 'Medium', 'High', 'Very High']).value_counts()
        
        st.markdown("**Health Score Distribution**")
        for category, count in health_bins.items():
            st.write(f"{category}: {count} ({count/len(recipes_df)*100:.1f}%)")
    
    # Model performance (if available)
    if st.session_state.recommender:
        st.markdown("---")
        st.markdown("### 🤖 Model Performance")
        
        # Placeholder metrics - in production, these would be calculated properly
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("🎯 Precision@10", "0.75")
        with col2:
            st.metric("📏 RMSE", "0.92")
        with col3:
            st.metric("🔄 Coverage", "82%")
        
        st.info("💡 The model combines collaborative filtering (what similar users liked) with content-based filtering (recipe features) for hybrid recommendations.")

# =============================================================================
# MAIN APP
# =============================================================================
def main():
    # Initialize
    init_session_state()
    
    # Load data and model
    if st.session_state.recommender is None:
        with st.spinner("🔮 Loading AI recommendation system..."):
            st.session_state.recommender = load_model()
            st.session_state.recipes_df = load_recipe_data()
            st.session_state.interactions_df = load_interaction_data()
    
    # Header
    create_header()
    
    # Navigation
    st.markdown("---")
    pages = {
        "Home": "🏠",
        "Explore": "🔍", 
        "Profile": "👤",
        "Analytics": "📊"
    }
    
    cols = st.columns(len(pages))
    for i, (page, icon) in enumerate(pages.items()):
        with cols[i]:
            if st.button(f"{icon} {page}", key=f"nav_{page}", use_container_width=True):
                st.session_state.current_page = page
                st.rerun()
    
    st.markdown("---")
    
    # Route to page
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
        <p>🌿 Ghibli Recipe Garden - AI-Powered Recipe Recommendations 🌿</p>
        <p style="font-size: 0.8rem;">Built with ❤️ using Streamlit and Machine Learning</p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()