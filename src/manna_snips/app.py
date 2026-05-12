from __future__ import annotations

import argparse
import ctypes
import json
import math
import os
import queue
import subprocess
import sys
import threading
import time
import tomllib
import winreg
from ctypes import wintypes
from datetime import datetime
from importlib import metadata as importlib_metadata
from pathlib import Path
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import winsound


APP_ID = "manna.snips.desktop"
APP_NAME = "Manna Snips"
DEFAULT_HOTKEY_TEXT = "Ctrl+Shift+S"
HOTKEY_ID = 0xA17
PROFILE_ENV_VAR = "MANNA_SNIPS_PROFILE"
STARTUP_RUN_KEY = r"Software\Microsoft\Windows\CurrentVersion\Run"
IS_FROZEN_BUILD = bool(getattr(sys, "frozen", False))

PACKAGE_DIR = Path(__file__).resolve().parent
SRC_DIR = PACKAGE_DIR.parent
PROJECT_ROOT = SRC_DIR.parent
RUNTIME_ROOT = Path(getattr(sys, "_MEIPASS", PROJECT_ROOT if not IS_FROZEN_BUILD else Path(sys.executable).resolve().parent))
APP_LAUNCH_ROOT = Path(sys.executable).resolve().parent if IS_FROZEN_BUILD else PROJECT_ROOT
WORKSPACE_ROOT = PROJECT_ROOT.parents[1] if len(PROJECT_ROOT.parents) >= 2 and PROJECT_ROOT.parent.name == "projects" else None
LOCAL_APPDATA = Path(os.environ.get("LOCALAPPDATA") or (Path.home() / "AppData" / "Local"))


def resolve_app_version() -> str:
    try:
        return importlib_metadata.version("manna-snips")
    except importlib_metadata.PackageNotFoundError:
        pass

    pyproject_path = PROJECT_ROOT / "pyproject.toml"
    if pyproject_path.exists():
        try:
            project_data = tomllib.loads(pyproject_path.read_text(encoding="utf-8"))
            version = str(project_data.get("project", {}).get("version", "")).strip()
            if version:
                return version
        except (OSError, tomllib.TOMLDecodeError):
            pass
    return "0.1.1"


def normalize_profile_name(raw: str) -> str:
    cleaned = "".join(char.lower() if char.isalnum() else "-" for char in raw.strip())
    while "--" in cleaned:
        cleaned = cleaned.replace("--", "-")
    return cleaned.strip("-") or "default"


RAW_PROFILE = os.environ.get(PROFILE_ENV_VAR, "")
PROFILE_NAME = normalize_profile_name(RAW_PROFILE) if RAW_PROFILE else "default"
PROFILE_SUFFIX = "" if PROFILE_NAME == "default" else f" ({PROFILE_NAME})"
PROFILE_SUBDIR = Path("default") if PROFILE_NAME == "default" else Path("profiles") / PROFILE_NAME
STARTUP_VALUE_NAME = "MannaSnips" if PROFILE_NAME == "default" else f"MannaSnips-{PROFILE_NAME}"
APP_VERSION = resolve_app_version()
STATE_ROOT = LOCAL_APPDATA / APP_NAME / PROFILE_SUBDIR
STATE_DIR = STATE_ROOT / "state"
STATE_PATH = STATE_DIR / "settings.json"
TEMP_DIR = STATE_ROOT / "temp"
TEMP_RAW_CAPTURE_PATH = TEMP_DIR / "raw-snip.png"
TEMP_EDITED_CAPTURE_PATH = TEMP_DIR / "edited-snip.png"
OUTPUT_ROOT_DEFAULT = Path.home() / "Downloads" / (APP_NAME if PROFILE_NAME == "default" else f"{APP_NAME}{PROFILE_SUFFIX}")
SAVE_HELPER_PATH = RUNTIME_ROOT / "scripts" / "save-clipboard-image.ps1"
SET_CLIPBOARD_HELPER_PATH = RUNTIME_ROOT / "scripts" / "set-clipboard-image.ps1"
ICON_PATH = RUNTIME_ROOT / "assets" / "icons" / "manna-snips.ico"
LEGACY_STATE_PATH = (WORKSPACE_ROOT / "state" / "manna_snips.json") if WORKSPACE_ROOT else None
LEGACY_OUTPUT_ROOT = (WORKSPACE_ROOT / "outputs" / "manna-snips") if WORKSPACE_ROOT else None

CREATE_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0)

MOD_ALT = 0x0001
MOD_CONTROL = 0x0002
MOD_SHIFT = 0x0004
WM_HOTKEY = 0x0312
PM_REMOVE = 0x0001
WM_QUIT = 0x0012

CF_BITMAP = 2
CF_DIB = 8
CF_DIBV5 = 17
IMAGE_BITMAP = 0
LR_CREATEDIBSECTION = 0x2000
HOTKEY_POLL_INTERVAL_MS = 50
CAPTURE_OVERLAY_DELAY_MS = 120
CAPTURE_COMMIT_DELAY_MS = 80

SM_XVIRTUALSCREEN = 76
SM_YVIRTUALSCREEN = 77
SM_CXVIRTUALSCREEN = 78
SM_CYVIRTUALSCREEN = 79
SRCCOPY = 0x00CC0020
CAPTUREBLT = 0x40000000

BG = "#071019"
PANEL = "#0d1824"
PANEL_ALT = "#101d2b"
TEXT = "#edf6ff"
TEXT_MUTED = "#8aa8c7"
TEXT_SYSTEM = "#9fffb8"
ACCENT = "#3da0ff"
ACCENT_SOFT = "#143354"
BORDER = "#22364b"
OVERLAY_TEXT = "#f4fbff"
OVERLAY_LINE = "#4bb6ff"

DEFAULT_SETTINGS = {
    "open_editor_after_snip": True,
    "download_root": str(OUTPUT_ROOT_DEFAULT),
    "last_save_dir": str(OUTPUT_ROOT_DEFAULT),
    "latest_capture": "",
    "hotkey_combo": DEFAULT_HOTKEY_TEXT,
    "editor_tool": "pen",
    "editor_color": "#3da0ff",
    "editor_width": 6,
}

HOTKEY_PRESETS = (
    "Ctrl+Shift+S",
    "Ctrl+Shift+A",
    "Ctrl+Shift+X",
    "Ctrl+Alt+S",
    "Ctrl+Alt+A",
    "Ctrl+Alt+X",
    "Alt+Shift+S",
    "Alt+Shift+A",
    "Alt+Shift+X",
    "F8",
    "F9",
    "F10",
)

HOTKEY_BINDINGS = {
    "Ctrl+Shift+S": (MOD_CONTROL | MOD_SHIFT, ord("S")),
    "Ctrl+Shift+A": (MOD_CONTROL | MOD_SHIFT, ord("A")),
    "Ctrl+Shift+X": (MOD_CONTROL | MOD_SHIFT, ord("X")),
    "Ctrl+Alt+S": (MOD_CONTROL | MOD_ALT, ord("S")),
    "Ctrl+Alt+A": (MOD_CONTROL | MOD_ALT, ord("A")),
    "Ctrl+Alt+X": (MOD_CONTROL | MOD_ALT, ord("X")),
    "Alt+Shift+S": (MOD_SHIFT | MOD_ALT, ord("S")),
    "Alt+Shift+A": (MOD_SHIFT | MOD_ALT, ord("A")),
    "Alt+Shift+X": (MOD_SHIFT | MOD_ALT, ord("X")),
    "F8": (0, 0x77),
    "F9": (0, 0x78),
    "F10": (0, 0x79),
}

HOTKEY_PRESET_ALIASES = {
    "".join(char for char in preset.lower() if char.isalnum()): preset for preset in HOTKEY_PRESETS
}

POWER_SHELL = [
    "powershell",
    "-NoProfile",
    "-STA",
    "-ExecutionPolicy",
    "Bypass",
]


user32 = ctypes.windll.user32
shell32 = ctypes.windll.shell32
gdi32 = ctypes.windll.gdi32
gdiplus = ctypes.windll.gdiplus


class POINT(ctypes.Structure):
    _fields_ = [
        ("x", wintypes.LONG),
        ("y", wintypes.LONG),
    ]


class MSG(ctypes.Structure):
    _fields_ = [
        ("hwnd", wintypes.HWND),
        ("message", wintypes.UINT),
        ("wParam", wintypes.WPARAM),
        ("lParam", wintypes.LPARAM),
        ("time", wintypes.DWORD),
        ("pt", POINT),
    ]


class GUID(ctypes.Structure):
    _fields_ = [
        ("Data1", wintypes.DWORD),
        ("Data2", wintypes.WORD),
        ("Data3", wintypes.WORD),
        ("Data4", ctypes.c_ubyte * 8),
    ]


class GdiplusStartupInput(ctypes.Structure):
    _fields_ = [
        ("GdiplusVersion", wintypes.UINT),
        ("DebugEventCallback", ctypes.c_void_p),
        ("SuppressBackgroundThread", wintypes.BOOL),
        ("SuppressExternalCodecs", wintypes.BOOL),
    ]


