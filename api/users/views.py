from .models import User, UserType
from rest_utils import create_viewset

users_viewset = create_viewset(User, UserType)
