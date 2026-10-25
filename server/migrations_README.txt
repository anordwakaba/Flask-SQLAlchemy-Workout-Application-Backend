Run Flask-Migrate commands from this directory after activating the project environment:
flask --app app db init
flask --app app db migrate -m 'create workout tables'
flask --app app db upgrade
