from __future__ import annotations

import os
import sys
from pathlib import Path


PROFILE_ENV_VAR = "MANNA_SNIPS_PROFILE"


def split_profile_args(argv: list[str]) -> tuple[list[str], str | None]:
    forward: list[str] = []
    profile: str | None = None
    index = 0
    while index < len(argv):
        arg = argv[index]
        if arg == "--profile" and index + 1 < len(argv):
            profile = argv[index + 1].strip()
            index += 2
            continue
        forward.append(arg)
        index += 1
    return forward, profile


forward_args, selected_profile = split_profile_args(sys.argv[1:])
if selected_profile:
    os.environ[PROFILE_ENV_VAR] = selected_profile
elif not os.environ.get(PROFILE_ENV_VAR):
    os.environ[PROFILE_ENV_VAR] = "readme-preview"

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

import tkinter as tk

from manna_snips.app import APP_NAME, AnnotationEditorWindow, MannaSnipsApp


GENERIC_DOWNLOAD_ROOT = r"C:\Users\You\Downloads\Manna Snips"
GENERIC_INSTALL_ROOT = r"C:\Program Files\Manna Snips"
GENERIC_DATA_ROOT = r"C:\Users\You\AppData\Local\Manna Snips\default"
GENERIC_LATEST_CAPTURE = r"C:\Users\You\Downloads\Manna Snips\2026-05-12\snip-20260512-120100.png"


def add_line_annotation(editor: AnnotationEditorWindow, points: list[tuple[int, int]], color: str, width: int) -> None:
    flattened = [coordinate for xy in points for coordinate in xy]
    preview_id = editor.canvas.create_line(
        *flattened,
        fill=color,
        width=width,
        capstyle="round",
        joinstyle="round",
        smooth=True,
    )
    editor.annotations.append(
        {
            "tool": "pen",
            "color": color,
            "width": width,
            "points": points,
            "preview_id": preview_id,
        }
    )


def add_rectangle_annotation(
    editor: AnnotationEditorWindow,
    start: tuple[int, int],
    end: tuple[int, int],
    color: str,
    width: int,
) -> None:
    preview_id = editor.canvas.create_rectangle(
        start[0],
        start[1],
        end[0],
        end[1],
        outline=color,
        width=width,
    )
    editor.annotations.append(
        {
            "tool": "rectangle",
            "color": color,
            "width": width,
            "points": [start, end],
            "preview_id": preview_id,
        }
    )


def add_arrow_annotation(
    editor: AnnotationEditorWindow,
    start: tuple[int, int],
    end: tuple[int, int],
    color: str,
    width: int,
) -> None:
    preview_id = editor.canvas.create_line(
        start[0],
        start[1],
        end[0],
        end[1],
        fill=color,
        width=width,
        arrow=tk.LAST,
        arrowshape=(16, 18, 6),
        capstyle="round",
    )
    editor.annotations.append(
        {
            "tool": "arrow",
            "color": color,
            "width": width,
            "points": [start, end],
            "preview_id": preview_id,
        }
    )


def configure_main_preview(app: MannaSnipsApp) -> None:
    app.unregister_hotkey()
    app.root.geometry("980x620+120+120")
    app.hotkey_state_var.set("ARMED")
    app.file_flow_var.set("COPY FIRST")
    app.open_editor_var.set(True)
    app.start_with_windows_var.set(True)
    app.latest_capture_var.set(GENERIC_LATEST_CAPTURE)
    app.download_root_var.set(GENERIC_DOWNLOAD_ROOT)
    app.install_root_var.set(GENERIC_INSTALL_ROOT)
    app.data_root_var.set(GENERIC_DATA_ROOT)
    app.set_status("Ready. Press Ctrl+Shift+S from any app to start a real copy-first snip.")
    app.root.update_idletasks()
    app.root.deiconify()
    app.root.lift()
    app.root.focus_force()


def configure_editor_preview(app: MannaSnipsApp, sample_path: Path) -> None:
    app.unregister_hotkey()
    app.root.withdraw()
    app.open_editor(sample_path)
    editor = app.editor_window
    if editor is None:
        raise RuntimeError("Could not open README preview editor window.")

    editor.window.geometry("1320x940+120+120")
    editor.tool_var.set("arrow")
    editor.color_var.set("#ffd166")
    editor.width_var.set(6)
    add_rectangle_annotation(editor, (42, 50), (316, 180), "#3da0ff", 6)
    add_arrow_annotation(editor, (560, 142), (390, 142), "#ffd166", 8)
    add_line_annotation(editor, [(520, 112), (586, 92), (646, 92), (708, 108)], "#9fffb8", 7)
    editor.status_var.set("Mark up the snip, then use Copy + Close to send it back to the clipboard.")
    editor.window.update_idletasks()
    editor.window.deiconify()
    editor.window.lift()
    editor.window.focus_force()


def main(argv: list[str]) -> int:
    if not argv:
        raise SystemExit("Usage: launch_readme_preview.py <main|editor> [sample-image-path]")

    mode = argv[0].strip().lower()

    root = tk.Tk()
    app = MannaSnipsApp(root)

    if mode == "main":
        configure_main_preview(app)
    elif mode == "editor":
        if len(argv) < 2:
            raise SystemExit("Editor preview mode requires a sample image path.")
        sample_path = Path(argv[1]).resolve()
        if not sample_path.exists():
            raise SystemExit(f"Sample image not found: {sample_path}")
        configure_editor_preview(app, sample_path)
    else:
        raise SystemExit(f"Unknown preview mode: {mode}")

    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(forward_args))