user32.RegisterHotKey.argtypes = [wintypes.HWND, ctypes.c_int, wintypes.UINT, wintypes.UINT]
user32.RegisterHotKey.restype = wintypes.BOOL
user32.UnregisterHotKey.argtypes = [wintypes.HWND, ctypes.c_int]
user32.UnregisterHotKey.restype = wintypes.BOOL
user32.GetMessageW.argtypes = [ctypes.POINTER(MSG), wintypes.HWND, wintypes.UINT, wintypes.UINT]
user32.GetMessageW.restype = wintypes.BOOL
user32.PeekMessageW.argtypes = [ctypes.POINTER(MSG), wintypes.HWND, wintypes.UINT, wintypes.UINT, wintypes.UINT]
user32.PeekMessageW.restype = wintypes.BOOL
user32.PostThreadMessageW.argtypes = [wintypes.DWORD, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
user32.PostThreadMessageW.restype = wintypes.BOOL
user32.OpenClipboard.argtypes = [wintypes.HWND]
user32.OpenClipboard.restype = wintypes.BOOL
user32.CloseClipboard.restype = wintypes.BOOL
user32.IsClipboardFormatAvailable.argtypes = [wintypes.UINT]
user32.IsClipboardFormatAvailable.restype = wintypes.BOOL
user32.GetClipboardData.argtypes = [wintypes.UINT]
user32.GetClipboardData.restype = wintypes.HANDLE
user32.CopyImage.argtypes = [wintypes.HANDLE, wintypes.UINT, ctypes.c_int, ctypes.c_int, wintypes.UINT]
user32.CopyImage.restype = wintypes.HANDLE
user32.GetSystemMetrics.argtypes = [ctypes.c_int]
user32.GetSystemMetrics.restype = ctypes.c_int
user32.GetDC.argtypes = [wintypes.HWND]
user32.GetDC.restype = wintypes.HDC
user32.ReleaseDC.argtypes = [wintypes.HWND, wintypes.HDC]
user32.ReleaseDC.restype = ctypes.c_int
gdi32.CreateCompatibleDC.argtypes = [wintypes.HDC]
gdi32.CreateCompatibleDC.restype = wintypes.HDC
gdi32.DeleteDC.argtypes = [wintypes.HDC]
gdi32.DeleteDC.restype = wintypes.BOOL
gdi32.CreateCompatibleBitmap.argtypes = [wintypes.HDC, ctypes.c_int, ctypes.c_int]
gdi32.CreateCompatibleBitmap.restype = wintypes.HBITMAP
gdi32.SelectObject.argtypes = [wintypes.HDC, wintypes.HGDIOBJ]
gdi32.SelectObject.restype = wintypes.HGDIOBJ
gdi32.BitBlt.argtypes = [
    wintypes.HDC,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    wintypes.HDC,
    ctypes.c_int,
    ctypes.c_int,
    wintypes.DWORD,
]
gdi32.BitBlt.restype = wintypes.BOOL
gdi32.DeleteObject.argtypes = [wintypes.HGDIOBJ]
gdi32.DeleteObject.restype = wintypes.BOOL
gdiplus.GdiplusStartup.argtypes = [ctypes.POINTER(ctypes.c_void_p), ctypes.POINTER(GdiplusStartupInput), ctypes.c_void_p]
gdiplus.GdiplusStartup.restype = ctypes.c_int
gdiplus.GdiplusShutdown.argtypes = [ctypes.c_void_p]
gdiplus.GdipLoadImageFromFile.argtypes = [ctypes.c_wchar_p, ctypes.POINTER(ctypes.c_void_p)]
gdiplus.GdipLoadImageFromFile.restype = ctypes.c_int
gdiplus.GdipCreateBitmapFromHBITMAP.argtypes = [wintypes.HBITMAP, wintypes.HPALETTE, ctypes.POINTER(ctypes.c_void_p)]
gdiplus.GdipCreateBitmapFromHBITMAP.restype = ctypes.c_int
gdiplus.GdipGetImageGraphicsContext.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.c_void_p)]
gdiplus.GdipGetImageGraphicsContext.restype = ctypes.c_int
gdiplus.GdipDeleteGraphics.argtypes = [ctypes.c_void_p]
gdiplus.GdipDeleteGraphics.restype = ctypes.c_int
gdiplus.GdipSetSmoothingMode.argtypes = [ctypes.c_void_p, ctypes.c_int]
gdiplus.GdipSetSmoothingMode.restype = ctypes.c_int
gdiplus.GdipCreatePen1.argtypes = [ctypes.c_uint32, ctypes.c_float, ctypes.c_int, ctypes.POINTER(ctypes.c_void_p)]
gdiplus.GdipCreatePen1.restype = ctypes.c_int
gdiplus.GdipDeletePen.argtypes = [ctypes.c_void_p]
gdiplus.GdipDeletePen.restype = ctypes.c_int
gdiplus.GdipDrawLineI.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
gdiplus.GdipDrawLineI.restype = ctypes.c_int
gdiplus.GdipDrawRectangleI.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
gdiplus.GdipDrawRectangleI.restype = ctypes.c_int
gdiplus.GdipSaveImageToFile.argtypes = [ctypes.c_void_p, ctypes.c_wchar_p, ctypes.POINTER(GUID), ctypes.c_void_p]
gdiplus.GdipSaveImageToFile.restype = ctypes.c_int
gdiplus.GdipDisposeImage.argtypes = [ctypes.c_void_p]
gdiplus.GdipDisposeImage.restype = ctypes.c_int

kernel32 = ctypes.windll.kernel32
kernel32.GetCurrentThreadId.restype = wintypes.DWORD
kernel32.GetLastError.restype = wintypes.DWORD


PNG_ENCODER_CLSID = GUID(
    0x557CF406,
    0x1A04,
    0x11D3,
    (ctypes.c_ubyte * 8)(0x9A, 0x73, 0x00, 0x00, 0xF8, 0x1E, 0xF3, 0x2E),
)
GDIP_OK = 0
UNIT_PIXEL = 2
SMOOTHING_MODE_ANTI_ALIAS = 4


def enable_dpi_awareness() -> None:
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(2)
    except Exception:
        try:
            user32.SetProcessDPIAware()
        except Exception:
            pass


def ensure_directories() -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    TEMP_DIR.mkdir(parents=True, exist_ok=True)


def resolve_launch_script_path() -> Path:
    preferred = APP_LAUNCH_ROOT / "scripts" / "manna_snips_app.pyw"
    if preferred.exists():
        return preferred

    raw_argv0 = str(sys.argv[0] or "").strip()
    if raw_argv0 and raw_argv0 not in {"-", "-c"}:
        argv_path = Path(raw_argv0)
        if argv_path.exists():
            return argv_path.resolve()

    return preferred


def get_launch_command(*, start_minimized: bool = False) -> str:
    if IS_FROZEN_BUILD:
        command_parts = [str(Path(sys.executable).resolve())]
    else:
        executable = Path(sys.executable).resolve()
        pythonw_candidate = executable.with_name("pythonw.exe")
        if pythonw_candidate.exists():
            executable = pythonw_candidate
        command_parts = [str(executable), str(resolve_launch_script_path())]

    if PROFILE_NAME != "default":
        command_parts.extend(["--profile", PROFILE_NAME])
    if start_minimized:
        command_parts.append("--minimized")
    return subprocess.list2cmdline(command_parts)


def get_startup_command() -> str:
    return get_launch_command(start_minimized=True)


def read_startup_command() -> str:
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, STARTUP_RUN_KEY, 0, winreg.KEY_READ) as key:
            value, _ = winreg.QueryValueEx(key, STARTUP_VALUE_NAME)
    except FileNotFoundError:
        return ""
    return str(value or "").strip()


def is_start_with_windows_enabled() -> bool:
    return read_startup_command().lower() == get_startup_command().lower()


def set_start_with_windows_enabled(enabled: bool) -> None:
    with winreg.CreateKey(winreg.HKEY_CURRENT_USER, STARTUP_RUN_KEY) as key:
        if enabled:
            winreg.SetValueEx(key, STARTUP_VALUE_NAME, 0, winreg.REG_SZ, get_startup_command())
            return
        try:
            winreg.DeleteValue(key, STARTUP_VALUE_NAME)
        except FileNotFoundError:
            return


def get_output_root(settings: dict[str, object] | None = None) -> Path:
    if settings:
        configured = str(settings.get("download_root", "") or "").strip()
        if configured:
            return Path(configured)
    return OUTPUT_ROOT_DEFAULT


def ensure_output_root(settings: dict[str, object] | None = None) -> Path:
    output_root = get_output_root(settings)
    output_root.mkdir(parents=True, exist_ok=True)
    return output_root


def delete_if_exists(path: Path) -> None:
    try:
        path.unlink()
    except FileNotFoundError:
        return
    except OSError:
        return


def cleanup_temp_capture_files() -> None:
    ensure_directories()
    for path in (TEMP_RAW_CAPTURE_PATH, TEMP_EDITED_CAPTURE_PATH):
        delete_if_exists(path)


def load_settings() -> dict[str, object]:
    ensure_directories()
    settings = dict(DEFAULT_SETTINGS)
    settings_path = STATE_PATH
    migrated = False
    if PROFILE_NAME == "default" and not settings_path.exists() and LEGACY_STATE_PATH and LEGACY_STATE_PATH.exists():
        settings_path = LEGACY_STATE_PATH
    if not settings_path.exists():
        return settings
    try:
        data = json.loads(settings_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return settings
    if isinstance(data, dict):
        settings.update({key: value for key, value in data.items() if key in DEFAULT_SETTINGS})
        latest_capture_value = str(settings.get("latest_capture", "") or "").strip()
        if latest_capture_value:
            latest_capture_path = Path(latest_capture_value)
            output_root = get_output_root(settings)
            if (
                PROFILE_NAME == "default"
                and LEGACY_OUTPUT_ROOT is not None
                and latest_capture_path.is_absolute()
                and str(latest_capture_path).lower().startswith(str(LEGACY_OUTPUT_ROOT).lower())
                and str(output_root).lower() == str(OUTPUT_ROOT_DEFAULT).lower()
            ):
                settings["latest_capture"] = ""
                migrated = True

        last_save_dir_value = str(settings.get("last_save_dir", "") or "").strip()
        if (
            PROFILE_NAME == "default"
            and LEGACY_OUTPUT_ROOT is not None
            and last_save_dir_value
            and last_save_dir_value.lower().startswith(str(LEGACY_OUTPUT_ROOT).lower())
            and str(get_output_root(settings)).lower() == str(OUTPUT_ROOT_DEFAULT).lower()
        ):
            settings["last_save_dir"] = str(get_output_root(settings))
            migrated = True

    if migrated:
        save_settings(settings)
    return settings


def save_settings(settings: dict[str, object]) -> None:
    ensure_directories()
    STATE_PATH.write_text(json.dumps(settings, indent=2), encoding="utf-8")


def clip_text(value: str, max_chars: int = 88) -> str:
    clean = value.strip()
    if len(clean) <= max_chars:
        return clean
    return clean[: max_chars - 3].rstrip() + "..."


def normalize_hotkey_text(raw: object) -> str:
    key = "".join(char for char in str(raw or "").lower() if char.isalnum())
    return HOTKEY_PRESET_ALIASES.get(key, DEFAULT_HOTKEY_TEXT)


def get_hotkey_binding(hotkey_text: str) -> tuple[int, int]:
    normalized = normalize_hotkey_text(hotkey_text)
    return HOTKEY_BINDINGS[normalized]


def default_capture_path(settings: dict[str, object] | None = None) -> Path:
    stamp = datetime.now()
    day_dir = get_output_root(settings) / stamp.strftime("%Y-%m-%d")
    filename = f"snip-{stamp.strftime('%Y%m%d-%H%M%S')}.png"
    return day_dir / filename


def get_virtual_screen_bounds() -> tuple[int, int, int, int]:
    x = int(user32.GetSystemMetrics(SM_XVIRTUALSCREEN))
    y = int(user32.GetSystemMetrics(SM_YVIRTUALSCREEN))
    width = int(user32.GetSystemMetrics(SM_CXVIRTUALSCREEN))
    height = int(user32.GetSystemMetrics(SM_CYVIRTUALSCREEN))
    return x, y, width, height


def clipboard_has_image() -> bool:
    for _ in range(10):
        if user32.OpenClipboard(None):
            try:
                return bool(
                    user32.IsClipboardFormatAvailable(CF_DIB)
                    or user32.IsClipboardFormatAvailable(CF_DIBV5)
                    or user32.IsClipboardFormatAvailable(CF_BITMAP)
                )
            finally:
                user32.CloseClipboard()
        time.sleep(0.04)
    return False


def save_clipboard_image_via_helper(target_path: Path) -> Path:
    command = POWER_SHELL + [
        "-File",
        str(SAVE_HELPER_PATH),
        "-Path",
        str(target_path),
    ]
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        creationflags=CREATE_NO_WINDOW,
        cwd=str(APP_LAUNCH_ROOT),
        check=False,
    )
    if result.returncode != 0:
        message = (result.stderr or result.stdout).strip() or "Clipboard image save failed."
        raise RuntimeError(message)

    output = (result.stdout or "").strip().splitlines()
    resolved = output[-1].strip() if output else str(target_path)
    return Path(resolved)


