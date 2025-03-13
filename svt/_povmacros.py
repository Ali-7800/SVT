""" POVray macros for mesh_pyelastica

This module includes utility methods to support POVray rendering.

"""

import subprocess
from collections import defaultdict
import numpy as np


def sphere_sweep(
    x,
    r,
    color="rgb<0.45,0.39,1>",
    transmit=0.0,
    interpolation="linear_spline",
    deform=None,
    tab="    ",
):
    """sphere sweep POVray script generator

    Generates povray sphere_sweep object in string.
    The sphere_sweep is given with the sphere radii (r) and positions (x)

    Parameters
    ----------
    x : numpy array
        Position vector
        Expected shape: [3, num_element]
    r : numpy array
        Radius vector
        Expected shape: [num_element]
    color : str
        Color of the rod (default: Purple <0.45,0.39,1>)
    transmit : float
        Transparency (0.0 to 1.0).
    interpolation : str
        Interpolation method for sphere_sweep
        Supporting type: 'linear_spline', 'b_spline', 'cubic_spline'
        (default: linear_spline)
    deform : str
        Additional object deformation
        Example: "scale<4,4,4> rotate<0,90,90> translate<2,0,4>"

    Returns
    -------
    cmd : string
        Povray script
    """

    assert interpolation in ["linear_spline", "b_spline", "cubic_spline"]
    tab = "    "

    # Parameters
    num_element = r.shape[0]

    lines = []
    lines.append("sphere_sweep {")
    lines.append(tab + f"{interpolation} {num_element}")
    for i in range(num_element):
        lines.append(tab + f",<{x[0,i]},{x[1,i]},{x[2,i]}>,{r[i]}")
    lines.append(tab + "texture{")
    lines.append(tab + tab + "pigment{ color %s transmit %f }" % (color, transmit))
    lines.append(tab + tab + "finish{ phong 1 }")
    lines.append(tab + "}")
    if deform is not None:
        lines.append(tab + deform)
    lines.append(tab + "}\n")

    cmd = "\n".join(lines)
    return cmd

def prism(
    x,
    directors,
    a,
    b,
    c,
    color="rgb<0.45,0.39,1>",
    transmit=0.0,
    interpolation="linear_spline",
    tab="    ",
):
    """A prism POVray script generator

    Generates povray prism object in string.
    Parameters
    ----------
    x : numpy array
        start position vector
        Expected shape: [3]
    director : numpy array
        Expected shape: [3,3]
    a : float
        length value
    b : float
        width value
    c : float
        thickeness value
    color : str
        Color of the rod (default: Purple <0.45,0.39,1>)
    transmit : float
        Transparency (0.0 to 1.0).
    interpolation : str
        Interpolation method for sphere_sweep
        Supporting type: 'linear_spline', 'b_spline', 'cubic_spline'
        (default: linear_spline)

    Returns
    -------
    cmd : string
        Povray script
    """
    assert interpolation in ["linear_spline", "b_spline", "cubic_spline"]
    tab = "    "
    

    lines = []
    directors = np.array([[1,0,0],[0,0,-1],[0,1,0]])@directors #rotate directors for POVray y up frame
    lines.append("prism {")
    lines.append(tab + "linear_sweep")
    lines.append(tab + f"{interpolation}")
    lines.append(tab + "0,")
    lines.append(tab + f"{a},") #length
    lines.append(tab + "5,") #number of points in shape
    lines.append(tab + f"<{b/2},{c/2}>,") #point 1
    lines.append(tab + f"<{-b/2},{c/2}>,") #point 2
    lines.append(tab + f"<{-b/2},{-c/2}>,") #point 3
    lines.append(tab + f"<{b/2},{-c/2}>,") #point 4
    lines.append(tab + f"<{b/2},{c/2}>") #point 1
    lines.append(tab + f"matrix <{directors[0,0]}, {directors[0,1]}, {directors[0,2]},")
    lines.append(tab + f"{directors[1,0]}, {directors[1,1]}, {directors[1,2]},")
    lines.append(tab + f"{directors[2,0]}, {directors[2,1]}, {directors[2,2]},")
    lines.append(tab + f"0, 0, 0 >")
    lines.append(tab + f"translate <{x[0]},{x[1]},{x[2]}>") #start point
    lines.append(tab + "texture{")
    lines.append(tab + tab + "pigment{ color %s transmit %f }" % (color, transmit))
    lines.append(tab + tab + "finish{ phong 1 }")
    lines.append(tab + "}")
    lines.append(tab + "}\n")
    cmd = "\n".join(lines)
    return cmd


