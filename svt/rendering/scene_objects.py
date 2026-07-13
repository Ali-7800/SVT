import numpy as np
from svt.rendering.scene import Scene
from svt.rendering.utils import (
    TimeScalar,
    TimeVecN,
    TimeVecMN,
    TimeIndexN,
    TimeIndexMN,
    _bool_property,
    sf,
)


class SphereSweep(Scene.Object):
    """A tube swept along a polyline of (position, radius) control points.

    http://www.povray.org/documentation/view/3.7.0/282/
    """

    def __init__(self, name, position, radius):
        super().__init__()
        self.name = name
        self.position = TimeVecMN(position)
        n = self.position(0).shape[-1]
        self.radius = TimeVecN(radius, n)
        self.color = TimeVecN([0.45, 0.39, 1])
        self.interpolation_method = "linear_spline"

    @property
    def interpolation_method(self):
        return self._interpolation_method

    @interpolation_method.setter
    def interpolation_method(self, value):
        if not isinstance(value, str):
            raise TypeError("interpolation_method must be a string")
        if value not in ("linear_spline", "b_spline", "cubic_spline"):
            raise ValueError(
                "interpolation method must be one of the following: "
                "linear_spline, b_spline, cubic_spline"
            )
        self._interpolation_method = value

    def generate_script(self, time):
        x = self.position(time)
        r = self.radius(time)
        num_element = x.shape[1]
        rows = [
            f",{self._fmt_vec(x[:, i], self.precision)},{sf(r[i], self.precision)}"
            for i in range(num_element)
        ]
        self.str = self._primitive_script(
            "sphere_sweep",
            f"{self.interpolation_method} {num_element}",
            rows,
            time,
        )


class Sphere(Scene.Object):
    """A single sphere primitive.

    http://www.povray.org/documentation/view/3.7.0/283/
    """

    def __init__(self, name, position, radius):
        super().__init__()
        self.name = name
        self.position = TimeVecN(position)
        self.radius = TimeScalar(radius)
        self.color = TimeVecN([1, 0, 0])

    def generate_script(self, time):
        x = self.position(time)
        r = self.radius(time)
        row = f"{self._fmt_vec(x, self.precision)},{sf(r, self.precision)}"
        self.str = self._primitive_script("sphere", None, [row], time)


class Cylinder(Scene.Object):
    """A capped cylinder between two end points.

    http://www.povray.org/documentation/view/3.7.0/284/
    """

    def __init__(self, name, start_position, end_position, radius):
        super().__init__()
        self.name = name
        self.start_position = TimeVecN(start_position)
        self.end_position = TimeVecN(end_position)
        self.radius = TimeScalar(radius)
        self.color = TimeVecN([1, 0, 0])

    def generate_script(self, time):
        x1 = self.start_position(time)
        x2 = self.end_position(time)
        r = self.radius(time)
        row = (
            f"{self._fmt_vec(x1, self.precision)},"
            f"{self._fmt_vec(x2, self.precision)},"
            f"{sf(r, self.precision)}"
        )
        self.str = self._primitive_script("cylinder", None, [row], time)


class Plane(Scene.Object):
    """An infinite plane defined by a normal vector and a signed distance.

    http://www.povray.org/documentation/view/3.7.0/297/
    """

    def __init__(self, name, normal, distance):
        super().__init__()
        self.name = name
        self.normal = TimeVecN(normal)
        self.distance = TimeScalar(distance)
        self.color = TimeVecN([1, 1, 1])

    def generate_script(self, time):
        n = self.normal(time)
        d = self.distance(time)
        row = f"{self._fmt_vec(n, self.precision)},{sf(d, self.precision)}"
        self.str = self._primitive_script("plane", None, [row], time)


class Cone(Scene.Object):
    """A (optionally open) cone/frustum between two circular end caps.

    http://www.povray.org/documentation/view/3.7.0/285/
    """

    def __init__(
        self, name, base_position, base_radius, cap_position, cap_radius, open=False
    ):
        super().__init__()
        self.name = name
        self.base_position = TimeVecN(base_position)
        self.base_radius = TimeScalar(base_radius)
        self.cap_position = TimeVecN(cap_position)
        self.cap_radius = TimeScalar(cap_radius)
        self.open = open
        self.color = TimeVecN([1, 0, 0])

    # Whether the end caps are rendered (open=True) or left off, giving
    # a hollow tube/funnel look (POV-Ray's `open` keyword).
    open = _bool_property("open", default=False)

    def generate_script(self, time):
        x1 = self.base_position(time)
        r1 = self.base_radius(time)
        x2 = self.cap_position(time)
        r2 = self.cap_radius(time)
        row = (
            f"{self._fmt_vec(x1, self.precision)},{sf(r1, self.precision)},"
            f"{self._fmt_vec(x2, self.precision)},{sf(r2, self.precision)}"
        )
        rows = [row, "open"] if self.open else [row]
        self.str = self._primitive_script("cone", None, rows, time)


