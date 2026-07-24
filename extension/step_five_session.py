"""Persistent Step 5 state, migration, correction sessions, and invalidation."""
from __future__ import annotations
import json
from collections.abc import Iterable
import bpy
from bpy.props import BoolProperty, EnumProperty, FloatProperty, IntProperty, PointerProperty, StringProperty
from mathutils import Vector
from . import crown_bottom_candidates, properties, restoration_utils, step_four_session, step_five_validation

STEP_FIVE_STATUS_ITEMS=(("READY_TO_GENERATE","Ready to Generate","Generate preparation die and crown bottom"),("GENERATING","Generating","Generation is running"),("GENERATED","Generated","Candidate ready for validation"),("CORRECTING","Correcting","Constrained correction active"),("VALIDATED","Validated","Candidate passed validation"),("VERIFIED","Verified","Step 5 approved"),("UPSTREAM_INVALID","Upstream Invalid","Step 4 must be approved"),("ERROR","Error","Blocking errors"))
AGGREGATE_STEP_FIVE_STATUS_ITEMS=(("NOT_STARTED","Not Started","Step 5 has not started"),*STEP_FIVE_STATUS_ITEMS)
DEFAULT_MARGINAL_GAP=.00002;DEFAULT_CEMENT_GAP=.00005;DEFAULT_SPACER_START=.001;DEFAULT_AXIAL_RELIEF=.00002;DEFAULT_OCCLUSAL_RELIEF=.00008;DEFAULT_SEAL_BAND_WIDTH=.00030;DEFAULT_BLOCKOUT_CLEARANCE=.00003;DEFAULT_SAMPLING_RESOLUTION=.00020;DEFAULT_SMOOTHING_STRENGTH=.35;DEFAULT_MAXIMUM_CANDIDATES=2;DEFAULT_MAXIMUM_ITERATIONS=8;DEFAULT_MAXIMUM_RUNTIME=15.;DEFAULT_CORRECTION_LIMIT=.00020

def clear_step_five_approval(r,preserve_snapshot=False):
 r.step_5_valid=False;r.step_5_review_confirmed=False;r.step_5_warning_acknowledged=False
 if not preserve_snapshot:r.approved_step_5_signature="";r.approved_candidate_id="";r.approved_settings_snapshot="";r.approved_metrics_snapshot=""

def invalidate_restoration(r,upstream=False,preserve_generated=True):
 r.step_5_correction_active=False;r.step_5_correction_snapshot="";clear_step_five_approval(r);r.step_5_generation_current=False
 if upstream:r.step_5_status="UPSTREAM_INVALID";r.step_5_summary="Step 5 was invalidated by an upstream workflow change."
 elif preserve_generated and crown_bottom_candidates.resolve_selected_candidate(r):r.step_5_status="GENERATED";r.step_5_summary="Step 5 results are stale. Regenerate before validation."
 else:r.step_5_status="READY_TO_GENERATE";r.step_5_summary="Generate the preparation die and crown-bottom candidates."
 r.step_5_errors="";r.step_5_warnings=""

def sync_step_five_state(state):
 items=tuple(state.restorations)
 if not items:state.step_5_status="NOT_STARTED";state.step_5_valid=False;return
 if not state.step_4_valid:state.step_5_status="UPSTREAM_INVALID";state.step_5_valid=False;return
 if any(x.step_5_correction_active for x in items):state.step_5_status="CORRECTING";state.step_5_valid=False;return
 if all(x.step_5_valid and x.step_5_status=="VERIFIED" for x in items):state.step_5_status="VERIFIED";state.step_5_valid=True;return
 active=restoration_utils.active_restoration(state);state.step_5_status=active.step_5_status if active else "NOT_STARTED";state.step_5_valid=False

def store_generation(r,result):
 clear_step_five_approval(r,preserve_snapshot=True);r.step_5_generation_current=True;r.step_5_generation_signature=result.dependency_signature;r.step_5_generation_id=result.generation_id;r.step_5_generation_duration=result.duration_seconds;r.step_5_generation_iterations=result.iterations;r.selected_candidate_id=result.selected_candidate_id;r.step_5_status="GENERATED";r.step_5_errors="";r.step_5_warnings="\n".join(result.warnings);r.step_5_summary=f"Generated {len(result.candidates)} bounded candidate(s); selected the highest-ranked accepted result."

