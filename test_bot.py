#!/usr/bin/env python3
"""
Test script for the Discord TLDR Bot functionality
"""

import os
import json
from datetime import datetime, timezone
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

def test_timeframe_parsing():
    """Test the timeframe parsing functionality"""
    print("🧪 Testing timeframe parsing...")
    
    test_cases = [
        "last hour",
        "yesterday",
        "last 3 hours",
        "this morning",
        "last week"
    ]
    
    for test_case in test_cases:
        print(f"\nTesting: '{test_case}'")
        
        prompt = f"""
        Parse the following natural language request and extract start and end times.
        Return ONLY a JSON object with 'start_time' and 'end_time' fields in ISO format.
        
        Request: {test_case}
        
        Examples:
        - "last hour" -> {{"start_time": "2024-01-01T10:00:00Z", "end_time": "2024-01-01T11:00:00Z"}}
        - "yesterday" -> {{"start_time": "2024-01-01T00:00:00Z", "end_time": "2024-01-01T23:59:59Z"}}
        - "last 3 hours" -> {{"start_time": "2024-01-01T08:00:00Z", "end_time": "2024-01-01T11:00:00Z"}}
        
        Return only the JSON object:
        """
        
        try:
            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful assistant that parses natural language time requests into JSON format with start and end times in ISO format."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1
            )
            
            json_str = response.choices[0].message.content.strip()
            if json_str.startswith('```json'):
                json_str = json_str[7:-3]
            elif json_str.startswith('```'):
                json_str = json_str[3:-3]
            
            timeframe_data = json.loads(json_str)
            print(f"✅ Success: {timeframe_data}")
            
        except Exception as e:
            print(f"❌ Error: {e}")

def test_summary_generation():
    """Test the summary generation functionality"""
    print("\n🧪 Testing summary generation...")
    
    # Mock message data
    mock_messages = [
        {
            "timestamp": "2024-01-01T10:00:00Z",
            "content": "Good morning everyone! How's the project going?",
            "username": "Alice"
        },
        {
            "timestamp": "2024-01-01T10:05:00Z",
            "content": "Morning! I've been working on the new feature. It's almost ready for testing.",
            "username": "Bob"
        },
        {
            "timestamp": "2024-01-01T10:10:00Z",
            "content": "Great! I can help test it. What's the main functionality?",
            "username": "Charlie"
        },
        {
            "timestamp": "2024-01-01T10:15:00Z",
            "content": "It's a new dashboard that shows real-time analytics. Should be much faster than the old one.",
            "username": "Bob"
        },
        {
            "timestamp": "2024-01-01T10:20:00Z",
            "content": "Perfect! Let me know when it's ready and I'll start testing.",
            "username": "Charlie"
        }
    ]
    
    messages_text = "\n".join([
        f"[{msg['timestamp']}] {msg['username']}: {msg['content']}"
        for msg in mock_messages
    ])
    
    prompt = f"""
    Please create a concise TLDR summary of the following Discord channel messages.
    Focus on the main topics, key discussions, and important points.
    Keep the summary under 500 words and make it easy to understand.
    
    Messages:
    {messages_text}
    
    TLDR Summary:
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that creates concise summaries of Discord conversations."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7
        )
        
        summary = response.choices[0].message.content.strip()
        print(f"✅ Summary generated successfully:")
        print(f"📝 {summary}")
        
    except Exception as e:
        print(f"❌ Error generating summary: {e}")

def main():
    """Run all tests"""
    print("🚀 Starting Discord TLDR Bot Tests...")
    
    # Check if OpenAI API key is available
    if not os.getenv('OPENAI_API_KEY'):
        print("❌ Error: OPENAI_API_KEY environment variable not set")
        print("Please create a .env file with your OpenAI API key")
        return
    
    test_timeframe_parsing()
    test_summary_generation()
    
    print("\n✅ All tests completed!")

if __name__ == "__main__":
    main() 