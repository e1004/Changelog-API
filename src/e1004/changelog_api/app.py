from datetime import date, datetime

from flask import Flask
from flask.json.provider import DefaultJSONProvider
from realerikrani.project import register_project

from e1004.changelog_api.blueprint import version


def create() -> Flask:
    app = register_project(Flask("changelog_api"))
    app.register_blueprint(version, url_prefix="/versions")
    app.json.default = (  # type: ignore[attr-defined]
        lambda obj: obj.isoformat()
        if isinstance(obj, datetime | date)
        else DefaultJSONProvider.default(obj)
    )
    return app
