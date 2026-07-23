"""Step 2 operators for B-Dental."""

from __future__ import annotations

import bpy

from . import alignment, occlusion_validation, properties, scene_utils, step_two_session


def _state(context):
    return context.scene.bdental_workflow


def _messages(state, summary="", errors=(), warnings=()):
    state.step_2_summary = summary
    state.step_2_errors = "\n".join(errors)
    state.step_2_warnings = "\n".join(warnings)
    state.warning_acknowledged = False
    state.review_confirmed = False


def _clear_metrics(state):
    state.registration_iterations = 0
    state.registration_inlier_count = 0
    state.registration_inlier_ratio = 0.0
    state.registration_rmse = 0.0
    state.registration_median_distance = 0.0
    state.registration_translation_delta = 0.0
    state.registration_rotation_delta = 0.0
    state.bilateral_translation_disagreement = 0.0
    state.bilateral_rotation_disagreement = 0.0


def _store_metrics(state, result):
    state.registration_iterations = result.iterations
    state.registration_inlier_count = result.inlier_count
    state.registration_inlier_ratio = result.inlier_ratio
    state.registration_rmse = result.rmse
    state.registration_median_distance = result.median_distance
    state.registration_translation_delta = result.translation_delta
    state.registration_rotation_delta = result.rotation_delta


def _ready(context):
    return bool(
        context.scene
        and hasattr(context.scene, "bdental_workflow")
        and context.scene.bdental_workflow.step_1_valid
    )


def _select_lower(context, lower):
    for obj in context.view_layer.objects:
        try:
            obj.select_set(False)
        except (ReferenceError, RuntimeError):
            continue
    lower.hide_viewport = False
    lower.select_set(True)
    context.view_layer.objects.active = lower


class BDENTAL_OT_analyze_step_two(bpy.types.Operator):
    bl_idname = "bdental.analyze_step_two"
    bl_label = "Analyze Imported Relationship"
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return _ready(context)

    def execute(self, context):
        state = _state(context)
        matrices = {
            role: obj.matrix_world.copy()
            for role in properties.SCAN_ROLES
            if (obj := scene_utils.get_role_object(state, role))
        }
        result = occlusion_validation.analyze_imported_relationship(state)
        for role, matrix in matrices.items():
            obj = scene_utils.get_role_object(state, role)
            if obj:
                obj.matrix_world = matrix

        state.alignment_session_active = False
        state.step_2_valid = False
        state.step_2_status = result.status
        state.alignment_mode = "IMPORTED"
        state.candidate_applied = result.ok
        _clear_metrics(state)
        _messages(state, result.summary, result.errors, result.warnings)
        return {"FINISHED"}


class BDENTAL_OT_complete_step_two_na(bpy.types.Operator):
    bl_idname = "bdental.complete_step_two_na"
    bl_label = "Complete as Not Applicable"

    @classmethod
    def poll(cls, context):
        return (
            _ready(context)
            and context.scene.bdental_workflow.scan_configuration == "SINGLE_ARCH"
        )

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)

    def execute(self, context):
        state = _state(context)
        state.step_2_status = "NOT_APPLICABLE"
        state.step_2_valid = True
        state.verification_method = "NOT_APPLICABLE"
        _messages(state, "Step 2 completed as not applicable for a single-arch case.")
        return {"FINISHED"}


class BDENTAL_OT_start_step_two_session(bpy.types.Operator):
    bl_idname = "bdental.start_step_two_session"
    bl_label = "Start Alignment Session"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        if not _ready(context):
            return False
        state = context.scene.bdental_workflow
        return (
            not state.alignment_session_active
            and state.alignment_mode in {"MANUAL", "BITE_GUIDED"}
        )

    def execute(self, context):
        state = _state(context)
        if state.alignment_mode == "IMPORTED":
            self.report(
                {"ERROR"},
                "Imported alignment does not use a session. Analyze and verify it directly.",
            )
            return {"CANCELLED"}

        result = occlusion_validation.validate_step_two_preconditions(state)
        if not result.ok or state.scan_configuration == "SINGLE_ARCH":
            _messages(state, result.summary, result.errors, result.warnings)
            return {"CANCELLED"}

        step_two_session.snapshot_session(state)
        state.alignment_session_active = True
        state.step_2_status = "ALIGNING"
        state.step_2_valid = False
        state.candidate_applied = False
        _clear_metrics(state)
        _messages(state, "Alignment session started. Upper Jaw remains fixed.")

        if state.alignment_mode == "MANUAL":
            lower = scene_utils.get_role_object(state, "LOWER_JAW")
            if lower:
                _select_lower(context, lower)
        return {"FINISHED"}


