if __name__ == "__main__":
    from app.demo_data import seed_demo_data

    print("Initializing demo data...")
    seed_demo_data()
    print("Starting REST API...")
    from app.api import app
    app.run(debug=True)