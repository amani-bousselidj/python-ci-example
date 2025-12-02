import unittest
import os
import tempfile
from fastapi.testclient import TestClient

# Use temporary file database for testing
test_db = tempfile.NamedTemporaryFile(delete=False, suffix=".db")
test_db_path = test_db.name
test_db.close()
os.environ["DATABASE_URL"] = f"sqlite:///{test_db_path}"

from app import app

class TestAdminDashboard(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Set up test client"""
        cls.client = TestClient(app)
    
    def setUp(self):
        """Clear database before each test"""
        from app import SessionLocal, MessageDB
        db = SessionLocal()
        try:
            db.query(MessageDB).delete()
            db.commit()
        finally:
            db.close()
    
    @classmethod
    def tearDownClass(cls):
        """Clean up test database"""
        if os.path.exists(test_db_path):
            try:
                os.remove(test_db_path)
            except:
                pass
    
    def test_root_endpoint(self):
        """Test root endpoint"""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn("message", response.json())
    
    def test_create_message(self):
        """Test creating a new message"""
        message_data = {
            "name": "John Doe",
            "email": "john@example.com",
            "subject": "Test Subject",
            "message": "This is a test message"
        }
        response = self.client.post("/api/messages", json=message_data)
        self.assertEqual(response.status_code, 201)
        data = response.json()
        self.assertEqual(data["name"], "John Doe")
        self.assertEqual(data["email"], "john@example.com")
        self.assertEqual(data["subject"], "Test Subject")
        self.assertEqual(data["message"], "This is a test message")
        self.assertFalse(data["read"])
        self.assertIn("id", data)
        self.assertIn("timestamp", data)
    
    def test_create_message_invalid_email(self):
        """Test creating a message with invalid email"""
        message_data = {
            "name": "John Doe",
            "email": "invalid-email",
            "subject": "Test Subject",
            "message": "This is a test message"
        }
        response = self.client.post("/api/messages", json=message_data)
        self.assertEqual(response.status_code, 422)
    
    def test_get_all_messages(self):
        """Test retrieving all messages"""
        # Create test messages
        messages = [
            {
                "name": "User 1",
                "email": "user1@example.com",
                "subject": "Subject 1",
                "message": "Message 1"
            },
            {
                "name": "User 2",
                "email": "user2@example.com",
                "subject": "Subject 2",
                "message": "Message 2"
            }
        ]
        for msg in messages:
            self.client.post("/api/messages", json=msg)
        
        # Get all messages
        response = self.client.get("/api/admin/messages")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 2)
        self.assertEqual(data[0]["name"], "User 1")
        self.assertEqual(data[1]["name"], "User 2")
    
    def test_get_single_message(self):
        """Test retrieving a single message"""
        # Create a message
        message_data = {
            "name": "Jane Doe",
            "email": "jane@example.com",
            "subject": "Test Subject",
            "message": "This is a test message"
        }
        create_response = self.client.post("/api/messages", json=message_data)
        message_id = create_response.json()["id"]
        
        # Get the message
        response = self.client.get(f"/api/admin/messages/{message_id}")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["name"], "Jane Doe")
        self.assertEqual(data["email"], "jane@example.com")
    
    def test_get_nonexistent_message(self):
        """Test retrieving a message that doesn't exist"""
        response = self.client.get("/api/admin/messages/999")
        self.assertEqual(response.status_code, 404)
    
    def test_update_message_status(self):
        """Test updating message read status"""
        # Create a message
        message_data = {
            "name": "Test User",
            "email": "test@example.com",
            "subject": "Test Subject",
            "message": "This is a test message"
        }
        create_response = self.client.post("/api/messages", json=message_data)
        message_id = create_response.json()["id"]
        
        # Update to read
        update_response = self.client.patch(
            f"/api/admin/messages/{message_id}",
            json={"read": True}
        )
        self.assertEqual(update_response.status_code, 200)
        self.assertTrue(update_response.json()["read"])
        
        # Update to unread
        update_response = self.client.patch(
            f"/api/admin/messages/{message_id}",
            json={"read": False}
        )
        self.assertEqual(update_response.status_code, 200)
        self.assertFalse(update_response.json()["read"])
    
    def test_delete_message(self):
        """Test deleting a message"""
        # Create a message
        message_data = {
            "name": "Delete User",
            "email": "delete@example.com",
            "subject": "Test Subject",
            "message": "This is a test message"
        }
        create_response = self.client.post("/api/messages", json=message_data)
        message_id = create_response.json()["id"]
        
        # Delete the message
        delete_response = self.client.delete(f"/api/admin/messages/{message_id}")
        self.assertEqual(delete_response.status_code, 200)
        
        # Verify it's deleted
        get_response = self.client.get(f"/api/admin/messages/{message_id}")
        self.assertEqual(get_response.status_code, 404)
    
    def test_delete_nonexistent_message(self):
        """Test deleting a message that doesn't exist"""
        response = self.client.delete("/api/admin/messages/999")
        self.assertEqual(response.status_code, 404)
    
    def test_message_stats(self):
        """Test getting message statistics"""
        # Create messages
        messages = [
            {
                "name": "User 1",
                "email": "user1@example.com",
                "subject": "Subject 1",
                "message": "Message 1"
            },
            {
                "name": "User 2",
                "email": "user2@example.com",
                "subject": "Subject 2",
                "message": "Message 2"
            },
            {
                "name": "User 3",
                "email": "user3@example.com",
                "subject": "Subject 3",
                "message": "Message 3"
            }
        ]
        message_ids = []
        for msg in messages:
            response = self.client.post("/api/messages", json=msg)
            message_ids.append(response.json()["id"])
        
        # Mark one as read
        self.client.patch(
            f"/api/admin/messages/{message_ids[0]}",
            json={"read": True}
        )
        
        # Get stats
        response = self.client.get("/api/admin/messages/stats/summary")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["total"], 3)
        self.assertEqual(data["read"], 1)
        self.assertEqual(data["unread"], 2)
    
    def test_pagination(self):
        """Test message pagination"""
        # Create 5 messages
        for i in range(5):
            message_data = {
                "name": f"User {i}",
                "email": f"user{i}@example.com",
                "subject": f"Subject {i}",
                "message": f"Message {i}"
            }
            self.client.post("/api/messages", json=message_data)
        
        # Get first 2 messages
        response = self.client.get("/api/admin/messages?skip=0&limit=2")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 2)
        
        # Get next 2 messages
        response = self.client.get("/api/admin/messages?skip=2&limit=2")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(len(data), 2)

if __name__ == "__main__":
    unittest.main()
