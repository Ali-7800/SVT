"""

This module includes utility methods to support POVRay and ThreeJs rendering.

"""

import os
import platform
import shutil
import subprocess
from pathlib import Path


def _find_povray_executable():
    """Locate a usable POV-Ray executable across platforms.

    Resolution order:
    1. POVRAY_BINARY environment variable (explicit override).
    2. A list of common executable names for the current OS, resolved
       via PATH with shutil.which.

    Returns
    -------
    str
        Path (or bare name resolvable via PATH) to the POV-Ray executable.

    Raises
    ------
    FileNotFoundError
        If no candidate executable can be found on PATH.
    """
    env_override = os.environ.get("POVRAY_BINARY")
    if env_override:
        if shutil.which(env_override):
            return env_override
        raise FileNotFoundError(
            f"POVRAY_BINARY was set to '{env_override}' but it could not be "
            "found on PATH. Check the environment variable or unset it to "
            "use auto-detection."
        )

    system = platform.system()
    if system == "Windows":
        candidates = ["pvengine.exe", "pvengine64.exe", "povray.exe"]
    elif system == "Darwin":
        candidates = ["povray", "/Applications/POV-Ray/povray"]
    else:  # Linux and other POSIX
        candidates = ["povray"]

    for candidate in candidates:
        found = shutil.which(candidate)
        if found:
            return found

    raise FileNotFoundError(
        "Could not find a POV-Ray executable on PATH (tried: "
        f"{', '.join(candidates)}). Install POV-Ray and ensure it is on "
        "PATH, or set the POVRAY_BINARY environment variable to its full path."
    )


def render_povray(
    filename,
    width,
    height,
    antialias="on",
    quality=11,
    display="Off",
    pov_thread=4,
    transparency=False,
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
    transparency : bool
        If True, enables alpha-channel output (+UA). [default=False]

    Raises
    ------
    FileNotFoundError
        If no POV-Ray executable can be located on the system.
    IOError
        If the povray run causes unexpected error, such as parsing error,
        this method will raise IOError.
    """

    if not (4 <= pov_thread <= 512):
        raise ValueError("pov_thread must be in the range (4, 512).")

    # Use pathlib so extensions/paths are built consistently regardless of OS
    # path separator conventions. `filename` may itself contain a path.
    base = Path(filename)
    script_file = base.with_suffix(".pov")
    image_file = base.with_suffix(".png")

    povray_exe = _find_povray_executable()

    # Build the argument list, dropping any falsy/empty entries so an
    # unused flag doesn't get passed as a literal empty string argument
    # (this can cause "File to render not specified" style errors on
    # some platforms/shells that don't silently ignore empty argv entries).
    cmds = [
        povray_exe,
        "+UA" if transparency else None,
        f"+I{script_file}",
        f"+O{image_file}",
        f"-H{height}",
        f"-W{width}",
        f"Work_Threads={pov_thread}",
        f"Antialias={antialias}",
        f"Quality={quality}",
        f"Display={display}",
    ]
    cmds = [c for c in cmds if c]

    # On Windows, the GUI-based pvengine needs explicit flags to run
    # headlessly and exit after rendering instead of staying open.
    if platform.system() == "Windows" and Path(povray_exe).stem.lower().startswith(
        "pvengine"
    ):
        cmds[1:1] = ["/EXIT", "/RENDER"]

    try:
        result = subprocess.run(
            cmds,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    except OSError as e:
        # e.g. permissions issues, or the resolved path vanished between
        # the `which` check and execution.
        raise IOError(f"Failed to launch POV-Ray ({povray_exe}): {e}") from e

    # Check execution error. Decode leniently since error text encoding
    # varies by OS/locale (Windows in particular is not reliably ASCII).
    if result.returncode:
        stderr_text = result.stderr.decode(errors="replace")
        raise IOError(
            "POVRay rendering failed with the following error: " + stderr_text
        )
