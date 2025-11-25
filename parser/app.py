import streamlit as st
import matplotlib.pyplot as plt
from core import DataFrame
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
import pandas as pd # Used only for internal display compatibility

# ==========================================
# 1. Page Configuration & Data Loading
# ==========================================
st.set_page_config(page_title="Mini-Pandas Music Analytics", layout="wide")

st.title("🎵 Mini-Pandas Music Analytics & AI Predictor")
st.markdown("""
This application is built upon a custom **Python-only Data Analysis Engine** (Mini-Pandas). 
It demonstrates data processing, visualization, and machine learning without relying on standard libraries like pandas for the core logic.
""")

# Cache data loading to improve performance
@st.cache_data
def load_data():
    try:
        df = DataFrame.from_csv('../data/spotify_songs.csv')
        return df
    except Exception as e:
        return None

df = load_data()

if df is None:
    st.error("Error loading 'spotify_songs.csv'. Please ensure the file exists in the directory.")
    st.stop()
else:
    st.sidebar.success(f"Data Loaded Successfully: {df.row_count} rows")
    st.sidebar.success("Version: 1.1.2")
    st.sidebar.success("Website Creator: Eric, Angus, Brain")

# Create 4 Tabs (Added Audio Feature Explorer)
tab1, tab2, tab3, tab4 = st.tabs([
    "🔍 Data Explorer", 
    "📊 Visualizations", 
    "🤖 AI Popularity Predictor",
    "🎧 Audio Feature Explorer"
])

# ==========================================
# Tab 1: Data Explorer
# ==========================================
with tab1:
    st.header("Data Explorer & Filtering")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        min_pop = st.slider("Minimum Popularity", 0, 100, 50)
    with col2:
        genre_options = ["edm", "latin", "pop", "r&b", "rap", "rock"]
        selected_genre = st.selectbox("Filter by Genre", genre_options)
    with col3:
        top_n_singers = st.slider("Show Top N Singers", 1, 50, 10)

    st.markdown("---")

    # Feature A: Filter Data
    st.subheader(f"Filtered Songs ({selected_genre.upper()} & Pop >= {min_pop})")
    
    filtered_df = df.filter(lambda row: 
        (row['track_popularity'] is not None and row['track_popularity'] >= min_pop) and 
        (row['playlist_genre'] == selected_genre)
    )
    
    st.caption(f"Found {filtered_df.row_count} songs matching your criteria.")
    
    if filtered_df.row_count > 0:
        display_limit = 100
        display_data = []
        cols = ['track_name', 'track_artist', 'track_popularity', 'playlist_subgenre']
        
        for i in range(min(filtered_df.row_count, display_limit)):
            row_data = {col: filtered_df[col][i] for col in cols}
            display_data.append(row_data)
            
        st.dataframe(display_data)
    else:
        st.warning("No songs found. Try adjusting the filters.")

    st.markdown("---")

    # Feature B: Top Popular Singers
    st.markdown("---")
    st.subheader("🏆 Most Popular Singers Ranking")

    # 1.  Slider for N
    top_n = st.slider("Select Number of Singers (Top N):", min_value=1, max_value=50, value=10, key="top_n_slider")

    # 2.  Data Processing
    grouped_artist = df.groupby('track_artist')
    artist_stats = grouped_artist.aggregate({
        'track_popularity': 'mean',
        'track_id': 'count'
    })
    
    artists = artist_stats['track_artist']
    avg_pop = artist_stats['track_popularity_mean']
    counts = artist_stats['track_id_count']
    
    combined = list(zip(artists, avg_pop, counts))
    # Sort by Popularity (index 1) in descending order. 
    combined.sort(key=lambda x: x[1] if x[1] is not None else 0, reverse=True)
    
    # 3. Prepare display data
    # Format data into a list of dictionaries for Streamlit
    display_data = []
    
    # Safety check to ensure N does not exceed total count
    safe_n = min(top_n, len(combined))
    
    for i in range(safe_n):
        display_data.append({
            "Rank": i + 1,
            "Artist": combined[i][0],
            "Avg Popularity": f"{combined[i][1]:.1f}", # Format to 1 decimal place
            "Song Count": combined[i][2]
        })

    # 4. Display table
    # Use st.table (static table) or st.dataframe (interactive table)
    st.table(display_data)


