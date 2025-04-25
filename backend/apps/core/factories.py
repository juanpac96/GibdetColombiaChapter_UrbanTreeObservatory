import uuid
import factory
from datetime import datetime


class BaseFactory(factory.django.DjangoModelFactory):
    """Base factory for models inheriting from BaseModel."""

    uuid = factory.LazyFunction(uuid.uuid4)
    created_at = factory.LazyFunction(datetime.now)
    updated_at = factory.LazyFunction(datetime.now)
