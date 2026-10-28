import bpy
import math
from mathutils import Vector


# -----------------------------------------------------------------------------
# Riverside first draft
# Coordinate convention:
#   X = along the river (115 m model length)
#   Y = from the opposite bank toward the project bank
#   Z = vertical; normal water surface at Z = 0
# The project bank is at Y = 0. The opposite-bank camera is at negative Y.
# -----------------------------------------------------------------------------

PREFIX = "DRAFT_"
PROJECT_ROOT = "RIVERSIDE_PROJECT"

COLLECTION_NAMES = [
    "00_REFERENCE", "01_TERRAIN", "02_WATER", "03_QUAY_AND_BANK",
    "04_ROADS_AND_ACCESS", "05_BUILDINGS_AND_INFRASTRUCTURE",
    "06_VESSELS_AND_EQUIPMENT", "07_VEGETATION",
    "08_LIGHTS_AND_CAMERAS", "09_MEASUREMENTS",
]


def get_collection(name):
    col = bpy.data.collections.get(name)
    if col is None:
        col = bpy.data.collections.new(name)
        bpy.context.scene.collection.children.link(col)
    return col


def move_to_collection(obj, collection):
    for old in list(obj.users_collection):
        old.objects.unlink(obj)
    collection.objects.link(obj)


def clear_draft_objects():
    for obj in list(bpy.data.objects):
        if obj.name.startswith(PREFIX):
            bpy.data.objects.remove(obj, do_unlink=True)


def material(name, color, roughness=0.7, metallic=0.0):
    mat = bpy.data.materials.get(name) or bpy.data.materials.new(name)
    mat.diffuse_color = (*color, 1.0)
    mat.use_nodes = True
    bsdf = mat.node_tree.nodes.get("Principled BSDF")
    if bsdf:
        bsdf.inputs["Base Color"].default_value = (*color, 1.0)
        bsdf.inputs["Roughness"].default_value = roughness
        bsdf.inputs["Metallic"].default_value = metallic
    return mat


def add_cube(name, location, scale, collection, mat=None, bevel=0.0):
    bpy.ops.mesh.primitive_cube_add(location=location)
    obj = bpy.context.object
    obj.name = PREFIX + name
    obj.scale = (scale[0] / 2.0, scale[1] / 2.0, scale[2] / 2.0)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    move_to_collection(obj, collection)
    if mat:
        obj.data.materials.append(mat)
    if bevel > 0:
        modifier = obj.modifiers.new("Soft_edges", "BEVEL")
        modifier.width = bevel
        modifier.segments = 3
    return obj


def add_cylinder(name, location, radius, depth, collection, mat=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=16, radius=radius, depth=depth, location=location)
    obj = bpy.context.object
    obj.name = PREFIX + name
    move_to_collection(obj, collection)
    if mat:
        obj.data.materials.append(mat)
    return obj


def add_tree(name, x, y, height, collection, trunk_mat, leaf_mat):
    trunk = add_cylinder(name + "_trunk", (x, y, height * 0.25), 0.18, height * 0.5, collection, trunk_mat)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=2, radius=height * 0.30, location=(x, y, height * 0.72))
    crown = bpy.context.object
    crown.name = PREFIX + name + "_crown"
    crown.scale = (1.0, 1.0, 1.25)
    bpy.ops.object.transform_apply(location=False, rotation=False, scale=True)
    move_to_collection(crown, collection)
    crown.data.materials.append(leaf_mat)
    return trunk, crown


def look_at(obj, target):
    direction = Vector(target) - obj.location
    obj.rotation_euler = direction.to_track_quat("-Z", "Y").to_euler()


def add_camera(collection):
    data = bpy.data.cameras.get(PREFIX + "Opposite_Bank_Camera") or bpy.data.cameras.new(PREFIX + "Opposite_Bank_Camera")
    camera = bpy.data.objects.get(PREFIX + "Opposite_Bank_Camera") or bpy.data.objects.new(PREFIX + "Opposite_Bank_Camera", data)
    if not camera.users_collection:
        collection.objects.link(camera)
    camera.location = (0.0, -68.0, 11.0)
    camera.data.lens = 42
    camera.data.sensor_width = 36
    look_at(camera, (0.0, 4.0, 2.5))
    bpy.context.scene.camera = camera
    return camera


def add_sun(collection):
    data = bpy.data.lights.get(PREFIX + "Sun") or bpy.data.lights.new(PREFIX + "Sun", type="SUN")
    light = bpy.data.objects.get(PREFIX + "Sun") or bpy.data.objects.new(PREFIX + "Sun", data)
    if not light.users_collection:
        collection.objects.link(light)
    light.location = (-25.0, -35.0, 45.0)
    light.rotation_euler = (math.radians(28), math.radians(-20), math.radians(-28))
    data.energy = 2.5
    data.angle = math.radians(8)
    return light


