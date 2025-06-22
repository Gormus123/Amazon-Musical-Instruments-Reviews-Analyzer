# Amazon-Musical-Instruments-Reviews-Analyzer
A web app that analyzes Amazon reviews for musical instruments. Users input a product name/ID and receive:
📊 Top 5 most frequent review terms 
😊😠 Sentiment analysis (positive/negative)
✍️ Automated review summary
⭐ Average product rating (1-5)
☁️ Interactive word cloud


[![Streamlit](https://static.streamlit.io/badges/streamlit_badge_black_white.svg)](https://your-app-url.streamlit.app)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# 🎵 Amazon Musical Instruments Review Analyzer
A Streamlit-powered dashboard that analyzes Amazon musical instrument reviews with sentiment analysis, keyword extraction, and interactive visualizations.

[Dashboard Screenshot]
![image](https://github.com/user-attachments/assets/01c93421-73ab-4ee7-9248-3d1a1a81f454)

## ✨ Key Features

### 🔍 Product Analysis
- **ASIN Search** (manual input or dropdown selection)
- **Top 5 Keywords** with frequency counts
- **Sentiment Distribution** pie chart (positive/neutral/negative)
- **Rating Gauge** with combined score visualization

### 📊 Data Insights
- **Review Summary** (AI-generated extractive summary)
- **Sample Reviews** expandable section
- **Dataset Overview** metrics
- **Top Products** by review count table

### 🎨 Interactive Visualizations
- Plotly-powered charts with responsive design
- Custom CSS-styled metric cards
- Sentiment-colored indicators
- Mobile-responsive layout


### 📊 Data Flow

1. Loads pre-processed json file
2. Create pre-processed CSVs (final_reviews_with_analysis.csv, product_ratings_analysis.csv)
3. Filters by selected ASIN
Performs:
Keyword extraction
Sentiment aggregation
Rating calculation
Outputs interactive dashboard components



🚀 Deployment


1. pip install -r requirements.txt   # Python dependencies


🔧 Dependencies


streamlit==1.29.0
pandas==2.0.3
plotly==5.18.0
textblob==0.17.1
nltk==3.8.1



2. cd "<YourFileLocation>"

3. streamlit run app.py




📝 Usage Example

Select product from dropdown or enter ASIN

Click "ANALYZE PRODUCT"

View:

Keyword frequency cards

Sentiment distribution pie chart

Interactive rating gauge

AI-generated summary

Sample reviews
