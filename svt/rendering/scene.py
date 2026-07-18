import multiprocessing
import os
from functools import partial
from multiprocessing import Pool
from tqdm import tqdm
from numbers import Real
from svt.rendering.stage import Stage
from svt.rendering.renderer import render_povray
from svt.rendering.utils import (
    TimeScalar,
    TimeVecN,
    _wrapped_property,
    _bool_property,
    _extension_from_path,
)
import dill
import gzip


class Scene(Stage):
    """Describes the objects to be rendered and the duration of the rendering."""

    def __init__(
        self,
    ) -> None:
        Stage.__init__(self)
        self.objects = []

    class Object(Stage.Object):
        """Base class for every renderable POV-Ray object.

        Holds the shared texture state (color, transmit, finish, image/bump
        maps) and `generate_texture_script`, which every primitive's
        `generate_script` calls to render its `texture { ... }` block.
        """

        def __init__(self):
            super().__init__()
            self.color = TimeVecN([1, 0, 0])
            self.transmit = TimeScalar(0)
            self.precision = 3
            self.finish = self.Finish()
            self.image_map = self.ImageMap()
            self.bump_map = self.BumpMap()

        def generate_texture_script(self, time):
            """Build this object's `texture { pigment { ... } normal { ... } finish { ... } }` block."""
            lines = ["texture{"]
            if self.image_map.path == "":
                lines.append(
                    "pigment{ color %s transmit %0.1f }"
                    % (self._color2str(self.color(time)), self.transmit(time))
                )
            else:
                lines.append(f"pigment{{ {self.image_map.generate_script()} }}")
            if self.bump_map.path != "":
                lines.append(self.bump_map.generate_script())
            lines.append(self.finish.generate_script(time))
            lines.append("}")
            return "\n".join(lines)

        color = _wrapped_property("color", TimeVecN, [0, 0, 0])
        transmit = _wrapped_property("transmit", TimeScalar, 0)

        @property
        def precision(self):
            return self._precision

        @precision.setter
        def precision(self, value):
            if not isinstance(value, int):
                raise TypeError("precision must be set to an integer value")
            if value <= 0:
                raise ValueError("precision must be greater than zero")
            self._precision = value

        @precision.deleter
        def precision(self):
            self._precision = None

        class ImageMap:
            """UV-mapped image texture (POV-Ray `image_map { ... }`)."""

            def __init__(self):
                self.path = ""
                self.extension = "png"
                self.type = 0

            @property
            def path(self):
                return self._path

            @path.setter
            def path(self, value):
                self.extension = _extension_from_path(value, "image map")
                self._path = value

            @path.deleter
            def path(self):
                self.path = ""

            @property
            def type(self):
                return self._type

            @type.setter
            def type(self, value):
                if not isinstance(value, int):
                    raise TypeError("image map type must be an integer")
                if value not in (0, 1, 2, 5):
                    raise ValueError(
                        "image map type must be one of the following: "
                        "0 (planar), 1 (spherical), 2 (cylindrical), 5 (torus)"
                    )
                self._type = value

            @type.deleter
            def type(self):
                self.type = 0

            def generate_script(self):
                return f"""image_map
                    {{ {self.extension} "{self.path}"
                        map_type {self.type}
                    }}
                """

        class BumpMap:
            """Bump/normal map texture (POV-Ray `normal { bump_map { ... } }`)."""

            def __init__(self):
                self.path = ""
                self.extension = "png"
                self.size = 0.1

            @property
            def path(self):
                return self._path

            @path.setter
            def path(self, value):
                self.extension = _extension_from_path(value, "bump map")
                self._path = value

            @path.deleter
            def path(self):
                self.path = ""

            @property
            def size(self):
                return self._size

            @size.setter
            def size(self, value):
                if not isinstance(value, Real):
                    raise TypeError("bump size must be a real number")
                if value <= 0:
                    raise ValueError("bump size must be a value greater than zero")
                self._size = value

            @size.deleter
            def size(self):
                # NOTE: originally `self.size = 0`, which routes through the
                # setter above and immediately raises ValueError (size must
                # be > 0). Reset to the __init__ default directly instead.
                self._size = 0.1

            def generate_script(self):
                return f"""
                    normal{{
                    bump_map
                    {{ {self.extension} "{self.path}"
                        bump_size {self.size}
                    }}
                    }}
                """

        class Finish:
            """POV-Ray `finish { ... }` block, including the nested
            `reflection { ... }` and `irid { ... }` sub-blocks."""

            def __init__(self):
                self.ambient = TimeScalar(0.1)
                self.diffuse = TimeScalar(0.6)
                self.brilliance = TimeScalar(1)
                self.roughness = TimeScalar(0.05)
                self.phong = TimeScalar(1)
                self.phong_size = TimeScalar(40)
                self.specular = TimeScalar(1)
                self.crand = TimeScalar(0)
                self.metallic = False
                self.reflection = TimeScalar(0)
                self.metallic_reflection = False
                self.iridescence = TimeScalar(0)
                self.iridescence_thickness = TimeScalar(0)
                self.iridescence_turbulence = TimeScalar(0)

            def generate_script(self, time):
                return f"""
                finish {{
                    ambient {self.ambient(time)}
                    diffuse {self.diffuse(time)}
                    brilliance {self.brilliance(time)}
                    specular {self.specular(time)}
                    roughness {self.roughness(time)}
                    phong {self.phong(time)}
                    phong_size {self.phong_size(time)}
                    crand {self.crand(time)}
                    {"metallic" if self.metallic else ""}
                    reflection {{
                    {self.reflection(time)}
                    {"metallic" if self.metallic_reflection else ""}
                    }}
                    irid {{
                    {self.iridescence(time)}
                    thickness {self.iridescence_thickness(time)}
                    turbulence {self.iridescence_turbulence(time)}
                    }}
                }}
                """

            ambient = _wrapped_property("ambient", TimeScalar, 0.1)
            diffuse = _wrapped_property("diffuse", TimeScalar, 0.6)
            brilliance = _wrapped_property("brilliance", TimeScalar, 1)
            roughness = _wrapped_property("roughness", TimeScalar, 0.05)
            phong = _wrapped_property("phong", TimeScalar, 1)
            phong_size = _wrapped_property("phong_size", TimeScalar, 40)
            specular = _wrapped_property("specular", TimeScalar, 1)
            crand = _wrapped_property("crand", TimeScalar, 0)
            metallic = _bool_property("metallic", default=False)
            reflection = _wrapped_property("reflection", TimeScalar, 0)
            metallic_reflection = _bool_property("metallic_reflection", default=False)
            iridescence = _wrapped_property("iridescence", TimeScalar, 0)
            iridescence_thickness = _wrapped_property(
                "iridescence_thickness", TimeScalar, 0
            )
            iridescence_turbulence = _wrapped_property(
                "iridescence_turbulence", TimeScalar, 0
            )

    def export(self, filename: str):
        with gzip.open(filename + ".gz", "wb") as file:
            dill.dump(
                [
                    self.objects,
                    self.cameras,
                    self.lights,
                    self._light_assign,
                    self.background,
                ],
                file,
            )

    @staticmethod
    def load(filename: str):
        with gzip.open(filename, "rb") as file:
            scene_attributes = dill.load(file)
        loaded_scene = Scene()
        for attribute_name, attribute in zip(
            ["objects", "cameras", "lights", "_light_assign", "background"],
            scene_attributes,
        ):
            setattr(loaded_scene, attribute_name, attribute)
        return loaded_scene

    def append(self, item):
        if not isinstance(item, Scene.Object):
            raise TypeError(
                "Objects appended to the Scene must be derived from the Scene.Object class"
            )
        self.objects.append(item)

    def render_frames(
        self,
        output_images_directory,
        times,
        name="time",
        WIDTH=1920,
        HEIGHT=1080,
        DISPLAY_FRAMES="Off",
    ):
        batch = []

        # Colect povray scripts for each camera
        for idx, camera in enumerate(self.cameras):
            view_name = camera.name
            output_path = os.path.join(output_images_directory, view_name)
            os.makedirs(output_path, exist_ok=True)
            light_ids = self._light_assign[idx] + self._light_assign[-1]

            # create script for each given time
            for frame_number, time in tqdm(enumerate(times), desc="Scripting"):
                frame_script = [self.background.generate_script(time)]

                # update and append camera
                camera.generate_script(time)
                frame_script.append(str(camera))

                # update and append lights
                for light_id in light_ids:  # Script Lightings
                    self.lights[light_id].generate_script(time)
                    frame_script.append(str(self.lights[light_id]))

                # append scene objects
                for scene_object in self.objects:
                    scene_object.generate_script(time)
                    frame_script.append(str(scene_object))

                pov_script = "\n".join(frame_script)
                # Write .pov script file
                file_path = os.path.join(
                    output_path, "{0}_{1:04d}".format(name, frame_number)
                )
                with open(file_path + ".pov", "w+") as f:
                    f.write(pov_script)
                batch.append(file_path)

        # Process POVray
        # For each frames, a 'png' image file is generated in OUTPUT_IMAGE_DIR directory.
        pbar = tqdm(total=len(batch), desc="Rendering")  # Progress Bar
        for filename in batch:
            render_povray(
                filename,
                width=WIDTH,
                height=HEIGHT,
                display=DISPLAY_FRAMES,
                pov_thread=multiprocessing.cpu_count(),
                transparency=self.background.transparent,
            )
            pbar.update()

    def render_video(
        self,
        output_images_directory,
        rendering_name,
        final_time,
        start_time=0,
        width=1920,
        height=1080,
        DISPLAY_FRAMES="Off",
        multiprocessing_flag: bool = False,
        threads_per_agent: int = 4,
        frames_per_second: int = 20,
    ):

        batch = []
        total_frames = int((final_time - start_time) * frames_per_second)

        # Colect povray scripts for each camera
        for idx, camera in enumerate(self.cameras):
            view_name = camera.name
            output_path = os.path.join(output_images_directory, view_name)
            os.makedirs(output_path, exist_ok=True)
            light_ids = self._light_assign[idx] + self._light_assign[-1]

            # create script for each frame
            for frame_number in tqdm(range(total_frames), desc="Scripting"):
                current_time = start_time + frame_number / frames_per_second
                frame_script = [self.background.generate_script(current_time)]

                # update and append camera
                camera.generate_script(current_time)
                frame_script.append(str(camera))

                # update and append lights
                for light_id in light_ids:  # Script Lightings
                    self.lights[light_id].generate_script(current_time)
                    frame_script.append(str(self.lights[light_id]))

                # append scene objects
                for scene_object in self.objects:
                    scene_object.generate_script(current_time)
                    frame_script.append(str(scene_object))

                pov_script = "\n".join(frame_script)
                # Write .pov script file
                file_path = os.path.join(
                    output_path, "frame_{:04d}".format(frame_number)
                )
                with open(file_path + ".pov", "w+") as f:
                    f.write(pov_script)
                batch.append(file_path)

        # Process POVray
        # For each frames, a 'png' image file is generated in OUTPUT_IMAGE_DIR directory.
        pbar = tqdm(total=len(batch), desc="Rendering")  # Progress Bar
        if multiprocessing_flag:
            n_agents = multiprocessing.cpu_count() // 2  # number of parallel rendering.
            func = partial(
                render_povray,
                width=width,
                height=height,
                display=DISPLAY_FRAMES,
                pov_thread=threads_per_agent,
                transparency=self.background.transparent,
            )
            with Pool(n_agents) as p:
                for message in p.imap_unordered(func, batch):
                    # (TODO) POVray error within child process could be an issue
                    pbar.update()
        else:
            for filename in batch:
                render_povray(
                    filename,
                    width=width,
                    height=height,
                    display=DISPLAY_FRAMES,
                    pov_thread=multiprocessing.cpu_count(),
                    transparency=self.background.transparent,
                )
                pbar.update()

        # Create Videos using ffmpeg
        for camera in self.cameras:
            view_name = camera.name
            imageset_path = os.path.join(output_images_directory, view_name)
            filename = rendering_name + "_" + view_name + ".mov"

            os.system(
                f"ffmpeg -y -r {frames_per_second} -i {imageset_path}/frame_%04d.png -c:v prores_ks -profile:v 4444 -pix_fmt yuva444p10le {filename}"
            )

    def render_interactive(
        self,
    ):
        return NotImplementedError