def set_clipboard_image_from_file(image_path: Path) -> Path:
    command = POWER_SHELL + [
        "-File",
        str(SET_CLIPBOARD_HELPER_PATH),
        "-Path",
        str(image_path),
    ]
    result = subprocess.run(
        command,
        capture_output=True,
        text=True,
        creationflags=CREATE_NO_WINDOW,
        cwd=str(APP_LAUNCH_ROOT),
        check=False,
    )
    if result.returncode != 0:
        message = (result.stderr or result.stdout).strip() or "Clipboard image copy failed."
        raise RuntimeError(message)

    output = (result.stdout or "").strip().splitlines()
    resolved = output[-1].strip() if output else str(image_path)
    return Path(resolved)


def copy_clipboard_bitmap_handle() -> tuple[int, bool]:
    for _ in range(10):
        if user32.OpenClipboard(None):
            try:
                handle = user32.GetClipboardData(CF_BITMAP)
                if not handle:
                    raise RuntimeError("No bitmap handle was available in the clipboard.")
                copied = user32.CopyImage(handle, IMAGE_BITMAP, 0, 0, LR_CREATEDIBSECTION)
                if copied:
                    return int(copied), True
                return int(handle), False
            finally:
                user32.CloseClipboard()
        time.sleep(0.04)
    raise RuntimeError("Could not open the clipboard to copy the bitmap handle.")


def save_bitmap_handle_as_png(bitmap_handle: int, target_path: Path) -> Path:
    target_path.parent.mkdir(parents=True, exist_ok=True)
    token = ctypes.c_void_p()
    image = ctypes.c_void_p()
    startup = GdiplusStartupInput(1, None, False, False)

    status = gdiplus.GdiplusStartup(ctypes.byref(token), ctypes.byref(startup), None)
    if status != GDIP_OK:
        raise RuntimeError(f"GDI+ startup failed with status {status}.")

    try:
        status = gdiplus.GdipCreateBitmapFromHBITMAP(bitmap_handle, None, ctypes.byref(image))
        if status != GDIP_OK:
            raise RuntimeError(f"GDI+ could not create a bitmap from the capture handle. Status {status}.")

        status = gdiplus.GdipSaveImageToFile(image, str(target_path), ctypes.byref(PNG_ENCODER_CLSID), None)
        if status != GDIP_OK:
            raise RuntimeError(f"GDI+ could not save the capture image. Status {status}.")
    finally:
        if image.value:
            gdiplus.GdipDisposeImage(image)
        gdiplus.GdiplusShutdown(token)

    return target_path


def save_clipboard_image(target_path: Path) -> Path:
    direct_error = ""
    bitmap_handle = 0
    owns_bitmap_handle = False
    try:
        bitmap_handle, owns_bitmap_handle = copy_clipboard_bitmap_handle()
        return save_bitmap_handle_as_png(bitmap_handle, target_path)
    except RuntimeError as exc:
        direct_error = str(exc)
    finally:
        if bitmap_handle and owns_bitmap_handle:
            gdi32.DeleteObject(bitmap_handle)

    try:
        return save_clipboard_image_via_helper(target_path)
    except RuntimeError as helper_exc:
        message = direct_error or "Direct clipboard save failed."
        raise RuntimeError(f"{message} Helper fallback also failed: {helper_exc}") from helper_exc


def hex_to_argb(color_hex: str, alpha: int = 255) -> int:
    clean = color_hex.lstrip("#")
    if len(clean) != 6:
        raise RuntimeError(f"Invalid color value: {color_hex}")
    red = int(clean[0:2], 16)
    green = int(clean[2:4], 16)
    blue = int(clean[4:6], 16)
    return ((alpha & 0xFF) << 24) | (red << 16) | (green << 8) | blue


def build_arrow_segments(start: tuple[int, int], end: tuple[int, int], width: int) -> list[tuple[int, int, int, int]]:
    x1, y1 = start
    x2, y2 = end
    angle = math.atan2(y2 - y1, x2 - x1)
    head_length = max(14, width * 3)
    wing_angle = math.radians(28)

    left_x = int(round(x2 - head_length * math.cos(angle - wing_angle)))
    left_y = int(round(y2 - head_length * math.sin(angle - wing_angle)))
    right_x = int(round(x2 - head_length * math.cos(angle + wing_angle)))
    right_y = int(round(y2 - head_length * math.sin(angle + wing_angle)))
    return [
        (x1, y1, x2, y2),
        (x2, y2, left_x, left_y),
        (x2, y2, right_x, right_y),
    ]


def render_annotated_image(source_path: Path, target_path: Path, annotations: list[dict[str, object]]) -> Path:
    token = ctypes.c_void_p()
    image = ctypes.c_void_p()
    graphics = ctypes.c_void_p()
    startup = GdiplusStartupInput(1, None, False, False)

    status = gdiplus.GdiplusStartup(ctypes.byref(token), ctypes.byref(startup), None)
    if status != GDIP_OK:
        raise RuntimeError(f"GDI+ startup failed with status {status}.")

    try:
        status = gdiplus.GdipLoadImageFromFile(str(source_path), ctypes.byref(image))
        if status != GDIP_OK:
            raise RuntimeError(f"GDI+ could not load the source image. Status {status}.")

        status = gdiplus.GdipGetImageGraphicsContext(image, ctypes.byref(graphics))
        if status != GDIP_OK:
            raise RuntimeError(f"GDI+ could not open a graphics context. Status {status}.")

        gdiplus.GdipSetSmoothingMode(graphics, SMOOTHING_MODE_ANTI_ALIAS)

        for annotation in annotations:
            tool = str(annotation.get("tool", ""))
            color = str(annotation.get("color", "#3da0ff"))
            width = int(annotation.get("width", 4))
            alpha = 255
            if tool == "highlight":
                alpha = 110

            pen = ctypes.c_void_p()
            status = gdiplus.GdipCreatePen1(hex_to_argb(color, alpha), float(width), UNIT_PIXEL, ctypes.byref(pen))
            if status != GDIP_OK:
                raise RuntimeError(f"GDI+ could not create a drawing pen. Status {status}.")
            try:
                points = [(int(point[0]), int(point[1])) for point in annotation.get("points", [])]
                if tool in {"pen", "highlight"}:
                    if len(points) == 1:
                        x, y = points[0]
                        gdiplus.GdipDrawRectangleI(graphics, pen, x, y, 1, 1)
                    else:
                        for start, end in zip(points, points[1:]):
                            gdiplus.GdipDrawLineI(graphics, pen, start[0], start[1], end[0], end[1])
                elif tool == "rectangle" and len(points) >= 2:
                    x1, y1 = points[0]
                    x2, y2 = points[-1]
                    left = min(x1, x2)
                    top = min(y1, y2)
                    rect_width = abs(x2 - x1)
                    rect_height = abs(y2 - y1)
                    gdiplus.GdipDrawRectangleI(graphics, pen, left, top, rect_width, rect_height)
                elif tool == "arrow" and len(points) >= 2:
                    for x1, y1, x2, y2 in build_arrow_segments(points[0], points[-1], width):
                        gdiplus.GdipDrawLineI(graphics, pen, x1, y1, x2, y2)
            finally:
                gdiplus.GdipDeletePen(pen)

        target_path.parent.mkdir(parents=True, exist_ok=True)
        status = gdiplus.GdipSaveImageToFile(image, str(target_path), ctypes.byref(PNG_ENCODER_CLSID), None)
        if status != GDIP_OK:
            raise RuntimeError(f"GDI+ could not save the annotated image. Status {status}.")
        return target_path
    finally:
        if graphics.value:
            gdiplus.GdipDeleteGraphics(graphics)
        if image.value:
            gdiplus.GdipDisposeImage(image)
        gdiplus.GdiplusShutdown(token)


def capture_screen_region(left: int, top: int, width: int, height: int) -> int:
    if width <= 0 or height <= 0:
        raise RuntimeError("Capture region must be larger than zero.")

    screen_dc = user32.GetDC(None)
    if not screen_dc:
        raise RuntimeError("Could not access the screen device context.")

    memory_dc = gdi32.CreateCompatibleDC(screen_dc)
    if not memory_dc:
        user32.ReleaseDC(None, screen_dc)
        raise RuntimeError("Could not create a compatible capture device context.")

    bitmap = gdi32.CreateCompatibleBitmap(screen_dc, width, height)
    if not bitmap:
        gdi32.DeleteDC(memory_dc)
        user32.ReleaseDC(None, screen_dc)
        raise RuntimeError("Could not allocate a capture bitmap.")

    previous = gdi32.SelectObject(memory_dc, bitmap)
    try:
        success = bool(gdi32.BitBlt(memory_dc, 0, 0, width, height, screen_dc, left, top, SRCCOPY | CAPTUREBLT))
        if not success:
            raise RuntimeError("BitBlt failed while capturing the selected region.")
    finally:
        gdi32.SelectObject(memory_dc, previous)
        gdi32.DeleteDC(memory_dc)
        user32.ReleaseDC(None, screen_dc)

    return int(bitmap)


def normalize_region(start_x: int, start_y: int, end_x: int, end_y: int) -> tuple[int, int, int, int]:
    left = min(start_x, end_x)
    top = min(start_y, end_y)
    width = abs(end_x - start_x)
    height = abs(end_y - start_y)
    return left, top, width, height


