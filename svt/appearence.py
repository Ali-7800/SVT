"""
This module includes utility functions to support POVray rendering.
"""
class DefaultAppearence:
    """
    DefaultAppearence defines the default appearence functions of all scene objects.
    Any appearence class should be derived from it.

    Attributes
    ----------
    background_color: list
        [r,g,b] values for the background color

    Methods
    -------
    rod_groups : 
        returns r,g,b,t values for a rod group at each frame
    beam_appearence : 
        returns r,g,b,t values for a beam at each frame
    static_mesh_appearence : callable
        returns r,g,b,t values for a static mesh at each frame
    dynamic_mesh_appearence : callable
        returns r,g,b,t values for a dynamic mesh at each frame
    sphere_appearence: callable
        returns r,g,b,t values for a sphere at each frame
    cylinder_appearence: callable
        returns r,g,b,t values for a cylinder at each frame

    """
    def __init__(self) -> None:
        self.background_color = [1,1,1]

    def rod_groups(self,name,frame):
        return 0.45,0.39,1,0
    
    def beam(self,name,frame):
        return 1,1,1,0
    
    def static_mesh(self,name,frame):
        return 1,1,1,0
    
    def dynamic_mesh(self,name,frame):
        return 1,1,1,0
    
    def sphere(self,name,frame):
        return 1,0,0,0
    
    def cylinder(self,name,frame):
        return 1,0,0,0
    