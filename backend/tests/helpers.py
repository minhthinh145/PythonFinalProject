"""
Test Helpers - Wrappers and utilities for tests
"""

class AuthenticatedUser:
    """
    Wrapper for Users model to satisfy DRF authentication.
    
    DRF requires user.is_authenticated property which the scaffolded
    Users model from DB doesn't have. This wrapper adds it without
    modifying the original model.
    
    Usage:
        from tests.helpers import AuthenticatedUser
        
        user = Users.objects.get(...)
        auth_user = AuthenticatedUser(user)
        client.force_authenticate(user=auth_user)
    """
    def __init__(self, user):
        self._user = user
        # Copy common attributes
        self.id = user.id
        self.pk = user.id
        
    @property
    def is_authenticated(self):
        return True
    
    @property 
    def is_anonymous(self):
        return False
    
    @property
    def is_active(self):
        return True
    
    def __getattr__(self, name):
        """Proxy all other attributes to the wrapped user"""
        return getattr(self._user, name)
    
    def __str__(self):
        return str(self._user)