def snapshot_approved(state,r):
 candidate=crown_bottom_candidates.resolve_selected_candidate(r);record=crown_bottom_candidates.record_for_id(r,r.selected_candidate_id)
 r.approved_candidate_id=r.selected_candidate_id;r.approved_step_5_signature=step_five_validation.approved_signature(state,r);r.approved_settings_snapshot=json.dumps(crown_bottom_candidates.settings_payload(r),sort_keys=True,separators=(",",":"));r.approved_metrics_snapshot=json.dumps(record.metrics if record else {},sort_keys=True,separators=(",",":"))
 if candidate:candidate[crown_bottom_candidates.META_MESH_SIGNATURE]=crown_bottom_candidates.object_mesh_signature(candidate)

def _coords(obj):return [[float(c) for c in v.co] for v in obj.data.vertices]
def _restore(obj,coords):
 if len(coords)!=len(obj.data.vertices):raise ValueError("Correction topology changed.")
 for vertex,value in zip(obj.data.vertices,coords):vertex.co=Vector(value[:3])
 obj.data.update()
def _payload(r):
 try:return json.loads(r.step_5_correction_snapshot)
 except Exception as exc:raise ValueError("The correction snapshot is unavailable or corrupt.") from exc

def start_correction(state,r):
 if r.step_5_correction_active:raise ValueError("A correction session is already active.")
 obj=crown_bottom_candidates.resolve_selected_candidate(r);record=crown_bottom_candidates.record_for_id(r,r.selected_candidate_id)
 if not obj or not record or not record.accepted:raise ValueError("Select an accepted current candidate first.")
 data={"candidate_id":r.selected_candidate_id,"coordinates":_coords(obj),"mesh_signature":str(obj.get(crown_bottom_candidates.META_MESH_SIGNATURE,"")),"status":r.step_5_status,"valid":bool(r.step_5_valid),"review":bool(r.step_5_review_confirmed),"ack":bool(r.step_5_warning_acknowledged),"approved_signature":r.approved_step_5_signature,"approved_id":r.approved_candidate_id,"summary":r.step_5_summary,"errors":r.step_5_errors,"warnings":r.step_5_warnings,"override":bool(r.step_5_override_used),"note":r.step_5_override_note}
 r.step_5_correction_snapshot=json.dumps(data,separators=(",",":"));r.step_5_correction_active=True;clear_step_five_approval(r);r.step_5_status="CORRECTING";r.step_5_summary="Reversible constrained correction session started.";sync_step_five_state(state);return obj

def _validate_correction(r,obj,data):
 original=data.get("coordinates",())
 if len(original)!=len(obj.data.vertices):raise ValueError("Candidate topology changed during correction.")
 moves=[(v.co-Vector(src[:3])).length for v,src in zip(obj.data.vertices,original)];maximum=max(moves,default=0.);limit=float(r.step_5_correction_limit)
 if maximum>limit+1e-9:raise ValueError(f"Correction displacement {maximum*1000:.3f} mm exceeds {limit*1000:.3f} mm.")
 boundary=tuple(int(x) for x in str(obj.get(crown_bottom_candidates.META_OUTER_LOOP,"")).split(",") if x);boundary_max=max((moves[i] for i in boundary if i<len(moves)),default=0.);boundary_limit=min(limit*.25,.00005)
 if boundary_max>boundary_limit+1e-9:raise ValueError("The protected margin boundary moved beyond its correction limit.")
 errors,_=crown_bottom_candidates.current_candidate_constraints(r)
 if errors:raise ValueError(errors[0])
 return maximum,boundary_max

def capture_correction(state,r):
 if not r.step_5_correction_active:raise ValueError("No correction session is active.")
 data=_payload(r);obj=crown_bottom_candidates.resolve_selected_candidate(r)
 if not obj or obj.get(crown_bottom_candidates.META_CANDIDATE_ID,"")!=data.get("candidate_id"):raise ValueError("The correction candidate changed.")
 maximum,boundary=_validate_correction(r,obj,data);obj[crown_bottom_candidates.META_MESH_SIGNATURE]=crown_bottom_candidates.object_mesh_signature(obj);r.step_5_override_used=True;r.step_5_override_note=f"Constrained correction captured; maximum displacement {maximum*1000:.3f} mm.";clear_step_five_approval(r);r.step_5_status="CORRECTING";sync_step_five_state(state);return maximum,boundary

def apply_correction(state,r):
 result=capture_correction(state,r);r.step_5_correction_active=False;r.step_5_correction_snapshot="";r.step_5_status="GENERATED";r.step_5_summary="Correction applied. Run Step 5 validation again.";sync_step_five_state(state);return result

