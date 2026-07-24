import sys
import subprocess
import importlib
from engine import refactor_code

# Mapping for known packages where PyPI name differs from import module name
KNOWN_PACKAGES = {
    "scikit-learn": ("scikit-learn", "sklearn"),
    "scikit_learn": ("scikit-learn", "sklearn"),
    "sklearn": ("scikit-learn", "sklearn"),
    "pillow": ("Pillow", "PIL"),
    "opencv-python": ("opencv-python", "cv2"),
    "opencv": ("opencv-python", "cv2"),
    "beautifulsoup4": ("beautifulsoup4", "bs4"),
    "pyyaml": ("PyYAML", "yaml"),
    "httpx": ("httpx", "httpx"),
    "requests": ("requests", "requests"),
    "django": ("Django", "django"),
    "flask": ("Flask", "flask"),
    "pandas": ("pandas", "pandas"),
    "numpy": ("numpy", "numpy"),
    "scipy": ("scipy", "scipy")
}

def resolve_and_install_package(user_input, model_name="qwen2.5:7b"):
    """
    Translates ANY package name in the world to its PyPI install name and Python import name.
    Strictly target-bound — never falls back to 'requests'.
    """
    clean_input = user_input.strip().lower()

    # 1. Check known mapping dictionary
    if clean_input in KNOWN_PACKAGES:
        pip_name, import_name = KNOWN_PACKAGES[clean_input]
    else:
        print(f"🤖 Querying LLM to map package metadata for '{user_input}'...")
        prompt = (
            f"The user wants to analyze the Python library: '{user_input}'.\n"
            "Return ONLY a raw JSON object with two keys: 'pip_name' (for pip install) and 'import_name' (for import in Python).\n"
            "Example: {\"pip_name\": \"scikit-learn\", \"import_name\": \"sklearn\"}"
        )
        res = refactor_code("PackageResolver", prompt, model_name=model_name)
        if res and isinstance(res, dict) and "import_name" in res:
            pip_name = res.get("pip_name", user_input.strip())
            import_name = res.get("import_name", user_input.strip())
        else:
            pip_name = user_input.strip()
            import_name = user_input.strip().replace("-", "_")

    print(f"💡 Target Resolved: pip install '{pip_name}' ➔ import '{import_name}'")

    # 2. Import or Auto-Install
    try:
        module = importlib.import_module(import_name)
        print(f"✅ Successfully imported '{import_name}'.")
        return module, pip_name, import_name
    except ImportError:
        print(f"📦 Auto-installing '{pip_name}' via pip...")

    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name])
        importlib.invalidate_caches()
        module = importlib.import_module(import_name)
        print(f"✅ Successfully installed and imported '{import_name}'.")
        return module, pip_name, import_name
    except Exception as e:
        print(f"❌ Failed to install or import target package '{pip_name}': {e}")
        return None, pip_name, import_name
