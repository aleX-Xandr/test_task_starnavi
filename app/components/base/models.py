from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

from app.components.accounts.models import Account
from app.components.auth.models import Auth
