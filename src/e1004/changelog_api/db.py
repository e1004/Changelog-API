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

CREATE TABLE IF NOT EXISTS change (
    id TEXT NOT NULL CHECK(
        length("id") = 36
    ),
    version_id TEXT NOT NULL CHECK(
        length("version_id") = 36
    ),
    body TEXT NOT NULL CHECK(
        length("body") <= 1000
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
    FOREIGN KEY(version_id) REFERENCES version(id) ON DELETE CASCADE,
    PRIMARY KEY(id) ON CONFLICT FAIL
) WITHOUT ROWID;
"""
