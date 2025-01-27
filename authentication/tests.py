from django.contrib.auth import get_user_model
from authentication.models import UserNode
import uuid

def test_user_sync():
    # Generate a unique username
    unique_username = f"testuser_{uuid.uuid4().hex[:8]}"
    
    # Create a Django user
    User = get_user_model()
    
    try:
        # First ensure no test user exists
        User.objects.filter(username=unique_username).delete()
        
        print(f"Creating test user: {unique_username}")
        user = User.objects.create_user(
            username=unique_username,
            email=f'{unique_username}@example.com',
            password='testpass123'
        )
        
        print("User created in PostgreSQL, checking Neo4j sync...")
        
        # Verify Neo4j node was created
        neo4j_user = UserNode.nodes.get(user_id=str(user.id))
        print(f"Success! User synced to Neo4j with ID: {neo4j_user.user_id}")
        
        # Test relationship creation
        neo4j_user.follows.connect(neo4j_user)  # Self-follow as a test
        print("Successfully created test relationship")
        
        # Verify relationship
        followers = list(neo4j_user.follows.all())
        print(f"Found {len(followers)} followers")
        
    except Exception as e:
        print(f"Error during test: {e}")
        raise
    
    finally:
        # Cleanup - make sure to clean up in both databases
        try:
            if 'user' in locals():
                print(f"Cleaning up user {user.username}")
                user.delete()  # Should trigger Neo4j deletion via signal
                
                # Verify Neo4j cleanup
                try:
                    UserNode.nodes.get(user_id=str(user.id))
                    print("Warning: Neo4j node still exists after deletion!")
                except UserNode.DoesNotExist:
                    print("Successfully verified Neo4j node deletion")
                    
        except Exception as cleanup_error:
            print(f"Error during cleanup: {cleanup_error}")

if __name__ == "__main__":
    test_user_sync()