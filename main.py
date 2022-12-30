from app import create_app, db

app = create_app()

if __name__ == '__main__':
    with app.app_context():
        #db.create_all()
        #create_user()
        # disable debug mode when deploy on server
        # NO GIT push DB
        app.run(debug=True)