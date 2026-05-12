$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $projectRoot

$screenshotsDir = Join-Path $projectRoot "docs\screenshots"
$sampleSourcePath = Join-Path $screenshotsDir "sample-snip-source.png"
$mainShotPath = Join-Path $screenshotsDir "main-window.png"
$editorShotPath = Join-Path $screenshotsDir "editor-window.png"

New-Item -ItemType Directory -Path $screenshotsDir -Force | Out-Null

$pythonExe = & py -3 -c "import pathlib, sys; print(pathlib.Path(sys.executable).resolve())"
if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($pythonExe)) {
    throw "Could not resolve the local Python executable."
}
$pythonExe = $pythonExe.Trim()
$pythonwExe = [System.IO.Path]::Combine([System.IO.Path]::GetDirectoryName($pythonExe), "pythonw.exe")
if (-not (Test-Path $pythonwExe)) {
    $pythonwExe = $pythonExe
}

Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.Windows.Forms

Add-Type -ReferencedAssemblies System.Drawing @'
using System;
using System.Drawing;
using System.Runtime.InteropServices;
using System.Text;

public struct RECT
{
    public int Left;
    public int Top;
    public int Right;
    public int Bottom;
}

public static class PreviewWindows
{
    public delegate bool EnumWindowsProc(IntPtr hWnd, IntPtr lParam);

    [DllImport("user32.dll")]
    public static extern bool EnumWindows(EnumWindowsProc lpEnumFunc, IntPtr lParam);

    [DllImport("user32.dll")]
    public static extern bool IsWindowVisible(IntPtr hWnd);

    [DllImport("user32.dll", SetLastError = true, CharSet = CharSet.Unicode)]
    public static extern int GetWindowText(IntPtr hWnd, StringBuilder text, int maxCount);

    [DllImport("user32.dll")]
    public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint processId);

    [DllImport("user32.dll")]
    public static extern bool GetWindowRect(IntPtr hWnd, out RECT rect);

    [DllImport("user32.dll")]
    public static extern bool SetForegroundWindow(IntPtr hWnd);

    [DllImport("user32.dll")]
    public static extern bool ShowWindow(IntPtr hWnd, int nCmdShow);

    [DllImport("user32.dll")]
    public static extern bool PrintWindow(IntPtr hWnd, IntPtr hdcBlt, int nFlags);

    public static IntPtr FindWindowForProcess(uint processId, string exactTitle)
    {
        IntPtr found = IntPtr.Zero;
        EnumWindows(delegate (IntPtr hWnd, IntPtr lParam)
        {
            if (!IsWindowVisible(hWnd))
            {
                return true;
            }

            uint candidatePid;
            GetWindowThreadProcessId(hWnd, out candidatePid);
            if (candidatePid != processId)
            {
                return true;
            }

            StringBuilder titleBuilder = new StringBuilder(512);
            GetWindowText(hWnd, titleBuilder, titleBuilder.Capacity);
            if (titleBuilder.ToString() == exactTitle)
            {
                found = hWnd;
                return false;
            }

            return true;
        }, IntPtr.Zero);

        return found;
    }

    public static bool CaptureWindow(IntPtr hWnd, string outputPath)
    {
        RECT rect;
        if (!GetWindowRect(hWnd, out rect))
        {
            return false;
        }

        int width = rect.Right - rect.Left;
        int height = rect.Bottom - rect.Top;
        if (width <= 0 || height <= 0)
        {
            return false;
        }

        using (Bitmap bitmap = new Bitmap(width, height))
        using (Graphics graphics = Graphics.FromImage(bitmap))
        {
            IntPtr hdc = graphics.GetHdc();
            bool ok = false;
            try
            {
                ok = PrintWindow(hWnd, hdc, 0);
            }
            finally
            {
                graphics.ReleaseHdc(hdc);
            }

            if (!ok)
            {
                return false;
            }

            bitmap.Save(outputPath, System.Drawing.Imaging.ImageFormat.Png);
            return true;
        }
    }
}
'@

