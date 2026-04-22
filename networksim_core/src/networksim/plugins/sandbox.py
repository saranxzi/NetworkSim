"""Sandboxed plugin execution using RestrictedPython."""
import threading
import ctypes
from RestrictedPython import compile_restricted, safe_builtins
from RestrictedPython.Guards import safer_getattr, guarded_unpack_sequence

# Maximum execution time in seconds
MAX_EXECUTION_TIME = 0.1

# Maximum loop iterations to prevent infinite loops
MAX_ITERATIONS = 50_000


def _guarded_getiter(obj):
    """Guard iterator access — wraps iterables with a bounded counter."""
    return _BoundedIterator(iter(obj))


class _BoundedIterator:
    """Iterator wrapper that raises after MAX_ITERATIONS to prevent infinite loops."""
    __slots__ = ('_iterator', '_count')

    def __init__(self, iterator):
        self._iterator = iterator
        self._count = 0

    def __iter__(self):
        return self

    def __next__(self):
        self._count += 1
        if self._count > MAX_ITERATIONS:
            raise RuntimeError(f"Loop exceeded {MAX_ITERATIONS} iterations")
        return next(self._iterator)


class PluginSandbox:
    """Execute user-supplied Python code in a restricted sandbox."""
    __slots__ = ("source_code", "compiled_code")

    def __init__(self, source_code: str):
        self.source_code = source_code
        try:
            self.compiled_code = compile_restricted(source_code, '<plugin>', 'exec')
        except Exception:
            self.compiled_code = None

    def execute_tick(self, state: dict, incoming_rps: float) -> dict:
        """Run the user's on_tick() function in a sandboxed environment."""
        default_res = {"forwarded": incoming_rps, "dropped": 0}
        if not self.compiled_code:
            return default_res

        env = {
            "__builtins__": {
                # Safe arithmetic/type builtins only
                "min": min, "max": max, "abs": abs, "round": round,
                "int": int, "float": float, "bool": bool, "str": str,
                "len": len, "range": range, "enumerate": enumerate,
                "sum": sum, "sorted": sorted,
                "True": True, "False": False, "None": None,
                "dict": dict, "list": list, "tuple": tuple,
                # RestrictedPython guards — these are CRITICAL for security
                '_getiter_': _guarded_getiter,
                '_getattr_': safer_getattr,  # Blocks dunder traversal
                '_getitem_': lambda obj, key: obj[key],
                '_write_': lambda x: x,
                '_inplacevar_': lambda op, x, y: op(x, y),
                '_unpack_sequence_': guarded_unpack_sequence,
            }
        }

        result = {}
        exception_occurred = [False]

        def worker():
            try:
                exec(self.compiled_code, env)
                if "on_tick" in env and callable(env["on_tick"]):
                    res = env["on_tick"](state, incoming_rps)
                    if isinstance(res, dict):
                        result.update(res)
                else:
                    exception_occurred[0] = True
            except Exception:
                exception_occurred[0] = True

        t = threading.Thread(target=worker, daemon=True)
        t.start()
        t.join(MAX_EXECUTION_TIME)

        if exception_occurred[0] or t.is_alive() or not result:
            return default_res

        return result
