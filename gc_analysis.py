import argparse
import csv
import pandas as pd
from google.cloud import language_v1
from googleapiclient import discovery
import glob
import time

def analyze_sentiment(text, client):
    """
    Run a sentiment analysis request using Google Cloud Natural Language API.
    """

    # Instantiates a plain text document
    document = language_v1.Document(
        content=text, type_=language_v1.Document.Type.PLAIN_TEXT
    )
    annotations = client.analyze_sentiment(request={"document": document})

    return annotations

def extract_sentiment(annotations):

    score = annotations.document_sentiment.score
    magnitude = annotations.document_sentiment.magnitude

    return score, magnitude

def analyze_characteristics(text, client):
    """
    Analyze the toxicity, profanity, etc. of a text using Google's Perspective API.
    """

    # Full breadth of the Google API 'commentanalyzer':    
    # 'TOXICITY': {},
    # 'SEVERE_TOXICITY': {},
    # 'IDENTITY_ATTACK': {},
    # 'INSULT': {},
    # 'PROFANITY': {},
    # 'THREAT': {},
    # 'SEXUALLY_EXPLICIT': {},
    # 'FLIRTATION': {}

    analyze_request = {
        'comment': {'text': text},
        'requestedAttributes': {'TOXICITY': {},
                                'IDENTITY_ATTACK': {},
                                'INSULT': {}}
    }

    response = client.comments().analyze(body=analyze_request).execute()
    return response

def extract_characteristics(attributeScores):
    
    toxicity_score = attributeScores.get('TOXICITY', {}).get('summaryScore', {}).get('value', 0.0)
    identity_attack_score = attributeScores.get('IDENTITY_ATTACK', {}).get('summaryScore', {}).get('value', 0.0)
    insult_score = attributeScores.get('INSULT', {}).get('summaryScore', {}).get('value', 0.0)
    
    return toxicity_score, identity_attack_score, insult_score

def process_csv(input_csv, sentiment_client, characteristic_client):
    """
    Iterate through rows in the CSV, analyze sentiment and toxicity of the 'text' column,
    and save results to a new CSV with additional columns.
    """
    updated_filename = "GCP-twitter-results/" + input_csv.split("/")[1]
    
    # Define column order explicitly
    columns = [
        "timestamp", "username", "icon-verified", "fact-checked", "text",
        "views", "likes", "replies", "reposts", "bookmarks",
        "Sentiment_Score", "Sentiment_Magnitude", 
        "Toxicity_Score", "Identity_Attack_Score", "Insult_Score"
    ]
    
    # Initialize an empty list to store processed rows
    processed_data = []

    with open(input_csv, 'r', encoding='utf-8') as file:
        # Use a DictReader to read the CSV, ensuring correct handling of quoted fields
        reader = csv.DictReader(file)
        
        for row in reader:
            text = row.get("text")
            if not text:
                print("No text found in this row, skipping...")
                continue

            print(f"Analyzing text: {text}")
            time.sleep(.8)
            
            # Initialize columns for results
            sentiment_score, sentiment_magnitude = None, None
            toxicity, identity_attack, insult = None, None, None

            # Sentiment Analysis
            try:
                sentiment_result = analyze_sentiment(text, sentiment_client)
                sentiment_score, sentiment_magnitude = extract_sentiment(sentiment_result)
                print(f"\nSentiment Analysis:")
                print(f"Score: {sentiment_score:.5f}")
                print(f"Magnitude: {sentiment_magnitude:.5f}\n")
            except Exception as e:
                print(f"Error analyzing sentiment: {e}")
                
            time.sleep(.8)

            # Characteristics Analysis
            try:
                characteristic_result = analyze_characteristics(text, characteristic_client)
                attribute_scores = characteristic_result.get("attributeScores", {})
                toxicity, identity_attack, insult = extract_characteristics(attribute_scores)
                print("Characteristic Analysis:")
                print(f"Toxicity Score: {toxicity:.5f}")
                print(f"Identity Attack Score: {identity_attack:.5f}")
                print(f"Insult Score: {insult:.5f}")
            except Exception as e:
                print(f"Error analyzing toxicity: {e}")

            print("-" * 50)
            
            # Add the new data to the row
            processed_row = row.copy()  # Create a copy of the original row
            processed_row.update({
                "Sentiment_Score": sentiment_score,
                "Sentiment_Magnitude": sentiment_magnitude,
                "Toxicity_Score": toxicity,
                "Identity_Attack_Score": identity_attack,
                "Insult_Score": insult
            })
            processed_data.append(processed_row)

        # Convert processed data to a DataFrame
        updated_file = pd.DataFrame(processed_data)

        # Save the updated DataFrame to a new CSV file
        updated_file.to_csv(updated_filename, columns=columns, index=False, encoding='utf-8-sig', quotechar='"')
        print(f"Processed data saved to {updated_filename}")
        return


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Analyze sentiment and toxicity of text in a CSV file.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    # parser.add_argument(
    #     "input_csv", help="The filename of the CSV file you'd like to analyze."
    # )
    parser.add_argument(
        "--api_key", required=True, help="API key for Google's Perspective API."
    )

    args = parser.parse_args()
    
    print("Connecting to Google Natural Language API...")
    
    sentiment_client = language_v1.LanguageServiceClient()
    
    characteristic_client = discovery.build(
        "commentanalyzer",
        "v1alpha1",
        developerKey=args.api_key,
        discoveryServiceUrl="https://commentanalyzer.googleapis.com/$discovery/rest?version=v1alpha1",
        static_discovery=False,
    )

    for csv_file in glob.glob("twitter_results/*.csv"):
        process_csv(csv_file, sentiment_client, characteristic_client)
        
