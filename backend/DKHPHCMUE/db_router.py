"""
Database Router để tách riêng Django internal tables và app tables
"""
import sys

class DjangoInternalRouter:
    """
    Router để:
    - Django internal apps (auth, admin, sessions, etc.) -> SQLite local (default)
    - App models của bạn -> Neon PostgreSQL (neon)
    """
    
    django_apps = {
        'admin',
        'auth',
        'contenttypes',
        'sessions',
        'messages',
    }
    
    def db_for_read(self, model, **hints):
        """Đọc từ database nào"""
        if model._meta.app_label in self.django_apps:
            return 'default'  # SQLite
        return 'neon'  # PostgreSQL trên Neon
    
    def db_for_write(self, model, **hints):
        """Ghi vào database nào"""
        if model._meta.app_label in self.django_apps:
            return 'default'  # SQLite
        return 'neon'  # PostgreSQL trên Neon
    
    def allow_relation(self, obj1, obj2, **hints):
        """Cho phép relation giữa các models"""
        db_set = {'default', 'neon'}
        if obj1._state.db in db_set and obj2._state.db in db_set:
            return True
        return None
    
    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """
        Quyết định migrate vào database nào
        """
        # In test mode, allow migration for both databases independently
        # to avoid circular dependency
        if 'pytest' in sys.modules or 'test' in sys.argv:
            if app_label in self.django_apps:
                return db == 'default'
            return db == 'neon'
        
        if app_label in self.django_apps:
            # Django apps chỉ migrate vào SQLite
            return db == 'default'
        else:
            # App của bạn chỉ migrate vào Neon
            return db == 'neon'