class BDENTAL_OT_reset_step_two_preview(bpy.types.Operator):
    bl_idname = "bdental.reset_step_two_preview"
    bl_label = "Reset Preview"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return _ready(context) and context.scene.bdental_workflow.alignment_session_active

    def execute(self, context):
        state = _state(context)
        step_two_session.restore_session(state)
        state.step_2_status = "ALIGNING"
        state.candidate_applied = False
        _clear_metrics(state)
        _messages(state, "Preview restored to the session start.")
        return {"FINISHED"}


class BDENTAL_OT_cancel_step_two_session(bpy.types.Operator):
    bl_idname = "bdental.cancel_step_two_session"
    bl_label = "Cancel Alignment"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return _ready(context) and context.scene.bdental_workflow.alignment_session_active

    def execute(self, context):
        state = _state(context)
        step_two_session.restore_session(state)
        state.alignment_session_active = False
        state.step_2_status = "NOT_STARTED"
        state.candidate_applied = False
        _clear_metrics(state)
        _messages(state, "Alignment cancelled and original matrices restored.")
        return {"FINISHED"}


class BDENTAL_OT_capture_manual_step_two(bpy.types.Operator):
    bl_idname = "bdental.capture_manual_step_two"
    bl_label = "Capture Manual Candidate"

    @classmethod
    def poll(cls, context):
        state = context.scene.bdental_workflow if context.scene else None
        return bool(
            state
            and state.alignment_session_active
            and state.alignment_mode == "MANUAL"
        )

    def execute(self, context):
        state = _state(context)
        upper = scene_utils.get_role_object(state, "UPPER_JAW")
        lower = scene_utils.get_role_object(state, "LOWER_JAW")
        start_upper = step_two_session.matrix_from_string(state.session_upper_matrix)
        errors = []

        if not upper or not lower or start_upper is None:
            errors.append("Session matrices are unavailable.")
        else:
            translation, rotation = occlusion_validation.matrix_distance(
                start_upper, upper.matrix_world
            )
            if translation > 1.0e-5 or rotation > 1.0e-3:
                errors.append("Upper Jaw moved. Reset and move only the Lower Jaw.")
            if occlusion_validation.matrix_uniform_scale(lower.matrix_world) is None:
                errors.append(
                    "Lower Jaw contains non-uniform scale, shear, reflection, or invalid values. Use move and rotate only."
                )

        if errors:
            _messages(state, "Manual candidate is invalid.", tuple(errors))
            return {"CANCELLED"}

        state.step_2_status = "CANDIDATE"
        _messages(state, "Manual candidate captured. Run verification checks.")
        return {"FINISHED"}


def _sample(context, obj):
    return alignment.sample_object_points(obj, context.evaluated_depsgraph_get())


def _run_registration(context, moving, target_points):
    return alignment.run_icp(_sample(context, moving), target_points)


class BDENTAL_OT_run_bite_step_two(bpy.types.Operator):
    bl_idname = "bdental.run_bite_step_two"
    bl_label = "Run Bite-Guided Registration"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        state = context.scene.bdental_workflow if context.scene else None
        return bool(
            state
            and state.alignment_session_active
            and state.alignment_mode == "BITE_GUIDED"
        )

    def execute(self, context):
        state = _state(context)
        upper = scene_utils.get_role_object(state, "UPPER_JAW")
        lower = scene_utils.get_role_object(state, "LOWER_JAW")
        roles = {
            "RIGHT": ("RIGHT_BITE",),
            "LEFT": ("LEFT_BITE",),
            "BOTH": ("RIGHT_BITE", "LEFT_BITE"),
        }[state.bite_source]
        bites = [scene_utils.get_role_object(state, role) for role in roles]

        if not upper or not lower or any(not bite for bite in bites):
            _messages(
                state,
                "Selected bite input is missing.",
                ("Import the selected bite scan and retry.",),
            )
            return {"CANCELLED"}

        step_two_session.restore_session(state)
        safe = {obj.name: obj.matrix_world.copy() for obj in (upper, lower, *bites)}
        warnings = []
        diagnostics = []

        try:
            target_groups = []
            upper_points = _sample(context, upper)
            for bite in bites:
                result = _run_registration(context, bite, upper_points)
                if not result.ok:
                    raise RuntimeError(result.errors[0])

                bite.matrix_world = result.transform @ bite.matrix_world
                target_points = _sample(context, bite)
                target_groups.append(target_points)

                diagnostic = _run_registration(context, lower, target_points)
                if diagnostic.ok:
                    diagnostics.append(diagnostic.transform @ lower.matrix_world)
                warnings.extend(result.warnings)

            lower_result = _run_registration(
                context,
                lower,
                alignment.combine_points(*target_groups),
            )
            if not lower_result.ok:
                raise RuntimeError(lower_result.errors[0])

            lower.matrix_world = lower_result.transform @ lower.matrix_world
            _store_metrics(state, lower_result)
            warnings.extend(lower_result.warnings)

            if len(diagnostics) == 2:
                disagreement = alignment.transform_disagreement(
                    diagnostics[0], diagnostics[1]
                )
                state.bilateral_translation_disagreement = disagreement.translation
                state.bilateral_rotation_disagreement = disagreement.rotation
                if (
                    disagreement.translation > 0.003
                    or disagreement.rotation > 0.0872665
                ):
                    warnings.append(
                        "Right and left bite results disagree; inspect both sides carefully."
                    )

            state.step_2_status = "CANDIDATE"
            _messages(
                state,
                "Bite-guided candidate created. Run verification checks.",
                warnings=tuple(dict.fromkeys(warnings)),
            )
            return {"FINISHED"}
        except Exception as exc:
            for obj in (upper, lower, *bites):
                obj.matrix_world = safe[obj.name]
            state.step_2_status = "ERROR"
            _messages(state, "Bite-guided registration failed.", (str(exc),))
            return {"CANCELLED"}


