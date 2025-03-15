import numpy as np
import os
import pickle

class DataFile:
    def __init__(self,name:str,time:np.ndarray):
        self.name = name
        self.time = time
        self.rod_groups = []
        self.rectangular_beams = []
        self.mesh_surfaces = []
        self.mesh_rigid_bodies = []
        self.spheres = []
        self.cylinders = []
    
    def add_rod_group(self,group_name:str,post_processing_dict_list:list):
        for i,post_processing_dict in enumerate(post_processing_dict_list):
            try:
                assert "position" in post_processing_dict
            except:
                raise("Rod {0}'s post processing dictionary does not have position data, make sure 'position' is a key in the dictionary".format(i))
            try:
                assert "radius" in post_processing_dict
            except:
                raise("Rod {0}'s post processing dictionary does not have radius data, make sure 'radius' is a key in the dictionary".format(i))
        self.rod_groups.append((group_name,post_processing_dict_list))
    
    def add_rectangular_beams(self,group_name:str,post_processing_dict:list,width:float,thickness:float):
        try:
            assert "position" in post_processing_dict
        except:
            raise("Beam's post processing dictionary does not have position data, make sure 'position' is a key in the dictionary")
        try:
            assert "radius" in post_processing_dict
        except:
            raise("Beam's post processing dictionary does not have radius data, make sure 'radius' is a key in the dictionary")
        try:
            assert "directors" in post_processing_dict
        except:
            raise("Beam's post processing dictionary does not have director data, make sure 'directors' is a key in the dictionary")        
        self.rectangular_beams.append((group_name,post_processing_dict,width,thickness))
    
    def add_static_mesh(self,name:str,mesh:object):
        try:
            assert hasattr(mesh, 'vertices')
        except AssertionError:
            raise("given mesh object does not have vertices")
        try:
            assert hasattr(mesh, 'vertex_normals')
        except AssertionError:
            raise("given mesh object does not have vertex normals")
        try:
            assert hasattr(mesh, 'texture_vertices')
        except AssertionError:
            raise("given mesh object does not have texture vertices")
        try:
            assert hasattr(mesh, 'face_indices')
        except AssertionError:
            raise("given mesh object does not have face indices")
        self.mesh_surfaces.append((name,mesh))
    
    def add_dynamic_mesh(self,name:str,mesh:object,post_processing_dict:dict):
        try:
            assert hasattr(mesh, 'texture_vertices')
        except AssertionError:
            raise("given mesh object does not have texture vertices")
        try:
            assert hasattr(mesh, 'face_indices')
        except AssertionError:
            raise("given mesh object does not have face indices")
        try:
            assert "vertices" in post_processing_dict
        except:
            raise("given mesh post processing dictionary does not have vertices")
        try:
            assert "vertex_normals" in post_processing_dict
        except:
            raise("given mesh post processing dictionary does not have vertex normals")
        self.mesh_rigid_bodies.append((name,mesh,post_processing_dict))
    
    def add_sphere(self,name:str,post_processing_dict:dict):
        try:
            assert "position" in post_processing_dict
        except:
            raise("given sphere post processing dictionary does not have position data, make sure 'position' is a key in the dictionary")
        try:
            assert "radius" in post_processing_dict
        except:
            raise("given sphere post processing dictionary does not have radius data, make sure 'radius' is a key in the dictionary")
        self.spheres.append((name,post_processing_dict))

    def add_cylinder(self,name:str,post_processing_dict:dict):
        try:
            assert "position" in post_processing_dict
        except:
            raise("given cylinder post processing dictionary does not have position data, make sure 'position' is a key in the dictionary")
        try:
            assert "radius" in post_processing_dict
        except:
            raise("given cylinder post processing dictionary does not have radius data, make sure 'radius' is a key in the dictionary")
        self.cylinders.append((name,post_processing_dict))
    
    def save_to(self,folder:str):
        pass


