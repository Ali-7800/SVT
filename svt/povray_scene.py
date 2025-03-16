import multiprocessing
import os
from functools import partial
from multiprocessing import Pool

import numpy as np
from scipy import interpolate
from tqdm import tqdm

from svt._povmacros import sphere_sweep,prism,sphere,cone,cylinder,plane,mesh,render
from svt.stage import Stage
from svt.appearence import DefaultAppearence

class PovrayScene(Stage):
    """ 
    This class creates a scene that can be used for rendering using POVray.
    The scene is initalized

    Notes
    -----
        PovrayScene requires POVray installed.
    """
    def __init__(
        self,
        FPS=20,
        appearence = DefaultAppearence(),
        ) -> None:

        self.appearence = appearence
        #initialize basic environment here
        self.pre_scripts = '''
        #version 3.6; // 3.7;
        #default{ finish{ ambient 0.1 diffuse 0.9 }}
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
        ''' + "background{"+"color rgb<{0},{1},{2}>".format(appearence.background_color[0],appearence.background_color[1],appearence.background_color[2])+"}"
        self.pre_scripts = ""
        Stage.__init__(self)
        self.FPS = FPS
        self.static_objects = []
        self.dynamic_objects = []
        
    def add_simulation_data(
        self,
        data:dict,):
        
        """
        Appends all objects in data from PovraySceneDataFile
        Parameters
        ----------
        data: dictionary
            Should contain data from a PovraySceneDataFile.
        appearence_functions: dictionary
            Should contact appearence functions for each object in data
        """

        self.times = data["times"]
        self.runtime = self.times.max()
        self.total_frame = int(self.runtime * self.FPS)  # Number of frames for the scene video
        self.times_true = np.linspace(0, self.runtime, self.total_frame)  # Adjusted timescale

        #add rod data
        if "rods_data" in data:
            rods_data = data["rods_data"]
            for rod_group_name in rods_data:
                rod_group_data = rods_data[rod_group_name]
                for rod_data in rod_group_data:
                    self.add_rod(
                        rod_data,
                        partial(self.appearence.rod_groups,rod_group_name),
                    )

        #add beam data
        if "beams_data" in data:
            beams_data = data["beams_data"]
            for beam_name in beams_data:
                beam_data = beams_data[beam_name]
                self.add_rectangular_beam(
                    beam_data,
                    partial(self.appearence.beam,beam_name),
                )

        #add static mesh data
        if "static_meshes_data" in data:
            meshes_data = data["static_meshes_data"]
            for mesh_name in meshes_data:
                mesh_data = meshes_data[mesh_name]
                self.add_mesh(
                    mesh_data,
                    partial(self.appearence.static_mesh,mesh_name),
                    static=True
                )

        #add dynamic mesh data
        if "dynamic_meshes_data" in data:
            meshes_data = data["dynamic_meshes_data"]
            for mesh_name in meshes_data:
                mesh_data = meshes_data[mesh_name]
                self.add_mesh(
                    mesh_data,
                    partial(self.appearence.dynamic_mesh,mesh_name),
                    static=False,
                )

        #add sphere data
        if "spheres_data" in data:
            spheres_data = data["spheres_data"]
            for sphere_name in spheres_data:
                sphere_data = spheres_data[sphere_name]
                self.add_sphere(
                    sphere_data,
                    partial(self.appearence.sphere,sphere_name),
                )

        #add cylinder data
        if "cylinders_data" in data:
            cylinders_data = data["cylinders_data"]
            for cylinder_name in cylinders_data:
                cylinder_data = cylinders_data[cylinder_name]
                self.add_cylinder(
                    cylinder_data,
                    partial(self.appearence.cylinder,cylinder_name),
                )


    def add_rod(self,
                rod_data,
                appearence_function,
                ):
        """
        Append rod dynamic object to povray scene.

        Parameters
        ----------
        rod_data: dictionary
            Should contain rod position and radius.
        appearence_function: function
            Should return values for rod color and transparency
        """

        rod_dynamic_object = [] #to store the rod povray scripts at each frame for later rendering
        rod_position = np.array(rod_data["position"])  # shape: (timelength, 3, num_element)
        rod_radius = np.array(rod_data["radius"])  # shape: (timelength, num_element)

        xs = interpolate.interp1d(self.times, rod_position, axis=0)(self.times_true)
        rs = interpolate.interp1d(self.times, rod_radius, axis=0)(self.times_true)

        for frame_number in range(self.total_frame):
            r,g,b,t = appearence_function(frame_number)
            rod_at_current_frame = sphere_sweep(
                xs[frame_number],
                rs[frame_number],
                color="rgb<{0},{1},{2}>".format(r,g,b),
                transmit=t,
                interpolation="linear_spline",
                deform=None,
                tab="    ",
            )
            rod_dynamic_object.append(rod_at_current_frame)
        self.dynamic_objects.append(rod_dynamic_object)
    
    def add_rectangular_beam(
                self,
                beam_data,
                appearence_function,
                ):
        """
        Append beam dynamic object to povray scene.

        Parameters
        ----------
        beam_data: dictionary
            Should contain beam node positions and element directors.
        appearence_function: function
            Should return values for rod color and transparency
        """

        beam_dynamic_object = [] #to store the beam povray scripts at each frame for later rendering
        beam_position = np.array(beam_data["position"])  # shape: (timelength, 3, num_element+1)
        beam_directors = np.array(beam_data["directors"]) # shape: (timelength, 3,3, num_element)

        xs = interpolate.interp1d(self.times, beam_position, axis=0)(self.times_true)
        Qs = interpolate.interp1d(self.times, beam_directors, axis=0)(self.times_true)
        n_elements = Qs.shape[-1]

        for frame_number in range(self.total_frame):
            r,g,b,t = appearence_function(frame_number)
            beam_elements_at_current_frame = []
            for i in range(n_elements):
                beam_elements_at_current_frame.append("\n")
                element_at_current_frame = prism(
                    xs[frame_number,:,i],
                    Qs[frame_number,:,:,i],
                    np.linalg.norm(xs[frame_number,:,i+1]-xs[frame_number,:,i]),
                    beam_data["width"],
                    beam_data["thickness"],
                    color="rgb<{0},{1},{2}>".format(r,g,b),
                    transmit=t,
                    interpolation="linear_spline",
                    tab="    ",
                )
                beam_elements_at_current_frame.append(element_at_current_frame)
            beam_at_current_frame = "\n".join(beam_elements_at_current_frame)
            beam_dynamic_object.append(beam_at_current_frame)
        self.dynamic_objects.append(beam_dynamic_object)

    def add_sphere(self,
                   sphere_data,
                   appearence_function,
                   static = False):
        
        if not static:
            sphere_dynamic_object = [] #to store the rod povray scripts at each frame for later rendering
            sphere_position = np.array(sphere_data["position"])  # shape: (timelength, 3)
            sphere_radius = np.array(sphere_data["radius"])  # shape: (timelength)

            xs = interpolate.interp1d(self.times, sphere_position, axis=0)(self.times_true)
            rs = interpolate.interp1d(self.times, sphere_radius, axis=0)(self.times_true)
            for frame_number in range(self.total_frame):
                r,g,b,t = appearence_function(frame_number)
                sphere_at_current_frame = sphere(
                xs[frame_number],
                rs[frame_number],
                color="rgb<{0},{1},{2}>".format(r,g,b),
                transmit=t,
                tab="    ",
                no_shadow = False,
                )
                sphere_dynamic_object.append(sphere_at_current_frame)
            self.dynamic_objects.append(sphere_dynamic_object)
        else:
            sphere_position = np.array(sphere_data["position"])  # shape: (3,)
            sphere_radius = sphere_data["radius"]  # float
            r,g,b,t = appearence_function(0)
            sphere_static_object = sphere(
                sphere_position,
                sphere_radius,
                color="rgb<{0},{1},{2}>".format(r,g,b),
                transmit=t,
                tab="    ",
                no_shadow = False,
                )
            self.static_objects.append(sphere_static_object)
            
    
    def add_cylinder(self,
                     cylinder_data,
                     appearence_function,
                     static = False,):
        if not static:
            cylinder_dynamic_object = [] #to store the rod povray scripts at each frame for later rendering
            cylinder_position = np.array(cylinder_data["position"])  # shape: (timelength, 2, 3)
            cylinder_radius = np.array(cylinder_data["radius"])  # shape: (timelength)

            xs = interpolate.interp1d(self.times, cylinder_position, axis=0)(self.times_true)
            rs = interpolate.interp1d(self.times, cylinder_radius, axis=0)(self.times_true)
            for frame_number in range(self.total_frame):
                r,g,b,t = appearence_function(frame_number)
                cylinder_at_current_frame = cylinder(
                                                    xs[frame_number,0,:],
                                                    xs[frame_number,1,:],
                                                    rs[frame_number],
                                                    color="rgb<{0},{1},{2}>".format(r,g,b),
                                                    transmit=t,
                                                    tab="    ",
                                                    no_shadow = False,
                                                    )
                cylinder_dynamic_object.append(cylinder_at_current_frame)
            self.dynamic_objects.append(cylinder_dynamic_object)
        else:
            cylinder_position = np.array(cylinder_data["position"])  # shape: (2,3)
            cylinder_radius = np.array(cylinder_data["radius"])  # float
            r,g,b,t = appearence_function(0)
            cylinder_static_object = cylinder(
                                            cylinder_position[0,:],
                                            cylinder_position[1,:],
                                            cylinder_radius,
                                            color="rgb<{0},{1},{2}>".format(r,g,b),
                                            transmit=t,
                                            tab="    ",
                                            no_shadow = False,
                                            )
            self.static_objects.append(cylinder_static_object)

    def add_cone(self,
                cone_data,
                appearence_function,
                static,
                ):
        pass

    def add_plane(self,
                plane,
                appearence_function,
                static,):
        pass
    
    def add_mesh(
        self,
        mesh_data,
        static=False,
        **kwargs):
        if not static:
            mesh_dynamic_object = [] #to store the rod povray scripts at each frame for later rendering
            mesh_face_indices = np.array(mesh_data["face_indices"])  # shape: (n_faces, 3)
            mesh_vertices = np.array(mesh_data["vertices"])  # shape: (timelength,n_vertices,3)
            # mesh_vertex_normals = np.array(mesh_data["vertex_normals"])  # shape: (timelength,n_vertices,3)
            # texture_vertices = np.array(mesh_data["texture_vertices"])  # shape: (timelength,n_vertices,2)
            mesh_vertices = interpolate.interp1d(self.times, mesh_vertices, axis=0)(self.times_true)
            mesh_vertex_normals = interpolate.interp1d(self.times, mesh_vertex_normals, axis=0)(self.times_true)
            for frame_number in range(self.total_frame):
                mesh_at_current_frame = mesh(
                    mesh_vertices[frame_number],
                    # texture_vertices,
                    # mesh_vertex_normals[frame_number],
                    mesh_face_indices,
                    **kwargs,
                )
                mesh_dynamic_object.append(mesh_at_current_frame)
            self.dynamic_objects.append(mesh_dynamic_object)
        else:
            mesh_face_indices = np.array(mesh_data["face_indices"])  # shape: (n_faces, 3)
            mesh_vertices = np.array(mesh_data["vertices"])  # shape: (n_vertices,3)
            # mesh_vertex_normals = np.array(mesh_data["vertex_normals"])  # shape: (n_vertices,3)
            # texture_vertices = np.array(mesh_data["texture_vertices"])  # shape: (n_vertices,2)
            mesh_static_object = mesh(
                    mesh_vertices,
                    # texture_vertices,
                    # mesh_vertex_normals,
                    mesh_face_indices,
                    **kwargs,
                )
            self.static_objects.append(mesh_static_object)

    def generate_camera_scripts(self):
        """
        Generate pov-ray script for all camera setup
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
            scripts[camera.name] = "\n".join(cmds)
        return scripts

    def render_frames(
                self,
                output_images_directory,
                frames,
                WIDTH = 1920,
                HEIGHT = 1080,
                DISPLAY_FRAMES = "Off",):
        batch = []
        stage_scripts = self.generate_camera_scripts()
        for view_name in stage_scripts.keys():  # Make Directory
            output_path = os.path.join(output_images_directory, view_name)
            os.makedirs(output_path, exist_ok=True)
        
        # Colect povray scripts
        for view_name, stage_script in stage_scripts.items():
            script = [stage_script] + self.static_objects.copy() #add static objects to current stage script
            output_path = os.path.join(output_images_directory, view_name)
            for frame_number in tqdm(frames, desc="Scripting"):
                frame_script = script.copy()
                for dynamic_object in self.dynamic_objects:
                    frame_script.append(dynamic_object[frame_number])

                pov_script = "\n".join(frame_script)
                # Write .pov script file
                file_path = os.path.join(output_path, "frame_{:04d}".format(frame_number))
                with open(file_path + ".pov", "w+") as f:
                    f.write(pov_script)
                batch.append(file_path)

        # Process POVray
        # For each frames, a 'png' image file is generated in OUTPUT_IMAGE_DIR directory.
        pbar = tqdm(total=len(batch), desc="Rendering")  # Progress Bar
        for filename in batch:
            render(
                filename,
                width=WIDTH,
                height=HEIGHT,
                display=DISPLAY_FRAMES,
                pov_thread=multiprocessing.cpu_count(),
            )
            pbar.update()

    def render_video(
                    self,
                    output_images_directory,
                    rendering_name,
                    WIDTH = 1920,
                    HEIGHT = 1080,
                    DISPLAY_FRAMES = "Off",
                    multiprocessing_flag=False,
                    threads_per_agent=4):
            
        batch = []
        stage_scripts = self.generate_camera_scripts()
        for view_name in stage_scripts.keys():  # Make Directory
            output_path = os.path.join(output_images_directory, view_name)
            os.makedirs(output_path, exist_ok=True)
        
        # Colect povray scripts
        for view_name, stage_script in stage_scripts.items():
            script = [stage_script] + self.static_objects.copy() #add static objects to current stage script
            output_path = os.path.join(output_images_directory, view_name)
            for frame_number in tqdm(range(self.total_frame), desc="Scripting"):
                frame_script = script.copy()
                for dynamic_object in self.dynamic_objects:
                    frame_script.append(dynamic_object[frame_number])

                pov_script = "\n".join(frame_script)
                # Write .pov script file
                file_path = os.path.join(output_path, "frame_{:04d}".format(frame_number))
                with open(file_path + ".pov", "w+") as f:
                    f.write(pov_script)
                batch.append(file_path)

        # Process POVray
        # For each frames, a 'png' image file is generated in OUTPUT_IMAGE_DIR directory.
        pbar = tqdm(total=len(batch), desc="Rendering")  # Progress Bar
        if multiprocessing_flag:
            n_agents = multiprocessing.cpu_count() // 2  # number of parallel rendering.
            func = partial(
                render,
                width=WIDTH,
                height=HEIGHT,
                display=DISPLAY_FRAMES,
                pov_thread=threads_per_agent,
            )
            with Pool(n_agents) as p:
                for message in p.imap_unordered(func, batch):
                    # (TODO) POVray error within child process could be an issue
                    pbar.update()
        else:
            for filename in batch:
                render(
                    filename,
                    width=WIDTH,
                    height=HEIGHT,
                    display=DISPLAY_FRAMES,
                    pov_thread=multiprocessing.cpu_count(),
                )
                pbar.update()

        # Create Videos using ffmpeg
        for view_name in stage_scripts.keys():
            imageset_path = os.path.join(output_images_directory, view_name)
            filename = rendering_name + "_" + view_name + ".mp4"

            os.system(f"ffmpeg -y -r {self.FPS} -i {imageset_path}/frame_%04d.png {filename}")
