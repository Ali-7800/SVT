from collections import defaultdict
from typing import Any
import numpy as np
class Stage:
    """Stage definition

    Collection of the camera and light sources.
    Each camera added to the stage represent distinct viewpoints to render.
    Lights can be assigned to multiple cameras.

    (TODO) Implement transform camera for dynamic camera moves
    (TODO) make stage less Povray oriented

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

    Class Objects
    -------------
    StageObject
    Camera
    Light


    """

    def __init__(self):
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

        def generate_script(self,frame):
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
        
        class Vec3:
            """
            3D vector object, for defining stage position, directions, and colors in time.
            Attributes
            ----------
            vec : callable or iterable
                Must either be a length 3 iterable of floats or returns a length 3 iterable of floats
            """
            def __init__(self,vec) -> None:
                if callable(vec):
                    assert len(vec(0)) == 3,"callable Vec3 must return an object of length 3"
                    self.vec = vec
                else:
                    try:
                        assert len(vec) == 3,"static Vec3 must be an object of length 3"
                        self.vec = lambda frame:vec
                    except TypeError:
                        raise TypeError("Vec3 input must be either be a length 3 iterable of floats or returns a length 3 iterable of floats")
            
            def __call__(self, frame) -> Any:
                return self.vec(frame)
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
            super().__init__()
            self.name = name
            self.location = self.Vec3(location)
            self.angle = angle
            self.look_at = self.Vec3(look_at)
            self.sky = self.Vec3(sky)

        def generate_script(self,frame):
            location = self._position2str(self.location(frame))
            look_at = self._position2str(self.look_at(frame))
            sky = self._position2str(self.sky(frame))
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
            self.location = self.Vec3(location)
            self.color = self.Vec3(color)
            super().__init__()

        def generate_script(self,frame):
            location = self._position2str(self.location(frame))
            color = self._color2str(self.color(frame))
            cmds = []
            cmds.append("light_source{")
            cmds.append(f"    {location}")
            cmds.append(f"    color {color}")
            cmds.append("}")
            self.str = "\n".join(cmds)
