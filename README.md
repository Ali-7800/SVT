<div align='center'>
<h1> SVT </h1>
</div>

The scientific visualization toolbox (SVT) is a Python package that contains a collection of tools for creating static and interactive renderings and dashboards for
scientific visualization purposes.

## Installation

### Prerequisites

- **[uv](https://docs.astral.sh/uv/getting-started/installation/)** for dependency management.
- **[POV-Ray](https://www.povray.org/)** — SVT generates POV-Ray scene scripts and shells out to the `povray` binary to render them, so it must be installed separately and available on your `PATH`.
  - Debian/Ubuntu: `sudo apt install povray`
  - macOS: `brew install povray`
  - Windows: download an installer from the [POV-Ray downloads page](http://www.povray.org/download/)

  > Any POV-Ray 3.6+ install works. Note that POV-Ray 3.6 itself has no built-in multithreading — SVT works around this by invoking it per-frame via generated INI files and parallelizing at the Python level, so rendering still scales across cores even on older POV-Ray builds.

### Steps

```bash
git clone https://github.com/Ali-7800/SVT.git
cd svt
uv sync
```

This installs SVT and its dependencies into a local `.venv` managed by uv. Run any script or the test suite through `uv run`, e.g.:

```bash
uv run python my_scene.py
```

## Usage

A minimal example: build a scene, add a camera and light, drop in a couple of primitives with different textures, and render it.

```python
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


```

### Available objects

- **Primitives**: `Sphere`, `Cylinder`, `Cone`, `Plane`, `SphereSweep`, `Mesh`
- **Stage**: `Scene` (cameras, lights, and the objects to render)

Every object supports a shared texture/finish API:

- `color`, `transmit` — base pigment
- `image_map` — UV/planar/spherical/cylindrical/torus image textures
- `bump_map` — normal mapping
- `finish` — `ambient`, `diffuse`, `specular`, `roughness`, `phong`, `metallic`, `reflection`, `iridescence`, and related parameters

Most numeric attributes accept either a static value or a time-varying callable, so scenes can be animated across frames.

## License

TBD.