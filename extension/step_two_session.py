"""Reversible matrix-session helpers for B-Dental Step 2."""

from __future__ import annotations

from mathutils import Matrix

from . import alignment, scene_utils


def matrix_to_string(matrix: Matrix) -> str:
    return ";".join(",".join(f"{float(value):.17g}" for value in row) for row in matrix)


def matrix_from_string(value: str) -> Matrix | None:
    if not value:
        return None
    try:
        rows = [[float(item) for item in row.split(",")] for row in value.split(";")]
        if len(rows) != 4 or any(len(row) != 4 for row in rows):
            return None
        matrix = Matrix(rows)
    except (TypeError, ValueError):
        return None
    return matrix if alignment.matrix_is_finite(matrix) else None


def snapshot_role(state, role: str, attribute: str) -> None:
    obj = scene_utils.get_role_object(state, role)
    setattr(state, attribute, matrix_to_string(obj.matrix_world.copy()) if obj else "")


def restore_role(state, role: str, attribute: str) -> None:
    obj = scene_utils.get_role_object(state, role)
    matrix = matrix_from_string(getattr(state, attribute))
    if obj is not None and matrix is not None:
        obj.matrix_world = matrix


def snapshot_session(state) -> None:
    snapshot_role(state, "UPPER_JAW", "session_upper_matrix")
    snapshot_role(state, "LOWER_JAW", "session_lower_matrix")
    snapshot_role(state, "RIGHT_BITE", "session_right_bite_matrix")
    snapshot_role(state, "LEFT_BITE", "session_left_bite_matrix")


def restore_session(state) -> None:
    restore_role(state, "UPPER_JAW", "session_upper_matrix")
    restore_role(state, "LOWER_JAW", "session_lower_matrix")
    restore_role(state, "RIGHT_BITE", "session_right_bite_matrix")
    restore_role(state, "LEFT_BITE", "session_left_bite_matrix")


def snapshot_approved(state) -> None:
    snapshot_role(state, "UPPER_JAW", "approved_upper_matrix")
    snapshot_role(state, "LOWER_JAW", "approved_lower_matrix")
    snapshot_role(state, "RIGHT_BITE", "approved_right_bite_matrix")
    snapshot_role(state, "LEFT_BITE", "approved_left_bite_matrix")
