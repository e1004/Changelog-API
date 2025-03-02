from uuid import UUID

from flask import Blueprint, current_app, render_template, request, url_for
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
    versions_page = service.read_versions(project_id, 4, token)
    project_name = project_repo.read_project(project_id).name

    app_prefix_enabled = current_app.config["APP_PREFIX_ENABLED"]
    styles_location = url_for("ui_controller.static", filename="css/styles.css")
    script_location = url_for("ui_controller.static", filename="script.js")
    link_location = url_for("ui_controller.static", filename="icons/link.svg")
    if app_prefix_enabled:
        prefix = "app"
        styles_location = f"{prefix}{styles_location}"
        script_location = f"{prefix}{script_location}"
        link_location = f"{prefix}{link_location}"

    return render_template(
        "index.html",
        versions=versions_page.versions,
        previous_token=versions_page.prev_token,
        next_token=versions_page.next_token,
        project_id=project_id,
        project_name=project_name,
        styles_location=styles_location,
        script_location=script_location,
        link_location=link_location,
    )


@ui.route("/<uuid:project_id>/<version_number>", methods=["GET"])
def changes(project_id: UUID, version_number: str):  # noqa: ANN201
    c = service.read_changes_for_version(version_number, project_id)

    app_prefix_enabled = current_app.config["APP_PREFIX_ENABLED"]
    styles_location = url_for("ui_controller.static", filename="css/styles.css")
    if app_prefix_enabled:
        styles_location = "app" + styles_location

    return render_template(
        "changes.html",
        changes=c,
        version_number=version_number,
        styles_location=styles_location,
    )
