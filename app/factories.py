"""Generic Factories."""
import factory
import factory.fuzzy

from django.contrib.auth.models import Group, User


class UserFactory(factory.django.DjangoModelFactory):
    """User Factory."""

    class Meta:
        model = User

    first_name = factory.fuzzy.FuzzyText()
    username = factory.Sequence(lambda n: 'person{0}'.format(n))


class GroupFactory(factory.django.DjangoModelFactory):
    """Group Factory."""

    class Meta:
        model = Group
