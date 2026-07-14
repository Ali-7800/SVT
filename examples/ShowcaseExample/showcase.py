"""Showcase scene using every Scene.Object primitive and every
texture/finish feature (plain color, image maps, bump maps, metallic
reflection, iridescence, per-face mesh coloring).
"""

from svt import Scene, Sphere, SphereSweep, Cylinder, Cone, Plane, Mesh
import numpy as np


def build_showcase_scene():
    scene = Scene(FPS=20, background_color=[0.02, 0.02, 0.05, 0])

    camera_id = scene.add_camera(
        name="main",
        location=lambda t: [
            20 * np.sin(2 * np.pi * t / 5),
            5,
            -20 * np.cos(2 * np.pi * t / 5),
        ],  # moving camera
        angle=50,
        look_at=[0, 1, 0],
    )
    # camera_id=-1 (default) assigns this light to every camera.
    scene.add_light(location=[-8, 12, -10], color=[1, 1, 1])
    scene.add_light(location=[8, 6, -6], color=[0.6, 0.6, 0.8], shadow=False)

    # --- Ground plane, planar image map -------------------------------
    ground = Plane("ground", normal=[0, 1, 0], distance=-1)
    ground.image_map.path = "image_map.jpg"
    ground.image_map.type = 0  # planar
    scene.append(ground)

    # --- Row of spheres: one feature each ------------------------------
    sphere_plain = Sphere(
        "sphere_plain", position=lambda t: [-8, 1 + np.sin(t), 0], radius=1
    )  # moving position
    sphere_plain.color = [0.2, 0.6, 0.9]
    sphere_plain.shadow = False
    scene.append(sphere_plain)

    sphere_image = Sphere(
        "sphere_image", position=[-5, 1, 0], radius=lambda t: 1 + 0.5 * np.sin(t)
    )  # chaning size
    sphere_image.image_map.path = "image_map.jpg"
    sphere_image.image_map.type = 2  # spherical
    scene.append(sphere_image)

    sphere_bump = Sphere("sphere_bump", position=[-2, 1, 0], radius=1)
    sphere_bump.color = [0.8, 0.2, 0.2]
    sphere_bump.bump_map.path = "bump_map.jpg"
    sphere_bump.bump_map.size = 0.3
    scene.append(sphere_bump)

    sphere_metal = Sphere("sphere_metal", position=[1, 1, 0], radius=1)
    sphere_metal.color = lambda t: [0.5 + 0.5 * np.cos(t), 0.8, 0.3]  # changing color
    sphere_metal.finish.metallic = True
    sphere_metal.finish.metallic_reflection = True
    sphere_metal.finish.specular = 1
    sphere_metal.finish.roughness = 0.02
    sphere_metal.finish.reflection = 0.6
    scene.append(sphere_metal)

    sphere_irid = Sphere("sphere_irid", position=[4, 1, 0], radius=1)
    sphere_irid.color = [0.9, 0.9, 0.9]
    sphere_irid.finish.iridescence = 0.6
    sphere_irid.finish.iridescence_thickness = 0.3
    sphere_irid.finish.iridescence_turbulence = 0.5
    scene.append(sphere_irid)

    # --- Cylinder: cylindrical image map -------------------------------
    cylinder = Cylinder(
        "cylinder_image",
        start_position=[-8, 0, 4],
        end_position=[-8, 2.5, 4],
        radius=0.8,
    )
    cylinder.image_map.path = "image_map.jpg"
    cylinder.image_map.type = 2  # cylindrical
    scene.append(cylinder)

    # --- Cone: open frustum, bump-mapped plain color -------------------
    cone = Cone(
        "cone_bump",
        base_position=[-4, 0, 4],
        base_radius=lambda t: 1.2 + np.sin(2 * t),  # base radius changing with time
        cap_position=lambda t: [
            -4,
            2.5 + np.cos(t),
            4,
        ],  # cap position changing with time
        cap_radius=0.3,
        open=True,
    )
    cone.color = [0.3, 0.7, 0.4]
    cone.bump_map.path = "bump_map.jpg"
    cone.bump_map.size = 4
    scene.append(cone)

    # --- SphereSweep: curved, varying-radius tube ----------------------
    sweep_positions = np.array(
        [
            [0, 0, 4],
            [0, 1.5, 5],
            [1, 2.5, 4],
            [2, 1.5, 3],
            [2, 0, 4],
        ]
    ).T  # shape (3, n_points)
    sweep_radii = [0.4, 0.6, 0.7, 0.5, 0.3]
    sweep = SphereSweep("sweep", position=sweep_positions, radius=sweep_radii)
    sweep.interpolation_method = "cubic_spline"
    sweep.color = [0.8, 0.4, 0.9]
    sweep.transmit = lambda t: 0.5 + 0.5 * np.sin(t)  # changing transparency
    scene.append(sweep)

    # --- Mesh: single UV-mapped quad (two triangles) -------------------
    mesh_vertices = np.array(
        [
            [5, 0, 4],
            [7, 0, 4],
            [7, 2, 4],
            [5, 2, 4],
        ]
    ).T  # (3, 4)
    mesh_faces = np.array(
        [
            [0, 1, 2],
            [0, 2, 3],
        ]
    ).T  # (3, 2)
    mesh_uv = np.array(
        [
            [0, 0],
            [1, 0],
            [1, 1],
            [0, 1],
        ]
    ).T  # (2, 4)

    mesh_image = Mesh("mesh_image", vertices=mesh_vertices, faces_indices=mesh_faces)
    mesh_image.uv_vectors = mesh_uv
    mesh_image.image_map.path = "image_map.jpg"
    scene.objects.append(mesh_image)

    # --- Mesh: per-face colored quad (no shared texture) ---------------
    mesh2_vertices = lambda t: np.array(
        [
            [5, 3, 4],
            [7, 3, 4],
            [7, 5 + np.sin(t), 4],
            [5, 5, 4],
        ]
    ).T  # deforming mesh
    mesh2_faces = np.array(
        [
            [0, 1, 2],
            [0, 2, 3],
        ]
    ).T
    mesh_colors = Mesh(
        "mesh_facecolors", vertices=mesh2_vertices, faces_indices=mesh2_faces
    )
    mesh_colors.face_color.list = lambda t: np.array(
        [
            [1, 0, 0, 0],  # opaque red
            [0, 0, 1, 0.5 + 0.5 * np.cos(t)],  # blue with changing transparency
        ]
    ).T
    mesh_colors.face_color.indices = [0, 1]  # one palette entry per face
    scene.objects.append(mesh_colors)

    return scene, camera_id


if __name__ == "__main__":
    scene, camera_id = build_showcase_scene()

    scene.render_video(
        output_images_directory="",
        rendering_name="showcase",
        start_time=0,
        final_time=5,
        multiprocessing_flag=True,
    )