class CaptureSelectionOverlay:
    def __init__(
        self,
        parent: tk.Tk,
        on_complete,
        on_cancel,
    ) -> None:
        self.parent = parent
        self.on_complete = on_complete
        self.on_cancel = on_cancel
        self.origin_x, self.origin_y, self.width, self.height = get_virtual_screen_bounds()
        self.drag_start_canvas: tuple[int, int] | None = None
        self.drag_current_canvas: tuple[int, int] | None = None
        self.cursor_canvas_point: tuple[int, int] = (40, 40)

        self.window = tk.Toplevel(parent)
        self.window.overrideredirect(True)
        self.window.configure(bg="black")
        self.window.attributes("-topmost", True)
        try:
            self.window.attributes("-alpha", 0.22)
        except tk.TclError:
            pass
        self.window.geometry(f"{self.width}x{self.height}{self.origin_x:+d}{self.origin_y:+d}")

        self.canvas = tk.Canvas(
            self.window,
            bg="black",
            highlightthickness=0,
            cursor="none",
        )
        self.canvas.pack(fill="both", expand=True)

        self.hint_id = self.canvas.create_text(
            28,
            28,
            anchor="nw",
            text="Drag to capture. Esc cancels.",
            fill=OVERLAY_TEXT,
            font=("Segoe UI Semibold", 15),
        )
        self.detail_id = self.canvas.create_text(
            28,
            58,
            anchor="nw",
            text="Copy image is built into this snip flow.",
            fill=OVERLAY_TEXT,
            font=("Segoe UI", 11),
        )
        self.selection_rect = self.canvas.create_rectangle(0, 0, 0, 0, outline=OVERLAY_LINE, width=2, state="hidden")
        self.selection_label = self.canvas.create_text(
            0,
            0,
            anchor="nw",
            text="",
            fill=OVERLAY_TEXT,
            font=("Consolas", 11),
            state="hidden",
        )
        self.cursor_diamond = self.canvas.create_polygon(0, 0, 0, 0, 0, 0, 0, 0, fill="#3da0ff", outline="#edf6ff", width=1.4)
        self.cursor_plus_h = self.canvas.create_line(0, 0, 0, 0, fill="#edf6ff", width=2)
        self.cursor_plus_v = self.canvas.create_line(0, 0, 0, 0, fill="#edf6ff", width=2)
        self.cursor_flare = self.canvas.create_line(0, 0, 0, 0, fill="#9fffb8", width=2)
        self.cursor_flare_cross = self.canvas.create_line(0, 0, 0, 0, fill="#9fffb8", width=1.6)
        self.cursor_ring = self.canvas.create_oval(0, 0, 0, 0, outline="#9fffb8", width=1.2)
        self.cursor_core = self.canvas.create_oval(0, 0, 0, 0, fill="#edf6ff", outline="")

        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<Motion>", self.on_motion)
        self.window.bind("<Escape>", self.on_escape)
        self.update_cursor_art(40, 40)
        self.window.focus_force()

    def on_press(self, event: tk.Event) -> None:
        self.drag_start_canvas = (int(event.x), int(event.y))
        self.drag_current_canvas = (int(event.x), int(event.y))
        self.update_selection_art()

    def on_drag(self, event: tk.Event) -> None:
        if self.drag_start_canvas is None:
            return
        self.drag_current_canvas = (int(event.x), int(event.y))
        self.update_cursor_art(int(event.x), int(event.y))
        self.update_selection_art()

    def on_motion(self, event: tk.Event) -> None:
        self.update_cursor_art(int(event.x), int(event.y))

    def on_release(self, event: tk.Event) -> None:
        if self.drag_start_canvas is None:
            self.on_cancel()
            return

        self.drag_current_canvas = (int(event.x), int(event.y))
        left, top, width, height = normalize_region(
            self.drag_start_canvas[0] + self.origin_x,
            self.drag_start_canvas[1] + self.origin_y,
            self.drag_current_canvas[0] + self.origin_x,
            self.drag_current_canvas[1] + self.origin_y,
        )
        self.destroy()
        if width < 2 or height < 2:
            self.on_cancel()
            return
        self.on_complete((left, top, width, height))

    def on_escape(self, _event: tk.Event) -> None:
        self.destroy()
        self.on_cancel()

    def update_selection_art(self) -> None:
        if self.drag_start_canvas is None or self.drag_current_canvas is None:
            return

        x1, y1 = self.drag_start_canvas
        x2, y2 = self.drag_current_canvas
        left = min(x1, x2)
        top = min(y1, y2)
        right = max(x1, x2)
        bottom = max(y1, y2)
        width = abs(x2 - x1)
        height = abs(y2 - y1)
        label_x = left + 12
        label_y = max(18, top - 24)

        self.canvas.itemconfigure(self.selection_rect, state="normal")
        self.canvas.coords(self.selection_rect, left, top, right, bottom)
        self.canvas.itemconfigure(self.selection_label, state="normal", text=f"{width} x {height}")
        self.canvas.coords(self.selection_label, label_x, label_y)

    def update_cursor_art(self, x: int, y: int) -> None:
        self.cursor_canvas_point = (x, y)
        size = 10
        self.canvas.coords(
            self.cursor_diamond,
            x,
            y - size,
            x + size,
            y,
            x,
            y + size,
            x - size,
            y,
        )
        self.canvas.coords(self.cursor_plus_h, x - 4, y, x + 4, y)
        self.canvas.coords(self.cursor_plus_v, x, y - 4, x, y + 4)
        self.canvas.coords(self.cursor_flare, x + 7, y - 7, x + 16, y - 16)
        self.canvas.coords(self.cursor_flare_cross, x + 10, y - 16, x + 16, y - 10)
        self.canvas.coords(self.cursor_ring, x - 15, y - 15, x + 15, y + 15)
        self.canvas.coords(self.cursor_core, x - 2, y - 2, x + 2, y + 2)

    def destroy(self) -> None:
        try:
            self.window.destroy()
        except tk.TclError:
            pass


