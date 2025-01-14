from app.database import Session, UserModel

def seed_demo_data():
    session = Session()
    user = UserModel(username="demo_user", email="demo@example.com", password_hash="hashed_password")
    admin = UserModel(username="admin", email="admin@example.com", password_hash="hashed_admin_password")
    session.add_all([user, admin])
    session.commit()
    print("Demo data added.")