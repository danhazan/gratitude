import os
import sys
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context

# Import your models and Base
from app.core.database import Base
from app.models.user import User
from app.models.post import Post
from app.models.interaction import Interaction
from app.models.notification import Notification

# Set target_metadata to Base.metadata
print("DEBUG: Current working directory:", os.getcwd())
print("DEBUG: Python path:", sys.path)
print("DEBUG: Available tables:", list(Base.metadata.tables.keys()))
target_metadata = Base.metadata 