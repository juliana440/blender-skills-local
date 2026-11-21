"""Example scene: an enamel camping mug with coffee on a wooden table. Builds geometry only
(materials and light come from the skills). Units: meters.

  blender -b --factory-startup -P examples/scene_mug.py -- --save examples/out/mug.blend
"""
import math
import sys

import bmesh
import bpy
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
SAVE = argv[argv.index("--save") + 1] if "--save" in argv else None

bpy.ops.wm.read_factory_settings(use_empty=True)
scene = bpy.context.scene
scene.unit_settings.system = "METRIC"


def mesh_obj(name, bm):
    me = bpy.data.meshes.new(name)
    bm.to_mesh(me)
    bm.free()
    ob = bpy.data.objects.new(name, me)
    scene.collection.objects.link(ob)
    return ob


def smooth(ob, levels=2):
    for p in ob.data.polygons:
        p.use_smooth = True
    m = ob.modifiers.new("Subdivision", "SUBSURF")
    m.levels = m.render_levels = levels


def mat(name, color, rough=0.5, metal=0.0):
    m = bpy.data.materials.new(name)
    b = next(n for n in m.node_tree.nodes if n.type == "BSDF_PRINCIPLED")
    b.inputs["Base Color"].default_value = (*color, 1)
    b.inputs["Roughness"].default_value = rough
    b.inputs["Metallic"].default_value = metal
    return m


# ---- mug body: a lathe profile (radius, height), closed bottom, rolled rim ----
R, H, SEG = 0.043, 0.088, 48
profile = [(0.0, 0.0), (0.036, 0.0), (0.0395, 0.002), (0.0405, 0.006), (R, H - 0.004),
           (R + 0.0022, H - 0.001), (R + 0.0016, H + 0.0016), (R - 0.0012, H + 0.0012),
           (R - 0.0025, H - 0.004), (0.0385, 0.008), (0.0, 0.008)]
def densify(pts, step=0.004):
    # extra loops along long segments keep the thin wall from collapsing under subdivision
    out = [pts[0]]
    for (r0, z0), (r1, z1) in zip(pts, pts[1:]):
        n = max(1, int(((r1 - r0) ** 2 + (z1 - z0) ** 2) ** 0.5 / step))
        out += [(r0 + (r1 - r0) * k / n, z0 + (z1 - z0) * k / n) for k in range(1, n + 1)]
    return out


profile = densify(profile)
bm = bmesh.new()
rings = []
for i in range(SEG):
    a = 2 * math.pi * i / SEG
    rings.append([bm.verts.new((r * math.cos(a), r * math.sin(a), z)) for r, z in profile])
for i in range(SEG):
    A, B = rings[i], rings[(i + 1) % SEG]
    for k in range(len(profile) - 1):
        try:
            bm.faces.new((A[k], B[k], B[k + 1], A[k + 1]))
        except ValueError:
            pass
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-6)
bmesh.ops.recalc_face_normals(bm, faces=bm.faces)
body = mesh_obj("Mug", bm)
# rim band = the rolled lip (dark enamel edge, like real camping mugs)
body.data.materials.append(mat("M_Enamel", (0.05, 0.28, 0.42), 0.18))
body.data.materials.append(mat("M_Rim", (0.02, 0.03, 0.06), 0.25))
body.data.materials.append(mat("M_EnamelInside", (0.85, 0.84, 0.8), 0.15))
for p in body.data.polygons:
    zc = sum(body.data.vertices[v].co.z for v in p.vertices) / len(p.vertices)
    rc = max(Vector(body.data.vertices[v].co.xy).length for v in p.vertices)
    radial = Vector((p.center.x, p.center.y, 0)).normalized()
    inside = p.normal.dot(radial) < -0.3 or (p.normal.z > 0.9 and zc > 0.004)
    p.material_index = 1 if (zc > H - 0.0035 and rc > R - 0.004) else (2 if inside else 0)
smooth(body, 1)

# ---- handle: a C-shaped tube following a curve ----
cu = bpy.data.curves.new("HandleCurve", "CURVE")
cu.dimensions = "3D"
sp = cu.splines.new("BEZIER")
pts = [(R - 0.006, 0, 0.074), (R + 0.024, 0, 0.072), (R + 0.03, 0, 0.045), (R + 0.02, 0, 0.022), (R - 0.006, 0, 0.02)]   # ends sink into the wall (no coplanar faces)
sp.bezier_points.add(len(pts) - 1)
for bp, co in zip(sp.bezier_points, pts):
    bp.co = co
    bp.handle_left_type = bp.handle_right_type = "AUTO"
