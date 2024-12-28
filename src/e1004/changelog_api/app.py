from flask import Flask
from realerikrani.project import register_project

from e1004.changelog_api.blueprint import version


def create() -> Flask:
    app = register_project(Flask("changelog_api"))
    app.register_blueprint(version, url_prefix="/versions")
    return app