def sphere(
    x,
    r,
    color="rgb<0.45,0.39,1>",
    transmit=0.0,
    tab="    ",
    no_shadow = False,
):
    """Sphere POVray script generator

    Generates povray sphere object in string.
    The sphere is given with the radius (r) and position (x)

    Parameters
    ----------
    x : numpy array
        Position vector
        Expected shape: [3]
    r : float
        Sphere radius
        Expected shape: float
    color : str
        Color of the sphere (default: Purple <0.45,0.39,1>)
    transmit : float
        Transparency (0.0 to 1.0).

    Returns
    -------
    cmd : string
        Povray script
    """

    tab = "    "

    # Parameters
    lines = []
    lines.append("sphere {")
    lines.append(tab + f"<{x[0]},{x[1]},{x[2]}>,{r}")
    lines.append(tab + "texture{")
    lines.append(tab + tab + "pigment{ color %s transmit %f }" % (color, transmit))
    lines.append(tab + tab + "finish{ phong 1 }")
    if no_shadow is True:
            lines.append(tab + "no_shadow")
    lines.append(tab + "}")
    lines.append(tab + "}\n")

    cmd = "\n".join(lines)
    return cmd

def cylinder(
    x1,
    x2,
    r,
    color="rgb<0.45,0.39,1>",
    transmit=0.0,
    tab="    ",
    no_shadow = False,
):
    """cylinder POVray script generator

    Generates povray cylinder object in string.
    The cylinder is given with the radius (r) and positions (x1) and (x2)

    Parameters
    ----------
    x1 : numpy array
        Position vector for cylinder start point
        Expected shape: [3]
    x2 : numpy array
        Position vector for cylinder end point
        Expected shape: [3]
    r : float
        cylinder radius
        Expected shape: float
    color : str
        Color of the cylinder (default: Purple <0.45,0.39,1>)
    transmit : float
        Transparency (0.0 to 1.0).

    Returns
    -------
    cmd : string
        Povray script
    """

    tab = "    "

    # Parameters
    lines = []
    lines.append("cylinder {")
    lines.append(tab + f"<{x1[0]},{x1[1]},{x1[2]}>,<{x2[0]},{x2[1]},{x2[2]}>,{r}")
    lines.append(tab + tab + "pigment{ color %s transmit %f }" % (color, transmit))
    if no_shadow is True:
            lines.append(tab + "no_shadow")
    lines.append(tab + "}\n")

    cmd = "\n".join(lines)
    return cmd

def cone(
    x1,
    x2,
    r1,
    r2,
    color="rgb<0.45,0.39,1>",
    transmit=0.0,
    tab="    ",
    no_shadow = False,
):
    """cone POVray script generator

    Generates povray cone object in string.
    The cone is given with the radii (r1) and (r2) and positions (x1) and (x2)

    Parameters
    ----------
    x1 : numpy array
        Position vector for cone base
        Expected shape: [3]
    x2 : numpy array
        Position vector for cone top
        Expected shape: [3]
    r1 : float
        cone start radius
        Expected shape: float
    r2 : float
        cone end radius
        Expected shape: float
    color : str
        Color of the cone (default: Purple <0.45,0.39,1>)
    transmit : float
        Transparency (0.0 to 1.0).

    Returns
    -------
    cmd : string
        Povray script
    """

    tab = "    "

    # Parameters
    lines = []
    lines.append("cone {")
    lines.append(tab + f"<{x1[0]},{x1[1]},{x1[2]}>,{r1},<{x2[0]},{x2[1]},{x2[2]}>,{r2}")
    lines.append(tab + tab + "pigment{ color %s transmit %f }" % (color, transmit))
    if no_shadow is True:
            lines.append(tab + "no_shadow")
    lines.append(tab + "}\n")

    cmd = "\n".join(lines)
    return cmd

def plane(
    normal = "z",
    shift = 0.0,
    image = None,
    clipped_by = None,
    tab="    ",
):
    """Plane POVray script generator

    Generates povray Plane object in string.
    The plane is given with a normal vector and shift with respect to that position

    Parameters
    ----------
    normal : str
        normal vector
        Expected shape: <N1,N2,N3>, or just one of x, y, or z
    shift : float
        plane shift
        Expected shape: float
    image : str
        Image path
    clipped_by: str
        povray object to clip the plane by
        Example: sphere{ <-3,2,0>, 2 }

    Returns
    -------
    cmd : string
        Povray script
    """

    tab = "    "

    # Parameters
    lines = []
    lines.append("plane {")
    lines.append(tab + normal+","+str(shift))
    if clipped_by is not None:
        lines.append(tab +"clipped_by{")
        lines.append(tab + tab +clipped_by)
        lines.append(tab + "}")
    if image is not None:
        lines.append(tab + "pigment{")
        lines.append(tab+tab+'image_map {jpeg "' +image +'"}')
        lines.append(tab + "}")
    else:
        lines.append(tab + tab + "pigment{ color %s transmit %f }" % ("<0.5,0.5,0.5>", 0.8))

    lines.append(tab + "}\n")

    cmd = "\n".join(lines)
    return cmd

