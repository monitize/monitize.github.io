import json

# The ChatCompletion object
chat_completion = {
    "id": "chatcmpl-8n7tfXD1c76pVmN5gQXU59uSMZXfS",
    "choices": [
        {
            "finish_reason": "stop",
            "index": 0,
            "message": {
                "content": 'Sure, Here\'s a JSON representation of the transaction.\n\n```json\n{\n  "TransactionDetails": {\n    "transactionType": "Deposit",\n    "amount": 100.00,\n    "currency": "INR",\n    "merchantName": "Federal Bank",\n    "merchantApp": "Fi"\n  },\n  \n  "AccountInformation": {\n    "accountNo": "XXXXXXX3765",\n    "accountType": "Smart Deposit"\n  },\n  \n  "LocationDetails": {\n    "location": null\n  },\n  \n  "Category": {\n    "mainCategory": "Banking",\n    "subCategory": "Deposit",\n    "description": "INR 100.00 has been added to your Smart Deposit account"\n  }\n}\n```\nNote: Since no location detail provided, `LocationDetails.location` value is set to `null`.',
                "role": "assistant",
                "function_call": None,
                "tool_calls": None
            },
            "logprobs": None
        }
    ],
    "created": 1706719119,
    "model": "gpt-4-0613",
    "object": "chat.completion",
    "system_fingerprint": None,
    "usage": {
        "completion_tokens": 177,
        "prompt_tokens": 84,
        "total_tokens": 261
    }
}

# Extracting the JSON content from the message field
json_content = chat_completion["choices"][0]["message"]["content"]

# Parsing the JSON content
parsed_json = json.loads(json_content)

# Now, 'parsed_json' contains the extracted JSON object
print(parsed_json)
