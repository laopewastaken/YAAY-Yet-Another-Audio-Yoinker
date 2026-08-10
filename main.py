
from utils import ensure_dependencies


if __name__ == "__main__":
    ensure_dependencies()

    from gui import start_app
    start_app()
    