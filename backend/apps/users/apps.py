from django.apps import AppConfig


class UsersConfig(AppConfig):
    name = "apps.users"

    def ready(self):
        # ensure signal receivers are loaded
        import apps.users.models  # noqa F401