def reset_correction(state,r):
 data=_payload(r);obj=crown_bottom_candidates.resolve_selected_candidate(r)
 if not obj:raise ValueError("The correction candidate is missing.")
 _restore(obj,data.get("coordinates",()));obj[crown_bottom_candidates.META_MESH_SIGNATURE]=data.get("mesh_signature","");r.step_5_override_used=bool(data.get("override",False));r.step_5_override_note=str(data.get("note",""));clear_step_five_approval(r);r.step_5_correction_active=True;r.step_5_status="CORRECTING";r.step_5_summary="Candidate restored to session start.";sync_step_five_state(state)

def cancel_correction(state,r):
 data=_payload(r);obj=crown_bottom_candidates.resolve_selected_candidate(r)
 if not obj:raise ValueError("The correction candidate is missing.")
 _restore(obj,data.get("coordinates",()));obj[crown_bottom_candidates.META_MESH_SIGNATURE]=data.get("mesh_signature","");r.step_5_correction_active=False;r.step_5_correction_snapshot="";r.step_5_status=str(data.get("status","GENERATED"));r.step_5_valid=bool(data.get("valid",False));r.step_5_review_confirmed=bool(data.get("review",False));r.step_5_warning_acknowledged=bool(data.get("ack",False));r.approved_step_5_signature=str(data.get("approved_signature",""));r.approved_candidate_id=str(data.get("approved_id",""));r.step_5_summary=str(data.get("summary",""));r.step_5_errors=str(data.get("errors",""));r.step_5_warnings=str(data.get("warnings",""));r.step_5_override_used=bool(data.get("override",False));r.step_5_override_note=str(data.get("note",""));sync_step_five_state(state)

def _setting_updated(r,context):
 state=context.scene.bdental_workflow if context and context.scene else None
 if not state or state.internal_update_lock:return
 invalidate_restoration(r,preserve_generated=True);r.step_5_summary="A Step 5 setting changed. Regenerate before validation.";sync_step_five_state(state)

def _inject_properties():
 workflow=properties.BDENTAL_PG_WorkflowState.__annotations__;workflow["current_step"]=EnumProperty(name="Current Step",items=(*properties.WORKFLOW_STEP_ITEMS,("STEP_4","Step 4","Define insertion axes and analyze preparations"),("STEP_5","Step 5","Generate preparation dies and crown bottoms")),default="STEP_1")
 workflow.setdefault("step_5_status",EnumProperty(name="Step 5 Status",items=AGGREGATE_STEP_FIVE_STATUS_ITEMS,default="NOT_STARTED"));workflow.setdefault("step_5_valid",BoolProperty(default=False));workflow.setdefault("step_5_summary",StringProperty(default=""));workflow.setdefault("step_5_errors",StringProperty(default=""));workflow.setdefault("step_5_warnings",StringProperty(default=""))
 a=properties.BDENTAL_PG_RestorationState.__annotations__
 for name,prop in {"step_5_status":EnumProperty(name="Step 5 Status",items=STEP_FIVE_STATUS_ITEMS,default="READY_TO_GENERATE"),"step_5_valid":BoolProperty(default=False),"step_5_generation_current":BoolProperty(default=False),"step_5_generation_signature":StringProperty(default=""),"step_5_generation_id":StringProperty(default=""),"step_5_generation_duration":FloatProperty(default=0.,min=0.),"step_5_generation_iterations":IntProperty(default=0,min=0),"preparation_die_object":PointerProperty(type=bpy.types.Object),"blocked_die_object":PointerProperty(type=bpy.types.Object),"selected_candidate_object":PointerProperty(type=bpy.types.Object),"approved_candidate_object":PointerProperty(type=bpy.types.Object),"candidate_metadata":StringProperty(default=""),"selected_candidate_id":StringProperty(default=""),"step_5_summary":StringProperty(default=""),"step_5_errors":StringProperty(default=""),"step_5_warnings":StringProperty(default=""),"step_5_review_confirmed":BoolProperty(name="I Reviewed the Step 5 Geometry",default=False),"step_5_warning_acknowledged":BoolProperty(name="Acknowledge Step 5 Warnings",default=False),"approved_step_5_signature":StringProperty(default=""),"approved_candidate_id":StringProperty(default=""),"approved_settings_snapshot":StringProperty(default=""),"approved_metrics_snapshot":StringProperty(default=""),"step_5_correction_active":BoolProperty(default=False),"step_5_correction_snapshot":StringProperty(default=""),"step_5_override_used":BoolProperty(default=False),"step_5_override_note":StringProperty(default="")}.items():a.setdefault(name,prop)
 def fp(name,default,minimum,maximum):a.setdefault(name,FloatProperty(name=name.replace("step_5_","").replace("_"," ").title(),default=default,min=minimum,max=maximum,subtype="DISTANCE",unit="LENGTH",update=_setting_updated))
 fp("step_5_marginal_gap",DEFAULT_MARGINAL_GAP,0,.0002);fp("step_5_cement_gap",DEFAULT_CEMENT_GAP,0,.0003);fp("step_5_spacer_start",DEFAULT_SPACER_START,.0002,.003);fp("step_5_axial_relief",DEFAULT_AXIAL_RELIEF,0,.0003);fp("step_5_occlusal_relief",DEFAULT_OCCLUSAL_RELIEF,0,.0005);fp("step_5_seal_band_width",DEFAULT_SEAL_BAND_WIDTH,.00015,.002);fp("step_5_blockout_clearance",DEFAULT_BLOCKOUT_CLEARANCE,0,.0003);fp("step_5_sampling_resolution",DEFAULT_SAMPLING_RESOLUTION,.00005,.001);fp("step_5_correction_limit",DEFAULT_CORRECTION_LIMIT,.00002,.0005)
 a.setdefault("step_5_smoothing_strength",FloatProperty(default=DEFAULT_SMOOTHING_STRENGTH,min=0,max=1,update=_setting_updated));a.setdefault("step_5_maximum_candidates",IntProperty(default=DEFAULT_MAXIMUM_CANDIDATES,min=1,max=3,update=_setting_updated));a.setdefault("step_5_maximum_iterations",IntProperty(default=DEFAULT_MAXIMUM_ITERATIONS,min=1,max=20,update=_setting_updated));a.setdefault("step_5_maximum_runtime",FloatProperty(default=DEFAULT_MAXIMUM_RUNTIME,min=1,max=60,subtype="TIME",update=_setting_updated))