class AnnotationEditorWindow:
    COLOR_CHOICES = [
        ("Manna Blue", "#3da0ff"),
        ("Signal Green", "#9fffb8"),
        ("Alert Red", "#ff5f6d"),
        ("Marker Yellow", "#ffd166"),
        ("White", "#f4fbff"),
    ]
    WIDTH_CHOICES = [
        ("Thin", 3),
        ("Medium", 6),
        ("Bold", 10),
    ]
    TOOL_OPTIONS = (
        ("Pen", "pen"),
        ("Highlight", "highlight"),
        ("Rectangle", "rectangle"),
        ("Arrow", "arrow"),
    )
    SHORTCUT_HINT = "Shortcuts: P/H/R/A tools   1/2/3 width   Ctrl+C copy   Ctrl+D download   Ctrl+Enter copy+close   Ctrl+Z undo   Esc close"

    def __init__(self, app: "MannaSnipsApp", source_path: Path) -> None:
        self.app = app
        self.root = app.root
        self.source_path = source_path
        self.window = tk.Toplevel(self.root)
        self.window.title(f"{APP_NAME} Editor")
        self.window.geometry("1180x860")
        self.window.minsize(860, 640)
        self.window.configure(bg=BG)
        self.window.protocol("WM_DELETE_WINDOW", self.on_close)

        if ICON_PATH.exists():
            try:
                self.window.iconbitmap(default=str(ICON_PATH))
            except tk.TclError:
                pass

        tool_values = {value for _, value in self.TOOL_OPTIONS}
        tool_setting = str(app.settings.get("editor_tool", "pen") or "pen")
        if tool_setting not in tool_values:
            tool_setting = "pen"

        color_values = {value for _, value in self.COLOR_CHOICES}
        color_setting = str(app.settings.get("editor_color", "#3da0ff") or "#3da0ff")
        if color_setting not in color_values:
            color_setting = "#3da0ff"

        width_values = {value for _, value in self.WIDTH_CHOICES}
        width_setting = app.settings.get("editor_width", 6)
        width_setting = int(width_setting) if width_setting in width_values else 6

        self.tool_var = tk.StringVar(value=tool_setting)
        self.color_var = tk.StringVar(value=color_setting)
        self.width_var = tk.IntVar(value=width_setting)
        self.annotations: list[dict[str, object]] = []
        self.active_annotation: dict[str, object] | None = None

        self.image = tk.PhotoImage(file=str(source_path))
        self.image_width = int(self.image.width())
        self.image_height = int(self.image.height())

        self.status_var = tk.StringVar(value="Mark up the snip, then use Copy + Close to send it back to the clipboard.")

        self.build_ui()
        self.bind_shortcuts()
        self.window.after(60, self.focus_canvas)

    def build_ui(self) -> None:
        shell = ttk.Frame(self.window, style="Shell.TFrame", padding=14)
        shell.pack(fill="both", expand=True)

        header = ttk.Frame(shell, style="Shell.TFrame")
        header.pack(fill="x")
        ttk.Label(header, text="Manna Snips Editor", style="Header.TLabel").pack(anchor="w")
        ttk.Label(
            header,
            text="lightweight markup before copy so screenshots stay shareable without file clutter",
            style="SubHeader.TLabel",
        ).pack(anchor="w", pady=(3, 12))

        toolbar = ttk.Frame(shell, style="PanelAlt.TFrame", padding=(12, 10))
        toolbar.pack(fill="x", pady=(0, 12))
        self.app.decorate_panel(toolbar, PANEL_ALT)

        tools_row = ttk.Frame(toolbar, style="PanelAlt.TFrame")
        tools_row.pack(fill="x")
        ttk.Label(tools_row, text="TOOLS", style="State.TLabel").pack(side="left")
        for label, value in self.TOOL_OPTIONS:
            ttk.Radiobutton(
                tools_row,
                text=label,
                value=value,
                variable=self.tool_var,
                style="Tool.TRadiobutton",
                command=self.on_tool_changed,
            ).pack(side="left", padx=(10, 0))

        colors_row = ttk.Frame(toolbar, style="PanelAlt.TFrame")
        colors_row.pack(fill="x", pady=(10, 0))
        ttk.Label(colors_row, text="COLOR", style="State.TLabel").pack(side="left")
        for label, value in self.COLOR_CHOICES:
            ttk.Radiobutton(
                colors_row,
                text=label,
                value=value,
                variable=self.color_var,
                style="Tool.TRadiobutton",
                command=self.on_color_changed,
            ).pack(side="left", padx=(10, 0))

        width_row = ttk.Frame(toolbar, style="PanelAlt.TFrame")
        width_row.pack(fill="x", pady=(10, 0))
        ttk.Label(width_row, text="WIDTH", style="State.TLabel").pack(side="left")
        for label, value in self.WIDTH_CHOICES:
            ttk.Radiobutton(
                width_row,
                text=label,
                value=value,
                variable=self.width_var,
                style="Tool.TRadiobutton",
                command=self.on_width_changed,
            ).pack(side="left", padx=(10, 0))

        actions_row = ttk.Frame(toolbar, style="PanelAlt.TFrame")
        actions_row.pack(fill="x", pady=(12, 0))
        ttk.Button(actions_row, text="Undo", style="Quiet.TButton", command=self.undo_last).pack(side="left")
        ttk.Button(actions_row, text="Clear", style="Quiet.TButton", command=self.clear_all).pack(side="left", padx=(10, 0))
        ttk.Button(actions_row, text="Copy + Close", style="Action.TButton", command=lambda: self.copy_image(close_after=True)).pack(side="left", padx=(18, 0))
        ttk.Button(actions_row, text="Copy Image", style="Quiet.TButton", command=self.copy_image).pack(side="left", padx=(10, 0))
        ttk.Button(actions_row, text="Download PNG...", style="Quiet.TButton", command=self.download_image).pack(side="left", padx=(10, 0))

        editor_frame = ttk.Frame(shell, style="Panel.TFrame", padding=10)
        editor_frame.pack(fill="both", expand=True)
        self.app.decorate_panel(editor_frame, PANEL)

        canvas_host = ttk.Frame(editor_frame, style="Panel.TFrame")
        canvas_host.pack(fill="both", expand=True)

        x_scroll = ttk.Scrollbar(canvas_host, orient="horizontal")
        y_scroll = ttk.Scrollbar(canvas_host, orient="vertical")
        self.canvas = tk.Canvas(
            canvas_host,
            bg="#02070e",
            highlightthickness=0,
            xscrollcommand=x_scroll.set,
            yscrollcommand=y_scroll.set,
            cursor="crosshair",
        )
        x_scroll.config(command=self.canvas.xview)
        y_scroll.config(command=self.canvas.yview)

        self.canvas.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")
        canvas_host.grid_rowconfigure(0, weight=1)
        canvas_host.grid_columnconfigure(0, weight=1)

        self.image_item = self.canvas.create_image(0, 0, anchor="nw", image=self.image)
        self.canvas.configure(scrollregion=(0, 0, self.image_width, self.image_height))

        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

        status_panel = ttk.Frame(shell, style="PanelAlt.TFrame", padding=(12, 10))
        status_panel.pack(fill="x", pady=(12, 0))
        self.app.decorate_panel(status_panel, PANEL_ALT)
        ttk.Label(status_panel, text="EDITOR STATUS", style="State.TLabel").pack(anchor="w")
        ttk.Label(
            status_panel,
            textvariable=self.status_var,
            style="PanelAlt.TLabel",
            wraplength=1080,
            justify="left",
        ).pack(anchor="w", pady=(6, 0))
        ttk.Label(status_panel, text="KEY FLOW", style="State.TLabel").pack(anchor="w", pady=(10, 0))
        ttk.Label(
            status_panel,
            text=self.SHORTCUT_HINT,
            style="PanelAlt.TLabel",
            wraplength=1080,
            justify="left",
        ).pack(anchor="w", pady=(6, 0))

    def focus_canvas(self) -> None:
        try:
            self.window.deiconify()
            self.window.lift()
            self.window.focus_force()
            self.canvas.focus_set()
        except tk.TclError:
            return

    def bring_to_front(self) -> None:
        self.focus_canvas()

    def bind_shortcuts(self) -> None:
        for sequence in ("<Control-c>", "<Control-C>"):
            self.window.bind(sequence, self.on_shortcut_copy)
        self.window.bind("<Control-Return>", self.on_shortcut_copy_close)
        self.window.bind("<Control-d>", self.on_shortcut_download)
        self.window.bind("<Control-D>", self.on_shortcut_download)
        self.window.bind("<Control-z>", self.on_shortcut_undo)
        self.window.bind("<Control-Z>", self.on_shortcut_undo)
        self.window.bind("<Escape>", self.on_escape)

        for sequence, tool in (
            ("p", "pen"),
            ("P", "pen"),
            ("h", "highlight"),
            ("H", "highlight"),
            ("r", "rectangle"),
            ("R", "rectangle"),
            ("a", "arrow"),
            ("A", "arrow"),
        ):
            self.window.bind(sequence, lambda _event, selected_tool=tool: self.select_tool(selected_tool))

        for sequence, width in (("1", 3), ("2", 6), ("3", 10)):
            self.window.bind(sequence, lambda _event, selected_width=width: self.select_width(selected_width))

    def on_shortcut_copy(self, _event: tk.Event) -> str:
        self.copy_image()
        return "break"

    def on_shortcut_copy_close(self, _event: tk.Event) -> str:
        self.copy_image(close_after=True)
        return "break"

    def on_shortcut_download(self, _event: tk.Event) -> str:
        self.download_image()
        return "break"

    def on_shortcut_undo(self, _event: tk.Event) -> str:
        self.undo_last()
        return "break"

    def on_escape(self, _event: tk.Event) -> str:
        if self.active_annotation is not None:
            self.canvas.delete(int(self.active_annotation["preview_id"]))
            self.active_annotation = None
            self.status_var.set("Active stroke canceled. Press Esc again to close the editor.")
        else:
            self.on_close()
        return "break"

    def select_tool(self, tool: str) -> None:
        if self.tool_var.get() == tool:
            return
        self.tool_var.set(tool)
        self.on_tool_changed()

    def select_width(self, width: int) -> None:
        if int(self.width_var.get()) == width:
            return
        self.width_var.set(width)
        self.on_width_changed()

    def on_tool_changed(self) -> None:
        self.persist_editor_preferences()
        self.update_status_hint()

    def on_color_changed(self) -> None:
        self.persist_editor_preferences()
        self.status_var.set("Color updated. Keep marking up, then copy it back when you're ready.")

    def on_width_changed(self) -> None:
        self.persist_editor_preferences()
        self.status_var.set(f"Stroke width set to {self.width_var.get()}.")

    def persist_editor_preferences(self) -> None:
        self.app.settings["editor_tool"] = self.tool_var.get()
        self.app.settings["editor_color"] = self.color_var.get()
        self.app.settings["editor_width"] = int(self.width_var.get())
        save_settings(self.app.settings)

    def clamp_point(self, x: float, y: float) -> tuple[int, int]:
        clamped_x = max(0, min(int(round(x)), self.image_width - 1))
        clamped_y = max(0, min(int(round(y)), self.image_height - 1))
        return clamped_x, clamped_y

    def event_to_canvas_point(self, event: tk.Event) -> tuple[int, int]:
        raw_x = self.canvas.canvasx(event.x)
        raw_y = self.canvas.canvasy(event.y)
        return self.clamp_point(raw_x, raw_y)

    def current_preview_color(self) -> str:
        return self.color_var.get()

    def current_preview_width(self) -> int:
        base = int(self.width_var.get())
        if self.tool_var.get() == "highlight":
            return max(10, base * 2)
        return base

    def update_status_hint(self) -> None:
        tool = self.tool_var.get()
        if tool == "pen":
            self.status_var.set("Pen selected. Drag to draw freehand marks.")
        elif tool == "highlight":
            self.status_var.set("Highlight selected. Drag to create a broad marker trail.")
        elif tool == "rectangle":
            self.status_var.set("Rectangle selected. Drag corner to corner.")
        elif tool == "arrow":
            self.status_var.set("Arrow selected. Drag from source to target.")

    def on_press(self, event: tk.Event) -> None:
        point = self.event_to_canvas_point(event)
        tool = self.tool_var.get()
        preview_color = self.current_preview_color()
        preview_width = self.current_preview_width()

        annotation: dict[str, object] = {
            "tool": tool,
            "color": preview_color,
            "width": preview_width,
            "points": [point],
        }

        if tool in {"pen", "highlight"}:
            preview_id = self.canvas.create_line(
                point[0],
                point[1],
                point[0] + 1,
                point[1] + 1,
                fill=preview_color,
                width=preview_width,
                capstyle="round",
                joinstyle="round",
                smooth=True,
            )
        elif tool == "rectangle":
            preview_id = self.canvas.create_rectangle(
                point[0],
                point[1],
                point[0],
                point[1],
                outline=preview_color,
                width=preview_width,
            )
        else:
            preview_id = self.canvas.create_line(
                point[0],
                point[1],
                point[0],
                point[1],
                fill=preview_color,
                width=preview_width,
                arrow=tk.LAST,
                arrowshape=(16, 18, 6),
                capstyle="round",
            )

        annotation["preview_id"] = preview_id
        self.active_annotation = annotation

    def on_drag(self, event: tk.Event) -> None:
        if self.active_annotation is None:
            return

        point = self.event_to_canvas_point(event)
        points = self.active_annotation["points"]
        assert isinstance(points, list)
        tool = str(self.active_annotation["tool"])
        preview_id = int(self.active_annotation["preview_id"])

        if tool in {"pen", "highlight"}:
            points.append(point)
            flattened = [coordinate for xy in points for coordinate in xy]
            self.canvas.coords(preview_id, *flattened)
        else:
            if len(points) == 1:
                points.append(point)
            else:
                points[-1] = point
            start = points[0]
            self.canvas.coords(preview_id, start[0], start[1], point[0], point[1])

    def on_release(self, event: tk.Event) -> None:
        if self.active_annotation is None:
            return
        self.on_drag(event)
        points = self.active_annotation["points"]
        assert isinstance(points, list)
        tool = str(self.active_annotation["tool"])
        if tool in {"rectangle", "arrow"} and len(points) < 2:
            self.canvas.delete(int(self.active_annotation["preview_id"]))
            self.active_annotation = None
            return
        self.annotations.append(self.active_annotation)
        self.active_annotation = None
        self.status_var.set("Annotation added. Copy when you're ready.")

    def undo_last(self) -> None:
        if self.active_annotation is not None:
            self.canvas.delete(int(self.active_annotation["preview_id"]))
            self.active_annotation = None
            self.status_var.set("Active stroke canceled.")
            return
        if not self.annotations:
            self.status_var.set("Nothing to undo.")
            return
        annotation = self.annotations.pop()
        self.canvas.delete(int(annotation["preview_id"]))
        self.status_var.set("Removed the most recent annotation.")

    def clear_all(self) -> None:
        if self.active_annotation is not None:
            self.canvas.delete(int(self.active_annotation["preview_id"]))
            self.active_annotation = None
        for annotation in self.annotations:
            self.canvas.delete(int(annotation["preview_id"]))
        self.annotations.clear()
        self.status_var.set("All annotations cleared.")

    def export_current_image(self) -> Path:
        render_annotated_image(self.source_path, TEMP_EDITED_CAPTURE_PATH, self.annotations)
        return TEMP_EDITED_CAPTURE_PATH

    def copy_image(self, close_after: bool = False) -> None:
        try:
            final_path = self.export_current_image()
            set_clipboard_image_from_file(final_path)
        except RuntimeError as exc:
            messagebox.showerror(APP_NAME, f"Could not copy the edited image.\n\n{exc}")
            self.status_var.set(f"Copy failed: {clip_text(str(exc), 140)}")
            return

        self.app.beep_success()
        self.app.set_status("Edited snip copied to clipboard. Download only if you want a real file on disk.")
        self.status_var.set("Edited snip copied to clipboard. It stays temporary unless you download it.")

        if close_after:
            self.on_close()

    def download_image(self) -> None:
        chosen_path = self.app.prompt_download_target(parent=self.window, title="Download Snip As PNG")
        if chosen_path is None:
            self.status_var.set("Download canceled.")
            return

        try:
            saved_path = render_annotated_image(self.source_path, chosen_path, self.annotations)
        except RuntimeError as exc:
            messagebox.showerror(APP_NAME, f"Could not download the snip.\n\n{exc}")
            self.status_var.set(f"Download failed: {clip_text(str(exc), 140)}")
            return

        self.app.remember_saved_capture(saved_path)
        self.app.beep_success()
        self.app.set_status(f"Downloaded snip to {saved_path.name}.")
        self.status_var.set(f"Downloaded snip to {saved_path.name}.")

    def on_close(self) -> None:
        self.app.editor_window = None
        cleanup_temp_capture_files()
        try:
            self.window.destroy()
        except tk.TclError:
            return


class GlobalHotkeyListener:
    def __init__(self, on_hotkey, hotkey_text: str) -> None:
        self.on_hotkey = on_hotkey
        self.hotkey_text = normalize_hotkey_text(hotkey_text)
        self.modifiers, self.virtual_key = get_hotkey_binding(self.hotkey_text)
        self.thread: threading.Thread | None = None
        self.ready_event = threading.Event()
        self.thread_id: int | None = None
        self.registration_ok = False
        self.registration_error: int = 0
        self.stop_requested = False

    def start(self) -> bool:
        self.thread = threading.Thread(target=self._run, name="MannaSnipsHotkey", daemon=True)
        self.thread.start()
        self.ready_event.wait(timeout=2.0)
        return self.registration_ok

    def stop(self) -> None:
        self.stop_requested = True
        if self.thread_id is not None:
            user32.PostThreadMessageW(self.thread_id, WM_QUIT, 0, 0)
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=1.0)

    def _run(self) -> None:
        self.thread_id = int(kernel32.GetCurrentThreadId())

        # Ensure the thread owns a message queue before registering the hotkey.
        msg = MSG()
        user32.PeekMessageW(ctypes.byref(msg), None, 0, 0, PM_REMOVE)

        self.registration_ok = bool(user32.RegisterHotKey(None, HOTKEY_ID, self.modifiers, self.virtual_key))
        if not self.registration_ok:
            self.registration_error = int(kernel32.GetLastError())
            self.ready_event.set()
            return

        self.ready_event.set()

        try:
            while not self.stop_requested:
                result = user32.GetMessageW(ctypes.byref(msg), None, 0, 0)
                if result == 0:
                    break
                if result == -1:
                    break
                if msg.message == WM_HOTKEY and msg.wParam == HOTKEY_ID:
                    self.on_hotkey()
        finally:
            user32.UnregisterHotKey(None, HOTKEY_ID)


