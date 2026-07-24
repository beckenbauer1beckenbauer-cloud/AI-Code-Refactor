import inspect
import pkgutil
import importlib

def extract_functions_deep(module, max_functions=10):
    """
    Recursively inspects top-level module and submodules to find pure Python functions with source code.
    """
    functions_list = []
    seen_names = set()

    def search_module(mod, max_depth=2, current_depth=0):
        if len(functions_list) >= max_functions or current_depth > max_depth:
            return

        try:
            members = inspect.getmembers(mod)
        except Exception:
            return

        for name, obj in members:
            if len(functions_list) >= max_functions:
                break

            if inspect.isfunction(obj) and not name.startswith("_"):
                full_name = f"{mod.__name__}.{name}"
                if full_name not in seen_names:
                    try:
                        source = inspect.getsource(obj)
                        if len(source.strip().splitlines()) > 3:  # Exclude trivial functions
                            functions_list.append((name, source))
                            seen_names.add(full_name)
                    except (TypeError, OSError):
                        pass

        if len(functions_list) < max_functions and hasattr(mod, "__path__"):
            try:
                for _, subname, _ in pkgutil.walk_packages(mod.__path__, mod.__name__ + "."):
                    if len(functions_list) >= max_functions:
                        break
                    if ".tests" in subname or "._" in subname:
                        continue
                    try:
                        submod = importlib.import_module(subname)
                        search_module(submod, max_depth, current_depth + 1)
                    except Exception:
                        continue
            except Exception:
                pass

    search_module(module)
    return functions_list
