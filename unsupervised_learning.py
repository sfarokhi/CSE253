import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation, NMF
from sklearn.cluster import KMeans
import matplotlib.pyplot as plt
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords

# Load the cumulative dataset
file_path = 'reddit_data/cumulative_reddit_political_posts_analysis.csv'
df = pd.read_csv(file_path)

# Basic text preprocessing
def preprocess_text(text):
    stop_words = set(stopwords.words('english'))
    text = text.lower()
    text = ''.join([c for c in text if c.isalpha() or c.isspace()])
    text = ' '.join([word for word in text.split() if word not in stop_words])
    return text

df['processed_text'] = df['Title'].apply(preprocess_text)

# TF-IDF Vectorization
tfidf_vectorizer = TfidfVectorizer(max_df=0.9, min_df=50, max_features=1000)
tfidf_matrix = tfidf_vectorizer.fit_transform(df['processed_text'])

# Topic Modeling using LDA
lda = LatentDirichletAllocation(n_components=5, random_state=42)
lda.fit(tfidf_matrix)

# Display top words per topic
def display_topics(model, feature_names, n_top_words):
    for topic_idx, topic in enumerate(model.components_):
        print(f"Topic {topic_idx}")
        print(" ".join([feature_names[i] for i in topic.argsort()[:-n_top_words - 1:-1]]))
        print()

display_topics(lda, tfidf_vectorizer.get_feature_names_out(), 10)

# Clustering using K-Means
num_clusters = 5
kmeans = KMeans(n_clusters=num_clusters, random_state=42)
kmeans.fit(tfidf_matrix)

# Add cluster labels to the original dataframe
df['cluster'] = kmeans.labels_

# Visualize the clusters
plt.hist(df['cluster'], bins=num_clusters)
plt.xlabel('Cluster')
plt.ylabel('Number of Posts')
plt.title('Distribution of Posts across Clusters')
plt.show()