class Mesh(Scene.Object):
    """A triangle mesh (POV-Ray mesh2), optionally with vertex normals,
    per-face colors, or a single UV-mapped image/bump texture.

    http://www.povray.org/documentation/view/3.7.0/293/
    """

    def __init__(self, name, vertices, faces_indices):
        super().__init__()
        self.name = name
        self.vertices = TimeVecMN(vertices)
        self.faces_indices = TimeIndexMN(faces_indices, m=3)
        self.vertex_normals = None
        self.uv_vectors = None
        self.face_color = self.FaceColor(n_faces=self.faces_indices(0).shape[-1])
        self.finish.specular = 0

    class FaceColor:
        """Per-face coloring: a palette (`list`) plus a per-face palette
        index (`indices`). `indices=None` means per-face coloring is off
        and the mesh's single `generate_texture_script` texture is used
        instead.
        """

        def __init__(self, n_faces):
            self.n_faces = n_faces
            self.list = TimeVecMN(np.array([[1, 0, 0, 0]]).T, m=4)
            self.indices = None

        @property
        def list(self):
            return self._list

        @list.setter
        def list(self, value):
            self._list = TimeVecMN(value, m=4)

        @list.deleter
        def list(self):
            self._list = TimeVecMN(np.array([[0, 0, 0, 0]]).T, m=4)

        @property
        def indices(self):
            return self._indices

        @indices.setter
        def indices(self, value):
            if value is None:
                self._indices = value
            else:
                self._indices = TimeIndexN(value, n=self.n_faces)

        @indices.deleter
        def indices(self):
            self._indices = None

    @property
    def vertex_normals(self):
        return self._vertex_normals

    @vertex_normals.setter
    def vertex_normals(self, value):
        self._vertex_normals = None if value is None else TimeVecMN(value)

    @vertex_normals.deleter
    def vertex_normals(self):
        self._vertex_normals = None

    @property
    def uv_vectors(self):
        return self._uv_vectors

    @uv_vectors.setter
    def uv_vectors(self, value):
        self._uv_vectors = None if value is None else TimeVecMN(value, m=2)

    @uv_vectors.deleter
    def uv_vectors(self):
        self._uv_vectors = None

    def generate_script(self, time):
        """Build the POV-Ray mesh2 {...} script for this mesh at the given time.

        Section order is:
        vertex_vectors -> texture_list (if not image-mapped) -> normal_vectors
        -> uv_vectors (if image-mapped) -> face_indices -> uv_indices
        (if image-mapped) -> texture {...} (if image-mapped).
        """
        faces_indices = self.faces_indices(time)
        n_faces = faces_indices.shape[-1]
        vertices = self.vertices(time)
        n_vertices = vertices.shape[-1]

        use_image_map = self.image_map.path != ""
        use_face_colors = (not use_image_map) and self.face_color.indices is not None

        if use_image_map and self.uv_vectors is None:
            raise AttributeError("uv_vectors must be provided when image map is set")

        sections = [
            "mesh2 {",
            self._pov_block(
                "vertex_vectors",
                n_vertices,
                (
                    self._fmt_floats(vertices[:, i], self.precision)
                    for i in range(n_vertices)
                ),
            ),
        ]

        if not use_image_map:
            sections.append(self._generate_texture_list(time, use_face_colors))

        if self.vertex_normals is not None:
            vertex_normals = self.vertex_normals(time)
            sections.append(
                self._pov_block(
                    "normal_vectors",
                    n_vertices,
                    (
                        self._fmt_floats(vertex_normals[:, i], self.precision)
                        for i in range(n_vertices)
                    ),
                )
            )

        if use_image_map:
            uv_vectors = self.uv_vectors(time)
            sections.append(
                self._pov_block(
                    "uv_vectors",
                    n_vertices,
                    (self._fmt_floats(uv_vectors[:, i]) for i in range(n_vertices)),
                )
            )

        color_indices = None
        if use_face_colors:
            color_indices = self.face_color.indices(time)
        elif not use_image_map:
            color_indices = [0] * n_faces

        sections.append(
            self._pov_block(
                "face_indices",
                n_faces,
                (
                    self._fmt_ints(
                        faces_indices[:, i],
                        extra=None if color_indices is None else color_indices[i],
                    )
                    for i in range(n_faces)
                ),
            )
        )

        if use_image_map:
            sections.append(
                self._pov_block(
                    "uv_indices",
                    n_faces,
                    (self._fmt_ints(faces_indices[:, i]) for i in range(n_faces)),
                )
            )
            sections.append(self._generate_image_map_texture(time))

        sections.append("\n}")
        self.str = "\n".join(sections)

    def _generate_texture_list(self, time, use_face_colors):
        """texture_list block for the non-image-map case (per-face colors or a single texture)."""
        if use_face_colors:
            color_list = self.face_color.list(time)
            n_colors = color_list.shape[-1]
            items = [f"\ntexture_list {{\n{n_colors}"]
            for idx in range(n_colors):
                r, g, b, t = color_list[:, idx]
                items.append(
                    "texture {\npigment { color rgbt <%0.1f,%0.1f,%0.1f,%0.1f>}"
                    % (r, g, b, t)
                )
                if self.bump_map.path != "":
                    items.append(self.bump_map.generate_script())
                items.append("\n" + self.finish.generate_script(time))
                items.append("\n}")
            items.append("\n}")
            return "\n".join(items)

        return "\n".join(
            [
                "\ntexture_list {\n1",
                self.generate_texture_script(time),
                "\n}",
            ]
        )

    def _generate_image_map_texture(self, time):
        """texture {...} block for the image-map case, with optional bump map."""
        items = [
            '\ntexture {{\npigment {{\nuv_mapping \nimage_map {{\n{0} "{1}" \nmap_type {2} \n}}\n}}'.format(
                self.image_map.extension, self.image_map.path, self.image_map.type
            )
        ]
        if self.bump_map.path != "":
            items.append(
                '\nnormal {{\nuv_mapping \nbump_map {{\n{0} "{1}" \nmap_type 0\nbump_size {2}\n}}\n}}'.format(
                    self.bump_map.extension, self.bump_map.path, self.bump_map.size
                )
            )
        items.append("\n" + self.finish.generate_script(time))
        items.append("\n}")
        return "\n".join(items)
