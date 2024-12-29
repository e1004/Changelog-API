from flask import Blueprint
from realerikrani.flaskapierr import Error, ErrorGroup

from . import service
from .error import VersionNumberInvalidError

version = Blueprint("version_controller", __name__)


@version.route("", methods=["POST"])
def create_version():
    number = "1.0.0"
    try:
        version = service.create_version(number)
    except VersionNumberInvalidError as invalid:
        raise ErrorGroup("400", [Error(invalid.message, invalid.code)]) from None
    return {"version": version}, 201
