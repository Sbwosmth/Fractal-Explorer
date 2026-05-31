"""
Fractal Explorer - Main entry point.

Interactive application for visualizing and exploring fractals.
"""

import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt


def main():
    """Main application entry point."""
    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    # Create application
    app = QApplication(sys.argv)
    app.setApplicationName("Fractal Explorer")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("FractalExplorer")

    # Set application style
    app.setStyle("Fusion")

    # Import here to avoid circular imports
    from .ui.main_window import MainWindow

    # Create and show main window
    window = MainWindow()
    window.show()

    # Run event loop
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
