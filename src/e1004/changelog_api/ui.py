from uuid import UUID

from flask import Blueprint, render_template, request

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

    return render_template(
        "index.html",
        versions=versions_page.versions,
        previous_token=versions_page.prev_token,
        next_token=versions_page.next_token,
    )