function New-SampleSnipImage {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Path
    )

    $bitmap = New-Object System.Drawing.Bitmap 760, 430
    $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
    $graphics.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
    $graphics.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::ClearTypeGridFit

    try {
        $background = New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::FromArgb(7, 16, 25))
        $panelBrush = New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::FromArgb(13, 24, 36))
        $panelAltBrush = New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::FromArgb(16, 29, 43))
        $accentBrush = New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::FromArgb(61, 160, 255))
        $mutedBrush = New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::FromArgb(138, 168, 199))
        $textBrush = New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::FromArgb(237, 246, 255))
        $greenBrush = New-Object System.Drawing.SolidBrush ([System.Drawing.Color]::FromArgb(159, 255, 184))
        $borderPen = New-Object System.Drawing.Pen ([System.Drawing.Color]::FromArgb(34, 54, 75)), 2
        $thinPen = New-Object System.Drawing.Pen ([System.Drawing.Color]::FromArgb(26, 54, 83)), 1

        $headerFont = New-Object System.Drawing.Font("Segoe UI Semibold", 22)
        $bodyFont = New-Object System.Drawing.Font("Segoe UI", 12)
        $monoFont = New-Object System.Drawing.Font("Consolas", 11)

        $graphics.FillRectangle($background, 0, 0, 760, 430)
        $graphics.FillRectangle($panelBrush, 22, 22, 716, 386)
        $graphics.DrawRectangle($borderPen, 22, 22, 716, 386)

        $graphics.FillRectangle($panelAltBrush, 48, 56, 256, 106)
        $graphics.DrawRectangle($thinPen, 48, 56, 256, 106)
        $graphics.FillRectangle($panelAltBrush, 344, 64, 290, 50)
        $graphics.DrawRectangle($thinPen, 344, 64, 290, 50)
        $graphics.FillRectangle($panelAltBrush, 344, 128, 290, 98)
        $graphics.DrawRectangle($thinPen, 344, 128, 290, 98)
        $graphics.FillRectangle($panelAltBrush, 48, 198, 586, 168)
        $graphics.DrawRectangle($thinPen, 48, 198, 586, 168)

        $graphics.FillRectangle($accentBrush, 64, 74, 110, 14)
        $graphics.DrawString("Crash Summary", $headerFont, $textBrush, 64, 98)
        $graphics.DrawString("Ready to paste into Manna without saving a file first.", $bodyFont, $mutedBrush, 64, 134)

        $graphics.FillRectangle($accentBrush, 360, 78, 150, 10)
        $graphics.DrawString("STACK TRACE", $monoFont, $greenBrush, 360, 98)
        $graphics.DrawString("ValueError: capture region was empty", $bodyFont, $textBrush, 360, 134)
        $graphics.DrawString("app.py  line 1184", $monoFont, $mutedBrush, 360, 162)
        $graphics.DrawString("overlay.py line 204", $monoFont, $mutedBrush, 360, 184)
        $graphics.DrawString("hotkey.py  line 77", $monoFont, $mutedBrush, 360, 206)

        $graphics.FillRectangle($accentBrush, 360, 142, 92, 10)
        $graphics.DrawString("ACTION ITEMS", $monoFont, $greenBrush, 360, 244)
        $graphics.DrawString("1. retry with display scaling safe bounds", $bodyFont, $textBrush, 360, 272)
        $graphics.DrawString("2. copy the exact crash frame into chat", $bodyFont, $textBrush, 360, 298)
        $graphics.DrawString("3. keep the original snip temporary unless downloaded", $bodyFont, $textBrush, 360, 324)

        $graphics.DrawString("NOTES", $monoFont, $greenBrush, 64, 224)
        $graphics.DrawString("Clipboard-first screenshots help when sharing logs,", $bodyFont, $textBrush, 64, 252)
        $graphics.DrawString("stack traces, or small bugs without cluttering", $bodyFont, $textBrush, 64, 278)
        $graphics.DrawString("your downloads folder.", $bodyFont, $textBrush, 64, 304)
        $graphics.DrawString("Copy stays temporary unless you explicitly download.", $bodyFont, $mutedBrush, 64, 334)

        $graphics.FillEllipse($accentBrush, 558, 334, 14, 14)
        $graphics.DrawString("CAPTURE READY", $monoFont, $greenBrush, 580, 330)
    }
    finally {
        $graphics.Dispose()
        $bitmap.Save($Path, [System.Drawing.Imaging.ImageFormat]::Png)
        $bitmap.Dispose()
    }
}

