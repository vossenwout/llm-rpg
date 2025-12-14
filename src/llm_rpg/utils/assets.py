from contextlib import contextmanager
from importlib import resources
from pathlib import Path


@contextmanager
def asset_file(relative_path: str):
    resource = resources.files("llm_rpg.assets").joinpath(relative_path)
    with resources.as_file(resource) as path:
        yield Path(path)
