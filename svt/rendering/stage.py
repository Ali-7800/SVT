from collections import defaultdict
from svt.rendering.utils import TimeVecN, sf
from numbers import Real


class Stage:
    """Stage definition

    Collection of the camera and light sources.
    Each camera added to the stage represent distinct viewpoints to render.
    Lights can be assigned to multiple cameras.

    Attributes
    ----------
    cameras : list
        List of camera setup
    lights : list
        List of lightings
    _light_assign : dictionary[list]
        Dictionary that pairs lighting to camera.
        Example) _light_assign[2] is the list of light sources
            assigned to the cameras[2]

    Methods
    -------
    add_camera : Add new camera (viewpoint) to the stage.
    add_light : Add new light source to the stage for a assigned camera.
    generate_scripts : Generate list of povray script for each camera.
    export: exports stage using pickle

    Class Objects
    -------------
    StageObject
    Camera
    Light
    """

    def __init__(self, background_color=(0, 0, 0, 0)):
        if len(background_color) != 4:
            raise ValueError("Must be an iterable with length 4")
        for component in background_color:
            if not (isinstance(component, Real) and 0 <= component <= 1):
                raise ValueError(
                    "All color values must be real numbers between 0 and 1"
                )

        bg = ",".join(str(c) for c in background_color)
        self.pre_scripts = f"""
        #version 3.6; // 3.7;
        #default{{ finish{{ ambient 0.1 diffuse 0.9 }}}}
        #include "colors.inc"
        #include "textures.inc"
        #include "glass.inc"
        #include "metals.inc"
        #include "golds.inc"
        #include "stones.inc"
        #include "woods.inc"
        #include "shapes.inc"
        #include "shapes2.inc"
        #include "functions.inc"
        #include "math.inc"
        #include "transforms.inc"
        background{{color rgbt<{bg}>}}
        """

        self.cameras = []
        self.lights = []
        self._light_assign = defaultdict(list)

    def add_camera(self, name, **kwargs):
        """Add camera (viewpoint)
        name: str
            Name of the view-point.
        location : list or tuple or callable
            Position vector of camera location. (length=3)
        angle : int
            Camera angle
        look_at : list or tuple or callable
            Position vector of the location where camera points to (length=3)
        sky : list or tuple or callable
            Tilt of the camera (length=3) [default=[0,1,0]]
        """
        camera_id = len(self.cameras)
        self.cameras.append(self.Camera(name=name, **kwargs))
        return camera_id

    def add_light(self, camera_id=-1, **kwargs):
        """Add lighting and assign to camera
        Parameters
        ----------
        camera_id : int or list
            Assigned camera. [default=-1]
            If a list of camera_id is given, light is assigned for listed camera.
            If camera_id==-1, the lighting is assigned for all camera.
        """
        light_id = len(self.lights)
        self.lights.append(self.Light(**kwargs))
        if isinstance(camera_id, (list, tuple)):
            for idx in set(camera_id):
                self._light_assign[idx].append(light_id)
        elif isinstance(camera_id, int):
            self._light_assign[camera_id].append(light_id)
        else:
            raise NotImplementedError("camera_id can only be a list, tuple, or int")

    # Stage Objects: Camera, Light
    class Object:
        """Template for stage objects

        Objects (camera and light) is defined as an object in order to
        manipulate (translate or rotate) them during the rendering.

        Attributes
        ----------
        str : str
            String representation of object.
            The placeholder exist to avoid rescripting.

        Methods
        -------
        _color2str : str
            Change triplet tuple (or list) of color into rgb string.
        _position2str : str
            Change triplet tuple (or list) of position vector into string.
        _fmt_floats, _fmt_ints, _pov_block : POV-Ray `mesh2` block builders
            (used by Mesh's generate_script).
        _fmt_vec, _primitive_script : POV-Ray primitive-block builders
            (used by Sphere, SphereSweep, Cylinder, Plane's generate_script).
        """

        def __init__(self):
            self.str = ""

        def generate_script(self, time):
            raise NotImplementedError

        def __str__(self):
            return self.str

        def _color2str(self, color):
            if isinstance(color, str):
                return color
            elif isinstance(color, list) and len(color) == 3:
                # RGB
                return "rgb<{},{},{}>".format(*color)
            else:
                raise NotImplementedError(
                    "Only string-type color or RGB input is implemented"
                )

        def _position2str(self, position):
            assert len(position) == 3
            return "<{},{},{}>".format(*position)

        # --- mesh2 block helpers (used by Mesh) -------------------------

        @staticmethod
        def _fmt_floats(values, precision=None):
            """Format a POV-Ray vector row, e.g. ',< 1.0,2.0,3.0>'."""
            if precision is not None:
                values = [sf(v, precision) for v in values]
            return ",< %s>" % ",".join("%f" % v for v in values)

        @staticmethod
        def _fmt_ints(values, extra=None):
            """Format a POV-Ray index row, optionally with a trailing color index."""
            row = ",< %s>" % ",".join("%d" % v for v in values)
            if extra is not None:
                row += ",%d" % extra
            return row

        @staticmethod
        def _pov_block(name, count, rows):
            """Assemble a 'name { count, row, row, ... }' POV-Ray block."""
            items = [f"\n{name} {{", f"\n{count}", *rows, "\n}"]
            return "\n".join(items)

        # --- primitive block helpers (used by Sphere, SphereSweep, ...) -

        @staticmethod
        def _fmt_vec(values, precision):
            """Format a bare POV-Ray vector literal, e.g. '<1.0,2.0,3.0>'."""
            return "<%s>" % ",".join(str(sf(v, precision)) for v in values)

        def _primitive_script(self, name, header_extra, rows, time):
            """Assemble a simple POV-Ray primitive block:
                name {
                    [header_extra]
                    row
                    row
                    ...
                    <texture>
                }
            `rows` are pre-formatted, tab-indented here.
            """
            tab = "    "
            lines = [f"{name} {{"]
            if header_extra is not None:
                lines.append(tab + header_extra)
            lines.extend(tab + row for row in rows)
            lines.append(self.generate_texture_script(time))
            lines.append(tab + "}\n")
            return "\n".join(lines)

    class Camera(Object):
        """Camera object

        http://www.povray.org/documentation/view/3.7.0/246/

        Attributes
        ----------
        location : list or tuple
            Position vector of camera location. (length=3)
        angle : int
            Camera angle
        look_at : list or tuple
            Position vector of the location where camera points to (length=3)
        name : str
            Name of the view-point.
        sky : list or tuple
            Tilt of the camera (length=3) [default=[0,1,0]]
        """

        def __init__(self, name, location, angle, look_at, sky=(0, 1, 0)):
            super().__init__()
            self.name = name
            self.location = TimeVecN(location)
            self.angle = angle
            self.look_at = TimeVecN(look_at)
            self.sky = TimeVecN(sky)

        def generate_script(self, time):
            location = self._position2str(self.location(time))
            look_at = self._position2str(self.look_at(time))
            sky = self._position2str(self.sky(time))
            self.str = "\n".join(
                [
                    "camera{",
                    f"    location {location}",
                    f"    angle {self.angle}",
                    f"    look_at {look_at}",
                    f"    sky {sky}",
                    "    right -x*image_width/image_height",
                    "}",
                ]
            )

    class Light(Object):
        """Light object

        Attributes
        ----------
        location : list or tuple
            Position vector of light location. (length=3)
        color : str or list
            Color of the light.
            Both string form of color or rgb (normalized) form is supported.
            Example) color='White', color=[1,1,1]
        """

        def __init__(self, location, color):
            self.location = TimeVecN(location)
            self.color = TimeVecN(color)
            super().__init__()

        def generate_script(self, time):
            location = self._position2str(self.location(time))
            color = self._color2str(self.color(time))
            self.str = "\n".join(
                [
                    "light_source{",
                    f"    {location}",
                    f"    color {color}",
                    "}",
                ]
            )
