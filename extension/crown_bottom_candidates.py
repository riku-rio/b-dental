"""Transactional Step 5 generation and managed artifacts."""
from __future__ import annotations
import hashlib, json, time
from dataclasses import asdict, dataclass
import bpy
from mathutils import Matrix
from . import crown_bottom_overlay, restoration_utils, scene_utils, step_four_validation
from .crown_bottom_geometry import MeshGeometry, geometry_signature, topology_metrics
from .crown_bottom_scoring import evaluate_candidate, rank_candidates, serialize_metrics
from .preparation_die import build_blockout, build_closed_die
from .preparation_region import extract_preparation_patch
from .relief_field import ReliefSettings, build_relief
from .seal_band import build_seal_band

GENERATION_POLICY_VERSION=1
SETTINGS_SCHEMA_VERSION=1
ARTIFACT_PREPARATION_DIE="PREPARATION_DIE"
ARTIFACT_BLOCKED_DIE="BLOCKED_DIE"
ARTIFACT_CROWN_BOTTOM="CROWN_BOTTOM"
META_GENERATION_ID="bdental_step_5_generation_id"
META_CANDIDATE_ID="bdental_step_5_candidate_id"
META_STATUS="bdental_step_5_status"
META_MESH_SIGNATURE="bdental_step_5_mesh_signature"
META_DEPENDENCY_SIGNATURE="bdental_step_5_dependency_signature"
META_METRICS="bdental_step_5_metrics"
META_OUTER_LOOP="bdental_step_5_outer_loop"
META_INNER_LOOP="bdental_step_5_inner_loop"

@dataclass(frozen=True)
class CandidateRecord:
    candidate_id:str; object_name:str; accepted:bool; rank:int; score:float; status:str
    metrics:dict; rejection_reasons:tuple[str,...]; mesh_signature:str; smoothing_strength:float
    def payload(self):
        data=asdict(self); data["rejection_reasons"]=list(self.rejection_reasons); return data

@dataclass(frozen=True)
class GenerationResult:
    generation_id:str; dependency_signature:str; candidates:tuple[CandidateRecord,...]
    selected_candidate_id:str; duration_seconds:float; iterations:int; warnings:tuple[str,...]


def settings_payload(r):
    return {"schema":SETTINGS_SCHEMA_VERSION,"marginal_gap":round(float(r.step_5_marginal_gap),12),
      "cement_gap":round(float(r.step_5_cement_gap),12),"spacer_start":round(float(r.step_5_spacer_start),12),
      "axial_relief":round(float(r.step_5_axial_relief),12),"occlusal_relief":round(float(r.step_5_occlusal_relief),12),
      "seal_band_width":round(float(r.step_5_seal_band_width),12),"blockout_clearance":round(float(r.step_5_blockout_clearance),12),
      "sampling_resolution":round(float(r.step_5_sampling_resolution),12),"smoothing_strength":round(float(r.step_5_smoothing_strength),12),
      "maximum_candidates":int(r.step_5_maximum_candidates),"maximum_iterations":int(r.step_5_maximum_iterations),
      "maximum_runtime":round(float(r.step_5_maximum_runtime),6),"correction_limit":round(float(r.step_5_correction_limit),12),
      "policy":GENERATION_POLICY_VERSION}

def dependency_signature(state,r):
    target=restoration_utils.target_scan(state,r)
    payload={"target":restoration_utils.target_scan_signature(target),"target_matrix":restoration_utils.target_matrix_signature(target),
      "margin":r.approved_margin_points,"axis":r.approved_axis_local or r.insertion_axis_local,
      "step_4":step_four_validation.approved_signature(state,r),"step_4_approved":r.approved_step_4_signature,
      "analysis":r.approved_analysis_signature,"settings":settings_payload(r)}
    return json.dumps(payload,sort_keys=True,separators=(",",":"))

def generation_id_for(signature): return hashlib.sha256(signature.encode()).hexdigest()[:16]

def _geometry_world(obj):
    if not scene_utils.object_is_alive(obj) or obj.type!="MESH" or obj.data is None:return None
    return MeshGeometry(tuple(obj.matrix_world@v.co for v in obj.data.vertices),tuple(tuple(int(i) for i in p.vertices) for p in obj.data.polygons))

def object_mesh_signature(obj):
    g=_geometry_world(obj); return geometry_signature(g.vertices,g.faces) if g else ""

