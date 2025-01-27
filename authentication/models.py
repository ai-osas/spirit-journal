from django.contrib.auth.models import AbstractUser
from django.db import models
from neomodel import (
    StructuredNode, StringProperty, RelationshipTo,
    RelationshipFrom, DateTimeProperty, IntegerProperty,
    JSONProperty, UniqueIdProperty
)

class User(AbstractUser):
    """Extended User model stored in PostgreSQL"""
    is_premium = models.BooleanField(default=False)
    premium_until = models.DateTimeField(null=True, blank=True)
    profile_image = models.URLField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    google_id = models.CharField(max_length=255, null=True, blank=True)
    
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        blank=True,
        verbose_name='groups',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_set',
        blank=True,
        verbose_name='user permissions',
    )

    class Meta:
        db_table = 'users'

class UserNode(StructuredNode):
    """User representation in Neo4j for graph relationships"""
    # Use UniqueIdProperty for internal Neo4j ID management
    uid = UniqueIdProperty()
    user_id = StringProperty(unique_index=True, required=True)
    username = StringProperty(index=True)
    email = StringProperty(index=True)
    created_at = DateTimeProperty(default_now=True)
    metadata = JSONProperty(default={})


    follows = RelationshipTo('UserNode', 'FOLLOWS')

    @classmethod
    def create_or_update_from_django(cls, django_user):
        """Create or update Neo4j node from Django user"""
        props = {
            'username': django_user.username,
            'email': django_user.email,
            'metadata': {
                'is_premium': django_user.is_premium,
                'date_joined': django_user.date_joined.isoformat()
            }
        }
        
        try:
            user_node = cls.nodes.get(user_id=str(django_user.id))
            # Update existing node
            for key, value in props.items():
                setattr(user_node, key, value)
            user_node.save()
            return user_node, False
        except cls.DoesNotExist:
            # Create new node
            props['user_id'] = str(django_user.id)
            user_node = cls(**props)
            user_node.save()
            return user_node, True