def mesh(
        vertices,
        faces_indices,
        **kwargs,
    ):
        n_faces = faces_indices.shape[0]

        mesh_list = []
        mesh_list.append("mesh2 {")
        n_vertices = vertices.shape[0]

        vertex_list = []
        normals_list = []
        face_indices_list = []
        color_mapping = []
        uv_vectors_list = []
        uv_indices_list = []
        texture_mapping = []

        vertex_list.append("\nvertex_vectors {")
        vertex_list.append("\n" + str(n_vertices))
        for i in range(n_vertices):
            vertex_list.append(
                ",<"
                + str(vertices[i, 0])
                + ","
                + str(vertices[i, 1])
                + ","
                + str(vertices[i, 2])
                + ">"
            )
        vertex_list.append("\n}")

        if "vertex_normals" in kwargs:
            normals_list.append("\nnormal_vectors {")
            normals_list.append("\n" + str(n_vertices))
            for i in range(n_vertices):
                normals_list.append(
                    ",<"
                    + str(vertex_normals[i, 0])
                    + ","
                    + str(vertex_normals[i, 1])
                    + ","
                    + str(vertex_normals[i, 2])
                    + ">"
                )
            normals_list.append("\n}")

        face_indices_list.append("\nface_indices {")
        face_indices_list.append("\n" + str(n_faces))
        for i in range(n_faces):
            face_indices_list.append(
                ",<"
                + str(faces_indices[i, 0])
                + ","
                + str(faces_indices[i, 1])
                + ","
                + str(faces_indices[i, 2])
                + ">"
            )
        face_indices_list.append("\n}")

        if "texture_path" in kwargs:
            uv_vectors_list.append("\nuv_vectors {")
            uv_vectors_list.append("\n" + str(n_vertices))
            for i in range(n_vertices):
                uv_vectors_list.append(
                    ",<"
                    + str(texture_vertices[i, 0])
                    + ","
                    + str(texture_vertices[i, 1])
                    + ">"
                )
            uv_vectors_list.append("\n}")

            uv_indices_list.append("\nuv_indices {")
            uv_indices_list.append("\n" + str(n_faces))
            for i in range(n_faces):
                uv_indices_list.append(
                    ",<"
                    + str(faces_indices[i, 0])
                    + ","
                    + str(faces_indices[i, 1])
                    + ","
                    + str(faces_indices[i, 2])
                    + ">"
                )
            uv_indices_list.append("\n}")
            texture_mapping.append(
                '\ntexture {\npigment {\nuv_mapping \nimage_map {\njpeg "'
                + kwargs.get("texture_path")
                + '" \nmap_type 0\n}\n}'
            )
            if "normal_path" in kwargs:
                texture_mapping.append(
                    '\nnormal {\nuv_mapping \nbump_map { \njpeg "'
                    + kwargs.get("normal_path")
                    + '" \nmap_type 0\nbump_size 50\n}\n}'
                )
            texture_mapping.append("\n}")
        elif "color" in kwargs:
            color = kwargs.get("color")
            color_mapping.append(
                "\npigment { color rgbt <"
                + str(color[0])
                + ","
                + "{0},{1},{2}>".format(color[1], color[2], color[3])
                + "}"
            )
        else:
            raise("Please include a texture_path or an rgbt color")

        mesh_list += (
            vertex_list
            + normals_list
            + uv_vectors_list
            + face_indices_list
            + uv_indices_list
            + texture_mapping
            + color_mapping
        )
        mesh_list.append("\n}")
        mesh_str ="\n".join(mesh_list)
        return mesh_str


