from uuid import UUID

from flask import Blueprint, render_template, request
from realerikrani.project import project_repo

from e1004.changelog_api import service

ui = Blueprint(
    "ui_controller", __name__, template_folder="templates", static_folder="assets"
)


@ui.route("/<uuid:project_id>", methods=["GET", "POST"])
def index(project_id: UUID):  # noqa: ANN201
    token = None
    if request.method == "POST":
        if "load_next" in request.form:
            token = request.form.get("next", None)
        elif "load_previous" in request.form:
            token = request.form.get("previous", None)
    versions_page = service.read_versions(project_id, 5, token)
    project_name = project_repo.read_project(project_id).name

    return render_template(
        "index.html",
        versions=versions_page.versions,
        previous_token=versions_page.prev_token,
        next_token=versions_page.next_token,
        project_id=project_id,
        project_name=project_name,
    )


@ui.route("/<uuid:project_id>/<version_number>", methods=["GET"])
def changes(project_id: UUID, version_number: str):  # noqa: ANN201
    c = service.read_changes_for_version(version_number, project_id)
    return render_template("changes.html", changes=c)
