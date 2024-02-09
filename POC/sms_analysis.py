import pandas as pd
from collections import Counter
import re
from datetime import datetime
from openai import OpenAI
import requests
import json

# Your OpenAI API key
api_key = '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'

client = OpenAI(api_key=api_key)

# Load the CSV file to examine its contents
file_path = 'Monitize_Varun_SMS.csv'
data = pd.read_csv(file_path)

# Display the first few rows of the dataset to understand its structure, especially the "_body" column
# print(data.head())

# Extracting the '_body' column
messages = data['_body']

# Function to find common patterns
def find_common_patterns(messages, num_patterns=10):
    # Regular expressions for identifying common message components
    patterns = {
        # 'date': r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b',
        # 'time': r'\b\d{1,2}:\d{2}\b',
        # 'money': r'\bRs\.?\s?\d+[,.]?\d*\b',
        # 'amount': r'\bINR\.?\s?\d+[,.]?\d*\b',
        # 'account_number': r'\b[A-Z]{2,4}XX\d{3,4}\b',
        # 'phone_number': r'\b\d{10}\b',
        # 'email': r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
        # 'url': r'\b(https?://)?(www\.)?[a-z0-9]+\.[a-z]{2,}(\/[A-Za-z0-9._]*)*\b',
        # 'otp': r'\b\d{4,6}\b'  # assuming OTP as 4-6 digits number
    }

    # Replace patterns with placeholders
    for pattern_name, pattern in patterns.items():
        messages = messages.str.replace(pattern, f'[{pattern_name}]', regex=True)

    # Counting occurrences of each patterned message
    pattern_counts = Counter(messages)

    # Selecting the most common patterns
    common_patterns = pattern_counts.most_common(num_patterns)

    return common_patterns

# Function to filter patterns for only amount debit and credit related transactions
def filter_amount_related_patterns(patterns):
    amount_related_patterns = []
    for pattern, count in patterns:
        # Patterns that contain 'debited', 'credited', 'paid', 'added'
        # transaction_words = ['debited', 'credited', 'paid', 'added']
        transaction_words = ['xxx', 'upi', 'vpa']
        if any(word in pattern.lower() for word in transaction_words):
            amount_related_patterns.append((pattern, count))
    return amount_related_patterns

# Updating the filter_past_transactions function to include grammar-based filtering for past transactions
def filter_past_transactions(messages):
    past_transactions = []
    current_date = datetime.now()

    # Regular expressions for future-tense grammar
    future_grammar = re.compile(r'\bwill be\b|\bwould be\b|\bgoing to\b|\bshall be\b|\bhas requested\b', re.IGNORECASE)

    for message in messages:
        date_matches = re.findall(r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b', message[0])
        future_tense = future_grammar.search(message[0])

        if date_matches and not future_tense:
            for date_str in date_matches:
                try:
                    for fmt in ("%d-%m-%Y", "%m-%d-%Y", "%Y-%m-%d", "%d/%m/%Y", "%m/%d/%Y", "%Y/%m/%d"):
                        try:
                            message_date = datetime.strptime(date_str, fmt)
                            break
                        except ValueError:
                            continue
                    if message_date < current_date:
                        past_transactions.append(message)
                        break
                except ValueError:
                    continue
        elif not date_matches and not future_tense:
            past_transactions.append(message)

    return past_transactions

def convert_transaction_to_sms(transaction_sms):    
    # Preparing the prompt
    prompt = "Convert this SMS into JSON and find category based on merchant name: " + transaction_sms

    # API endpoint
    # url = 'https://api.openai.com/v1/engines/gpt-4/completions'
    url = 'https://api.openai.com/v1/chat/completions'

    # Request headers
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {api_key}'
    }

    # Data for the POST request
    # post_data = {
    #     'prompt': prompt,
    #     'max_tokens': 150
    # }

    # Data for the POST request
    post_data = {
        'model': 'gpt-4.0',  # Specify the model
        'messages': [{'role':'system', 'content':'You are a financial analyst.'}, {'role':'user', 'content': prompt}],
        'max_tokens': 150
    }

    # Make the POST request
    response = requests.post(url, headers=headers, json=post_data)

    # Print the response
    return response.json()

def convert_transaction_to_json_with_category(transaction_sms):
    response = client.chat.completions.create(
        model="gpt-4",

        messages=[
            {
            "role": "system",
            "content": "You are a financial analyst"
            },
            {
            "role": "user",
            "content": transaction_sms
            },
            {
            "role": "assistant",
            "content": "Convert this into JSON and add category from merchant name. JSON should have TransactionDetails, LocationDetails, AccountInformation and Category (Main category, Sub category, description). Return only the json and nothing else"
            }
        ],

        temperature=1,
        max_tokens=256,
        top_p=1,
        frequency_penalty=0,
        presence_penalty=0
    )

    return response

# Finding the top N common patterns
common_message_patterns = find_common_patterns(messages, 5)

# Filtering out patterns related to amount transactions
amount_related_message_patterns = filter_amount_related_patterns(common_message_patterns)

# Applying the updated filter to get past transactions
past_transactions_patterns = filter_past_transactions(amount_related_message_patterns)

for past_transactions_pattern in past_transactions_patterns:
  print(past_transactions_pattern[1], " :: ", past_transactions_pattern[0])

  chatgpt_response = convert_transaction_to_json_with_category(past_transactions_pattern[0])
#   import pdb;pdb.set_trace()
  print(chatgpt_response.choices[0].message.content)

print("Count: ", len(common_message_patterns), " :: ", len(amount_related_message_patterns), " :: ", len(past_transactions_patterns))