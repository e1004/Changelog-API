from flask import Blueprint, request
from realerikrani.flaskapierr import Error, ErrorGroup
from realerikrani.project import bearer_extractor

from . import service
from .error import (
    VersionCannotBeDeletedError,
    VersionNotFoundError,
    VersionNumberInvalidError,
)

version = Blueprint("version_controller", __name__)


def to_version_number(req: dict) -> str:
    try:
        return str(req["version_number"])
    except KeyError:
        raise ErrorGroup(
            "400", [Error("version number missing", "VALUE_MISSING")]
        ) from None


@version.route("", methods=["POST"])
def create_version():
    key = bearer_extractor.protect()
    number = to_version_number(dict(request.json))  # type: ignore[arg-type]
    try:
        version = service.create_version(number, key.project_id)
    except VersionNumberInvalidError as invalid:
        raise ErrorGroup("400", [Error(invalid.message, invalid.code)]) from None
    return {"version": version}, 201


@version.route("/<version_number>", methods=["DELETE"])
def delete_version(version_number: str):
    key = bearer_extractor.protect()
    try:
        version = service.delete_version(version_number, key.project_id)
    except VersionNumberInvalidError as invalid:
        raise ErrorGroup("400", [Error(invalid.message, invalid.code)]) from None
    except VersionCannotBeDeletedError as cbd:
        raise ErrorGroup("400", [Error(cbd.message, cbd.code)]) from None
    except VersionNotFoundError as nf:
        raise ErrorGroup("404", [Error(nf.message, nf.code)]) from None
    return {"version": version}
