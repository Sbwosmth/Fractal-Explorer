"""
Video encoder using FFmpeg for MP4 and GIF output.
"""

import os
import subprocess
import shutil
from pathlib import Path
from typing import Optional, Callable, Tuple
import tempfile


class VideoEncoder:
    """
    Video encoder using FFmpeg subprocess.

    Supports MP4 (H.264) and GIF output.
    """

    def __init__(self):
        """Initialize video encoder."""
        self._ffmpeg_path = self._find_ffmpeg()
        self._cancelled = False

    @staticmethod
    def _find_ffmpeg() -> Optional[str]:
        """Find FFmpeg executable in PATH."""
        ffmpeg = shutil.which("ffmpeg")
        if ffmpeg:
            return ffmpeg

        # Try common installation locations on Windows
        common_paths = [
            r"C:\ffmpeg\bin\ffmpeg.exe",
            r"C:\Program Files\ffmpeg\bin\ffmpeg.exe",
            r"C:\Program Files (x86)\ffmpeg\bin\ffmpeg.exe",
        ]
        for path in common_paths:
            if os.path.isfile(path):
                return path

        return None

    @property
    def is_available(self) -> bool:
        """Check if FFmpeg is available."""
        return self._ffmpeg_path is not None

    def get_ffmpeg_version(self) -> Optional[str]:
        """Get FFmpeg version string."""
        if not self._ffmpeg_path:
            return None

        try:
            result = subprocess.run(
                [self._ffmpeg_path, "-version"],
                capture_output=True,
                text=True,
                timeout=5
            )
            first_line = result.stdout.split('\n')[0]
            return first_line
        except Exception:
            return None

    def cancel(self):
        """Cancel ongoing encoding."""
        self._cancelled = True

    def reset(self):
        """Reset cancellation state."""
        self._cancelled = False

    def encode_mp4(self,
                   input_pattern: str,
                   output_path: str,
                   fps: int = 30,
                   crf: int = 18,
                   preset: str = "medium",
                   progress_callback: Optional[Callable[[float], None]] = None) -> bool:
        """
        Encode frames to MP4 using H.264.

        Args:
            input_pattern: FFmpeg input pattern (e.g., "frame_%06d.png")
            output_path: Output MP4 file path
            fps: Frames per second
            crf: Constant Rate Factor (0-51, lower = better quality)
            preset: Encoding preset (ultrafast, fast, medium, slow, veryslow)
            progress_callback: Callback with progress 0.0-1.0

        Returns:
            True if successful, False otherwise
        """
        if not self._ffmpeg_path:
            return False

        self._cancelled = False

        cmd = [
            self._ffmpeg_path,
            "-y",  # Overwrite output
            "-framerate", str(fps),
            "-i", input_pattern,
            "-c:v", "libx264",
            "-preset", preset,
            "-crf", str(crf),
            "-pix_fmt", "yuv420p",  # Compatibility
            "-progress", "pipe:1",  # Progress to stdout
            output_path
        ]

        try:
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )

            # Parse progress from FFmpeg output
            while True:
                if self._cancelled:
                    process.kill()
                    return False

                line = process.stdout.readline()
                if not line:
                    break

                # Parse progress information
                if line.startswith("frame="):
                    try:
                        frame_str = line.split("=")[1].strip()
                        if progress_callback and frame_str.isdigit():
                            # Approximate progress (we don't know total frames here)
                            pass
                    except (IndexError, ValueError):
                        pass

            process.wait()
            return process.returncode == 0

        except Exception as e:
            print(f"FFmpeg encoding error: {e}")
            return False

    def encode_gif(self,
                   input_pattern: str,
                   output_path: str,
                   fps: int = 15,
                   width: int = 480,
                   progress_callback: Optional[Callable[[float], None]] = None) -> bool:
        """
        Encode frames to GIF with palette optimization.

        Uses two-pass encoding for better color quality.

        Args:
            input_pattern: FFmpeg input pattern
            output_path: Output GIF file path
            fps: Frames per second
            width: Output width (height auto-calculated)
            progress_callback: Callback with progress 0.0-1.0

        Returns:
            True if successful, False otherwise
        """
        if not self._ffmpeg_path:
            return False

        self._cancelled = False

        # Create temporary palette file
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
            palette_path = f.name

        try:
            # Pass 1: Generate palette
            if progress_callback:
                progress_callback(0.1)

            palette_cmd = [
                self._ffmpeg_path,
                "-y",
                "-framerate", str(fps),
                "-i", input_pattern,
                "-vf", f"fps={fps},scale={width}:-1:flags=lanczos,palettegen=stats_mode=diff",
                palette_path
            ]

            result = subprocess.run(
                palette_cmd,
                capture_output=True,
                timeout=300
            )

            if result.returncode != 0:
                return False

            if self._cancelled:
                return False

            if progress_callback:
                progress_callback(0.5)

            # Pass 2: Encode with palette
            gif_cmd = [
                self._ffmpeg_path,
                "-y",
                "-framerate", str(fps),
                "-i", input_pattern,
                "-i", palette_path,
                "-lavfi", f"fps={fps},scale={width}:-1:flags=lanczos[x];[x][1:v]paletteuse=dither=bayer:bayer_scale=5:diff_mode=rectangle",
                output_path
            ]

            result = subprocess.run(
                gif_cmd,
                capture_output=True,
                timeout=600
            )

            if progress_callback:
                progress_callback(1.0)

            return result.returncode == 0

        except subprocess.TimeoutExpired:
            return False
        except Exception as e:
            print(f"GIF encoding error: {e}")
            return False
        finally:
            # Clean up palette file
            try:
                os.unlink(palette_path)
            except OSError:
                pass

    def encode_from_frames(self,
                           frames_dir: str,
                           frame_pattern: str,
                           output_path: str,
                           fps: int = 30,
                           format: str = "mp4",
                           **kwargs) -> bool:
        """
        Encode video from frame directory.

        Args:
            frames_dir: Directory containing frames
            frame_pattern: Frame filename pattern (e.g., "frame_%06d.png")
            output_path: Output video path
            fps: Frames per second
            format: Output format ("mp4" or "gif")
            **kwargs: Additional format-specific arguments

        Returns:
            True if successful
        """
        input_pattern = os.path.join(frames_dir, frame_pattern)

        if format.lower() == "gif":
            return self.encode_gif(input_pattern, output_path, fps, **kwargs)
        else:
            return self.encode_mp4(input_pattern, output_path, fps, **kwargs)


def check_ffmpeg_available() -> Tuple[bool, Optional[str]]:
    """
    Check if FFmpeg is available and get version.

    Returns:
        Tuple of (is_available, version_string)
    """
    encoder = VideoEncoder()
    if encoder.is_available:
        return True, encoder.get_ffmpeg_version()
    return False, None
