"""Minimal Scene showing basic package functionality."""

from svt import Scene, Sphere, Plane

scene = Scene(FPS=24, background_color=[0.02, 0.02, 0.05, 0])

camera_id = scene.add_camera(
    name="main",
    location=[0, 5, -14],
    angle=50,
    look_at=[0, 1, 0],
)
scene.add_light(location=[-8, 12, -10], color=[1, 1, 1])

ground = Plane("ground", normal=[0, 1, 0], distance=-1)
ground.color = [0.6, 0.6, 0.6]
scene.append(ground)

sphere = Sphere("sphere", position=[0, 1, 0], radius=1)
sphere.color = [0.2, 0.6, 0.9]
sphere.finish.metallic = True
sphere.finish.reflection = 0.4
scene.append(sphere)

if __name__ == "__main__":
    scene.render_frames(
        output_images_directory="",
        times=[0],
        name="Frame",
    )
