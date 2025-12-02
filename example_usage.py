"""
Example usage of the Portfolio Admin Dashboard API

This script demonstrates how to interact with the API endpoints.
Make sure the server is running (uvicorn app:app) before running this script.
"""

import requests
import json

BASE_URL = "http://localhost:8000"

def create_message():
    """Example: Create a new contact message"""
    print("\n=== Creating a new message ===")
    message_data = {
        "name": "Alice Johnson",
        "email": "alice@example.com",
        "subject": "Project Collaboration",
        "message": "I'm interested in collaborating on a web development project."
    }
    response = requests.post(f"{BASE_URL}/api/messages", json=message_data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.json()["id"]

def get_all_messages():
    """Example: Get all messages (admin)"""
    print("\n=== Getting all messages ===")
    response = requests.get(f"{BASE_URL}/api/admin/messages")
    print(f"Status: {response.status_code}")
    messages = response.json()
    print(f"Total messages: {len(messages)}")
    for msg in messages:
        print(f"  - ID {msg['id']}: {msg['name']} - {msg['subject']} (Read: {msg['read']})")
    return messages

def get_single_message(message_id):
    """Example: Get a specific message"""
    print(f"\n=== Getting message {message_id} ===")
    response = requests.get(f"{BASE_URL}/api/admin/messages/{message_id}")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def mark_as_read(message_id):
    """Example: Mark a message as read"""
    print(f"\n=== Marking message {message_id} as read ===")
    response = requests.patch(
        f"{BASE_URL}/api/admin/messages/{message_id}",
        json={"read": True}
    )
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def get_statistics():
    """Example: Get message statistics"""
    print("\n=== Getting message statistics ===")
    response = requests.get(f"{BASE_URL}/api/admin/messages/stats/summary")
    print(f"Status: {response.status_code}")
    stats = response.json()
    print(f"Total: {stats['total']}, Read: {stats['read']}, Unread: {stats['unread']}")

def delete_message(message_id):
    """Example: Delete a message"""
    print(f"\n=== Deleting message {message_id} ===")
    response = requests.delete(f"{BASE_URL}/api/admin/messages/{message_id}")
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")

def main():
    """Run all examples"""
    print("Portfolio Admin Dashboard API - Example Usage")
    print("=" * 50)
    
    try:
        # Check if server is running
        response = requests.get(f"{BASE_URL}/")
        print(f"Server status: {response.json()}")
        
        # Create a new message
        message_id = create_message()
        
        # Get all messages
        get_all_messages()
        
        # Get single message
        get_single_message(message_id)
        
        # Mark as read
        mark_as_read(message_id)
        
        # Get statistics
        get_statistics()
        
        # Uncomment to delete the message
        # delete_message(message_id)
        
        print("\n" + "=" * 50)
        print("All examples completed successfully!")
        
    except requests.exceptions.ConnectionError:
        print("\nError: Could not connect to the server.")
        print("Make sure the server is running with: uvicorn app:app")
    except Exception as e:
        print(f"\nError: {e}")

if __name__ == "__main__":
    main()