# ==========================================
# Tab 2: Visualizations
# ==========================================
with tab2:
    st.header("Visual Analytics")
    
    # Feature C: Group Analysis
    st.subheader("1. Group Analysis (Popularity & Count)")
    group_var = st.selectbox("Group Data By:", ['playlist_genre', 'playlist_subgenre', 'key', 'mode'])
    
    if group_var:
        grouped = df.groupby(group_var)
        stats = grouped.aggregate({
            'track_popularity': 'mean',
            'track_id': 'count'
        })
        
        labels = stats[group_var]
        pops = stats['track_popularity_mean']
        counts = stats['track_id_count']
        
        chart_data = list(zip(labels, pops, counts))
        chart_data.sort(key=lambda x: x[2] if x[2] is not None else 0, reverse=True)
        chart_data = chart_data[:15] 
        
        plot_labels = [str(x[0]) for x in chart_data]
        plot_pops = [x[1] for x in chart_data]
        plot_counts = [x[2] for x in chart_data]
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 5))
        
        ax1.bar(plot_labels, plot_pops, color='skyblue', edgecolor='black')
        ax1.set_title(f'Avg Popularity by {group_var}')
        ax1.tick_params(axis='x', rotation=45)
        ax1.set_ylim(0, 100)
        
        ax2.bar(plot_labels, plot_counts, color='salmon', edgecolor='black')
        ax2.set_title(f'Song Count by {group_var}')
        ax2.tick_params(axis='x', rotation=45)
        
        st.pyplot(fig)

    st.markdown("---")

    # Feature D: Trend Analysis
    st.subheader("2. Audio Feature Explorer")
    st.markdown("Explore relationships between audio features, genre, and popularity dynamically.")

    # 1. Define Options
    audio_features = [
        "danceability", "energy", "acousticness", 
        "valence", "speechiness", "tempo", "loudness"
    ]
    # Filter features that actually exist in the dataframe columns
    available_features = [f for f in audio_features if f in df.columns]

    # Get Genres (Manually extracting unique values because we don't have .unique())
    # Note: Accessing df.data directly as per your request structure
    if "playlist_genre" in df.columns:
        # Extract all genres and convert to set to get unique values
        raw_genres = df.data["playlist_genre"]
        unique_genres = sorted(list(set([g for g in raw_genres if g is not None])))
        genre_options = ["All"] + unique_genres
    else:
        genre_options = ["All"]

    # 2. UI Controls
    c1, c2, c3 = st.columns(3)
    
    with c1:
        feature_x = st.selectbox("X Axis Feature:", available_features, index=0)
    with c2:
        # Add "None" option for Y axis
        feature_y = st.selectbox("Y Axis Feature (Optional):", ["(None)"] + available_features, index=0)
    with c3:
        selected_genre_af = st.selectbox("Select Genre:", genre_options)

    # Popularity Range Slider (Streamlit allows tuples for ranges)
    pop_range = st.slider("Popularity Range", 0, 100, (0, 100))
    min_pop_af, max_pop_af = pop_range

    # 3. Data Processing (Manual Filtering)
    # Replicating the logic from your provided code but adapted for Streamlit
    
    x_vals = []
    y_vals = [] # Only used if feature_y is not "(None)"
    pops = []
    
    # Iterate through all rows in the dataframe
    for i in range(df.row_count):
        # 1. Filter by Genre
        if selected_genre_af != "All":
            current_genre = df.data["playlist_genre"][i]
            if current_genre != selected_genre_af:
                continue

        # 2. Filter by Popularity Range
        # Using .get() logic or direct access if column exists
        current_pop = df.data["track_popularity"][i]
        
        if current_pop is None:
            continue
        if not (min_pop_af <= current_pop <= max_pop_af):
            continue

        # 3. Get X Value
        val_x = df.data[feature_x][i]
        if val_x is None:
            continue

        # 4. Get Y Value (if applicable)
        if feature_y != "(None)":
            val_y = df.data[feature_y][i]
            if val_y is None:
                continue
            y_vals.append(val_y)
        
        # Append valid data
        x_vals.append(val_x)
        pops.append(current_pop)

    # 4. Display Logic
    st.markdown("---")
    
    if len(x_vals) == 0:
        st.warning("No songs match the current filters. Try widening the popularity range or changing the genre.")
    else:
        # Statistics
        col_stat1, col_stat2 = st.columns(2)
        with col_stat1:
            st.metric("Filtered Songs", len(x_vals))
            avg_x = sum(x_vals) / len(x_vals)
            st.write(f"**{feature_x}**: Mean={avg_x:.3f}, Min={min(x_vals):.3f}, Max={max(x_vals):.3f}")
        
        with col_stat2:
            if feature_y != "(None)" and len(y_vals) > 0:
                avg_y = sum(y_vals) / len(y_vals)
                st.write(f"**{feature_y}**: Mean={avg_y:.3f}, Min={min(y_vals):.3f}, Max={max(y_vals):.3f}")

        # Plotting
        fig_af, axes = plt.subplots(1, 2, figsize=(12, 5))
        
        # Left Plot: Histogram of X
        axes[0].hist(x_vals, bins=30, color='skyblue', edgecolor="black")
        axes[0].set_title(f"Distribution of {feature_x}")
        axes[0].set_xlabel(feature_x)
        axes[0].set_ylabel("Count")

        # Right Plot: Scatter
        if feature_y == "(None)":
            # Scatter: X vs Popularity
            axes[1].scatter(x_vals, pops, alpha=0.3, color='purple')
            axes[1].set_title(f"{feature_x} vs Popularity")
            axes[1].set_xlabel(feature_x)
            axes[1].set_ylabel("Popularity")
        else:
            # Scatter: X vs Y
            axes[1].scatter(x_vals, y_vals, alpha=0.3, color='green')
            axes[1].set_title(f"{feature_x} vs {feature_y}")
            axes[1].set_xlabel(feature_x)
            axes[1].set_ylabel(feature_y)

        plt.tight_layout()
        st.pyplot(fig_af)
    


