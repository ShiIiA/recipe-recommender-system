"""
Day 2 - Final Recipe App with Real Sustainability Data
Fixed to work within Streamlit's column limitations
"""
import streamlit as st
import pandas as pd
import numpy as np
import pickle
from pathlib import Path
from datetime import datetime
import json
import random
import plotly.express as px
import plotly.graph_objects as go

# Import our real sustainability module
from sustainability_real_data import (
    calculate_real_sustainability_score,
    get_sustainability_facts,
    CARBON_FOOTPRINT_REAL,
    SEASONAL_CALENDAR
)

# Page configuration
st.set_page_config(
    page_title="🌿 Sustainable Recipe Garden",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Constants
DATA_DIR = "user_data"
RECIPES_PATH = "processed_data/recipes_full.pkl"
Path(DATA_DIR).mkdir(exist_ok=True)

# =============================================================================
# MODERN UI STYLING
# =============================================================================
def inject_custom_css():
    st.markdown("""
    <style>
    /* Modern Typography */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
    }
    
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* Main container */
    .block-container {
        padding-top: 1rem;
        padding-bottom: 0rem;
        padding-left: 5rem;
        padding-right: 5rem;
        max-width: 1200px;
    }
    
    /* Custom header */
    .hero-header {
        background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
        color: white;
        padding: 2rem;
        border-radius: 20px;
        text-align: center;
        margin-bottom: 2rem;
    }
    
    .hero-title {
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0;
    }
    
    .hero-subtitle {
        font-size: 1.1rem;
        opacity: 0.9;
        margin-top: 0.5rem;
    }
    
    /* Card designs */
    .recipe-card {
        background: white;
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.08);
        border: 1px solid #e0e0e0;
        transition: all 0.2s ease;
    }
    
    .recipe-card:hover {
        box-shadow: 0 4px 16px rgba(0,0,0,0.12);
        transform: translateY(-2px);
    }
    
    .recipe-title {
        font-size: 1.3rem;
        font-weight: 600;
        color: #1e3c72;
        margin-bottom: 0.5rem;
    }
    
    /* Sustainability badges */
    .sus-badge {
        display: inline-block;
        padding: 0.4rem 0.8rem;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 600;
        margin: 0.25rem 0;
    }
    
    .eco-excellent {
        background: #10b981;
        color: white;
    }
    
    .eco-good {
        background: #3b82f6;
        color: white;
    }
    
    .eco-moderate {
        background: #f59e0b;
        color: white;
    }
    
    .eco-poor {
        background: #ef4444;
        color: white;
    }
    
    /* Metrics */
    .metric-card {
        background: #f8fafc;
        border-radius: 12px;
        padding: 1.5rem;
        text-align: center;
        border: 1px solid #e2e8f0;
    }
    
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #1e3c72;
        margin: 0;
    }
    
    .metric-label {
        font-size: 0.9rem;
        color: #64748b;
        margin-top: 0.25rem;
    }
    
    /* Info boxes */
    .info-box {
        background: #eff6ff;
        border: 1px solid #3b82f6;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    .success-box {
        background: #d1fae5;
        border: 1px solid #10b981;
        border-radius: 8px;
        padding: 1rem;
        margin: 0.5rem 0;
    }
    
    /* Buttons */
    .stButton > button {
        background: #3b82f6;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.2s;
    }
    
    .stButton > button:hover {
        background: #2563eb;
        transform: translateY(-1px);
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 2rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        padding-left: 20px;
        padding-right: 20px;
    }
    </style>
    """, unsafe_allow_html=True)

# =============================================================================
# DATA LOADING
# =============================================================================
@st.cache_data(show_spinner=False)
def load_recipes_with_sustainability():
    """Load recipes and calculate real sustainability scores"""
    try:
        if not Path(RECIPES_PATH).exists():
            st.error("Recipe data not found. Please run train_model.py first!")
            return pd.DataFrame()
        
        # Load recipes
        df = pd.read_pickle(RECIPES_PATH)
        
        # Calculate sustainability scores for a subset (for performance)
        max_recipes = min(1000, len(df))  # Limit for demo
        df = df.head(max_recipes)
        
        # Add sustainability scores
        sustainability_data = []
        for _, recipe in df.iterrows():
            try:
                sus_data = calculate_real_sustainability_score(recipe)
                sustainability_data.append(sus_data)
            except:
                # Fallback for any errors
                sustainability_data.append({
                    'score': 50,
                    'carbon_score': 50,
                    'water_score': 50,
                    'seasonality_score': 50,
                    'total_carbon_kg': 2.5,
                    'is_plant_based': False,
                    'is_vegetarian': False,
                    'category': 'Moderate Impact ⚡',
                    'badge_class': 'eco-moderate',
                    'impact': 'Moderate Environmental Impact'
                })
        
        # Add columns to dataframe
        for key in sustainability_data[0].keys():
            if key != 'carbon_breakdown':  # Skip complex objects
                df[f'sus_{key}'] = [s[key] for s in sustainability_data]
        
        return df
        
    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        return pd.DataFrame()

# =============================================================================
# USER PROFILE
# =============================================================================
def get_user_profile():
    """Get or create user profile"""
    if 'user_profile' not in st.session_state:
        st.session_state.user_profile = {
            'user_id': random.randint(1000, 999999),
            'liked_recipes': [],
            'cooked_recipes': [],
            'points': 0,
            'carbon_saved': 0.0,
            'badges': []
        }
    return st.session_state.user_profile

# =============================================================================
# UI COMPONENTS
# =============================================================================
def display_header():
    """Display custom header"""
    st.markdown("""
    <div class="hero-header">
        <h1 class="hero-title">🌿 Sustainable Recipe Garden</h1>
        <p class="hero-subtitle">Cook delicious meals with real environmental impact data</p>
    </div>
    """, unsafe_allow_html=True)

def display_recipe_card(recipe, idx):
    """Display a single recipe card"""
    with st.container():
        # Create card container
        st.markdown(f'<div class="recipe-card">', unsafe_allow_html=True)
        
        # Title
        st.markdown(f'<h3 class="recipe-title">{recipe["name"].title()}</h3>', unsafe_allow_html=True)
        
        # Sustainability badge
        badge_html = f'<span class="sus-badge {recipe["sus_badge_class"]}">{recipe["sus_category"]}</span>'
        st.markdown(badge_html, unsafe_allow_html=True)
        
        # Metrics in a row
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("🌍 Carbon", f"{recipe['sus_total_carbon_kg']:.1f} kg")
        
        with col2:
            st.metric("⏱️ Time", f"{int(recipe['minutes'])} min")
        
        with col3:
            st.metric("🥗 Ingredients", recipe['n_ingredients'])
        
        with col4:
            st.metric("💚 Score", f"{recipe['sus_score']:.0f}/100")
        
        # Diet info
        if recipe['sus_is_plant_based']:
            st.success("🌱 100% Plant-Based")
        elif recipe['sus_is_vegetarian']:
            st.info("🥗 Vegetarian")
        
        # Actions
        profile = get_user_profile()
        recipe_id = recipe['id']
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.button("👍 Like", key=f"like_{idx}_{recipe_id}"):
                if recipe_id not in profile['liked_recipes']:
                    profile['liked_recipes'].append(recipe_id)
                    profile['points'] += 10
                    st.success("Liked! +10 points")
                    st.rerun()
        
        with col2:
            if st.button("🍳 Cook", key=f"cook_{idx}_{recipe_id}"):
                if recipe_id not in profile['cooked_recipes']:
                    profile['cooked_recipes'].append(recipe_id)
                    profile['points'] += 25
                    # Calculate carbon saved vs average meal
                    carbon_saved = max(0, 3.0 - recipe['sus_total_carbon_kg'])
                    profile['carbon_saved'] += carbon_saved
                    st.success(f"Cooked! +25 points, saved {carbon_saved:.1f} kg CO₂")
                    st.rerun()
        
        with col3:
            if st.button("📖 View", key=f"view_{idx}_{recipe_id}"):
                st.session_state.selected_recipe = recipe_id
                st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

# =============================================================================
# MAIN PAGES
# =============================================================================
def home_page(recipes_df):
    """Main home page"""
    profile = get_user_profile()
    
    # User metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <p class="metric-value">{profile['points']}</p>
            <p class="metric-label">Total Points</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <p class="metric-value">{profile['carbon_saved']:.1f}</p>
            <p class="metric-label">kg CO₂ Saved</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <p class="metric-value">{len(profile['cooked_recipes'])}</p>
            <p class="metric-label">Recipes Cooked</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <p class="metric-value">{len(profile['liked_recipes'])}</p>
            <p class="metric-label">Recipes Liked</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Featured recipes tabs
    tab1, tab2, tab3 = st.tabs(["🌟 Climate Heroes", "🌱 Plant-Based", "📊 Impact Analysis"])
    
    with tab1:
        st.markdown("### Lowest Carbon Footprint Recipes")
        
        # Get top sustainable recipes
        top_sustainable = recipes_df.nlargest(6, 'sus_score')
        
        # Display in 2 columns
        for i in range(0, len(top_sustainable), 2):
            col1, col2 = st.columns(2)
            
            with col1:
                if i < len(top_sustainable):
                    display_recipe_card(top_sustainable.iloc[i], i)
            
            with col2:
                if i + 1 < len(top_sustainable):
                    display_recipe_card(top_sustainable.iloc[i + 1], i + 1)
    
    with tab2:
        st.markdown("### 100% Plant-Based Options")
        
        # Get plant-based recipes
        plant_based = recipes_df[recipes_df['sus_is_plant_based'] == True].head(6)
        
        if len(plant_based) > 0:
            # Display in 2 columns
            for i in range(0, len(plant_based), 2):
                col1, col2 = st.columns(2)
                
                with col1:
                    if i < len(plant_based):
                        display_recipe_card(plant_based.iloc[i], f"pb_{i}")
                
                with col2:
                    if i + 1 < len(plant_based):
                        display_recipe_card(plant_based.iloc[i + 1], f"pb_{i + 1}")
        else:
            st.info("No plant-based recipes found in this dataset")
    
    with tab3:
        st.markdown("### Environmental Impact Overview")
        
        # Carbon distribution
        fig1 = px.histogram(
            recipes_df,
            x='sus_total_carbon_kg',
            nbins=30,
            title='Carbon Footprint Distribution (kg CO₂ per recipe)',
            color_discrete_sequence=['#3b82f6']
        )
        fig1.update_layout(
            xaxis_title="Carbon Footprint (kg CO₂)",
            yaxis_title="Number of Recipes",
            showlegend=False
        )
        st.plotly_chart(fig1, use_container_width=True)
        
        # Impact categories
        col1, col2 = st.columns(2)
        
        with col1:
            # Category pie chart
            category_counts = recipes_df['sus_category'].value_counts()
            fig2 = px.pie(
                values=category_counts.values,
                names=category_counts.index,
                title='Recipe Impact Categories',
                color_discrete_map={
                    'Climate Hero 🌟': '#10b981',
                    'Eco Friendly 🌿': '#3b82f6',
                    'Moderate Impact ⚡': '#f59e0b',
                    'High Impact ⚠️': '#ef4444'
                }
            )
            st.plotly_chart(fig2, use_container_width=True)
        
        with col2:
            # Diet type distribution
            diet_data = pd.DataFrame({
                'Type': ['Plant-Based', 'Vegetarian', 'Contains Meat'],
                'Count': [
                    recipes_df['sus_is_plant_based'].sum(),
                    recipes_df[recipes_df['sus_is_vegetarian'] & ~recipes_df['sus_is_plant_based']].shape[0],
                    recipes_df[~recipes_df['sus_is_vegetarian']].shape[0]
                ]
            })
            
            fig3 = px.bar(
                diet_data,
                x='Type',
                y='Count',
                title='Recipe Diet Types',
                color='Type',
                color_discrete_map={
                    'Plant-Based': '#10b981',
                    'Vegetarian': '#3b82f6',
                    'Contains Meat': '#ef4444'
                }
            )
            st.plotly_chart(fig3, use_container_width=True)

def explore_page(recipes_df):
    """Recipe exploration page"""
    st.markdown("## 🔍 Find Sustainable Recipes")
    
    # Filters
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        search_term = st.text_input("🔍 Search", placeholder="Recipe or ingredient...")
    
    with col2:
        max_carbon = st.slider("🌍 Max Carbon (kg)", 0.0, 10.0, 5.0, 0.5)
    
    with col3:
        diet_type = st.selectbox("🥗 Diet Type", ["All", "Plant-Based", "Vegetarian"])
    
    with col4:
        sort_by = st.selectbox("📊 Sort By", ["Sustainability Score", "Carbon (Low to High)", "Time (Quick First)"])
    
    # Apply filters
    filtered_df = recipes_df.copy()
    
    # Search filter
    if search_term:
        search_lower = search_term.lower()
        mask = filtered_df['name'].str.lower().str.contains(search_lower, na=False)
        filtered_df = filtered_df[mask]
    
    # Carbon filter
    filtered_df = filtered_df[filtered_df['sus_total_carbon_kg'] <= max_carbon]
    
    # Diet filter
    if diet_type == "Plant-Based":
        filtered_df = filtered_df[filtered_df['sus_is_plant_based'] == True]
    elif diet_type == "Vegetarian":
        filtered_df = filtered_df[filtered_df['sus_is_vegetarian'] == True]
    
    # Sorting
    if sort_by == "Sustainability Score":
        filtered_df = filtered_df.sort_values('sus_score', ascending=False)
    elif sort_by == "Carbon (Low to High)":
        filtered_df = filtered_df.sort_values('sus_total_carbon_kg', ascending=True)
    else:
        filtered_df = filtered_df.sort_values('minutes', ascending=True)
    
    # Results summary
    st.markdown(f"### Found {len(filtered_df)} recipes")
    
    if len(filtered_df) > 0:
        # Quick stats
        col1, col2, col3 = st.columns(3)
        
        with col1:
            avg_carbon = filtered_df['sus_total_carbon_kg'].mean()
            st.metric("Avg Carbon", f"{avg_carbon:.1f} kg CO₂")
        
        with col2:
            plant_based_pct = (filtered_df['sus_is_plant_based'].sum() / len(filtered_df)) * 100
            st.metric("Plant-Based", f"{plant_based_pct:.0f}%")
        
        with col3:
            avg_time = filtered_df['minutes'].mean()
            st.metric("Avg Time", f"{int(avg_time)} min")
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        # Display results
        for idx, (_, recipe) in enumerate(filtered_df.head(20).iterrows()):
            display_recipe_card(recipe, f"explore_{idx}")
    else:
        st.info("No recipes found matching your criteria. Try adjusting the filters!")

def recipe_detail_page(recipes_df):
    """Detailed recipe view"""
    if 'selected_recipe' not in st.session_state:
        st.warning("No recipe selected!")
        return
    
    recipe_id = st.session_state.selected_recipe
    recipe = recipes_df[recipes_df['id'] == recipe_id]
    
    if recipe.empty:
        st.error("Recipe not found!")
        return
    
    recipe = recipe.iloc[0]
    
    # Back button
    if st.button("← Back to Recipes"):
        del st.session_state.selected_recipe
        st.rerun()
    
    # Recipe header
    st.markdown(f"# {recipe['name'].title()}")
    
    # Sustainability summary
    st.markdown(f"""
    <div class="info-box">
        <strong>{recipe['sus_category']}</strong> - 
        Sustainability Score: {recipe['sus_score']:.0f}/100 | 
        Carbon Footprint: {recipe['sus_total_carbon_kg']:.1f} kg CO₂
    </div>
    """, unsafe_allow_html=True)
    
    # Main content
    col1, col2 = st.columns([2, 1])
    
    with col1:
        # Description
        if 'description' in recipe and pd.notna(recipe['description']):
            st.markdown("### Description")
            st.write(recipe['description'])
        
        # Ingredients
        st.markdown("### Ingredients")
        ingredients = recipe.get('ingredients', [])
        if ingredients:
            # Display in 2 columns for better readability
            ing_col1, ing_col2 = st.columns(2)
            
            mid_point = len(ingredients) // 2
            
            with ing_col1:
                for ing in ingredients[:mid_point]:
                    st.write(f"• {ing}")
            
            with ing_col2:
                for ing in ingredients[mid_point:]:
                    st.write(f"• {ing}")
        
        # Steps
        if 'steps' in recipe and recipe['steps']:
            st.markdown("### Instructions")
            steps = recipe['steps']
            for i, step in enumerate(steps, 1):
                st.write(f"**Step {i}:** {step}")
    
    with col2:
        # Quick facts
        st.markdown("### Quick Facts")
        
        st.metric("⏱️ Cooking Time", f"{int(recipe['minutes'])} minutes")
        st.metric("🥗 Ingredients", f"{recipe['n_ingredients']} items")
        st.metric("📝 Steps", f"{recipe.get('n_steps', len(recipe.get('steps', [])))} steps")
        st.metric("🌱 Health Score", f"{recipe.get('health_score', 50):.0f}/100")
        
        # Environmental impact
        st.markdown("### Environmental Impact")
        
        sus_data = {
            'score': recipe['sus_score'],
            'total_carbon_kg': recipe['sus_total_carbon_kg'],
            'is_plant_based': recipe['sus_is_plant_based'],
            'seasonality_score': recipe['sus_seasonality_score']
        }
        
        facts = get_sustainability_facts(sus_data)
        for fact in facts[:3]:  # Show top 3 facts
            st.write(f"• {fact}")
        
        # Diet info
        if recipe['sus_is_plant_based']:
            st.markdown('<div class="success-box">✅ 100% Plant-Based</div>', unsafe_allow_html=True)
        elif recipe['sus_is_vegetarian']:
            st.markdown('<div class="info-box">✅ Vegetarian</div>', unsafe_allow_html=True)

# =============================================================================
# MAIN APP
# =============================================================================
def main():
    # Inject custom CSS
    inject_custom_css()
    
    # Initialize session state
    if 'page' not in st.session_state:
        st.session_state.page = 'home'
    
    # Load data
    with st.spinner("🌱 Loading sustainable recipes..."):
        recipes_df = load_recipes_with_sustainability()
    
    if recipes_df.empty:
        st.error("Failed to load recipe data!")
        return
    
    # Display header
    display_header()
    
    # Navigation
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("🏠 Home", use_container_width=True):
            st.session_state.page = 'home'
            if 'selected_recipe' in st.session_state:
                del st.session_state.selected_recipe
            st.rerun()
    
    with col2:
        if st.button("🔍 Explore", use_container_width=True):
            st.session_state.page = 'explore'
            if 'selected_recipe' in st.session_state:
                del st.session_state.selected_recipe
            st.rerun()
    
    with col3:
        if st.button("📊 My Impact", use_container_width=True):
            st.session_state.page = 'impact'
            if 'selected_recipe' in st.session_state:
                del st.session_state.selected_recipe
            st.rerun()
    
    with col4:
        if st.button("ℹ️ About", use_container_width=True):
            st.session_state.page = 'about'
            if 'selected_recipe' in st.session_state:
                del st.session_state.selected_recipe
            st.rerun()
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Page routing
    if 'selected_recipe' in st.session_state:
        recipe_detail_page(recipes_df)
    elif st.session_state.page == 'home':
        home_page(recipes_df)
    elif st.session_state.page == 'explore':
        explore_page(recipes_df)
    elif st.session_state.page == 'impact':
        # Impact page
        st.markdown("## 🌍 Your Environmental Impact")
        
        profile = get_user_profile()
        
        if profile['cooked_recipes']:
            cooked_df = recipes_df[recipes_df['id'].isin(profile['cooked_recipes'])]
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### Your Impact Summary")
                
                total_carbon = cooked_df['sus_total_carbon_kg'].sum()
                avg_carbon = cooked_df['sus_total_carbon_kg'].mean()
                
                st.metric("Total Carbon from Cooked Recipes", f"{total_carbon:.1f} kg CO₂")
                st.metric("Average Carbon per Recipe", f"{avg_carbon:.1f} kg CO₂")
                st.metric("Carbon Saved vs Average Diet", f"{profile['carbon_saved']:.1f} kg CO₂")
                
                # Equivalent calculations
                car_km = profile['carbon_saved'] * 4
                trees_needed = profile['carbon_saved'] / 20  # Trees absorb ~20kg/year
                
                st.info(f"""
                **Your positive impact equals:**
                - 🚗 Not driving {car_km:.0f} km
                - 🌳 Planting {trees_needed:.1f} trees for a year
                """)
            
            with col2:
                st.markdown("### Your Recipe Breakdown")
                
                # Diet type pie chart
                diet_breakdown = {
                    'Plant-Based': cooked_df['sus_is_plant_based'].sum(),
                    'Vegetarian (not plant-based)': (cooked_df['sus_is_vegetarian'] & ~cooked_df['sus_is_plant_based']).sum(),
                    'Contains Meat': (~cooked_df['sus_is_vegetarian']).sum()
                }
                
                fig = px.pie(
                    values=diet_breakdown.values(),
                    names=diet_breakdown.keys(),
                    title="Your Diet Composition",
                    color_discrete_map={
                        'Plant-Based': '#10b981',
                        'Vegetarian (not plant-based)': '#3b82f6',
                        'Contains Meat': '#ef4444'
                    }
                )
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Cook some recipes to see your environmental impact!")
    
    else:  # About page
        st.markdown("## ℹ️ About Sustainable Recipe Garden")
        
        st.markdown("""
        ### Real Environmental Data
        
        This app uses **real scientific data** to calculate the environmental impact of recipes:
        
        - **Carbon Footprint Data**: Based on Poore & Nemecek (2018) comprehensive study published in Science
        - **Water Usage**: FAO and Water Footprint Network data
        - **Seasonality**: Based on actual harvest calendars for temperate climates
        
        ### How We Calculate Sustainability Scores
        
        Each recipe gets a score from 0-100 based on:
        - **50%** - Carbon footprint (kg CO₂ equivalent)
        - **20%** - Water usage (liters)
        - **20%** - Seasonal ingredient usage
        - **10%** - Bonus for plant-based recipes
        
        ### Impact Categories
        
        - **🌟 Climate Hero**: Score 80-100 (Very low environmental impact)
        - **🌿 Eco Friendly**: Score 60-79 (Low environmental impact)
        - **⚡ Moderate Impact**: Score 40-59 (Average environmental impact)
        - **⚠️ High Impact**: Score 0-39 (High environmental impact)
        
        ### Why It Matters
        
        - Food systems contribute **26% of global greenhouse gas emissions**
        - Shifting to sustainable diets could reduce emissions by up to **70%**
        - Every meal choice makes a difference!
        
        ### Data Sources
        
        - Poore, J., & Nemecek, T. (2018). Reducing food's environmental impacts. *Science*, 360(6392), 987-992.
        - FAO Food and Agriculture Organization statistics
        - EPA Environmental Protection Agency data
        """)
        
        st.markdown("---")
        
        # Export data option
        st.markdown("### 💾 Export Your Data")
        
        profile = get_user_profile()
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Export profile
            profile_json = json.dumps(profile, indent=2)
            st.download_button(
                label="📥 Download My Profile (JSON)",
                data=profile_json,
                file_name=f"sustainable_cooking_profile_{profile['user_id']}.json",
                mime="application/json"
            )
        
        with col2:
            # Export liked recipes
            if profile['liked_recipes']:
                liked_df = recipes_df[recipes_df['id'].isin(profile['liked_recipes'])]
                csv_data = liked_df[['name', 'sus_score', 'sus_total_carbon_kg', 'minutes', 'n_ingredients']].to_csv(index=False)
                
                st.download_button(
                    label="📥 Download Liked Recipes (CSV)",
                    data=csv_data,
                    file_name="my_sustainable_recipes.csv",
                    mime="text/csv"
                )

if __name__ == "__main__":
    main()