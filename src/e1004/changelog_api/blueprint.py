from uuid import UUID

from flask import Blueprint, request
from realerikrani.flaskapierr import Error, ErrorGroup
from realerikrani.project import bearer_extractor

from . import service
from .error import (
    ChangeBodyInvalidError,
    ChangeKindInvalidError,
    ChangeNotFoundError,
    VersionCannotBeDeletedError,
    VersionCannotBeReleasedError,
    VersionNotFoundError,
    VersionNumberInvalidError,
    VersionReleasedAtError,
    VersionReleasedError,
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


def to_released_at(req: dict) -> str:
    try:
        return str(req["released_at"])
    except KeyError:
        raise ErrorGroup(
            "400", [Error("released at missing", "VALUE_MISSING")]
        ) from None


@version.route("/<version_number>", methods=["PATCH"])
def release_version(version_number: str):
    key = bearer_extractor.protect()
    released_at = to_released_at(dict(request.json))  # type: ignore[arg-type]
    try:
        version = service.release_version(version_number, key.project_id, released_at)
    except VersionNumberInvalidError as invalid:
        raise ErrorGroup("400", [Error(invalid.message, invalid.code)]) from None
    except VersionNotFoundError as nf:
        raise ErrorGroup("404", [Error(nf.message, nf.code)]) from None
    except VersionCannotBeReleasedError as br:
        raise ErrorGroup("400", [Error(br.message, br.code)]) from None
    except VersionReleasedAtError as ra:
        raise ErrorGroup("400", [Error(ra.message, ra.code)]) from None
    return {"version": version}


@version.route("", methods=["GET"])
def read_versions():
    key = bearer_extractor.protect()
    page_size = request.args.get("page_size", type=int, default=5)
    page_token = request.args.get("page_token", default=None)
    version_page = service.read_versions(key.project_id, page_size, page_token)
    return {
        "versions": version_page.versions,
        "previous_token": version_page.prev_token,
        "next_token": version_page.next_token,
    }


def to_kind(req: dict) -> str:
    try:
        return str(req["kind"])
    except KeyError:
        raise Error("kind missing", "VALUE_MISSING") from None


def to_body(req: dict) -> str:
    try:
        return str(req["body"])
    except KeyError:
        raise Error("body missing", "VALUE_MISSING") from None


@version.route("/<version_number>/changes", methods=["POST"])
def create_change(version_number: str):
    key = bearer_extractor.protect()
    payload = dict(request.json)  # type: ignore[arg-type]
    errors = []
    try:
        kind = to_kind(payload)
    except Error as e:
        errors.append(e)

    try:
        body = to_body(payload)
    except Error as e:
        errors.append(e)

    if errors:
        raise ErrorGroup("400", errors)

    try:
        change = service.create_change(version_number, key.project_id, kind, body)
    except (
        ChangeKindInvalidError,
        ChangeBodyInvalidError,
        VersionNumberInvalidError,
    ) as e:
        raise ErrorGroup("400", [Error(e.message, e.code)]) from None
    return {"change": change}, 201


@version.route("/<version_number>/changes/<uuid:change_id>", methods=["DELETE"])
def delete_change(version_number: str, change_id: UUID):
    key = bearer_extractor.protect()
    try:
        change = service.delete_change(version_number, change_id, key.project_id)
    except (VersionNumberInvalidError, VersionReleasedError) as v:
        raise ErrorGroup("400", [Error(v.message, v.code)]) from None
    except (VersionNotFoundError, ChangeNotFoundError) as n:
        raise ErrorGroup("404", [Error(n.message, n.code)]) from None
    return {"change": change}


@version.route("/<version_number>/changes", methods=["GET"])
def read_changes_for_version(version_number: str):
    key = bearer_extractor.protect()
    try:
        changes = service.read_changes_for_version(version_number, key.project_id)
    except VersionNumberInvalidError as n:
        raise ErrorGroup("400", [Error(n.message, n.code)]) from None
    except VersionNotFoundError as v:
        raise ErrorGroup("404", [Error(v.message, v.code)]) from None
    return {"changes": changes}


@version.route("/<version_number>/changes/<uuid:change_id>", methods=["PATCH"])
def move_change_to_other_version(version_number: str, change_id: UUID): ...