def _patch_dependencies():
 if not hasattr(step_four_session,"_bdental_step_five_original_clear_step_four_approval"):
  original=step_four_session.clear_step_four_approval;step_four_session._bdental_step_five_original_clear_step_four_approval=original
  def wrapped(r):original(r);invalidate_restoration(r,upstream=True,preserve_generated=True)
  step_four_session.clear_step_four_approval=wrapped
 if not hasattr(restoration_utils,"_bdental_step_five_original_iter_artifacts"):
  original=restoration_utils.iter_managed_restoration_artifacts;restoration_utils._bdental_step_five_original_iter_artifacts=original
  def combined(scene):
   seen=set()
   for obj in (*tuple(original(scene)),*tuple(crown_bottom_candidates.iter_managed_artifacts(scene))):
    if obj.as_pointer() not in seen:seen.add(obj.as_pointer());yield obj
  restoration_utils.iter_managed_restoration_artifacts=combined

def monitor_scene(scene):
 if not hasattr(scene,"bdental_workflow"):return
 state=scene.bdental_workflow
 if state.internal_update_lock or not state.case_initialized:return
 for r in state.restorations:
  if not state.step_4_valid or not r.step_4_valid or r.step_4_status!="VERIFIED":
   if any(True for _ in crown_bottom_candidates.iter_managed_artifacts(scene,r)):crown_bottom_candidates.remove_restoration_artifacts(scene,r)
   invalidate_restoration(r,upstream=True,preserve_generated=False);continue
  if r.step_5_generation_current:
   current=crown_bottom_candidates.dependency_signature(state,r)
   if r.step_5_generation_signature!=current:invalidate_restoration(r,preserve_generated=True);continue
   for obj,label in ((crown_bottom_candidates.resolve_preparation_die(r),"preparation die"),(crown_bottom_candidates.resolve_blocked_die(r),"blocked die"),(crown_bottom_candidates.resolve_selected_candidate(r),"selected crown bottom")):
    if not obj or obj.get(crown_bottom_candidates.META_DEPENDENCY_SIGNATURE,"")!=current:
     r.step_5_generation_current=False;r.step_5_status="ERROR";r.step_5_errors=f"The managed {label} is missing or stale.";break
    if not r.step_5_correction_active and obj.get(crown_bottom_candidates.META_MESH_SIGNATURE,"")!=crown_bottom_candidates.object_mesh_signature(obj):r.step_5_generation_current=False;r.step_5_status="ERROR";r.step_5_errors=f"The managed {label} changed outside its workflow.";break
  if r.step_5_valid and r.approved_step_5_signature!=step_five_validation.approved_signature(state,r):invalidate_restoration(r,preserve_generated=True)
 sync_step_five_state(state)

_inject_properties();_patch_dependencies()