class PovraySceneDataFile(DataFile):
    def __init__(self, name:str, time:np.ndarray):
        DataFile.__init__(self,name,time)

    def save_to(self, folder: str):
        # Save data as npz file
        data = {}
        data["time"] = np.array(self.time)
        
        #add rod data
        rod_data = {}
        for rod_group_name,rod_group in self.rod_groups:
            rod_group_data = []
            for rod_dict in rod_group:
                rod_data = {}
                rod_data["position"] = rod_dict["position"]
                rod_data["radius"] = rod_dict["radius"]
                rod_group_data.append(rod_data)
            rod_data[rod_group_name] = rod_group_data
        
        #add beam data
        beam_data = {}
        for beam_name,beam_dict,width,thickness in self.rectangular_beams:
            beam_data = {}
            beam_data["position"] = beam_dict["position"]
            beam_data["radius"] = beam_dict["radius"]
            beam_data["directors"] = beam_dict["directors"]
            beam_data["width"] = width
            beam_data["thickness"] = thickness
            beam_data[beam_name] = beam_data
        
        #add mesh surface data
        for mesh_name,mesh in self.mesh_surfaces:
            mesh_surface_data = {}
            mesh_surface_data["vertices"] = np.array(mesh.vertices)
            mesh_surface_data["texture_vertices"] = np.array(mesh.texture_vertices)
            mesh_surface_data["vertex_normals"] = np.array(mesh.vertex_normals)
            mesh_surface_data["face_indices"] = np.array(mesh.face_indices)
            data[mesh_name] = mesh_surface_data

        #add mesh rigid body data
        for mesh_name,mesh,mesh_dict in self.mesh_rigid_bodies:
            mesh_rigid_body_data = {}
            mesh_rigid_body_data["vertices"] = mesh_dict["vertices"]
            mesh_rigid_body_data["vertex_normals"] = mesh_dict["vertex_normals"]
            mesh_rigid_body_data["texture_vertices"] = np.array(mesh.texture_vertices)
            mesh_rigid_body_data["face_indices"] = np.array(mesh.face_indices)
            data[mesh_name] = mesh_surface_data

        #add sphere data
        for sphere_name,sphere_dict in self.spheres:
            sphere_data = {}
            sphere_data["position"] = sphere_dict["position"]
            sphere_data["radius"] = sphere_dict["radius"]
            data[sphere_name] = sphere_data
        
        #add cylinder data
        for cylinder_name,cylinder_dict in self.cylinders:
            cylinder_data = {}
            cylinder_data["position"] = cylinder_dict["position"]
            cylinder_data["radius"] = cylinder_dict["radius"]
            data[cylinder_name] = cylinder_data
        
        save_file = os.path.join(folder, self.name+".dat")
        if os.path.exists(save_file):
            os.remove(save_file)
        else:
            os.makedirs(os.path.dirname(save_file), exist_ok=True)
        file = open(save_file, "wb")
        pickle.dump(data, file)
        file.close()
        
class RhinoSceneDataFile(DataFile):
    def __init__(self, name:str, time:np.ndarray):
        DataFile.__init__(self,name,time)

    #TODO:finish implementing this
    # def save_muscle_rods_rhino(post_processing_dict_list,filename,save_folder):
    #     # Save data as npz file
    #     time = np.array(post_processing_dict_list[0]["time"])
    #     n_elem = np.array(post_processing_dict_list[0]["position"]).shape[-1]
    #     n_rods = len(post_processing_dict_list)

    #     position_history = np.zeros(
    #         (n_rods, time.shape[0], 3, n_elem + 1)
    #     )
    #     radius_history = np.zeros((n_rods, time.shape[0], n_elem))

    #     for i in range(n_rods):
    #         position_history[i, :, :, :] = np.array(
    #             post_processing_dict_list[i]["position"]
    #         )
    #         radius_history[i, :, :] = np.array(
    #             post_processing_dict_list[i]["radius"]
    #         )

    #     np.savez(
    #             os.path.join(save_folder, filename),
    #             time=time,
    #             position_history=position_history,
    #             radius_history=radius_history,
    #         )

class ThreeJSSceneDataFile(DataFile):
    def __init__(self, name:str, time:np.ndarray):
        DataFile.__init__(self,name,time)
    #TODO:finish implementing this
