param(
    [string]$ShortcutPath = "",
    [string]$Profile = "",
    [ValidateSet("source", "release")]
    [string]$Mode = "source"
)

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$appScriptPath = Join-Path $scriptDir "manna_snips_app.pyw"
$projectRoot = Split-Path -Parent $scriptDir
$releaseExePath = Join-Path $projectRoot "dist\MannaSnips\MannaSnips.exe"
$iconPath = Join-Path (Split-Path -Parent $scriptDir) "assets\icons\manna-snips.ico"

if (-not $ShortcutPath) {
    $modeSuffix = if ($Mode -eq "release") { "-RELEASE" } else { "" }
    if ([string]::IsNullOrWhiteSpace($Profile)) {
        $ShortcutPath = Join-Path $scriptDir ("MANNA-SNIPS{0}.lnk" -f $modeSuffix)
    }
    else {
        $safeProfile = ($Profile -replace '[^A-Za-z0-9_-]', '-').Trim('-')
        if (-not $safeProfile) {
            $safeProfile = "PROFILE"
        }
        $ShortcutPath = Join-Path $scriptDir ("MANNA-SNIPS{0}-{1}.lnk" -f $modeSuffix, $safeProfile.ToUpperInvariant())
    }
}

$shortcutDir = Split-Path -Parent $ShortcutPath
if ($shortcutDir -and -not (Test-Path $shortcutDir)) {
    New-Item -ItemType Directory -Path $shortcutDir -Force | Out-Null
}

$shell = New-Object -ComObject WScript.Shell
$shortcut = $shell.CreateShortcut($ShortcutPath)

$targetPath = ""
$workingDirectory = ""
$arguments = @()
$description = "Launch Manna Snips"

if ($Mode -eq "release") {
    if (-not (Test-Path $releaseExePath)) {
        throw "Release executable not found: $releaseExePath"
    }
    $targetPath = $releaseExePath
    $workingDirectory = Split-Path -Parent $releaseExePath
    $description = "Launch Manna Snips release build"
}
else {
    if (-not (Test-Path $appScriptPath)) {
        throw "App script not found: $appScriptPath"
    }
    $pythonExe = & py -3 -c "import pathlib, sys; print(pathlib.Path(sys.executable).with_name('pythonw.exe'))"
    if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($pythonExe)) {
        throw "Could not resolve pythonw.exe through py -3."
    }
    $pythonExe = $pythonExe.Trim()
    if (-not (Test-Path $pythonExe)) {
        throw "Resolved pythonw.exe does not exist: $pythonExe"
    }
    $targetPath = $pythonExe
    $workingDirectory = $scriptDir
    $arguments += "`"$appScriptPath`""
}

if (-not [string]::IsNullOrWhiteSpace($Profile)) {
    $arguments += "--profile"
    $arguments += $Profile
}
$shortcut.TargetPath = $targetPath
$shortcut.Arguments = ($arguments -join " ")
$shortcut.WorkingDirectory = $workingDirectory
$shortcut.Description = $description
if (Test-Path $iconPath) {
    $shortcut.IconLocation = $iconPath
}
$shortcut.Save()

Write-Output "Shortcut updated: $ShortcutPath"
Write-Output "Mode: $Mode"
Write-Output "Target: $targetPath"
Write-Output ("Arguments: {0}" -f $shortcut.Arguments)
