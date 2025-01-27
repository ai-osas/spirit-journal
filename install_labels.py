import os
import django
from django.conf import settings

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.settings')
django.setup()

from neomodel import install_labels, remove_all_labels
from authentication.models import UserNode
# Import other Neo4j models here as needed

def setup_neo4j_schema():
    # Install labels for all neomodel classes
    install_labels(UserNode)
    # Add other models as needed
    # install_labels(OtherNode)
    
    print("Neo4j labels installed successfully!")

if __name__ == '__main__':
    setup_neo4j_schema()