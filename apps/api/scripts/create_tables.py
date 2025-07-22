from sqlalchemy import create_engine
from app.core.database import Base
import app.models.user
import app.models.post
import app.models.interaction
import app.models.notification

if __name__ == "__main__":
    # Use the postgres superuser for schema creation
    engine = create_engine("postgresql://postgres:iamgreatful@localhost:5432/grateful")
    print("Creating all tables as postgres...")
    Base.metadata.create_all(bind=engine)
    print("Done.") 