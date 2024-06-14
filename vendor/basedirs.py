from pathlib import Path

from platformdirs import PlatformDirs


class Directories:
    """
    Provides paths to application-specific directories.

    Parameters
    ----------
    name : str
        Sub-path part specific to the application.

    root : pathlib.Path, default None
        If set, makes all XDG variables equal to it.
    """

    def __init__(self, name: str | None = None, *, root: Path | None = None) -> None:
        self.name = name or ""
        if root is None:
            self.base = PlatformDirs(self.name, appauthor=False, ensure_exists=True)
        else:
            self.base = Path(root).expanduser().resolve()

    @property
    def data(self) -> Path:
        """
        Application user-specific data files.
        """
        if isinstance(self.base, PlatformDirs):
            return Path(self.base.user_data_dir)
        return getchild(self.base, self.name)

    @property
    def config(self) -> Path:
        """
        Application user-specific configuration files.
        """
        if isinstance(self.base, PlatformDirs):
            return Path(self.base.user_config_dir)
        return getchild(self.base, self.name)

    @property
    def state(self) -> Path:
        """
        Application user-specific state data.
        """
        if isinstance(self.base, PlatformDirs):
            return Path(self.base.user_state_dir)
        return getchild(self.base, self.name)

    @property
    def cache(self) -> Path:
        """
        Application user-specific non-essential (cached) data.
        """
        if isinstance(self.base, PlatformDirs):
            return Path(self.base.user_cache_dir)
        return getchild(self.base, self.name)

    @property
    def runtime(self) -> Path:
        """
        Application user-specific non-essential runtime files and other file objects.
        """
        if isinstance(self.base, PlatformDirs):
            return Path(self.base.user_runtime_dir)
        return getchild(self.base, self.name)


def getchild(base: Path, *segments, mode: int = 0o755) -> Path:
    """
    Get subdir path of base directory represented as sequence of path segments.

    Returns
    -------
    pathlib.Path
        Path relative to the base directory

    Raises
    ------
    ValueError
        If segments contain path separator and becomes not relative to the base.
    """
    path = base.joinpath(*segments)
    if not path.is_relative_to(base):
        message = "path separator is not allowed in segments"
        raise ValueError(message)
    path.mkdir(mode=mode, parents=True, exist_ok=True)
    return path
