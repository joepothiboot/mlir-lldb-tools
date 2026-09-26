"""Make `import lldb` work, or explain precisely why it can't."""
import os, subprocess, sys

class LldbUnavailable(RuntimeError):
    pass

def ensure_lldb():
    try:
        import lldb  # noqa
        return lldb
    except ImportError:
        pass
    exe = os.environ.get("LLDB", "lldb")
    try:
        path = subprocess.check_output([exe, "-P"], text=True).strip()
    except Exception as e:
        raise LldbUnavailable(
            f"Could not run `{exe} -P`. Install LLDB or set $LLDB. ({e})") from e
    if path not in sys.path:
        sys.path.insert(0, path)
    try:
        import lldb
        return lldb
    except ImportError as e:
        raise LldbUnavailable(
            "LLDB's Python module exists at:\n"
            f"    {path}\n"
            f"but will not import into this interpreter ({sys.version.split()[0]}).\n"
            "LLDB's module is built against ONE CPython minor version. Either run\n"
            "with the matching python3, or recreate the venv with "
            "--system-site-packages.\n"
            f"Underlying error: {e}") from e