# ==========================================
# Tab 3: AI Popularity Predictor
# ==========================================
with tab3:
    st.header("🤖 AI Song Popularity Predictor")
    st.markdown("This module uses **Linear Regression** to predict a song's popularity.")
    
    features_list = ['danceability', 'energy', 'loudness', 'acousticness', 'valence', 'tempo']
    X, y = [], []
    
    raw_X = list(zip(*[df[col] for col in features_list]))
    raw_y = df['track_popularity']
    
    for i in range(len(raw_y)):
        row_vals = raw_X[i]
        target_val = raw_y[i]
        if target_val is not None and all(v is not None for v in row_vals):
            X.append(row_vals)
            y.append(target_val)
            
    if len(X) > 0:
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        model = LinearRegression()
        model.fit(X_train, y_train)
        score = model.score(X_test, y_test)
        
        st.success(f"Model Trained! Accuracy (R²): {score:.4f}")
        
        col_in1, col_in2 = st.columns(2)
        user_inputs = []
        for i, feat in enumerate(features_list):
            col_vals = [row[i] for row in X]
            min_v, max_v, avg_v = min(col_vals), max(col_vals), sum(col_vals)/len(col_vals)
            with (col_in1 if i % 2 == 0 else col_in2):
                val = st.slider(f"{feat.capitalize()}", float(min_v), float(max_v), float(avg_v))
                user_inputs.append(val)
        
        if st.button("🚀 Predict Popularity"):
            prediction = model.predict([user_inputs])[0]
            st.metric(label="Predicted Score", value=f"{prediction:.1f} / 100")
            if prediction >= 80: st.balloons()
    else:
        st.error("Not enough data to train model.")