function Wait-PreviewWindow {
    param(
        [Parameter(Mandatory = $true)]
        [int]$ProcessId,
        [Parameter(Mandatory = $true)]
        [string]$Title,
        [int]$TimeoutSeconds = 15
    )

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        $handle = [PreviewWindows]::FindWindowForProcess([uint32]$ProcessId, $Title)
        if ($handle -ne [IntPtr]::Zero) {
            return $handle
        }
        Start-Sleep -Milliseconds 200
    }

    throw "Timed out waiting for preview window '$Title' from process $ProcessId."
}

function Save-WindowCapture {
    param(
        [Parameter(Mandatory = $true)]
        [IntPtr]$Handle,
        [Parameter(Mandatory = $true)]
        [string]$OutputPath
    )

    [void][PreviewWindows]::ShowWindow($Handle, 9)
    [void][PreviewWindows]::SetForegroundWindow($Handle)
    Start-Sleep -Milliseconds 500

    $rect = New-Object RECT
    if (-not [PreviewWindows]::GetWindowRect($Handle, [ref]$rect)) {
        throw "Could not read preview window bounds."
    }

    $width = $rect.Right - $rect.Left
    $height = $rect.Bottom - $rect.Top
    if ($width -le 0 -or $height -le 0) {
        throw "Preview window bounds were invalid."
    }

    if (-not [PreviewWindows]::CaptureWindow($Handle, $OutputPath)) {
        $bitmap = New-Object System.Drawing.Bitmap $width, $height
        $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
        try {
            $graphics.CopyFromScreen($rect.Left, $rect.Top, 0, 0, $bitmap.Size)
            $bitmap.Save($OutputPath, [System.Drawing.Imaging.ImageFormat]::Png)
        }
        finally {
            $graphics.Dispose()
            $bitmap.Dispose()
        }
    }
}

function Invoke-PreviewCapture {
    param(
        [Parameter(Mandatory = $true)]
        [string[]]$ArgumentList,
        [Parameter(Mandatory = $true)]
        [string]$WindowTitle,
        [Parameter(Mandatory = $true)]
        [string]$OutputPath
    )

    $process = Start-Process -FilePath $pythonwExe -ArgumentList $ArgumentList -WorkingDirectory $projectRoot -PassThru
    try {
        $handle = Wait-PreviewWindow -ProcessId $process.Id -Title $WindowTitle
        Save-WindowCapture -Handle $handle -OutputPath $OutputPath
    }
    finally {
        if (-not $process.HasExited) {
            Stop-Process -Id $process.Id -Force
        }
    }
}

New-SampleSnipImage -Path $sampleSourcePath

Invoke-PreviewCapture -ArgumentList @("scripts\launch_readme_preview.py", "--profile", "readme-preview", "main") -WindowTitle "Manna Snips" -OutputPath $mainShotPath
Invoke-PreviewCapture -ArgumentList @("scripts\launch_readme_preview.py", "--profile", "readme-preview", "editor", $sampleSourcePath) -WindowTitle "Manna Snips Editor" -OutputPath $editorShotPath

Write-Output "README screenshot capture complete."
Write-Output "Sample source: $sampleSourcePath"
Write-Output "Main window: $mainShotPath"
Write-Output "Editor window: $editorShotPath"