def render(
    filename, width, height, antialias="on", quality=11, display="Off", pov_thread=4
):
    """Rendering frame

    Generate the povray script file '.pov' and image file '.png'
    The directory must be made before calling this method.

    Parameters
    ----------
    filename : str
        POV filename (without extension)
    width : int
        The width of the output image.
    height : int
        The height of the output image.
    antialias : str ['on', 'off']
        Turns anti-aliasing on/off [default='on']
    quality : int
        Image output quality. [default=11]
    display : str
        Turns display option on/off during POVray rendering. [default='off']
    pov_thread : int
        Number of thread per povray process. [default=4]
        Acceptable range is (4,512).
        Refer 'Symmetric Multiprocessing (SMP)' for further details
        https://www.povray.org/documentation/3.7.0/r3_2.html#r3_2_8_1

    Raises
    ------
    IOError
        If the povray run causes unexpected error, such as parsing error,
        this method will raise IOerror.

    """

    # Define script path and image path
    script_file = filename + ".pov"
    image_file = filename + ".png"

    # Run Povray as subprocess
    cmds = [
        "povray",
        "+I" + script_file,
        "+O" + image_file,
        f"-H{height}",
        f"-W{width}",
        f"Work_Threads={pov_thread}",
        f"Antialias={antialias}",
        f"Quality={quality}",
        f"Display={display}",
    ]
    process = subprocess.Popen(
        cmds, stderr=subprocess.PIPE, stdin=subprocess.PIPE, stdout=subprocess.PIPE
    )
    _, stderr = process.communicate()

    # Check execution error
    if process.returncode:
        print(type(stderr), stderr)
        raise IOError(
            "POVRay rendering failed with the following error: "
            + stderr.decode("ascii")
        )

class Stage:
    """Stage definition

    Collection of the camera and light sources.
    Each camera added to the stage represent distinct viewpoints to render.
    Lights can be assigned to multiple cameras.
    The povray script can be generated for each viewpoints created using 'generate_scripts.'

    (TODO) Implement transform camera for dynamic camera moves

    Attributes
    ----------
    pre_scripts : str
        Prepending script for all viewpoints
    post_scripts : str
        Appending script for all viewpoints
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

    Class Objects
    -------------
    StageObject
    Camera
    Light

    Properties
    ----------
    len : number of camera
        The number of viewpoints
    """

    def __init__(self, pre_scripts="", post_scripts=""):
        self.pre_scripts = pre_scripts
        self.post_scripts = post_scripts
        self.cameras = []
        self.lights = []
        self._light_assign = defaultdict(list)

    def add_camera(self, name, **kwargs):
        """Add camera (viewpoint)"""
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
        if isinstance(camera_id, list) or isinstance(camera_id, tuple):
            camera_id = list(set(camera_id))
            for idx in camera_id:
                self._light_assign[idx].append(light_id)
        elif isinstance(camera_id, int):
            self._light_assign[camera_id].append(light_id)
        else:
            raise NotImplementedError("camera_id can only be a list or int")

    def generate_scripts(self):
        """Generate pov-ray script for all camera setup
        Returns
        -------
        scripts : list
            Return list of pov-scripts (string) that includes camera and assigned lightings.
        """
        scripts = {}
        for idx, camera in enumerate(self.cameras):
            light_ids = self._light_assign[idx] + self._light_assign[-1]
            cmds = []
            cmds.append(self.pre_scripts)
            cmds.append(str(camera))  # Script camera
            for light_id in light_ids:  # Script Lightings
                cmds.append(str(self.lights[light_id]))
            cmds.append(self.post_scripts)
            scripts[camera.name] = "\n".join(cmds)
        return scripts

    def transform_camera(self, dx, R, camera_id):
        # (TODO) translate or rotate the assigned camera
        raise NotImplementedError

    def __len_(self):
        return len(self.cameras)

    # Stage Objects: Camera, Light
    class StageObject:
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
        """

        def __init__(self):
            self.str = ""
            self.update_script()

        def update_script(self):
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

    class Camera(StageObject):
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
            self.name = name
            self.location = location
            self.angle = angle
            self.look_at = look_at
            self.sky = sky
            super().__init__()

        def update_script(self):
            location = self._position2str(self.location)
            look_at = self._position2str(self.look_at)
            sky = self._position2str(self.sky)
            cmds = []
            cmds.append("camera{")
            cmds.append(f"    location {location}")
            cmds.append(f"    angle {self.angle}")
            cmds.append(f"    look_at {look_at}")
            cmds.append(f"    sky {sky}")
            cmds.append("    right x*image_width/image_height")
            cmds.append("}")
            self.str = "\n".join(cmds)

    class Light(StageObject):
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
            self.location = location
            self.color = color
            super().__init__()

        def update_script(self):
            location = self._position2str(self.location)
            color = self._color2str(self.color)
            cmds = []
            cmds.append("light_source{")
            cmds.append(f"    {location}")
            cmds.append(f"    color {color}")
            cmds.append("}")
            self.str = "\n".join(cmds)
