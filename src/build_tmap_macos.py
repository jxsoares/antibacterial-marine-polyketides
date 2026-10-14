"""Build the tested upstream TMAP on macOS arm64 inside the active virtualenv."""
from pathlib import Path
import hashlib
import json
import platform
import shutil
import subprocess
import sys
import sysconfig
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
COMMIT = "49234b5779c032d1d4a7249b4cb96e43c31375ea"
OPENMP_URL = "https://api.anaconda.org/download/conda-forge/llvm-openmp/15.0.5/osx-arm64/llvm-openmp-15.0.5-h7cfbb63_0.tar.bz2"
OPENMP_SHA = "df8d545338b3a895d5d010aa1d672d484006b4f3f406ff5146b18f51f3acd0ea"

def run(*args, **kwargs):
    subprocess.run([str(x) for x in args], check=True, **kwargs)

def main():
    if platform.system() != "Darwin" or platform.machine() != "arm64":
        raise SystemExit("This recipe was tested only on macOS arm64. Use upstream installation instructions elsewhere.")
    if sys.prefix == sys.base_prefix:
        raise SystemExit("Run this script using the project virtualenv Python.")
    cmake = Path(sys.executable).parent / "cmake"
    if not cmake.is_file():
        raise SystemExit("Install the native-build extra first: python -m pip install -e '.[tmap,native-build]'")
    work = ROOT / ".native-build"
    work.mkdir(exist_ok=True)
    source = work / "tmap"
    if not source.exists():
        run("git", "clone", "https://github.com/reymond-group/tmap.git", source)
    run("git", "-C", source, "checkout", "--detach", COMMIT)
    actual = subprocess.check_output(["git", "-C", str(source), "rev-parse", "HEAD"], text=True).strip()
    assert actual == COMMIT
    archive = work / "openmp.tar.bz2"
    if not archive.exists():
        urllib.request.urlretrieve(OPENMP_URL, archive)
    assert hashlib.sha256(archive.read_bytes()).hexdigest() == OPENMP_SHA, "OpenMP archive checksum mismatch"
    native = work / "native"
    native.mkdir(exist_ok=True)
    run("tar", "-xjf", archive, "-C", native)
    ogdf = work / "ogdf-build"
    run(cmake, "-S", source / "ogdf-conda/src", "-B", ogdf,
        "-DCMAKE_BUILD_TYPE=Release", f"-DCMAKE_INSTALL_PREFIX={native}", "-DCMAKE_POSITION_INDEPENDENT_CODE=ON")
    run(cmake, "--build", ogdf, "-j", "6")
    run(cmake, "--install", ogdf)
    build = work / "tmap-build"
    output = work / "built"
    import os
    env = dict(os.environ, LIBOGDF_INSTALL_PATH=str(native))
    run(cmake, "-S", source, "-B", build, "-DCMAKE_BUILD_TYPE=Release",
        f"-DPYTHON_EXECUTABLE={sys.executable}", f"-DCMAKE_LIBRARY_OUTPUT_DIRECTORY={output}",
        f"-DOpenMP_C_FLAGS=-Xpreprocessor -fopenmp -I{native}/include",
        f"-DOpenMP_CXX_FLAGS=-Xpreprocessor -fopenmp -I{native}/include",
        "-DOpenMP_C_LIB_NAMES=omp", "-DOpenMP_CXX_LIB_NAMES=omp",
        f"-DOpenMP_omp_LIBRARY={native}/lib/libomp.dylib", env=env)
    run(cmake, "--build", build, "-j", "4")
    site = Path(sysconfig.get_paths()["platlib"])
    shutil.copytree(source / "src/tmap", site / "tmap", dirs_exist_ok=True)
    extension, = output.glob("_tmap*.so")
    shutil.copy2(extension, site / extension.name)
    run(sys.executable, "-c", "import tmap; print(tmap.Minhash(512))")
    record = {"upstream_commit": COMMIT, "openmp_archive_sha256": OPENMP_SHA,
              "python": platform.python_version(), "platform": platform.platform(),
              "extension_sha256": hashlib.sha256(extension.read_bytes()).hexdigest(),
              "installation": "native extension and upstream Python wrapper copied into this virtualenv; not managed by pip"}
    (Path(sys.prefix) / "native-tmap-build.json").write_text(json.dumps(record, indent=2) + "\n")

if __name__ == "__main__":
    main()