def tag_artifact(obj,r,kind,*,generation_id,dependency,candidate_id="",status=""):
    obj[scene_utils.META_MANAGED]=True; obj[restoration_utils.META_ARTIFACT_TYPE]=kind
    obj[restoration_utils.META_RESTORATION_ID]=r.restoration_id; obj[restoration_utils.META_TARGET_ROLE]=r.target_arch
    obj[restoration_utils.META_TARGET_TOOTH]=r.target_tooth_fdi; obj[restoration_utils.META_SCHEMA_VERSION]=1
    obj[META_GENERATION_ID]=generation_id; obj[META_CANDIDATE_ID]=candidate_id; obj[META_STATUS]=status; obj[META_DEPENDENCY_SIGNATURE]=dependency

def is_managed_artifact(obj,r=None,kind=""):
    if not scene_utils.object_is_alive(obj):return False
    try:
      current=str(obj.get(restoration_utils.META_ARTIFACT_TYPE,""))
      if obj.type!="MESH" or not obj.get(scene_utils.META_MANAGED,False) or current not in {ARTIFACT_PREPARATION_DIE,ARTIFACT_BLOCKED_DIE,ARTIFACT_CROWN_BOTTOM}:return False
      if kind and current!=kind:return False
      return r is None or (obj.get(restoration_utils.META_RESTORATION_ID)==r.restoration_id and obj.get(restoration_utils.META_TARGET_ROLE)==r.target_arch and obj.get(restoration_utils.META_TARGET_TOOTH)==r.target_tooth_fdi)
    except (ReferenceError,RuntimeError,AttributeError):return False

def iter_managed_artifacts(scene,r=None):
    col=bpy.data.collections.get(restoration_utils.RESTORATION_COLLECTION_NAME)
    if col:
      for obj in list(col.objects):
        if scene.objects.get(obj.name) is obj and is_managed_artifact(obj,r):yield obj

def find_artifact(r,kind,*,candidate_id="",status="",generation_id=""):
    col=bpy.data.collections.get(restoration_utils.RESTORATION_COLLECTION_NAME)
    if not col:return None
    for obj in col.objects:
      if not is_managed_artifact(obj,r,kind):continue
      if candidate_id and obj.get(META_CANDIDATE_ID,"")!=candidate_id:continue
      if status and obj.get(META_STATUS,"")!=status:continue
      if generation_id and obj.get(META_GENERATION_ID,"")!=generation_id:continue
      return obj
    return None

def _resolve(r,attr,kind):
    obj=getattr(r,attr,None)
    if is_managed_artifact(obj,r,kind):return obj
    obj=find_artifact(r,kind,generation_id=str(getattr(r,"step_5_generation_id","")))
    if obj:setattr(r,attr,obj)
    return obj

def resolve_preparation_die(r):return _resolve(r,"preparation_die_object",ARTIFACT_PREPARATION_DIE)
def resolve_blocked_die(r):return _resolve(r,"blocked_die_object",ARTIFACT_BLOCKED_DIE)
def resolve_selected_candidate(r):
    obj=getattr(r,"selected_candidate_object",None)
    if is_managed_artifact(obj,r,ARTIFACT_CROWN_BOTTOM) and (not r.selected_candidate_id or obj.get(META_CANDIDATE_ID,"")==r.selected_candidate_id):return obj
    obj=find_artifact(r,ARTIFACT_CROWN_BOTTOM,candidate_id=r.selected_candidate_id)
    if obj:r.selected_candidate_object=obj
    return obj

def resolve_approved_candidate(r):
    obj=getattr(r,"approved_candidate_object",None)
    if is_managed_artifact(obj,r,ARTIFACT_CROWN_BOTTOM) and obj.get(META_STATUS,"")=="APPROVED":return obj
    obj=find_artifact(r,ARTIFACT_CROWN_BOTTOM,candidate_id=r.approved_candidate_id,status="APPROVED")
    if obj:r.approved_candidate_object=obj
    return obj

def remove_artifact(obj):
    if not scene_utils.object_is_alive(obj):return False
    mesh=obj.data if obj.type=="MESH" else None; bpy.data.objects.remove(obj,do_unlink=True)
    if mesh and mesh.users==0:bpy.data.meshes.remove(mesh)
    return True

def remove_restoration_artifacts(scene,r,*,preserve_approved=False):
    approved=resolve_approved_candidate(r) if preserve_approved else None; count=0
    for obj in list(iter_managed_artifacts(scene,r)):
      if obj is approved:continue
      count+=int(remove_artifact(obj))
    if not preserve_approved:r.approved_candidate_object=None;r.approved_candidate_id=""
    r.preparation_die_object=None;r.blocked_die_object=None;r.selected_candidate_object=approved
    return count