def create_first_draft():
    clear_draft_objects()
    terrain = get_collection("01_TERRAIN")
    water = get_collection("02_WATER")
    quay = get_collection("03_QUAY_AND_BANK")
    access = get_collection("04_ROADS_AND_ACCESS")
    vessels = get_collection("06_VESSELS_AND_EQUIPMENT")
    vegetation = get_collection("07_VEGETATION")
    lights = get_collection("08_LIGHTS_AND_CAMERAS")
    measures = get_collection("09_MEASUREMENTS")

    # Materials: intentionally simple blockout colours.
    water_mat = material(PREFIX + "Water", (0.08, 0.24, 0.30), roughness=0.18)
    soil_mat = material(PREFIX + "Bank", (0.27, 0.20, 0.12), roughness=0.95)
    grass_mat = material(PREFIX + "Grass", (0.16, 0.32, 0.12), roughness=1.0)
    path_mat = material(PREFIX + "Path", (0.38, 0.35, 0.29), roughness=0.95)
    quay_mat = material(PREFIX + "Quay", (0.35, 0.35, 0.32), roughness=0.8)
    hull_a_mat = material(PREFIX + "Boat_A", (0.16, 0.20, 0.23), roughness=0.45, metallic=0.25)
    hull_b_mat = material(PREFIX + "Boat_B", (0.28, 0.16, 0.10), roughness=0.5, metallic=0.2)
    gangway_mat = material(PREFIX + "Gangway", (0.35, 0.35, 0.32), roughness=0.8)
    trunk_mat = material(PREFIX + "Tree_Trunk", (0.18, 0.08, 0.03), roughness=1.0)
    leaf_mat = material(PREFIX + "Tree_Crown", (0.08, 0.28, 0.07), roughness=1.0)
    marker_mat = material(PREFIX + "Site_Marker", (0.95, 0.65, 0.05), roughness=0.45)

    # 115 m context: 55 m site envelope plus 30 m at each end.
    add_cube("Water_115m_context", (0.0, -22.0, -0.12), (115.0, 72.0, 0.24), water, water_mat)

    # Project-side riverbank and opposite-bank viewing side.
    add_cube("Project_Bank_Base", (0.0, 6.5, 0.7), (115.0, 13.0, 1.4), terrain, soil_mat, bevel=0.4)
    add_cube("Project_Bank_Grass", (0.0, 8.0, 1.45), (115.0, 10.0, 0.25), terrain, grass_mat, bevel=0.2)
    add_cube("Opposite_Bank_Base", (0.0, -56.0, 1.0), (115.0, 10.0, 2.0), terrain, soil_mat, bevel=0.4)
    add_cube("Opposite_Bank_Grass", (0.0, -54.0, 2.15), (115.0, 8.0, 0.25), terrain, grass_mat, bevel=0.2)

    # Riverside path and a small parking/access strip on the project bank.
    add_cube("Project_Bank_Path", (0.0, 9.5, 1.70), (115.0, 2.5, 0.18), access, path_mat, bevel=0.08)
    add_cube("Access_Parking_Block", (31.0, 6.2, 1.65), (18.0, 5.0, 0.18), access, path_mat, bevel=0.08)

    # 55 m x 15 m maximum water envelope, shown with four low marker beams.
    # The project bank is at Y=0; the water-side envelope extends toward -Y.
    site_x, site_y, site_w, site_l = 0.0, -7.5, 15.0, 55.0
    marker_z = 0.35
    add_cube("Site_Marker_North", (site_x, site_y + site_w / 2, marker_z), (site_l, 0.12, 0.12), measures, marker_mat)
    add_cube("Site_Marker_South", (site_x, site_y - site_w / 2, marker_z), (site_l, 0.12, 0.12), measures, marker_mat)
    add_cube("Site_Marker_West", (site_x - site_l / 2, site_y, marker_z), (0.12, site_w, 0.12), measures, marker_mat)
    add_cube("Site_Marker_East", (site_x + site_l / 2, site_y, marker_z), (0.12, site_w, 0.12), measures, marker_mat)

    # Two parallel placeholder boats. Replace these later with real hull models.
    boat_length, boat_beam, boat_height = 42.0, 5.2, 2.2
    boat_a_y, boat_b_y = -4.2, -10.5
    add_cube("Placeholder_Boat_A", (0.0, boat_a_y, 1.25), (boat_length, boat_beam, boat_height), vessels, hull_a_mat, bevel=0.8)
    add_cube("Placeholder_Boat_B", (0.0, boat_b_y, 1.25), (boat_length, boat_beam, boat_height), vessels, hull_b_mat, bevel=0.8)

    # Two simple gangways from the bank to the two placeholder boats.
    add_cube("Gangway_A", (-15.0, -1.8, 2.1), (2.2, 3.6, 0.18), quay, gangway_mat, bevel=0.05)
    add_cube("Gangway_B", (15.0, -4.8, 2.1), (2.2, 9.6, 0.18), quay, gangway_mat, bevel=0.05)

    # Stylised trees: enough to read the landscape without modelling every tree.
    for i, x in enumerate(range(-52, 56, 9)):
        add_tree(f"Project_Tree_{i:02d}", x, 11.0 + (i % 3) * 1.0, 8.0 + (i % 4) * 1.2, vegetation, trunk_mat, leaf_mat)
    for i, x in enumerate(range(-52, 56, 11)):
        add_tree(f"Opposite_Tree_{i:02d}", x, -52.0 - (i % 2) * 1.5, 10.0 + (i % 3) * 1.5, vegetation, trunk_mat, leaf_mat)

    # Scene and render settings.
    scene = bpy.context.scene
    scene.unit_settings.system = "METRIC"
    scene.unit_settings.scale_length = 1.0
    scene.unit_settings.length_unit = "METERS"
    scene.render.resolution_x = 1600
    scene.render.resolution_y = 900
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = False
    scene.world.color = (0.055, 0.075, 0.11)
    add_camera(lights)
    add_sun(lights)

    # Store blockout assumptions on the project collection.
    project = bpy.data.collections.get(PROJECT_ROOT)
    if project:
        project["draft_context_length_m"] = 115.0
        project["site_envelope_length_m"] = 55.0
        project["site_envelope_width_m"] = 15.0
        project["water_level_assumption_m"] = 0.0
        project["boats"] = "Two parallel placeholders; replace with survey/GA dimensions."

    print("Riverside first draft created: 115 m context, 55 x 15 m site envelope, two placeholder boats.")


create_first_draft()
