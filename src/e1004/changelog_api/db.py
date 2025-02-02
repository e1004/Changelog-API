CREATE_TABLES = """
CREATE TABLE IF NOT EXISTS version (
    project_id TEXT NOT NULL CHECK(
        length("project_id") = 36
    ),
    major INTEGER NOT NULL,
    minor INTEGER NOT NULL,
    patch INTEGER NOT NULL,
    id TEXT NOT NULL CHECK(
        length("id") = 36
    ),
    created_at INTEGER NOT NULL,
    released_at INTEGER,
    FOREIGN KEY(project_id) REFERENCES project(id) ON DELETE CASCADE,
    PRIMARY KEY(id) ON CONFLICT FAIL,
    UNIQUE(project_id, major, minor, patch)
) WITHOUT ROWID;

CREATE INDEX idx_version_project_id_major_minor_patch_desc
ON version (project_id, major DESC, minor DESC, patch DESC);

CREATE INDEX idx_version_project_id_major_minor_patch_asc
ON version (project_id, major ASC, minor ASC, patch ASC);

CREATE TABLE IF NOT EXISTS change (
    id TEXT NOT NULL CHECK(
        length("id") = 36
    ),
    version_id TEXT NOT NULL CHECK(
        length("version_id") = 36
    ),
    body TEXT NOT NULL CHECK(
        length("body") <= 1000
        AND length("body") >= 1
    ),
    kind TEXT NOT NULL CHECK(
        "kind" in (
            "added",
            "changed",
            "deprecated",
            "removed",
            "fixed",
            "security"
        )
    ),
    author TEXT NOT NULL CHECK(
        length("author") <= 30
        AND length("author") >= 1
    ),
    FOREIGN KEY(version_id) REFERENCES version(id) ON DELETE CASCADE,
    PRIMARY KEY(id) ON CONFLICT FAIL
) WITHOUT ROWID;

CREATE INDEX idx_change_version_id_kind
ON change (version_id, kind);

CREATE INDEX idx_change_id_version_id
ON change (id, version_id);
"""