cu.bevel_depth = 0.0042
cu.bevel_resolution = 4
cu.resolution_u = 16
cu.use_fill_caps = True
hc = bpy.data.objects.new("HandleCurve", cu)
scene.collection.objects.link(hc)
bpy.context.view_layer.objects.active = hc
hc.select_set(True)
bpy.ops.object.convert(target="MESH")
handle = bpy.context.object
handle.name = "Handle"
handle.scale = (1, 1.9, 1)          # flat strap, wider than deep
bpy.ops.object.transform_apply(scale=True)
handle.data.materials.append(body.data.materials[0])
bm = bmesh.new()
bm.from_mesh(handle.data)
bmesh.ops.remove_doubles(bm, verts=bm.verts, dist=1e-5)
bm.to_mesh(handle.data)
bm.free()
for p in handle.data.polygons:
    p.use_smooth = True

# ---- coffee surface ----
bm = bmesh.new()
bmesh.ops.create_circle(bm, cap_ends=True, radius=R - 0.0028, segments=SEG)
coffee = mesh_obj("Coffee", bm)
coffee.location.z = H - 0.014
coffee.data.materials.append(mat("M_Coffee", (0.09, 0.04, 0.015), 0.3))
for p in coffee.data.polygons:
    p.use_smooth = True

def wood_material():
    # procedural oak: stretched noise -> wave rings -> color ramp, plus roughness breakup
    m = bpy.data.materials.new("M_TableWood")
    nt = m.node_tree
    b = next(n for n in nt.nodes if n.type == "BSDF_PRINCIPLED")
    tc = nt.nodes.new("ShaderNodeTexCoord")
    mp = nt.nodes.new("ShaderNodeMapping")
    mp.inputs["Scale"].default_value = (1.2, 16.0, 1.2)
    nt.links.new(tc.outputs["Object"], mp.inputs["Vector"])
    wave = nt.nodes.new("ShaderNodeTexWave")
    wave.wave_type, wave.bands_direction = "BANDS", "Y"
    wave.inputs["Scale"].default_value = 9.0
    wave.inputs["Distortion"].default_value = 5.0
    wave.inputs["Detail"].default_value = 6.0
    wave.inputs["Detail Scale"].default_value = 1.4
    nt.links.new(mp.outputs[0], wave.inputs["Vector"])
    ramp = nt.nodes.new("ShaderNodeValToRGB")
    ramp.color_ramp.elements[0].color = (0.16, 0.075, 0.03, 1)
    ramp.color_ramp.elements[1].color = (0.42, 0.24, 0.11, 1)
    nt.links.new(wave.outputs["Fac"], ramp.inputs[0])
    nt.links.new(ramp.outputs[0], b.inputs["Base Color"])
    rr = nt.nodes.new("ShaderNodeMapRange")
    rr.inputs[3].default_value, rr.inputs[4].default_value = 0.45, 0.7
    nt.links.new(wave.outputs["Fac"], rr.inputs[0])
    nt.links.new(rr.outputs[0], b.inputs["Roughness"])
    return m


# ---- table top: a thick plank with bevelled edges ----
bm = bmesh.new()
bmesh.ops.create_cube(bm, size=1)
table = mesh_obj("Table", bm)
table.scale = (0.9, 0.6, 0.03)
table.location = (0.05, 0.08, -0.015)
bpy.context.view_layer.objects.active = table
table.select_set(True)
bpy.ops.object.transform_apply(scale=True)
bev = table.modifiers.new("Bevel", "BEVEL")
bev.width, bev.segments = 0.004, 3
table.data.materials.append(wood_material())

# ---- backdrop wall so low sun and fog have something to land on ----
bm = bmesh.new()
bmesh.ops.create_grid(bm, x_segments=1, y_segments=1, size=1)
wall = mesh_obj("Wall", bm)
wall.scale = (3, 1.5, 1)
wall.rotation_euler = (math.radians(90), 0, 0)
wall.location = (0, 0.6, 0.5)
wall.data.materials.append(mat("M_Wall", (0.72, 0.68, 0.62), 0.9))

# ---- camera: 4:5 Instagram portrait, low three-quarter view ----
cam = bpy.data.objects.new("Camera", bpy.data.cameras.new("Camera"))
scene.collection.objects.link(cam)
cam.data.lens = 70
cam.location = (0.32, -0.38, 0.2)
target = Vector((0.012, 0.0, 0.048))
cam.rotation_euler = (target - cam.location).to_track_quat("-Z", "Y").to_euler()
cam.data.dof.use_dof = True
cam.data.dof.focus_object = body
cam.data.dof.aperture_fstop = 8
scene.camera = cam
scene.render.resolution_x, scene.render.resolution_y = 1080, 1350

if SAVE:
    bpy.ops.wm.save_as_mainfile(filepath=bpy.path.abspath(SAVE))
print("@@JSON@@" + '{"ok": true, "objects": %d}' % len(scene.objects))