def candidate_records(r):
    try:payload=json.loads(r.candidate_metadata or "[]")
    except (TypeError,ValueError,json.JSONDecodeError):return ()
    out=[]
    for item in payload:
      try:
       out.append(CandidateRecord(str(item["candidate_id"]),str(item.get("object_name","")),bool(item.get("accepted",False)),int(item.get("rank",0)),float(item.get("score",0)),str(item.get("status","")),dict(item.get("metrics",{})),tuple(item.get("rejection_reasons",())),str(item.get("mesh_signature","")),float(item.get("smoothing_strength",0))))
      except (KeyError,TypeError,ValueError):return ()
    return tuple(out)
def record_for_id(r,cid):return next((x for x in candidate_records(r) if x.candidate_id==cid),None)

def _create(scene,state,r,g,name,kind,gid,dependency,cid="",status=""):
    target=restoration_utils.target_scan(state,r); inv=target.matrix_world.inverted_safe() if target else Matrix.Identity(4)
    mesh=bpy.data.meshes.new(name+"_Mesh"); mesh.from_pydata([inv@v for v in g.vertices],[],[tuple(f) for f in g.faces]); mesh.validate(verbose=False); mesh.update(calc_edges=True)
    obj=bpy.data.objects.new(name,mesh); restoration_utils.move_to_restoration_collection(obj,scene)
    if target:obj.parent=target;obj.matrix_parent_inverse=Matrix.Identity(4);obj.matrix_basis=Matrix.Identity(4)
    tag_artifact(obj,r,kind,generation_id=gid,dependency=dependency,candidate_id=cid,status=status)
    if g.boundary_loop:obj[META_OUTER_LOOP]=",".join(map(str,g.boundary_loop))
    obj[META_MESH_SIGNATURE]=object_mesh_signature(obj); crown_bottom_overlay.configure_object(obj,kind,status=status); return obj

def _variants(base,count):
    values=[max(0,min(1,base))]
    if count>1:values.append(max(0,min(1,base*0.65)))
    if count>2:values.append(max(0,min(1,base*1.35)))
    return tuple(dict.fromkeys(round(v,6) for v in values))[:count]

