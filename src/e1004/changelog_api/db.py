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
"""
