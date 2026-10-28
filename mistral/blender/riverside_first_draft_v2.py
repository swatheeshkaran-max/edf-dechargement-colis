import bpy
from mathutils import Vector

# Riverside blockout: X = along river, Y = toward the project bank, Z = height.
# Project bank is Y=0; water and boats are on the negative-Y side.
P = "DRAFT2_"


def col(name):
    c = bpy.data.collections.get(name)
    if c is None:
        c = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(c)
    return c


def clear():
    for o in list(bpy.data.objects):
        if o.name.startswith(P):
            bpy.data.objects.remove(o, do_unlink=True)


def mat(name, rgba, rough=0.8):
    m = bpy.data.materials.get(P + name) or bpy.data.materials.new(P + name)
    m.diffuse_color = (*rgba, 1)
    m.use_nodes = True
    bs = m.node_tree.nodes.get("Principled BSDF")
    if bs:
        bs.inputs["Base Color"].default_value = (*rgba, 1)
        bs.inputs["Roughness"].default_value = rough
    return m


def cube(name, loc, size, target, material=None, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(location=loc)
    o = bpy.context.object
    o.name = P + name
    o.dimensions = size
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for old in list(o.users_collection):
        old.objects.unlink(o)
    target.objects.link(o)
    if material:
        o.data.materials.append(material)
    if bevel:
        b = o.modifiers.new("soft_edges", "BEVEL")
        b.width = bevel
        b.segments = 3
    return o


def tree(x, y, h, vegetation, trunk, leaves):
    bpy.ops.mesh.primitive_cylinder_add(vertices=12, radius=0.18, depth=h * 0.5, location=(x, y, h * 0.25))
    t = bpy.context.object
    t.name = P + "tree_trunk"
    for old in list(t.users_collection):
        old.objects.unlink(t)
    vegetation.objects.link(t)
    t.data.materials.append(trunk)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=h * 0.30, location=(x, y, h * 0.72))
    l = bpy.context.object
    l.name = P + "tree_crown"
    l.scale.z = 1.25
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    for old in list(l.users_collection):
        old.objects.unlink(l)
    vegetation.objects.link(l)
    l.data.materials.append(leaves)


def point_camera(camera, target):
    direction = Vector(target) - camera.location
    camera.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


clear()
terrain = col("01_TERRAIN")
water = col("02_WATER")
quay = col("03_QUAY_AND_BANK")
access = col("04_ROADS_AND_ACCESS")
boats = col("06_VESSELS_AND_EQUIPMENT")
vegetation = col("07_VEGETATION")
lights = col("08_LIGHTS_AND_CAMERAS")
measure = col("09_MEASUREMENTS")

water_m = mat("water", (0.06, 0.22, 0.28), 0.18)
soil_m = mat("soil", (0.25, 0.17, 0.10), 0.95)
grass_m = mat("grass", (0.12, 0.28, 0.08), 1.0)
path_m = mat("path", (0.38, 0.34, 0.27), 0.95)
quay_m = mat("quay", (0.34, 0.34, 0.31), 0.8)
boat_a_m = mat("boat_a", (0.10, 0.16, 0.20), 0.45)
boat_b_m = mat("boat_b", (0.28, 0.12, 0.06), 0.50)
marker_m = mat("site_marker", (0.95, 0.60, 0.02), 0.45)
trunk_m = mat("trunk", (0.16, 0.07, 0.02), 1.0)
leaf_m = mat("leaves", (0.06, 0.25, 0.05), 1.0)

# 115 m context: 55 m site + 30 m upstream + 30 m downstream.
cube("water_115m", (0, -22, -0.12), (115, 72, 0.24), water, water_m)
cube("project_bank", (0, 6.5, 0.7), (115, 13, 1.4), terrain, soil_m, 0.4)
cube("project_grass", (0, 8, 1.45), (115, 10, 0.25), terrain, grass_m, 0.2)
cube("opposite_bank", (0, -56, 1.0), (115, 10, 2.0), terrain, soil_m, 0.4)
cube("opposite_grass", (0, -54, 2.15), (115, 8, 0.25), terrain, grass_m, 0.2)
cube("riverside_path", (0, 9.5, 1.7), (115, 2.5, 0.18), access, path_m, 0.08)
cube("parking_block", (31, 6.2, 1.65), (18, 5, 0.18), access, path_m, 0.08)

# Maximum 55 m x 15 m water envelope, extending from the project bank toward -Y.
cube("site_edge_1", (0, 0, 0.35), (55, 0.12, 0.12), measure, marker_m)
cube("site_edge_2", (0, -15, 0.35), (55, 0.12, 0.12), measure, marker_m)
cube("site_edge_3", (-27.5, -7.5, 0.35), (0.12, 15, 0.12), measure, marker_m)
cube("site_edge_4", (27.5, -7.5, 0.35), (0.12, 15, 0.12), measure, marker_m)

# Two generic parallel boats; replace them later with real hull models.
cube("placeholder_boat_A", (0, -4.2, 1.25), (42, 5.2, 2.2), boats, boat_a_m, 0.8)
cube("placeholder_boat_B", (0, -10.5, 1.25), (42, 5.2, 2.2), boats, boat_b_m, 0.8)
cube("gangway_A", (-15, -1.8, 2.1), (2.2, 3.6, 0.18), quay, quay_m, 0.05)
cube("gangway_B", (15, -4.8, 2.1), (2.2, 9.6, 0.18), quay, quay_m, 0.05)

for i, x in enumerate(range(-52, 56, 9)):
    tree(x, 11 + (i % 3), 8 + (i % 4) * 1.2, vegetation, trunk_m, leaf_m)
for i, x in enumerate(range(-52, 56, 11)):
    tree(x, -52 - (i % 2) * 1.5, 10 + (i % 3) * 1.5, vegetation, trunk_m, leaf_m)

# Camera from the opposite bank, looking toward the project bank.
cam_data = bpy.data.cameras.new(P + "opposite_bank_camera")
cam = bpy.data.objects.new(P + "opposite_bank_camera", cam_data)
lights.objects.link(cam)
cam.location = (0, -68, 11)
cam_data.lens = 42
point_camera(cam, (0, 3, 2.5))
bpy.context.scene.camera = cam

sun_data = bpy.data.lights.new(P + "sun", "SUN")
sun = bpy.data.objects.new(P + "sun", sun_data)
lights.objects.link(sun)
sun.location = (-25, -35, 45)
sun.rotation_euler = (0.45, -0.35, -0.5)
sun_data.energy = 2.5
sun_data.angle = 0.14

scene = bpy.context.scene
scene.unit_settings.system = "METRIC"
scene.unit_settings.scale_length = 1.0
scene.unit_settings.length_unit = "METERS"
scene.render.resolution_x = 1600
scene.render.resolution_y = 900
scene.render.resolution_percentage = 100
scene.world.color = (0.055, 0.075, 0.11)

root = bpy.data.collections.get("RIVERSIDE_PROJECT")
if root:
    root["draft_context_length_m"] = 115.0
    root["site_envelope_length_m"] = 55.0
    root["site_envelope_width_m"] = 15.0
    root["water_level_assumption_m"] = 0.0

print("Riverside first draft v2 created successfully.")
