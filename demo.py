import os

os.environ["PROJECT_DATABASE_PATH"] = "./database.sqlite"

from e1004.changelog_api.app import create

if __name__ == "__main__":
    app = create()
    app.run(port=5000, debug=True)
