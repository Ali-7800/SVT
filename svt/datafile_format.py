import numpy as np
import os
import pickle
from svt._check import Check

class SceneDataFile:
    def __init__(self,name:str,times=None):
        self.name = name
        self.times = times
        self.data = {}
        self.rod_groups = []
        self.rectangular_beams = []
        self.static_meshes = []
        self.dynamic_meshes = []
        self.spheres = []
        self.cylinders = []
    
    def add_times(self,times:np.ndarray):
        self.times = times

    def add_rod_group(self,group_name:str,post_processing_dict_list:list):
        for i,post_processing_dict in enumerate(post_processing_dict_list):
            Check.condition(
                "position" in post_processing_dict,
                KeyError,
                "Rod {0}'s post processing dictionary does not have position data, make sure 'position' is a key in the dictionary".format(i))
            Check.condition(
                "radius" in post_processing_dict,
                KeyError,
                "Rod {0}'s post processing dictionary does not have radius data, make sure 'radius' is a key in the dictionary".format(i))
        self.rod_groups.append((group_name,post_processing_dict_list))
    
    def add_rectangular_beam(self,name:str,post_processing_dict:list,width:float,thickness:float):
        Check.condition(
            "position" in post_processing_dict,
            KeyError,
            "Beam's post processing dictionary does not have position data, make sure 'position' is a key in the dictionary")
        Check.condition(
            "radius" in post_processing_dict,
            KeyError,
            "Beam's post processing dictionary does not have radius data, make sure 'radius' is a key in the dictionary")
        Check.condition(
            "directors" in post_processing_dict,
            KeyError,
            "Beam's post processing dictionary does not have director data, make sure 'directors' is a key in the dictionary")   
        self.rectangular_beams.append((name,post_processing_dict,width,thickness))
    
    def add_static_mesh(self,name:str,mesh:object):
        Check.condition(
            hasattr(mesh, 'vertices'),
            AttributeError,
            "Given mesh object does not have vertices!")
        Check.condition(
            hasattr(mesh, 'face_indices'),
            AttributeError,
            "Given mesh object does not have face indices!")
        self.static_meshes.append((name,mesh))
    
    def add_dynamic_mesh(self,name:str,mesh:object,post_processing_dict:dict):
        Check.condition(
            hasattr(mesh, 'face_indices'),
            AttributeError,
            "Given mesh object does not have face indices!")
        Check.condition(
            "vertices" in post_processing_dict,
            AttributeError,
            "Given mesh post processing dictionary does not have vertices!")
        self.dynamic_meshes.append((name,mesh,post_processing_dict))
    
    def add_sphere(self,name:str,post_processing_dict:dict):
        Check.condition(
            "position" in post_processing_dict,
            KeyError,
            "Given sphere post processing dictionary does not have position data, make sure 'position' is a key in the dictionary")
        Check.condition(
            "radius" in post_processing_dict,
            KeyError,
            "Given sphere post processing dictionary does not have radius data, make sure 'radius' is a key in the dictionary")
        self.spheres.append((name,post_processing_dict))

    def add_cylinder(self,name:str,post_processing_dict:dict):
        Check.condition(
            "position" in post_processing_dict,
            KeyError,
            "Given cylinder post processing dictionary does not have position data, make sure 'position' is a key in the dictionary")
        Check.condition(
            "radius" in post_processing_dict,
            KeyError,
            "Given cylinder post processing dictionary does not have radius data, make sure 'radius' is a key in the dictionary")
        self.cylinders.append((name,post_processing_dict))
    
    def save_to(self,folder:str):
        pass

    def data_dict(self):
        pass


class PovraySceneDataFile(SceneDataFile):
    def __init__(self, name:str, times=None):
        SceneDataFile.__init__(self,name,times)

    def save_to(self, folder: str):
        # Save data as dat file
        data = self.data_dict()
        save_file = os.path.join(folder, self.name+".dat")
        if os.path.exists(save_file):
            os.remove(save_file)
        else:
            os.makedirs(os.path.dirname(save_file), exist_ok=True)
        file = open(save_file, "wb")
        pickle.dump(data, file)
        file.close()

    def data_dict(self):
        # return data dictionary
        data = {}
        data["times"] = np.array(self.times)
        #add rod data
        if len(self.rod_groups)>0:
            rods_data = {}
            for rod_group_name,rod_group in self.rod_groups:
                rod_group_data = []
                for rod_dict in rod_group:
                    rod_data = {}
                    rod_data["position"] = rod_dict["position"]
                    rod_data["radius"] = rod_dict["radius"]
                    rod_group_data.append(rod_data)
                rods_data[rod_group_name] = rod_group_data
            data["rods_data"] = rods_data
        
        #add beam data
        if len(self.rectangular_beams)>0:
            beams_data = {}
            for beam_name,beam_dict,width,thickness in self.rectangular_beams:
                beam_data = {}
                beam_data["position"] = beam_dict["position"]
                beam_data["radius"] = beam_dict["radius"]
                beam_data["directors"] = beam_dict["directors"]
                beam_data["width"] = width
                beam_data["thickness"] = thickness
                beams_data[beam_name] = beam_data
            data["beams_data"] = beams_data
        
        #add static mesh data
        if len(self.static_meshes)>0:
            static_meshes_data = {}
            for mesh_name,mesh in self.static_meshes:
                static_mesh_data = {}
                static_mesh_data["vertices"] = np.array(mesh.vertices)
                static_mesh_data["texture_vertices"] = np.array(mesh.texture_vertices)
                static_mesh_data["vertex_normals"] = np.array(mesh.vertex_normals)
                static_mesh_data["face_indices"] = np.array(mesh.face_indices)
                static_meshes_data[mesh_name] = static_mesh_data
            data["static_meshes_data"] = static_meshes_data
            
        #add dynamic mesh data
        if len(self.dynamic_meshes)>0:
            dynamic_meshes_data = {}
            for mesh_name,mesh,mesh_dict in self.dynamic_meshes:
                dynamic_mesh_data = {}
                dynamic_mesh_data["vertices"] = mesh_dict["vertices"]
                dynamic_mesh_data["vertex_normals"] = mesh_dict["vertex_normals"]
                dynamic_mesh_data["texture_vertices"] = np.array(mesh.texture_vertices)
                dynamic_mesh_data["face_indices"] = np.array(mesh.face_indices)
                dynamic_meshes_data[mesh_name] = dynamic_mesh_data
            data["dynamic_meshes_data"] = dynamic_meshes_data

        #add sphere data
        if len(self.spheres)>0:
            spheres_data = []
            for sphere_name,sphere_dict in self.spheres:
                sphere_data = {}
                sphere_data["position"] = sphere_dict["position"]
                sphere_data["radius"] = sphere_dict["radius"]
                spheres_data[sphere_name] = sphere_data
            data["spheres_data"] = spheres_data
            
        #add cylinder data
        if len(self.cylinders)>0:
            cylinders_data = []
            for cylinder_name,cylinder_dict in self.cylinders:
                cylinder_data = {}
                cylinder_data["position"] = cylinder_dict["position"]
                cylinder_data["radius"] = cylinder_dict["radius"]
                cylinders_data[cylinder_name] = cylinder_data
            data["cylinders_data"] = cylinders_data

        return data

class ThreeJSSceneDataFile(SceneDataFile):
    def __init__(self, name:str, times=None):
        SceneDataFile.__init__(self,name,times)
    #TODO:finish implementing this