# ==========================================
# Tab 4: Underrated vs Overrated (NEW)
# ==========================================
with tab4:
    st.header("💎 Finding Underrated & Overrated Songs")
    st.markdown("""
    This section uses a **Demo Dataset** (with user ratings) to identify songs that deviate from the norm.
    """)

    # 1. Prepare Data (Using the user's hardcoded dictionary)
    raw_data_demo = {
        'track_name': ['Senorita', 'Happier', 'Circles', 'Believer', 'Levitating', 'Someone You Loved', 'Blinding Lights', 'Sunflower', 'Stay', 'Memories', 'Shape of You', 'Rockstar', 'Dance Monkey', 'Perfect', 'Bad Guy'],
        'track_rating_mean': [3.27, 3.03, 3.07, 2.45, 2.94, 3.32, 3.29, 2.61, 3.32, 3.0, 2.88, 3.19, 3.2, 2.90, 2.93],
        'track_popularity_mean': [94.33, 71.33, 72.75, 46.0, 25.0, 61.71, 60.0, 48.0, 94.0, 67.6, 69.5, 72.85, 54.33, 45.67, 30.5]
    }
    df_demo = DataFrame(raw_data_demo)

    # Layout: Two columns for side-by-side comparison
    col_u1, col_u2 = st.columns(2)

    # --- Section 1: Finding Underrated ---
    with col_u1:
        st.subheader("📉 Underrated Songs")
        st.info("Logic: **High Rating** but **Low Popularity**")
        
        # Sliders
        min_rating_u = st.slider("Min Rating", 0.0, 5.0, 2.5, step=0.1, key="u_rating")
        max_pop_u = st.slider("Max Popularity", 0, 100, 50, step=5, key="u_pop")
        top_n_u = st.slider("Show Top N", 1, 10, 5, key="u_n")

        # Logic
        underrated_res = df_demo.filter(lambda row:
            row['track_rating_mean'] >= min_rating_u and
            row['track_popularity_mean'] <= max_pop_u
        )
        
        # Display
        if underrated_res.row_count > 0:
            st.success(f"Found {underrated_res.row_count} records")
            # Convert to list of dicts for display
            u_data = []
            for i in range(min(underrated_res.row_count, top_n_u)):
                u_data.append({
                    "Song": underrated_res['track_name'][i],
                    "Rating": underrated_res['track_rating_mean'][i],
                    "Popularity": underrated_res['track_popularity_mean'][i]
                })
            st.table(u_data)
        else:
            st.warning("No songs match criteria.")

    # --- Section 2: Finding Overrated ---
    with col_u2:
        st.subheader("📈 Overrated Songs")
        st.error("Logic: **Low Rating** but **High Popularity**")
        
        # Sliders
        max_rating_o = st.slider("Max Rating", 0.0, 5.0, 3.0, step=0.1, key="o_rating")
        min_pop_o = st.slider("Min Popularity", 0, 100, 60, step=5, key="o_pop")
        top_n_o = st.slider("Show Top N", 1, 10, 5, key="o_n")

        # Logic
        overrated_res = df_demo.filter(lambda row:
            row['track_rating_mean'] <= max_rating_o and
            row['track_popularity_mean'] >= min_pop_o
        )
        
        # Display
        if overrated_res.row_count > 0:
            st.success(f"Found {overrated_res.row_count} records")
            o_data = []
            for i in range(min(overrated_res.row_count, top_n_o)):
                o_data.append({
                    "Song": overrated_res['track_name'][i],
                    "Rating": overrated_res['track_rating_mean'][i],
                    "Popularity": overrated_res['track_popularity_mean'][i]
                })
            st.table(o_data)
        else:
            st.warning("No songs match criteria.")



# Footer
st.markdown("---")
st.caption("Developed with Mini-Pandas Core | 2025")