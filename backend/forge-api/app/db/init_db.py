"""Create all tables from models. Run before seeding."""
from app.db.session import engine, Base

# Import all models so Base knows about them
import app.models  # noqa: F401


def init_db():
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    init_db()
    print("Database tables created.")
