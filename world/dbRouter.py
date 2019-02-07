class WorldDatabaseRouter(object):
    """
    Determine how to route database calls for an app's models
    All other models will be routed to the next router in the DATABASE_ROUTERS setting if applicable,
    or otherwise to the default database.
    """

    def db_for_read(self, model, **hints):
        """Send all read operations on world app models to `world`."""
        if model._meta.app_label == 'world':
            return 'world'
        return None

    def db_for_write(self, model, **hints):
        """Send all write operations on world app models to `world`."""
        if model._meta.app_label == 'world':
            return 'world'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """Determine if relationship is allowed between two objects."""

        # Allow any relation between two models that are both in the world app.
        if obj1._meta.app_label == 'world' and obj2._meta.app_label == 'world':
            return True
        # No opinion if neither object is in the world app (defer to default or other routers).
        elif 'world' not in [obj1._meta.app_label, obj2._meta.app_label]:
            return None

        # Block relationship if one object is in the world app and the other isn't.
        return False

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """Ensure that the world app's models get created on the right database."""
        if app_label == 'world':
            # The world app should be migrated only on the world database.
            return db == 'world'
        elif db == 'world':
            # Ensure that all other apps don't get migrated on the world database.
            return False

        # No opinion for all other scenarios
        return None

    def allow_syncdb(self, db, model):
        "Make sure the world app only appears on the 'world' db"
        if db == 'world':
            return model._meta.app_label == 'world'
        elif model._meta.app_label == 'world':
            return False
        return None