class MannaSnipsApp:
    def __init__(self, root: tk.Tk, *, start_minimized: bool = False) -> None:
        self.root = root
        self.root.title(APP_NAME)
        self.root.geometry("980x620")
        self.root.minsize(900, 560)
        self.root.configure(bg=BG)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

        try:
            shell32.SetCurrentProcessExplicitAppUserModelID(APP_ID)
        except OSError:
            pass

        if ICON_PATH.exists():
            try:
                self.root.iconbitmap(default=str(ICON_PATH))
            except tk.TclError:
                pass

        self.settings = load_settings()
        self.current_hotkey_text = normalize_hotkey_text(self.settings.get("hotkey_combo", DEFAULT_HOTKEY_TEXT))
        if self.settings.get("hotkey_combo") != self.current_hotkey_text:
            self.settings["hotkey_combo"] = self.current_hotkey_text
            save_settings(self.settings)
        cleanup_temp_capture_files()
        self.output_root = ensure_output_root(self.settings)
        self.latest_capture_path = self.load_latest_capture()
        self.hotkey_registered = False
        self.hotkey_listener: GlobalHotkeyListener | None = None
        self.hotkey_queue: queue.SimpleQueue[str] = queue.SimpleQueue()
        self.capture_in_progress = False
        self.capture_overlay: CaptureSelectionOverlay | None = None
        self.editor_window: AnnotationEditorWindow | None = None
        self.restore_window_state = "normal"
        self.launch_minimized = start_minimized

        self.open_editor_var = tk.BooleanVar(value=bool(self.settings.get("open_editor_after_snip", True)))
        self.start_with_windows_var = tk.BooleanVar(value=is_start_with_windows_enabled())
        self.hotkey_choice_var = tk.StringVar(value=self.current_hotkey_text)
        self.hotkey_text_var = tk.StringVar(value=self.current_hotkey_text)
        self.hotkey_help_var = tk.StringVar(value=self.build_hotkey_help_text())
        self.hotkey_state_var = tk.StringVar(value="ARMING HOTKEY")
        self.file_flow_var = tk.StringVar(value="")
        self.latest_capture_var = tk.StringVar(value="No downloaded snip yet.")
        self.download_root_var = tk.StringVar(value=str(self.output_root))
        self.install_root_var = tk.StringVar(value=str(APP_LAUNCH_ROOT))
        self.data_root_var = tk.StringVar(value=str(STATE_ROOT))
        self.status_var = tk.StringVar(value=f"Ready. Press {self.current_hotkey_text} from any app to start a real copy-first snip.")

        self.build_ui()
        self.refresh_path_display()
        self.refresh_file_flow_state()
        self.refresh_latest_capture_display()

        self.root.update_idletasks()
        self.register_hotkey()
        self.poll_hotkey_queue()
        if self.launch_minimized:
            self.root.after(120, self.start_minimized)

    def load_latest_capture(self) -> Path | None:
        value = str(self.settings.get("latest_capture", "") or "").strip()
        if not value:
            return None
        path = Path(value)
        return path if path.exists() else None

    def build_ui(self) -> None:
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass

        style.configure("Shell.TFrame", background=BG)
        style.configure("Panel.TFrame", background=PANEL)
        style.configure("PanelAlt.TFrame", background=PANEL_ALT)
        style.configure("Shell.TLabel", background=BG, foreground=TEXT, font=("Segoe UI", 10))
        style.configure("Muted.TLabel", background=BG, foreground=TEXT_MUTED, font=("Segoe UI", 10))
        style.configure("Panel.TLabel", background=PANEL, foreground=TEXT, font=("Segoe UI", 10))
        style.configure("PanelAlt.TLabel", background=PANEL_ALT, foreground=TEXT, font=("Segoe UI", 10))
        style.configure("Header.TLabel", background=BG, foreground=TEXT, font=("Segoe UI Semibold", 24))
        style.configure("SubHeader.TLabel", background=BG, foreground=TEXT_MUTED, font=("Segoe UI", 10))
        style.configure("Section.TLabel", background=PANEL, foreground=TEXT, font=("Segoe UI Semibold", 12))
        style.configure("State.TLabel", background=PANEL_ALT, foreground=TEXT_SYSTEM, font=("Consolas", 10))
        style.configure("HeroEyebrow.TLabel", background=PANEL, foreground=TEXT_SYSTEM, font=("Consolas", 10))
        style.configure("HeroTitle.TLabel", background=PANEL, foreground=TEXT, font=("Bahnschrift SemiBold", 30))
        style.configure("HeroBody.TLabel", background=PANEL, foreground=TEXT_MUTED, font=("Segoe UI", 11))
        style.configure("ChipValue.TLabel", background=PANEL_ALT, foreground=TEXT, font=("Bahnschrift SemiBold", 15))
        style.configure("ChipHint.TLabel", background=PANEL_ALT, foreground=TEXT_MUTED, font=("Segoe UI", 9))
        style.configure("Body.TCheckbutton", background=PANEL, foreground=TEXT, font=("Segoe UI", 10))
        style.configure("Tool.TRadiobutton", background=PANEL_ALT, foreground=TEXT, font=("Segoe UI", 10))
        style.configure(
            "Hotkey.TCombobox",
            fieldbackground=PANEL_ALT,
            background=PANEL_ALT,
            foreground=TEXT,
            arrowcolor=TEXT,
            bordercolor=BORDER,
            lightcolor=BORDER,
            darkcolor=BORDER,
            padding=(8, 6),
        )
        style.map(
            "Hotkey.TCombobox",
            fieldbackground=[("readonly", PANEL_ALT)],
            foreground=[("readonly", TEXT)],
            selectbackground=[("readonly", PANEL_ALT)],
            selectforeground=[("readonly", TEXT)],
        )
        style.map(
            "Body.TCheckbutton",
            background=[("active", PANEL)],
            foreground=[("active", TEXT)],
        )
        style.map(
            "Tool.TRadiobutton",
            background=[("active", PANEL_ALT), ("selected", PANEL_ALT)],
            foreground=[("active", TEXT), ("selected", TEXT_SYSTEM)],
        )
        style.configure(
            "Action.TButton",
            background=ACCENT,
            foreground=TEXT,
            bordercolor=ACCENT,
            focusthickness=0,
            padding=(14, 8),
            font=("Segoe UI Semibold", 10),
        )
        style.map(
            "Action.TButton",
            background=[("active", "#63b4ff"), ("disabled", ACCENT_SOFT)],
            foreground=[("disabled", "#8ea6c7")],
        )
        style.configure(
            "Quiet.TButton",
            background=PANEL_ALT,
            foreground=TEXT,
            bordercolor=BORDER,
            focusthickness=0,
            padding=(13, 8),
            font=("Segoe UI", 10),
        )
        style.map(
            "Quiet.TButton",
            background=[("active", "#16293b"), ("disabled", PANEL_ALT)],
            foreground=[("disabled", "#6d83a3")],
        )
        self.root.option_add("*TCombobox*Listbox*Background", PANEL_ALT)
        self.root.option_add("*TCombobox*Listbox*Foreground", TEXT)
        self.root.option_add("*TCombobox*Listbox*selectBackground", ACCENT_SOFT)
        self.root.option_add("*TCombobox*Listbox*selectForeground", TEXT)

        shell = ttk.Frame(self.root, style="Shell.TFrame", padding=18)
        shell.pack(fill="both", expand=True)

        hero_panel = ttk.Frame(shell, style="Panel.TFrame", padding=(18, 16))
        hero_panel.pack(fill="x")
        self.decorate_panel(hero_panel, PANEL)

        hero_top = ttk.Frame(hero_panel, style="Panel.TFrame")
        hero_top.pack(fill="x")

        hero_left = ttk.Frame(hero_top, style="Panel.TFrame")
        hero_left.pack(side="left", fill="x", expand=True)
        self.create_crystal_badge(hero_left, size=76, background=PANEL).pack(side="left", padx=(0, 16))

        hero_copy = ttk.Frame(hero_left, style="Panel.TFrame")
        hero_copy.pack(side="left", fill="x", expand=True)
        ttk.Label(hero_copy, text="CRYSTAL NODE", style="HeroEyebrow.TLabel").pack(anchor="w")
        ttk.Label(hero_copy, text=APP_NAME, style="HeroTitle.TLabel").pack(anchor="w", pady=(1, 0))
        ttk.Label(
            hero_copy,
            text=f"Copy-first screenshot tool. v{APP_VERSION}",
            style="HeroBody.TLabel",
            wraplength=420,
            justify="left",
        ).pack(anchor="w", pady=(4, 0))

        status_row = ttk.Frame(shell, style="Shell.TFrame")
        status_row.pack(fill="x", pady=(14, 14))
        self.build_signal_chip(status_row, "HOTKEY", textvariable=self.hotkey_text_var, hint="")
        self.build_signal_chip(status_row, "READY", textvariable=self.hotkey_state_var, hint="")
        self.build_signal_chip(status_row, "FLOW", textvariable=self.file_flow_var, hint="")

        main_panel = ttk.Frame(shell, style="Panel.TFrame", padding=16)
        main_panel.pack(fill="both", expand=True)
        self.decorate_panel(main_panel, PANEL)

        ttk.Label(main_panel, text="ACTIONS", style="Section.TLabel").pack(anchor="w")
        ttk.Label(
            main_panel,
            text="Take a snip, copy it, or download it.",
            style="Panel.TLabel",
            wraplength=680,
            justify="left",
        ).pack(anchor="w", pady=(6, 14))

        action_row = ttk.Frame(main_panel, style="Panel.TFrame")
        action_row.pack(fill="x", pady=(0, 14))
        ttk.Button(action_row, text="Take Snip", style="Action.TButton", command=self.begin_capture).pack(side="left")
        ttk.Button(action_row, text="Download Clipboard As...", style="Quiet.TButton", command=self.download_clipboard_as).pack(side="left", padx=(10, 0))
        ttk.Button(action_row, text="Open Downloads Folder", style="Quiet.TButton", command=self.open_snips_folder).pack(side="left", padx=(10, 0))

        preferences_row = ttk.Frame(main_panel, style="Panel.TFrame")
        preferences_row.pack(fill="x", pady=(0, 14))
        ttk.Checkbutton(
            preferences_row,
            text="Open editor after snip",
            variable=self.open_editor_var,
            style="Body.TCheckbutton",
            command=self.on_toggle_open_editor,
        ).pack(side="left")
        ttk.Checkbutton(
            preferences_row,
            text="Start with Windows",
            variable=self.start_with_windows_var,
            style="Body.TCheckbutton",
            command=self.on_toggle_start_with_windows,
        ).pack(side="left", padx=(18, 0))

        shortcut_panel = ttk.Frame(main_panel, style="PanelAlt.TFrame", padding=12)
        shortcut_panel.pack(fill="x", pady=(0, 14))
        self.decorate_panel(shortcut_panel, PANEL_ALT)
        ttk.Label(shortcut_panel, text="SHORTCUT", style="State.TLabel").pack(anchor="w")
        shortcut_row = ttk.Frame(shortcut_panel, style="PanelAlt.TFrame")
        shortcut_row.pack(fill="x", pady=(10, 0))
        ttk.Label(shortcut_row, text="Capture Shortcut", style="PanelAlt.TLabel").pack(side="left")
        ttk.Combobox(
            shortcut_row,
            textvariable=self.hotkey_choice_var,
            values=HOTKEY_PRESETS,
            state="readonly",
            width=18,
            style="Hotkey.TCombobox",
        ).pack(side="left", padx=(12, 0))
        ttk.Button(shortcut_row, text="Apply", style="Quiet.TButton", command=self.apply_hotkey_choice).pack(side="left", padx=(10, 0))
        ttk.Button(shortcut_row, text="Default", style="Quiet.TButton", command=self.restore_default_hotkey).pack(side="left", padx=(10, 0))

        latest_panel = ttk.Frame(main_panel, style="PanelAlt.TFrame", padding=12)
        latest_panel.pack(fill="x", pady=(0, 14))
        self.decorate_panel(latest_panel, PANEL_ALT)
        ttk.Label(latest_panel, text="LAST DOWNLOAD", style="State.TLabel").pack(anchor="w")
        ttk.Label(
            latest_panel,
            textvariable=self.latest_capture_var,
            style="PanelAlt.TLabel",
            wraplength=460,
            justify="left",
        ).pack(anchor="w", pady=(8, 0))
        latest_actions = ttk.Frame(latest_panel, style="PanelAlt.TFrame")
        latest_actions.pack(fill="x", pady=(10, 0))
        ttk.Button(latest_actions, text="Open Last Download", style="Quiet.TButton", command=self.open_latest_capture).pack(side="left")
        ttk.Button(latest_actions, text="Copy Last Download Path", style="Quiet.TButton", command=self.copy_latest_path).pack(side="left", padx=(10, 0))

        paths_panel = ttk.Frame(main_panel, style="PanelAlt.TFrame", padding=12)
        paths_panel.pack(fill="x", pady=(0, 14))
        self.decorate_panel(paths_panel, PANEL_ALT)
        ttk.Label(paths_panel, text="PATHS", style="State.TLabel").pack(anchor="w")
        ttk.Label(paths_panel, text="Downloads Folder", style="ChipHint.TLabel").pack(anchor="w", pady=(8, 0))
        ttk.Label(paths_panel, textvariable=self.download_root_var, style="PanelAlt.TLabel", wraplength=760, justify="left").pack(anchor="w", pady=(2, 0))
        downloads_actions = ttk.Frame(paths_panel, style="PanelAlt.TFrame")
        downloads_actions.pack(fill="x", pady=(8, 0))
        ttk.Button(downloads_actions, text="Change Downloads Folder...", style="Quiet.TButton", command=self.choose_download_root).pack(side="left")
        ttk.Button(downloads_actions, text="Reset Downloads Folder", style="Quiet.TButton", command=self.reset_download_root).pack(side="left", padx=(10, 0))

        ttk.Label(paths_panel, text="Installed App Folder", style="ChipHint.TLabel").pack(anchor="w", pady=(12, 0))
        ttk.Label(paths_panel, textvariable=self.install_root_var, style="PanelAlt.TLabel", wraplength=760, justify="left").pack(anchor="w", pady=(2, 0))
        ttk.Label(paths_panel, text="Settings + Temp Folder", style="ChipHint.TLabel").pack(anchor="w", pady=(12, 0))
        ttk.Label(paths_panel, textvariable=self.data_root_var, style="PanelAlt.TLabel", wraplength=760, justify="left").pack(anchor="w", pady=(2, 0))
        utility_actions = ttk.Frame(paths_panel, style="PanelAlt.TFrame")
        utility_actions.pack(fill="x", pady=(8, 0))
        ttk.Button(utility_actions, text="Open Install Folder", style="Quiet.TButton", command=self.open_install_folder).pack(side="left")
        ttk.Button(utility_actions, text="Open App Data Folder", style="Quiet.TButton", command=self.open_app_data_folder).pack(side="left", padx=(10, 0))

        status_panel = ttk.Frame(main_panel, style="PanelAlt.TFrame", padding=12)
        status_panel.pack(fill="both", expand=True)
        self.decorate_panel(status_panel, PANEL_ALT)
        ttk.Label(status_panel, text="STATUS", style="State.TLabel").pack(anchor="w")
        ttk.Label(
            status_panel,
            textvariable=self.status_var,
            style="PanelAlt.TLabel",
            wraplength=760,
            justify="left",
        ).pack(anchor="w", pady=(8, 0))
        ttk.Label(
            status_panel,
            textvariable=self.hotkey_help_var,
            style="ChipHint.TLabel",
            wraplength=760,
            justify="left",
        ).pack(anchor="w", pady=(10, 0))

    def create_crystal_badge(self, parent: ttk.Frame, size: int, background: str) -> tk.Canvas:
        canvas = tk.Canvas(parent, width=size, height=size, bg=background, highlightthickness=0)
        center = size / 2
        outer = size * 0.34
        inner = size * 0.22

        canvas.create_oval(center - 24, center - 24, center + 24, center + 24, outline=ACCENT_SOFT, width=1.2)
        canvas.create_line(center - 26, center + 18, center + 26, center + 18, fill=BORDER, width=1)
        canvas.create_polygon(
            center,
            center - outer,
            center + outer,
            center,
            center,
            center + outer,
            center - outer,
            center,
            fill=ACCENT,
            outline="#edf6ff",
            width=1.8,
        )
        canvas.create_polygon(
            center,
            center - inner,
            center + inner,
            center,
            center,
            center + inner,
            center - inner,
            center,
            fill=ACCENT_SOFT,
            outline="",
        )
        canvas.create_line(center - 7, center, center + 7, center, fill="#edf6ff", width=2)
        canvas.create_line(center, center - 7, center, center + 7, fill="#edf6ff", width=2)
        canvas.create_line(center + 12, center - 14, center + 20, center - 22, fill=TEXT_SYSTEM, width=2)
        return canvas

    def build_signal_chip(
        self,
        parent: ttk.Frame,
        label: str,
        *,
        text: str | None = None,
        textvariable: tk.StringVar | None = None,
        hint: str,
    ) -> ttk.Frame:
        chip = ttk.Frame(parent, style="PanelAlt.TFrame", padding=(12, 10))
        chip.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.decorate_panel(chip, PANEL_ALT)
        ttk.Label(chip, text=label, style="State.TLabel").pack(anchor="w")
        value_kwargs = {"style": "ChipValue.TLabel"}
        if textvariable is not None:
            ttk.Label(chip, textvariable=textvariable, **value_kwargs).pack(anchor="w", pady=(5, 0))
        else:
            ttk.Label(chip, text=text or "", **value_kwargs).pack(anchor="w", pady=(5, 0))
        if hint:
            ttk.Label(chip, text=hint, style="ChipHint.TLabel", wraplength=180, justify="left").pack(anchor="w", pady=(6, 0))
        return chip

    def decorate_panel(self, panel: ttk.Frame, bg_color: str) -> None:
        border = tk.Frame(panel, bg=BORDER, height=1)
        border.pack(side="bottom", fill="x")
        panel.configure(style="Panel.TFrame" if bg_color == PANEL else "PanelAlt.TFrame")

    def build_hotkey_help_text(self) -> str:
        return f"{self.current_hotkey_text} anywhere. Ctrl+C copies in editor. Ctrl+D downloads in editor."

    def set_current_hotkey_text(self, hotkey_text: str) -> None:
        self.current_hotkey_text = normalize_hotkey_text(hotkey_text)
        self.hotkey_choice_var.set(self.current_hotkey_text)
        self.hotkey_text_var.set(self.current_hotkey_text)
        self.hotkey_help_var.set(self.build_hotkey_help_text())

    def register_hotkey(self, *, update_status: bool = True) -> bool:
        self.hotkey_listener = GlobalHotkeyListener(on_hotkey=self.on_hotkey_signal, hotkey_text=self.current_hotkey_text)
        success = self.hotkey_listener.start()
        self.hotkey_registered = success
        if success:
            self.hotkey_state_var.set("ARMED")
            if update_status:
                self.set_status(f"Hotkey armed. Press {self.current_hotkey_text} anywhere, drag a region, then paste into Manna.")
            return True

        error_code = self.hotkey_listener.registration_error if self.hotkey_listener else 0
        if error_code == 1409:
            self.hotkey_state_var.set("HOTKEY BUSY")
            if update_status:
                self.set_status(f"{self.current_hotkey_text} is already owned by another app. Take Snip still works.")
            return False

        self.hotkey_state_var.set("BUTTON ONLY")
        if update_status:
            if error_code:
                self.set_status(f"Could not register {self.current_hotkey_text}. Windows error {error_code}. Take Snip still works.")
            else:
                self.set_status(f"Could not register {self.current_hotkey_text}. The app still works through the Take Snip button.")
        return False

    def unregister_hotkey(self) -> None:
        if self.hotkey_listener is not None:
            self.hotkey_listener.stop()
            self.hotkey_listener = None
        self.hotkey_registered = False

    def apply_hotkey_choice(self) -> None:
        selected_hotkey = normalize_hotkey_text(self.hotkey_choice_var.get())
        previous_hotkey = self.current_hotkey_text

        if selected_hotkey == previous_hotkey:
            self.set_status(f"{previous_hotkey} is already the capture shortcut.")
            return

        self.unregister_hotkey()
        self.set_current_hotkey_text(selected_hotkey)
        success = self.register_hotkey(update_status=False)
        error_code = self.hotkey_listener.registration_error if self.hotkey_listener else 0
        if success:
            self.settings["hotkey_combo"] = self.current_hotkey_text
            save_settings(self.settings)
            self.set_status(f"Capture shortcut changed to {self.current_hotkey_text}.")
            return

        self.unregister_hotkey()
        self.set_current_hotkey_text(previous_hotkey)
        self.register_hotkey(update_status=False)
        self.settings["hotkey_combo"] = self.current_hotkey_text
        save_settings(self.settings)
        if error_code == 1409:
            self.set_status(f"{selected_hotkey} is already owned by another app. Keeping {previous_hotkey} as the configured shortcut.")
            return
        if error_code:
            self.set_status(f"Could not register {selected_hotkey}. Keeping {previous_hotkey} as the configured shortcut.")
            return
        self.set_status(f"Could not register {selected_hotkey}. Keeping {previous_hotkey} as the configured shortcut.")

    def restore_default_hotkey(self) -> None:
        self.hotkey_choice_var.set(DEFAULT_HOTKEY_TEXT)
        if self.current_hotkey_text == DEFAULT_HOTKEY_TEXT:
            self.set_status("Default capture shortcut already active.")
            return
        self.apply_hotkey_choice()

    def on_hotkey_signal(self) -> None:
        self.hotkey_queue.put("capture")

    def poll_hotkey_queue(self) -> None:
        while True:
            try:
                signal = self.hotkey_queue.get_nowait()
            except queue.Empty:
                break
            if signal == "capture":
                self.begin_capture()
        self.root.after(HOTKEY_POLL_INTERVAL_MS, self.poll_hotkey_queue)

    def begin_capture(self) -> None:
        if self.capture_in_progress:
            self.set_status("A capture is already in progress.")
            return
        if self.editor_window is not None:
            self.editor_window.bring_to_front()
            self.set_status("Finish or close the current editor before starting another snip.")
            return

        cleanup_temp_capture_files()
        self.capture_in_progress = True
        self.restore_window_state = self.root.state()
        self.set_status("Capture armed. Drag a region in the overlay; Manna Snips will copy it automatically.")
        self.root.withdraw()
        self.root.update_idletasks()
        self.root.after(CAPTURE_OVERLAY_DELAY_MS, self.open_capture_overlay)

    def open_capture_overlay(self) -> None:
        self.capture_overlay = CaptureSelectionOverlay(
            parent=self.root,
            on_complete=self.finish_capture,
            on_cancel=self.cancel_capture,
        )

    def cancel_capture(self) -> None:
        self.capture_overlay = None
        self.capture_in_progress = False
        self.restore_root_state()
        self.set_status("Capture canceled.")

    def finish_capture(self, region: tuple[int, int, int, int]) -> None:
        self.capture_overlay = None
        self.root.after(CAPTURE_COMMIT_DELAY_MS, lambda: self.commit_capture(region))

    def commit_capture(self, region: tuple[int, int, int, int]) -> None:
        left, top, width, height = region
        bitmap_handle = 0
        status_message = ""
        error_message = ""

        try:
            bitmap_handle = capture_screen_region(left, top, width, height)
            save_bitmap_handle_as_png(bitmap_handle, TEMP_RAW_CAPTURE_PATH)

            if self.open_editor_var.get():
                status_message = "Capture loaded into the editor. Add marks, then copy it back to the clipboard."
            else:
                set_clipboard_image_from_file(TEMP_RAW_CAPTURE_PATH)
                status_message = "Snip copied to clipboard. Download it only if you want a real file on disk."
        except RuntimeError as exc:
            error_message = str(exc)
            status_message = f"Capture failed: {clip_text(error_message, 140)}"
        finally:
            if bitmap_handle:
                gdi32.DeleteObject(bitmap_handle)
            self.capture_in_progress = False
            self.restore_root_state()

        if error_message:
            self.set_status(status_message)
            messagebox.showerror(APP_NAME, f"Could not complete the snip.\n\n{error_message}")
            return

        if self.open_editor_var.get():
            self.open_editor(TEMP_RAW_CAPTURE_PATH)
            self.set_status(status_message)
            return

        self.beep_success()
        self.set_status(status_message)

    def restore_root_state(self) -> None:
        if self.restore_window_state == "iconic":
            self.root.iconify()
            return
        self.root.deiconify()
        if self.restore_window_state == "zoomed":
            self.root.state("zoomed")
        self.root.lift()

    def remember_saved_capture(self, path: Path) -> None:
        self.latest_capture_path = path
        self.settings["latest_capture"] = str(path)
        self.settings["last_save_dir"] = str(path.parent)
        save_settings(self.settings)
        self.refresh_latest_capture_display()

    def refresh_latest_capture_display(self) -> None:
        if self.latest_capture_path and self.latest_capture_path.exists():
            latest_text = str(self.latest_capture_path)
            try:
                self.latest_capture_path.relative_to(self.output_root)
            except ValueError:
                latest_text += "  (outside current downloads folder)"
            self.latest_capture_var.set(latest_text)
        else:
            self.latest_capture_var.set("No downloaded snip yet.")

    def refresh_file_flow_state(self) -> None:
        self.file_flow_var.set("COPY FIRST")

    def on_toggle_open_editor(self) -> None:
        self.settings["open_editor_after_snip"] = bool(self.open_editor_var.get())
        save_settings(self.settings)
        if self.open_editor_var.get():
            self.set_status("Editor enabled. Future snips will return to Manna Snips for markup before copy.")
        else:
            self.set_status("Editor disabled. Future snips will copy straight to the clipboard and stay temporary.")

    def on_toggle_start_with_windows(self) -> None:
        enabled = bool(self.start_with_windows_var.get())
        try:
            set_start_with_windows_enabled(enabled)
        except OSError as exc:
            self.start_with_windows_var.set(is_start_with_windows_enabled())
            messagebox.showerror(APP_NAME, f"Could not update Start with Windows.\n\n{exc}")
            self.set_status("Could not update Start with Windows.")
            return

        if enabled:
            self.set_status("Start with Windows enabled. Manna Snips will launch minimized at sign-in.")
        else:
            self.set_status("Start with Windows disabled.")

    def open_editor(self, source_path: Path) -> None:
        if self.editor_window is not None:
            self.editor_window.on_close()
        self.editor_window = AnnotationEditorWindow(self, source_path)
        self.editor_window.bring_to_front()

    def refresh_path_display(self) -> None:
        self.output_root = ensure_output_root(self.settings)
        self.download_root_var.set(str(self.output_root))
        self.install_root_var.set(str(APP_LAUNCH_ROOT))
        self.data_root_var.set(str(STATE_ROOT))

    def choose_download_root(self) -> None:
        initial_dir = str(self.output_root if self.output_root.exists() else OUTPUT_ROOT_DEFAULT)
        chosen = filedialog.askdirectory(parent=self.root, title="Choose Downloads Folder", initialdir=initial_dir, mustexist=False)
        if not chosen:
            self.set_status("Downloads folder change canceled.")
            return
        chosen_path = Path(chosen)
        chosen_path.mkdir(parents=True, exist_ok=True)
        self.settings["download_root"] = str(chosen_path)
        self.settings["last_save_dir"] = str(chosen_path)
        save_settings(self.settings)
        self.refresh_path_display()
        self.set_status(f"Downloads folder set to {chosen_path}.")

    def reset_download_root(self) -> None:
        self.settings["download_root"] = str(OUTPUT_ROOT_DEFAULT)
        self.settings["last_save_dir"] = str(OUTPUT_ROOT_DEFAULT)
        save_settings(self.settings)
        self.refresh_path_display()
        self.set_status("Downloads folder reset to the default Manna Snips location.")

    def prompt_download_target(self, parent: tk.Misc, title: str) -> Path | None:
        default_path = default_capture_path(self.settings)
        initial_dir = Path(str(self.settings.get("last_save_dir", self.output_root)))
        if not initial_dir.exists():
            initial_dir = default_path.parent

        chosen = filedialog.asksaveasfilename(
            parent=parent,
            title=title,
            defaultextension=".png",
            filetypes=[("PNG Image", "*.png")],
            initialdir=str(initial_dir),
            initialfile=default_path.name,
        )
        if not chosen:
            return None
        return Path(chosen)

    def download_clipboard_as(self) -> None:
        if not clipboard_has_image():
            messagebox.showwarning(APP_NAME, "There is no image in the clipboard right now.")
            self.set_status("Download skipped because the clipboard does not contain an image.")
            return

        chosen_path = self.prompt_download_target(parent=self.root, title="Download Clipboard Image As PNG")
        if chosen_path is None:
            self.set_status("Download canceled.")
            return

        try:
            saved_path = save_clipboard_image(chosen_path)
        except RuntimeError as exc:
            messagebox.showerror(APP_NAME, f"Could not download the clipboard image.\n\n{exc}")
            self.set_status("Download failed.")
            return

        self.remember_saved_capture(saved_path)
        self.beep_success()
        self.set_status(f"Clipboard image downloaded to {saved_path.name}.")

    def open_snips_folder(self) -> None:
        ensure_output_root(self.settings)
        os.startfile(str(self.output_root))

    def open_install_folder(self) -> None:
        os.startfile(str(APP_LAUNCH_ROOT))

    def open_app_data_folder(self) -> None:
        ensure_directories()
        os.startfile(str(STATE_ROOT))

    def open_latest_capture(self) -> None:
        if not self.latest_capture_path or not self.latest_capture_path.exists():
            messagebox.showinfo(APP_NAME, "There is no downloaded snip to open yet.")
            return
        os.startfile(str(self.latest_capture_path))

    def copy_latest_path(self) -> None:
        if not self.latest_capture_path or not self.latest_capture_path.exists():
            messagebox.showinfo(APP_NAME, "There is no downloaded snip path to copy yet.")
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(str(self.latest_capture_path))
        self.set_status("Last download path copied to the clipboard.")

    def set_status(self, message: str) -> None:
        self.status_var.set(clip_text(message, max_chars=180))

    def beep_success(self) -> None:
        try:
            winsound.MessageBeep()
        except RuntimeError:
            pass

    def start_minimized(self) -> None:
        self.root.update_idletasks()
        self.root.iconify()

    def on_close(self) -> None:
        if self.capture_overlay is not None:
            self.capture_overlay.destroy()
            self.capture_overlay = None
        if self.editor_window is not None:
            self.editor_window.on_close()
        self.unregister_hotkey()
        cleanup_temp_capture_files()
        self.root.destroy()


