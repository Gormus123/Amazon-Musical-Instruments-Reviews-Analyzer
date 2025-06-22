import streamlit as st
import pandas as pd
import json
from collections import Counter
import re
from textblob import TextBlob
import plotly.express as px
import plotly.graph_objects as go
import os

# Set page config
st.set_page_config(
    page_title="Product Review Analyzer",
    page_icon="📊",
    layout="wide"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #1f77b4;
        margin-bottom: 2rem;
    }
    .product-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
        border-left: 5px solid #1f77b4;
    }
    .metric-card {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 8px;
        text-align: center;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .sentiment-positive {
        color: #28a745;
        font-weight: bold;
    }
    .sentiment-negative {
        color: #dc3545;
        font-weight: bold;
    }
    .sentiment-neutral {
        color: #6c757d;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_data():
    """Load the processed data with better error handling"""
    # Check if files exist
    required_files = ['final_reviews_with_analysis.csv', 'product_ratings_analysis.csv']
    missing_files = []
    
    for file in required_files:
        if not os.path.exists(file):
            missing_files.append(file)
    
    if missing_files:
        st.error(f"❌ Missing required files: {', '.join(missing_files)}")
        st.info("""
        **To fix this issue:**
        1. Make sure you have run the data preprocessing script
        2. Ensure these files are in the same directory as your Streamlit app:
           - `final_reviews_with_analysis.csv`
           - `product_ratings_analysis.csv`
        3. Check file permissions
        """)
        return None, None
    
    try:
        # Try to load the final processed data
        st.info("📂 Loading data files...")
        df = pd.read_csv('final_reviews_with_analysis.csv')
        product_ratings = pd.read_csv('product_ratings_analysis.csv', index_col=0)
        
        # Validate data structure
        required_columns_df = ['asin', 'reviewText_english', 'sentiment_label', 'reviewerName', 'overall', 'detected_language']
        required_columns_ratings = ['avg_rating', 'combined_rating', 'avg_sentiment', 'review_count']
        
        missing_cols_df = [col for col in required_columns_df if col not in df.columns]
        missing_cols_ratings = [col for col in required_columns_ratings if col not in product_ratings.columns]
        
        if missing_cols_df:
            st.error(f"❌ Missing columns in reviews data: {', '.join(missing_cols_df)}")
            return None, None
            
        if missing_cols_ratings:
            st.error(f"❌ Missing columns in ratings data: {', '.join(missing_cols_ratings)}")
            return None, None
        
        st.success(f"✅ Successfully loaded {len(df)} reviews for {len(product_ratings)} products")
        return df, product_ratings
        
    except pd.errors.EmptyDataError:
        st.error("❌ One or more CSV files are empty!")
        return None, None
    except pd.errors.ParserError as e:
        st.error(f"❌ Error parsing CSV files: {str(e)}")
        return None, None
    except Exception as e:
        st.error(f"❌ Unexpected error loading data: {str(e)}")
        st.info("Please check your data files and try again.")
        return None, None

def get_top_words(text_series, top_n=5):
    """Extract top N most frequent words from review text"""
    # Combine all text
    all_text = ' '.join(text_series.fillna('').astype(str))
    
    # Clean text and extract words
    words = re.findall(r'\b[a-zA-Z]{3,}\b', all_text.lower())
    
    # Remove common words that aren't meaningful
    stop_words = {'the', 'and', 'for', 'are', 'but', 'not', 'you', 'all', 'can', 'had', 'her', 'was', 'one', 'our', 'out', 'day', 'get', 'has', 'him', 'his', 'how', 'man', 'new', 'now', 'old', 'see', 'two', 'way', 'who', 'boy', 'did', 'its', 'let', 'put', 'say', 'she', 'too', 'use'}
    
    filtered_words = [word for word in words if word not in stop_words]
    
    # Count frequency
    word_counts = Counter(filtered_words)
    
    return word_counts.most_common(top_n)

def generate_summary(reviews, max_length=200):
    """Generate a short summary from reviews"""
    # Take first few reviews and create summary
    sample_reviews = reviews.head(3).tolist()
    combined_text = ' '.join(sample_reviews)
    
    # Simple extractive summary - take first sentences
    sentences = combined_text.split('.')
    summary = '. '.join(sentences[:2])
    
    if len(summary) > max_length:
        summary = summary[:max_length] + "..."
    
    return summary.strip()

def analyze_product(df, product_ratings, product_code):
    """Analyze and display product information"""
    
    # Filter data for selected product
    product_reviews = df[df['asin'] == product_code]
    
    if len(product_reviews) == 0:
        st.error("No reviews found for this product!")
        return
    
    # Get product rating info
    try:
        rating_info = product_ratings.loc[product_code]
    except KeyError:
        st.error("Rating information not available for this product!")
        return
    
    # Main content area
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.markdown(f'<div class="product-card">', unsafe_allow_html=True)
        st.markdown(f"## 📦 Product: {product_code}")
        st.markdown(f"**Total Reviews:** {len(product_reviews)}")
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Top 5 most frequent words
        st.subheader("🔤 Top 5 Most Frequent Words")
        top_words = get_top_words(product_reviews['reviewText_english'], 5)
        
        if top_words:
            word_cols = st.columns(5)
            for i, (word, count) in enumerate(top_words):
                with word_cols[i]:
                    st.markdown(f'''
                    <div class="metric-card">
                        <h3 style="color: #1f77b4; margin: 0;">{word}</h3>
                        <p style="margin: 0; color: #666;">({count} times)</p>
                    </div>
                    ''', unsafe_allow_html=True)
        
        # Sentiment Analysis
        st.subheader("😊 Sentiment Analysis")
        sentiment_counts = product_reviews['sentiment_label'].value_counts()
        
        # Create sentiment chart
        fig = px.pie(
            values=sentiment_counts.values, 
            names=sentiment_counts.index,
            title="Review Sentiment Distribution",
            color_discrete_map={
                'positive': '#28a745',
                'negative': '#dc3545', 
                'neutral': '#6c757d'
            }
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Sentiment summary
        total_reviews = len(product_reviews)
        positive_pct = sentiment_counts.get('positive', 0) / total_reviews * 100
        negative_pct = sentiment_counts.get('negative', 0) / total_reviews * 100
        neutral_pct = sentiment_counts.get('neutral', 0) / total_reviews * 100
        
        col_pos, col_neu, col_neg = st.columns(3)
        with col_pos:
            st.markdown(f'<p class="sentiment-positive">Positive: {positive_pct:.1f}%</p>', unsafe_allow_html=True)
        with col_neu:
            st.markdown(f'<p class="sentiment-neutral">Neutral: {neutral_pct:.1f}%</p>', unsafe_allow_html=True)
        with col_neg:
            st.markdown(f'<p class="sentiment-negative">Negative: {negative_pct:.1f}%</p>', unsafe_allow_html=True)
    
    with col2:
        # Rating display
        st.subheader("⭐ Product Rating")
        
        # Show ratings
        avg_rating = rating_info['avg_rating']
        combined_rating = rating_info['combined_rating']
        
        # Create gauge chart for rating
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number+delta",
            value = combined_rating,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': "Combined Rating"},
            delta = {'reference': avg_rating},
            gauge = {
                'axis': {'range': [None, 5]},
                'bar': {'color': "darkblue"},
                'steps': [
                    {'range': [0, 2], 'color': "lightgray"},
                    {'range': [2, 4], 'color': "gray"},
                    {'range': [4, 5], 'color': "lightgreen"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 4.5
                }
            }
        ))
        fig_gauge.update_layout(height=300)
        st.plotly_chart(fig_gauge, use_container_width=True)
        
        # Rating details
        st.markdown(f"""
        **Average User Rating:** {avg_rating:.2f}/5.0  
        **Combined Rating:** {combined_rating:.2f}/5.0  
        **Sentiment Score:** {rating_info['avg_sentiment']:.3f}  
        **Review Count:** {int(rating_info['review_count'])}
        """)
    
    # Review Summary
    st.subheader("📝 Review Summary")
    summary = generate_summary(product_reviews['reviewText_english'])
    st.markdown(f'<div class="product-card">{summary}</div>', unsafe_allow_html=True)
    
    # Sample reviews
    with st.expander("📖 View Sample Reviews"):
        sample_reviews = product_reviews.head(3)
        for idx, review in sample_reviews.iterrows():
            st.markdown(f"**Reviewer:** {review['reviewerName']}")
            st.markdown(f"**Rating:** {'⭐' * int(review['overall'])}")
            st.markdown(f"**Sentiment:** {review['sentiment_label'].title()}")
            st.markdown(f"**Review:** {review['reviewText_english'][:200]}...")
            st.markdown("---")

def show_general_stats(df, product_ratings):
    """Show general statistics when no product is selected"""
    st.markdown("## 📈 Dataset Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Reviews", len(df))
    with col2:
        st.metric("Total Products", df['asin'].nunique())
    with col3:
        st.metric("Avg Reviews per Product", f"{len(df) / df['asin'].nunique():.1f}")
    with col4:
        st.metric("Languages Detected", df['detected_language'].nunique())
    
    # Top products
    st.subheader("🏆 Top Products by Review Count")
    top_products = product_ratings.nlargest(10, 'review_count')[['avg_rating', 'combined_rating', 'review_count']]
    st.dataframe(top_products, use_container_width=True)
    
    # Sentiment distribution
    st.subheader("😊 Overall Sentiment Distribution")
    sentiment_dist = df['sentiment_label'].value_counts()
    fig = px.bar(x=sentiment_dist.index, y=sentiment_dist.values, 
                title="Sentiment Distribution Across All Reviews",
                color=sentiment_dist.index,
                color_discrete_map={
                    'positive': '#28a745',
                    'negative': '#dc3545', 
                    'neutral': '#6c757d'
                })
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)

def main():
    # Header
    st.markdown('<div class="main-header">📊 Product Review Analyzer</div>', unsafe_allow_html=True)
    
    # Load data
    df, product_ratings = load_data()
    
    if df is None or product_ratings is None:
        st.stop()
    
    # Sidebar for input
    st.sidebar.header("🔍 Search Product")
    
    # Get unique products for dropdown
    unique_products = df['asin'].unique()
    unique_names = df.groupby('asin')['reviewerName'].first().to_dict()
    
    # Create product options with names
    product_options = []
    for asin in unique_products:
        review_count = len(df[df['asin'] == asin])
        product_options.append(f"{asin} ({review_count} reviews)")
    
    # Input methods
    input_method = st.sidebar.radio("Choose input method:", ["Select from list", "Enter product code manually"])
    
    selected_product = None
    
    if input_method == "Select from list":
        selected_option = st.sidebar.selectbox("Select a product:", [""] + product_options)
        if selected_option:
            selected_product = selected_option.split(' (')[0]
    else:
        entered_code = st.sidebar.text_input("Enter product code (ASIN):")
        if entered_code:
            if entered_code in unique_products:
                selected_product = entered_code
            else:
                st.sidebar.error("Product code not found!")
    
    # OK button
    if st.sidebar.button("🔍 ANALYZE PRODUCT", type="primary"):
        if selected_product:
            analyze_product(df, product_ratings, selected_product)
        else:
            st.sidebar.error("Please select or enter a product code!")
    
    # Show general statistics when no product is selected
    if not selected_product:
        show_general_stats(df, product_ratings)

if __name__ == "__main__":
    main()