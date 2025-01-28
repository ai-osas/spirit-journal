# authentication/signals.py
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.db import transaction
import logging
from .models import User, UserNode

logger = logging.getLogger(__name__)

@receiver(post_save, sender=User)
def sync_user_to_neo4j(sender, instance, created, **kwargs):
    """Signal to sync User changes to Neo4j"""
    try:
        transaction.on_commit(lambda: UserNode.create_or_update_from_django(instance))
    except Exception as e:
        logger.error(f"Error syncing user {instance.id} to Neo4j: {str(e)}", exc_info=True)

@receiver(post_delete, sender=User)
def remove_neo4j_user(sender, instance, **kwargs):
    """Signal to remove Neo4j user when Django user is deleted"""
    try:
        node = UserNode.nodes.get(user_id=str(instance.id))
        # Use elementId() instead of id()
        node.cypher("MATCH (n) WHERE elementId(n)=$self DETACH DELETE n")
    except UserNode.DoesNotExist:
        logger.warning(f"Neo4j node for user {instance.id} not found")
    except Exception as e:
        logger.error(f"Error deleting user {instance.id} from Neo4j: {str(e)}", exc_info=True)