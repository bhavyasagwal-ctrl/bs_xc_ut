from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

from PySide6.QtCore import Qt
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QApplication,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from app.project import VideoProject


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.project = VideoProject()
        self.setWindowTitle("bs_xc_ut")
        self.resize(1200, 700)

        self._build_menu()
        self._build_widgets()
        self.refresh_timeline()
        self.statusBar().showMessage("Project ready")

    def _build_menu(self) -> None:
        menubar = self.menuBar()
        file_menu = menubar.addMenu("File")

        add_action = QAction("Add media", self)
        add_action.triggered.connect(self.import_media)
        file_menu.addAction(add_action)

        export_action = QAction("Export timeline", self)
        export_action.triggered.connect(self.export_project)
        file_menu.addAction(export_action)

        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)

    def _build_widgets(self) -> None:
        central_widget = QWidget(self)
        root_layout = QHBoxLayout(central_widget)

        left_panel = QWidget(self)
        left_layout = QVBoxLayout(left_panel)

        self.media_library = QListWidget(self)
        self.media_library.setFixedWidth(280)
        left_layout.addWidget(QLabel("Media library"))
        left_layout.addWidget(self.media_library)

        buttons = QHBoxLayout()
        add_button = QPushButton("Add media")
        add_button.clicked.connect(self.import_media)
        buttons.addWidget(add_button)

        preview_button = QPushButton("Preview")
        preview_button.clicked.connect(self.preview_selected_clip)
        buttons.addWidget(preview_button)
        left_layout.addLayout(buttons)

        root_layout.addWidget(left_panel)

        main_panel = QWidget(self)
        main_layout = QVBoxLayout(main_panel)

        self.preview_label = QLabel("Select a clip to preview.")
        self.preview_label.setStyleSheet(
            "QLabel { background-color: #111827; color: white; border: 1px solid #374151; border-radius: 8px; padding: 24px; }"
        )
        self.preview_label.setAlignment(Qt.AlignCenter)
        self.preview_label.setMinimumHeight(260)
        main_layout.addWidget(self.preview_label)

        self.timeline = QListWidget(self)
        self.timeline.setAlternatingRowColors(True)
        self.timeline.setMinimumHeight(220)
        main_layout.addWidget(QLabel("Timeline"))
        main_layout.addWidget(self.timeline)

        actions = QHBoxLayout()
        export_button = QPushButton("Export project")
        export_button.clicked.connect(self.export_project)
        actions.addWidget(export_button)

        clear_button = QPushButton("Clear timeline")
        clear_button.clicked.connect(self.clear_timeline)
        actions.addWidget(clear_button)
        main_layout.addLayout(actions)

        root_layout.addWidget(main_panel)
        self.setCentralWidget(central_widget)

    def refresh_timeline(self) -> None:
        self.media_library.clear()
        self.timeline.clear()

        for clip in self.project.clips:
            self.media_library.addItem(f"{clip.filename} ({clip.duration:.1f}s)")
            self.timeline.addItem(f"{clip.filename} | {clip.duration:.1f}s")

        if self.project.clips:
            self.preview_label.setText(
                f"Loaded {len(self.project.clips)} clip(s)\nTotal duration: {self.project.total_duration():.1f}s"
            )
        else:
            self.preview_label.setText("Select a clip to preview.")

    def import_media(self) -> None:
        dialog = QFileDialog(self)
        dialog.setFileMode(QFileDialog.ExistingFiles)
        dialog.setNameFilter(
            "Video and image files (*.mp4 *.mov *.mkv *.avi *.m4v *.webm *.jpg *.jpeg *.png *.gif *.mp3 *.wav)"
        )
        if dialog.exec():
            paths = dialog.selectedFiles()
            if not paths:
                return

            for file_path in paths:
                try:
                    self.project.add_clip(file_path)
                    self.statusBar().showMessage(f"Added: {Path(file_path).name}")
                except Exception as exc:  # pragma: no cover - UI feedback only
                    QMessageBox.warning(self, "Import failed", str(exc))

            self.refresh_timeline()

    def preview_selected_clip(self) -> None:
        if not self.project.clips:
            QMessageBox.information(self, "Preview", "Import a clip first.")
            return

        row = self.timeline.currentRow()
        if row < 0:
            row = 0

        clip = self.project.clips[row]
        ffplay = shutil.which("ffplay")
        if not ffplay:
            QMessageBox.information(
                self,
                "Preview not available",
                "ffplay is not installed. Install FFmpeg to preview clips.",
            )
            return

        self.preview_label.setText(f"Previewing: {clip.filename}\nRuntime: {clip.duration:.1f}s")
        subprocess.Popen([ffplay, "-autoexit", "-i", clip.path])

    def export_project(self) -> None:
        if not self.project.clips:
            QMessageBox.warning(self, "Export failed", "No clips available to export.")
            return

        file_name, _ = QFileDialog.getSaveFileName(
            self,
            "Save exported video",
            "output.mp4",
            "MP4 Video (*.mp4)",
        )
        if not file_name:
            return

        try:
            output_path = self.project.export(file_name)
            self.statusBar().showMessage(f"Export complete: {output_path}")
            QMessageBox.information(self, "Export complete", f"Saved to:\n{output_path}")
        except Exception as exc:  # pragma: no cover - UI feedback only
            QMessageBox.critical(self, "Export failed", str(exc))

    def clear_timeline(self) -> None:
        self.project.clear()
        self.refresh_timeline()
        self.statusBar().showMessage("Timeline cleared")


def main() -> None:
    app = QApplication([])
    app.setApplicationName("bs_xc_ut")
    window = MainWindow()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()