class BDENTAL_OT_apply_step_two_candidate(bpy.types.Operator):
    bl_idname = "bdental.apply_step_two_candidate"
    bl_label = "Apply Candidate"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        state = context.scene.bdental_workflow if context.scene else None
        return bool(
            state
            and state.alignment_session_active
            and state.step_2_status == "CANDIDATE"
        )

    def execute(self, context):
        state = _state(context)
        state.alignment_session_active = False
        state.candidate_applied = True
        state.step_2_valid = False
        _messages(
            state,
            "Candidate applied. Verification and approval are still required.",
        )
        return {"FINISHED"}


class BDENTAL_OT_verify_step_two(bpy.types.Operator):
    bl_idname = "bdental.verify_step_two"
    bl_label = "Run Verification Checks"

    @classmethod
    def poll(cls, context):
        return _ready(context)

    def execute(self, context):
        state = _state(context)
        result = occlusion_validation.verify_candidate(state)
        state.step_2_status = result.status
        state.step_2_valid = False
        _messages(state, result.summary, result.errors, result.warnings)
        return {"FINISHED"}


class BDENTAL_OT_approve_step_two(bpy.types.Operator):
    bl_idname = "bdental.approve_step_two"
    bl_label = "Approve Occlusion"

    @classmethod
    def poll(cls, context):
        state = context.scene.bdental_workflow if context.scene else None
        return bool(
            state
            and state.step_2_status in {"CANDIDATE", "IMPORTED_CANDIDATE"}
            and state.review_confirmed
            and not state.step_2_errors
            and (not state.step_2_warnings or state.warning_acknowledged)
            and not state.alignment_session_active
        )

    def execute(self, context):
        state = _state(context)
        result = occlusion_validation.verify_candidate(state)
        if not result.ok or (result.warnings and not state.warning_acknowledged):
            _messages(state, result.summary, result.errors, result.warnings)
            return {"CANCELLED"}

        step_two_session.snapshot_approved(state)
        state.verification_method = state.alignment_mode
        state.step_2_status = "VERIFIED"
        state.step_2_valid = True
        _messages(
            state,
            f"Step 2 approved using {state.alignment_mode.replace('_', ' ').title()} mode.",
            warnings=result.warnings,
        )

        for role in ("RIGHT_BITE", "LEFT_BITE"):
            obj = scene_utils.get_role_object(state, role)
            if obj:
                obj.hide_viewport = True
        return {"FINISHED"}


class BDENTAL_OT_back_to_step_one_safe(bpy.types.Operator):
    bl_idname = "bdental.back_to_step_one_safe"
    bl_label = "Back to Step 1"
    bl_options = {"REGISTER", "UNDO"}

    def invoke(self, context, event):
        if _state(context).alignment_session_active:
            return context.window_manager.invoke_confirm(self, event)
        return self.execute(context)

    def execute(self, context):
        state = _state(context)
        if state.alignment_session_active:
            step_two_session.restore_session(state)
            state.alignment_session_active = False
        state.current_step = "STEP_1"
        return {"FINISHED"}


CLASSES = (
    BDENTAL_OT_analyze_step_two,
    BDENTAL_OT_complete_step_two_na,
    BDENTAL_OT_start_step_two_session,
    BDENTAL_OT_reset_step_two_preview,
    BDENTAL_OT_cancel_step_two_session,
    BDENTAL_OT_capture_manual_step_two,
    BDENTAL_OT_run_bite_step_two,
    BDENTAL_OT_apply_step_two_candidate,
    BDENTAL_OT_verify_step_two,
    BDENTAL_OT_approve_step_two,
    BDENTAL_OT_back_to_step_one_safe,
)