def run_smoke() -> int:
    ensure_directories()
    settings = load_settings()
    output_root = ensure_output_root(settings)
    hotkey_text = normalize_hotkey_text(settings.get("hotkey_combo", DEFAULT_HOTKEY_TEXT))
    print(f"APP: {APP_NAME}")
    print(f"VERSION: {APP_VERSION}")
    print(f"PROFILE: {PROFILE_NAME}")
    print(f"FROZEN: {IS_FROZEN_BUILD}")
    print(f"RUNTIME_ROOT: {RUNTIME_ROOT}")
    print(f"APP_LAUNCH_ROOT: {APP_LAUNCH_ROOT}")
    print(f"HOTKEY: {hotkey_text}")
    print(f"STARTUP_VALUE_NAME: {STARTUP_VALUE_NAME}")
    print(f"STARTUP_ENABLED: {is_start_with_windows_enabled()}")
    print(f"STARTUP_COMMAND: {get_startup_command()}")
    print(f"SAVE_HELPER: {SAVE_HELPER_PATH}")
    print(f"SAVE_HELPER_EXISTS: {SAVE_HELPER_PATH.exists()}")
    print(f"SET_CLIPBOARD_HELPER: {SET_CLIPBOARD_HELPER_PATH}")
    print(f"SET_CLIPBOARD_HELPER_EXISTS: {SET_CLIPBOARD_HELPER_PATH.exists()}")
    print(f"OUTPUT_ROOT: {output_root}")
    print(f"TEMP_RAW_CAPTURE_PATH: {TEMP_RAW_CAPTURE_PATH}")
    print(f"TEMP_EDITED_CAPTURE_PATH: {TEMP_EDITED_CAPTURE_PATH}")
    print("FILE_FLOW: COPY_FIRST")
    print(f"OPEN_EDITOR_AFTER_SNIP: {bool(settings.get('open_editor_after_snip', True))}")
    print(f"LATEST_CAPTURE: {settings.get('latest_capture', '')}")
    return 0


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=APP_NAME)
    parser.add_argument("--smoke", action="store_true", help="Print environment details and exit.")
    parser.add_argument("--minimized", action="store_true", help="Start minimized to the taskbar.")
    parser.add_argument("--version", action="store_true", help="Print the app version and exit.")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    enable_dpi_awareness()
    args = parse_args(argv or sys.argv[1:])
    if args.version:
        print(APP_VERSION)
        return 0
    if args.smoke:
        return run_smoke()

    ensure_directories()
    root = tk.Tk()
    app = MannaSnipsApp(root, start_minimized=args.minimized)
    root.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
