"""
Bookmark system for saving and loading fractal locations.
"""

import json
import os
from dataclasses import dataclass, asdict
from typing import List, Optional, Dict, Any
from pathlib import Path


@dataclass
class Bookmark:
    """A saved fractal location."""
    name: str
    fractal_type: str
    center_re: float
    center_im: float
    scale: float
    max_iterations: int
    colormap: str = "twilight"
    # Optional parameters for specific fractals
    julia_c_re: Optional[float] = None
    julia_c_im: Optional[float] = None
    phoenix_p_re: Optional[float] = None
    phoenix_p_im: Optional[float] = None
    tree_angle: Optional[float] = None
    tree_depth: Optional[int] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert bookmark to dictionary."""
        return {k: v for k, v in asdict(self).items() if v is not None}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Bookmark':
        """Create bookmark from dictionary."""
        return cls(
            name=data.get('name', 'Unnamed'),
            fractal_type=data.get('fractal_type', 'mandelbrot'),
            center_re=data.get('center_re', -0.5),
            center_im=data.get('center_im', 0.0),
            scale=data.get('scale', 3.5),
            max_iterations=data.get('max_iterations', 200),
            colormap=data.get('colormap', 'twilight'),
            julia_c_re=data.get('julia_c_re'),
            julia_c_im=data.get('julia_c_im'),
            phoenix_p_re=data.get('phoenix_p_re'),
            phoenix_p_im=data.get('phoenix_p_im'),
            tree_angle=data.get('tree_angle'),
            tree_depth=data.get('tree_depth'),
        )


class BookmarkManager:
    """
    Manages bookmarks for fractal locations.

    Stores bookmarks in a JSON file in the user's config directory.
    """

    DEFAULT_FILENAME = "fractal_bookmarks.json"

    def __init__(self, filepath: Optional[str] = None):
        """
        Initialize bookmark manager.

        Args:
            filepath: Optional custom filepath for bookmark storage
        """
        if filepath:
            self._filepath = Path(filepath)
        else:
            self._filepath = self._get_default_path()

        self._bookmarks: List[Bookmark] = []
        self._load()

    def _get_default_path(self) -> Path:
        """Get default bookmark file path."""
        # Use user's home directory
        if os.name == 'nt':  # Windows
            config_dir = Path(os.environ.get('APPDATA', Path.home())) / 'FractalExplorer'
        else:  # Linux/Mac
            config_dir = Path.home() / '.config' / 'fractal_explorer'

        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir / self.DEFAULT_FILENAME

    def _load(self):
        """Load bookmarks from file."""
        if not self._filepath.exists():
            self._bookmarks = self._get_default_bookmarks()
            self._save()  # Create file with defaults
            return

        try:
            with open(self._filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self._bookmarks = [Bookmark.from_dict(b) for b in data.get('bookmarks', [])]
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            print(f"Error loading bookmarks: {e}")
            self._bookmarks = self._get_default_bookmarks()

    def _save(self):
        """Save bookmarks to file."""
        try:
            data = {
                'version': 1,
                'bookmarks': [b.to_dict() for b in self._bookmarks]
            }
            with open(self._filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"Error saving bookmarks: {e}")

    def _get_default_bookmarks(self) -> List[Bookmark]:
        """Get default preset bookmarks."""
        return [
            # Mandelbrot interesting points
            Bookmark(
                name="Mandelbrot - Seahorse Valley",
                fractal_type="mandelbrot",
                center_re=-0.7463,
                center_im=0.1102,
                scale=0.005,
                max_iterations=500
            ),
            Bookmark(
                name="Mandelbrot - Elephant Valley",
                fractal_type="mandelbrot",
                center_re=0.281,
                center_im=0.01,
                scale=0.01,
                max_iterations=500
            ),
            Bookmark(
                name="Mandelbrot - Triple Spiral",
                fractal_type="mandelbrot",
                center_re=-0.088,
                center_im=0.654,
                scale=0.01,
                max_iterations=800
            ),
            Bookmark(
                name="Mandelbrot - Mini Mandelbrot",
                fractal_type="mandelbrot",
                center_re=-1.7497,
                center_im=0.0,
                scale=0.0001,
                max_iterations=1000
            ),
            # Julia sets
            Bookmark(
                name="Julia - Dragon",
                fractal_type="julia",
                center_re=0.0,
                center_im=0.0,
                scale=3.5,
                max_iterations=200,
                julia_c_re=-0.8,
                julia_c_im=0.156
            ),
            Bookmark(
                name="Julia - Galaxy Spiral",
                fractal_type="julia",
                center_re=0.0,
                center_im=0.0,
                scale=3.5,
                max_iterations=300,
                julia_c_re=-0.7269,
                julia_c_im=0.1889
            ),
            # Burning Ship
            Bookmark(
                name="Burning Ship - Main Ship",
                fractal_type="burning_ship",
                center_re=-1.762,
                center_im=-0.028,
                scale=0.05,
                max_iterations=500
            ),
            Bookmark(
                name="Burning Ship - Antenna",
                fractal_type="burning_ship",
                center_re=-1.756,
                center_im=-0.0235,
                scale=0.001,
                max_iterations=800
            ),
            # Tricorn
            Bookmark(
                name="Tricorn - Left Horn",
                fractal_type="tricorn",
                center_re=-1.0,
                center_im=0.0,
                scale=0.1,
                max_iterations=500
            ),
            # Phoenix
            Bookmark(
                name="Phoenix - Classic",
                fractal_type="phoenix",
                center_re=0.0,
                center_im=0.0,
                scale=3.5,
                max_iterations=200,
                phoenix_p_re=0.5667,
                phoenix_p_im=-0.5
            ),
            Bookmark(
                name="Phoenix - Flame",
                fractal_type="phoenix",
                center_re=0.0,
                center_im=0.0,
                scale=3.5,
                max_iterations=200,
                phoenix_p_re=0.2,
                phoenix_p_im=-0.6
            ),
            # Newton
            Bookmark(
                name="Newton - Center",
                fractal_type="newton",
                center_re=0.0,
                center_im=0.0,
                scale=4.0,
                max_iterations=50
            ),
        ]

    def get_bookmarks(self) -> List[Bookmark]:
        """Get all bookmarks."""
        return self._bookmarks.copy()

    def get_bookmark(self, name: str) -> Optional[Bookmark]:
        """Get a bookmark by name."""
        for b in self._bookmarks:
            if b.name == name:
                return b
        return None

    def add_bookmark(self, bookmark: Bookmark) -> bool:
        """
        Add a new bookmark.

        Returns:
            True if added, False if name already exists
        """
        if any(b.name == bookmark.name for b in self._bookmarks):
            return False

        self._bookmarks.append(bookmark)
        self._save()
        return True

    def update_bookmark(self, name: str, bookmark: Bookmark) -> bool:
        """
        Update an existing bookmark.

        Args:
            name: Name of bookmark to update
            bookmark: New bookmark data

        Returns:
            True if updated, False if not found
        """
        for i, b in enumerate(self._bookmarks):
            if b.name == name:
                self._bookmarks[i] = bookmark
                self._save()
                return True
        return False

    def remove_bookmark(self, name: str) -> bool:
        """
        Remove a bookmark by name.

        Returns:
            True if removed, False if not found
        """
        for i, b in enumerate(self._bookmarks):
            if b.name == name:
                del self._bookmarks[i]
                self._save()
                return True
        return False

    def rename_bookmark(self, old_name: str, new_name: str) -> bool:
        """
        Rename a bookmark.

        Returns:
            True if renamed, False if old name not found or new name exists
        """
        if any(b.name == new_name for b in self._bookmarks):
            return False

        for b in self._bookmarks:
            if b.name == old_name:
                b.name = new_name
                self._save()
                return True
        return False

    def get_bookmarks_for_fractal(self, fractal_type: str) -> List[Bookmark]:
        """Get all bookmarks for a specific fractal type."""
        return [b for b in self._bookmarks if b.fractal_type == fractal_type]

    def reset_to_defaults(self):
        """Reset bookmarks to defaults."""
        self._bookmarks = self._get_default_bookmarks()
        self._save()

    def export_bookmarks(self, filepath: str) -> bool:
        """Export bookmarks to a file."""
        try:
            data = {
                'version': 1,
                'bookmarks': [b.to_dict() for b in self._bookmarks]
            }
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            return True
        except IOError:
            return False

    def import_bookmarks(self, filepath: str, merge: bool = True) -> bool:
        """
        Import bookmarks from a file.

        Args:
            filepath: File to import from
            merge: If True, merge with existing; if False, replace

        Returns:
            True if successful
        """
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
                imported = [Bookmark.from_dict(b) for b in data.get('bookmarks', [])]

            if merge:
                # Add only new bookmarks
                existing_names = {b.name for b in self._bookmarks}
                for b in imported:
                    if b.name not in existing_names:
                        self._bookmarks.append(b)
            else:
                self._bookmarks = imported

            self._save()
            return True
        except (IOError, json.JSONDecodeError, KeyError):
            return False
