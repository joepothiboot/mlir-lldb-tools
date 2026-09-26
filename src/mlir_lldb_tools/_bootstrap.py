"""Make `import lldb` work, or explain precisely why it can't."""
import glob, os, subprocess, sys

class LldbUnavailable(RuntimeError):
    pass

def _try_import():
    """Import lldb, rejecting empty namespace packages left by broken distro symlinks."""
    try:
        import lldb
    except ImportError as e:
        return None, e
    if hasattr(lldb, "SBDebugger"):
        return lldb, None
    sys.modules.pop("lldb", None)
    return None, ImportError(f"`lldb` at {list(getattr(lldb, '__path__', []))} "
                             "has no SBDebugger (broken install?)")

def _candidate_paths(exe):
    try:
        yield subprocess.check_output([exe, "-P"], text=True, stderr=subprocess.DEVNULL).strip()
    except Exception:
        pass
    # Debian/Ubuntu: `lldb -P` can point at a nonexistent dir; the module lives here.
    ver = f"python3.{sys.version_info.minor}"
    for pattern in (f"/usr/lib/llvm-*/lib/{ver}/*-packages",
                    "/usr/lib/llvm-*/lib/python3/*-packages"):
        yield from sorted(glob.glob(pattern), reverse=True)

def ensure_lldb():
    lldb, err = _try_import()
    if lldb:
        return lldb
    exe = os.environ.get("LLDB", "lldb")
    tried, errors = [], []
    for path in _candidate_paths(exe):
        if not path or not os.path.isdir(os.path.join(path, "lldb")):
            continue
        tried.append(path)
        sys.path.insert(0, path)
        lldb, err = _try_import()
        if lldb:
            return lldb
        errors.append(f"    {path}: {err}")
        sys.path.remove(path)
    if not tried:
        raise LldbUnavailable(
            f"Could not find LLDB's Python module (tried `{exe} -P` and /usr/lib/llvm-*). "
            "Install LLDB or set $LLDB.")
    raise LldbUnavailable(
        "LLDB's Python module exists at:\n"
        + "".join(f"    {p}\n" for p in tried)
        + f"but will not import into this interpreter ({sys.version.split()[0]}).\n"
        "LLDB's module is built against ONE CPython minor version. Either run\n"
        "with the matching python3, or recreate the venv with "
        "--system-site-packages.\n"
        "Errors:\n" + "\n".join(errors))
