from flask import Blueprint

version = Blueprint("version_controller", __name__)


@version.route("", methods=["POST"])
def create_version():
    version = "1.0.0"
    return {"version": version}, 201
