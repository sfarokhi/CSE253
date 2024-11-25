import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.cluster import KMeans
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import classification_report, accuracy_score
import matplotlib.pyplot as plt
import nltk
nltk.download('stopwords')
from nltk.corpus import stopwords

#cumulative dataset
file_path = 'reddit_data/cumulative_reddit_political_posts_analysis.csv'
df_cumulative = pd.read_csv(file_path)
df_cumulative = df_cumulative.drop_duplicates(subset='Title', keep='first')

#labeled data
sample_file_path = 'reddit_data/small_sample.xlsx'
df_sample = pd.read_excel(sample_file_path)

#Basic text preprocessing (lowercase, language, etc)
def preprocess_text(text):
    stop_words = set(stopwords.words('english'))
    text = text.lower()
    text = ''.join([c for c in text if c.isalpha() or c.isspace()])
    text = ' '.join([word for word in text.split() if word not in stop_words])
    return text

# Preprocess text in both datasets
df_cumulative['processed_text'] = df_cumulative['Title'].apply(preprocess_text)
df_sample['processed_text'] = df_sample['Title'].apply(preprocess_text)

# TF-IDF Vectorization (transforming text to numerical value)
tfidf_vectorizer = TfidfVectorizer(max_df=0.9, min_df=1, max_features=1000)
# Fit the vectorizer on the combined data to maintain consistency
df_combined = pd.concat([df_sample['processed_text'], df_cumulative['processed_text']])
tfidf_vectorizer.fit(df_combined)

# Transform the sample and cumulative datasets consistently
X_sample = tfidf_vectorizer.transform(df_sample['processed_text'])
X_cumulative = tfidf_vectorizer.transform(df_cumulative['processed_text'])

# Prepare labels (Bias column) for the sample dataset
y_sample = df_sample['Bias']
# Split the sample dataset into training and testing sets
X_train, X_test, y_train, y_test = train_test_split(X_sample, y_sample, test_size=0.2, random_state=42)

# Train a Naive Bayes classifier - learns the relationship between the processed text and the bias labels (L, R, or N).
classifier = MultinomialNB()
classifier.fit(X_train, y_train)

# Evaluate the classifier on the test set - mainly for debugging
y_pred = classifier.predict(X_test)
print("Classification Report:\n", classification_report(y_test, y_pred))
print("Accuracy Score:", accuracy_score(y_test, y_pred))

# Predict the Bias for the cumulative dataset
y_cumulative_pred = classifier.predict(X_cumulative)
df_cumulative['Bias'] = y_cumulative_pred

# Self-training loop (adding high-confidence predictions back to training data) aka learning from itself
confidence_threshold = 0.8
iteration = 0
max_iterations = 10
while iteration < max_iterations:
    # Get the predicted probabilities for each class
    y_cumulative_prob = classifier.predict_proba(X_cumulative)
    
    # Find high-confidence predictions
    high_confidence_indices = np.max(y_cumulative_prob, axis=1) >= confidence_threshold
    X_high_confidence = X_cumulative[high_confidence_indices]
    y_high_confidence = y_cumulative_pred[high_confidence_indices]
    
    # If no high-confidence samples, stop the self-training loop
    if len(y_high_confidence) == 0:
        break
    
    # Add high-confidence samples to the training set
    X_train = np.vstack((X_train, X_high_confidence.toarray()))
    y_train = np.concatenate([y_train, y_high_confidence])
    
    # Retrain the classifier
    classifier.fit(X_train, y_train)
    iteration += 1

# Final prediction on the cumulative dataset after self-training
df_cumulative['Bias'] = classifier.predict(X_cumulative)

output_file_path = 'reddit_data/cumulative_reddit_political_posts_analysis_with_bias.csv'
df_cumulative.to_csv(output_file_path, index=False)

# Plot
bias_counts = df_cumulative['Bias'].value_counts()
plt.bar(bias_counts.index, bias_counts.values)
plt.xlabel('Bias')
plt.ylabel('Number of Posts')
plt.title('Distribution of Posts by Bias (L: Left, R: Right, N: Neutral)')
plt.show()

