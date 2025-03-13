"""
This module includes utility functions to support POVray rendering.
"""

def constant_appearence_function(r,g,b,t):
    def constant_appearence(frame):
        return r,g,b,t
    return constant_appearence