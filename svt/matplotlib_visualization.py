import numpy as np
import matplotlib
matplotlib.use("Agg")  # Must be before importing matplotlib.pyplot or pylab!
from matplotlib import pyplot as plt
from tqdm import tqdm
from typing import Dict, Sequence


def plot_video_with_surface(
    surface_vertices:np.ndarray,
    rods_history: Sequence[Dict],
    video_name="video.mp4",
    fps=60,
    step=1,
    **kwargs,
):
    plt.rcParams.update({"font.size": 22})

    folder_name = kwargs.get("folder_name", "")

    # 2d case <always 2d case for now>
    import matplotlib.animation as animation

    # simulation time
    sim_time = np.array(rods_history[0]["time"])

    # Rod
    n_visualized_rods = len(rods_history)  # should be one for now
    # Rod info
    rod_history_unpacker = lambda rod_idx, t_idx: (
        rods_history[rod_idx]["position"][t_idx],
        rods_history[rod_idx]["radius"][t_idx],
    )
    # Rod center of mass
    com_history_unpacker = lambda rod_idx, t_idx: rods_history[rod_idx]["com"][time_idx]

    # video pre-processing
    print("plot scene visualization video")
    FFMpegWriter = animation.writers["ffmpeg"]
    metadata = dict(title="Movie Test", artist="Matplotlib", comment="Movie support!")
    writer = FFMpegWriter(fps=fps, metadata=metadata)
    dpi = kwargs.get("dpi", 100)

    xlim = kwargs.get("x_limits", (-1.0, 1.0))
    ylim = kwargs.get("y_limits", (-1.0, 1.0))
    zlim = kwargs.get("z_limits", (-0.05, 1.0))

    difference = lambda x: x[1] - x[0]
    max_axis_length = max(difference(xlim), difference(ylim))
    # The scaling factor from physical space to matplotlib space
    scaling_factor = (2 * 0.1) / max_axis_length  # Octopus head dimension
    scaling_factor *= 2.6e3  # Along one-axis

    fig = plt.figure(1, figsize=(10, 8), frameon=True, dpi=dpi)
    ax = plt.axes(projection="3d", computed_zorder=False)

    ax.set_xlabel("x")
    ax.set_ylabel("y")
    ax.set_zlabel("z")

    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    ax.set_zlim(*zlim)

    #plot surface
    ax.plot_trisurf(
        surface_vertices[:,0],
        surface_vertices[:,1],
        surface_vertices[:,2],
        linewidth=0.2,
        antialiased=True,
        cmap="copper"
        )

    time_idx = 0
    rod_lines = [None for _ in range(n_visualized_rods)]
    rod_com_lines = [None for _ in range(n_visualized_rods)]
    rod_scatters = [None for _ in range(n_visualized_rods)]


    for rod_idx in range(n_visualized_rods):
        inst_position, inst_radius = rod_history_unpacker(rod_idx, time_idx)
        if not inst_position.shape[1] == inst_radius.shape[0]:
            inst_position = 0.5 * (inst_position[..., 1:] + inst_position[..., :-1])

        rod_scatters[rod_idx] = ax.scatter(
            inst_position[0],
            inst_position[1],
            inst_position[2],
            s=np.pi * (scaling_factor * inst_radius) ** 2,
        )

    # ax.set_aspect("equal")
    video_name_3D = folder_name + "3D_" + video_name

    with writer.saving(fig, video_name_3D, dpi):
        with plt.style.context("seaborn-v0_8-whitegrid"):
            for time_idx in tqdm(range(0, sim_time.shape[0], int(step))):
                for rod_idx in range(n_visualized_rods):
                    inst_position, inst_radius = rod_history_unpacker(
                        rod_idx, time_idx
                    )
                    if not inst_position.shape[1] == inst_radius.shape[0]:
                        inst_position = 0.5 * (
                            inst_position[..., 1:] + inst_position[..., :-1]
                        )

                    rod_scatters[rod_idx]._offsets3d = (
                        inst_position[0],
                        inst_position[1],
                        inst_position[2],
                    )

                    # rod_scatters[rod_idx].set_offsets(inst_position[:2].T)
                    rod_scatters[rod_idx].set_sizes(
                        np.pi * (scaling_factor * inst_radius) ** 2
                    )

                writer.grab_frame()

    # Be a good boy and close figures
    # https://stackoverflow.com/a/37451036
    # plt.close(fig) alone does not suffice
    # See https://github.com/matplotlib/matplotlib/issues/8560/
    plt.close(plt.gcf())

    