def generate(scene,state,r,depsgraph):
    started=time.perf_counter(); dependency=dependency_signature(state,r); gid=generation_id_for(dependency)
    previous=(r.preparation_die_object,r.blocked_die_object,r.selected_candidate_object,r.selected_candidate_id,r.candidate_metadata)
    existing=list(iter_managed_artifacts(scene,r)); approved=resolve_approved_candidate(r); created=[]
    try:
      patch=extract_preparation_patch(state,r,depsgraph)
      block=build_blockout(patch,clearance=float(r.step_5_blockout_clearance),resolution=float(r.step_5_sampling_resolution),smoothing_strength=float(r.step_5_smoothing_strength),maximum_iterations=int(r.step_5_maximum_iterations))
      die=_create(scene,state,r,build_closed_die(patch),f"BDENTAL_Preparation_Die_{r.target_tooth_fdi}_{gid[:8]}",ARTIFACT_PREPARATION_DIE,gid,dependency);created.append(die);r.preparation_die_object=die
      blocked=_create(scene,state,r,build_closed_die(patch,surface_vertices=block.blocked_vertices),f"BDENTAL_Blocked_Die_{r.target_tooth_fdi}_{gid[:8]}",ARTIFACT_BLOCKED_DIE,gid,dependency);created.append(blocked);r.blocked_die_object=blocked
      scored=[]; objects={}; smoothings={}
      for idx,smooth in enumerate(_variants(float(r.step_5_smoothing_strength),int(r.step_5_maximum_candidates))):
       if time.perf_counter()-started>float(r.step_5_maximum_runtime):raise TimeoutError("Step 5 generation exceeded the configured runtime limit.")
       relief=build_relief(block,ReliefSettings(float(r.step_5_marginal_gap),float(r.step_5_cement_gap),float(r.step_5_spacer_start),float(r.step_5_axial_relief),float(r.step_5_occlusal_relief),float(r.step_5_seal_band_width),smooth,int(r.step_5_maximum_iterations)))
       seal=build_seal_band(block,relief,marginal_gap=float(r.step_5_marginal_gap),seal_band_width=float(r.step_5_seal_band_width)); cid=f"{gid}-{idx+1}"
       score=evaluate_candidate(cid,patch,block,relief,seal,generation_duration=time.perf_counter()-started);scored.append(score);status="ACCEPTED" if score.accepted else "REJECTED"
       obj=_create(scene,state,r,seal.geometry,f"BDENTAL_Crown_Bottom_{r.target_tooth_fdi}_{idx+1}_{gid[:8]}",ARTIFACT_CROWN_BOTTOM,gid,dependency,cid,status);created.append(obj)
       obj[META_METRICS]=serialize_metrics(score.metrics);obj[META_MESH_SIGNATURE]=object_mesh_signature(obj);obj.hide_viewport=not score.accepted;crown_bottom_overlay.set_candidate_status(obj,status);objects[cid]=obj;smoothings[cid]=smooth
      ranked=rank_candidates(scored)
      if not ranked:raise ValueError("No crown-bottom candidate passed blocking constraints. "+" ".join(dict.fromkeys(x for c in scored for x in c.rejection_reasons)))
      ranks={c.candidate_id:i+1 for i,c in enumerate(ranked)};records=[]
      for c in scored:
       m=asdict(c.metrics);m["rejection_reasons"]=list(c.metrics.rejection_reasons)
       records.append(CandidateRecord(c.candidate_id,objects[c.candidate_id].name,c.accepted,ranks.get(c.candidate_id,0),c.score,"ACCEPTED" if c.accepted else "REJECTED",m,c.rejection_reasons,object_mesh_signature(objects[c.candidate_id]),smoothings[c.candidate_id]))
      records.sort(key=lambda x:(not x.accepted,x.rank or 999,x.candidate_id));selected=ranked[0].candidate_id;r.selected_candidate_id=selected;r.selected_candidate_object=objects[selected];objects[selected].hide_viewport=False
      r.candidate_metadata=json.dumps([x.payload() for x in records],sort_keys=True,separators=(",",":"))
      approved_gid=str(approved.get(META_GENERATION_ID,"")) if approved else ""
      for obj in existing:
       preserve=approved and (obj is approved or (approved_gid and obj.get(META_GENERATION_ID,"")==approved_gid and obj.get(restoration_utils.META_ARTIFACT_TYPE) in {ARTIFACT_PREPARATION_DIE,ARTIFACT_BLOCKED_DIE}))
       if not preserve:remove_artifact(obj)
      return GenerationResult(gid,dependency,tuple(records),selected,time.perf_counter()-started,max((c.metrics.optimization_iterations for c in scored),default=0),patch.warnings)
    except Exception:
      for obj in reversed(created):remove_artifact(obj)
      r.preparation_die_object,r.blocked_die_object,r.selected_candidate_object,r.selected_candidate_id,r.candidate_metadata=previous
      raise

def select_candidate(r,cid):
    record=record_for_id(r,cid)
    if not record or not record.accepted:raise ValueError("Only accepted candidates can be selected.")
    obj=find_artifact(r,ARTIFACT_CROWN_BOTTOM,candidate_id=cid,status="ACCEPTED",generation_id=r.step_5_generation_id)
    if not obj:raise ValueError("The selected candidate artifact is missing.")
    r.selected_candidate_id=cid;r.selected_candidate_object=obj;return obj

def promote_selected_candidate(r):
    selected=resolve_selected_candidate(r)
    if not selected:raise ValueError("Select a current candidate before approval.")
    old=resolve_approved_candidate(r)
    if old and old is not selected:remove_artifact(old)
    selected[META_STATUS]="APPROVED";selected[META_MESH_SIGNATURE]=object_mesh_signature(selected);crown_bottom_overlay.set_candidate_status(selected,"APPROVED")
    r.approved_candidate_object=selected;return selected

def current_candidate_constraints(r):
    obj=resolve_selected_candidate(r);g=_geometry_world(obj) if obj else None
    if not g:return ("The selected crown-bottom mesh is unavailable.",),()
    m=topology_metrics(g);errors=[];warnings=[]
    if m.boundary_loop_count!=1:errors.append(f"The selected candidate has {m.boundary_loop_count} boundary loops instead of one.")
    if m.non_manifold_edge_count:errors.append(f"The selected candidate has {m.non_manifold_edge_count} non-manifold edges.")
    if m.degenerate_face_count:errors.append(f"The selected candidate has {m.degenerate_face_count} degenerate faces.")
    if m.minimum_edge_length and m.minimum_edge_length<0.00002:warnings.append("The selected candidate contains very small local features.")
    return tuple(errors),tuple(warnings)
