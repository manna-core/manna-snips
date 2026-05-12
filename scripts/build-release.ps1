$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $projectRoot

$pyArgs = @("-3")
$pyInstallerModuleArgs = @("-m", "PyInstaller")

$versionCheck = & $env:ComSpec /c 'py -3 -c "import PyInstaller; print(PyInstaller.__version__)" 2>nul'
if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($versionCheck)) {
    throw "PyInstaller is not installed for py -3. Run: py -3 -m pip install pyinstaller"
}

$packageVersion = & py -3 -c "import pathlib, tomllib; print(tomllib.loads(pathlib.Path('pyproject.toml').read_text(encoding='utf-8'))['project']['version'])"
if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($packageVersion)) {
    throw "Could not read project version from pyproject.toml."
}

$packageVersion = $packageVersion.Trim()
$releaseDir = Join-Path $projectRoot "dist\MannaSnips"
$releaseZip = Join-Path $projectRoot ("dist\MannaSnips-{0}-windows-x64.zip" -f $packageVersion)
$releaseZipHashPath = Join-Path $projectRoot ("dist\MannaSnips-{0}-windows-x64.sha256.txt" -f $packageVersion)

$pyInstallerArgs = @(
    "--noconfirm",
    "--clean",
    "--windowed",
    "--onedir",
    "--name", "MannaSnips",
    "--icon", "assets\icons\manna-snips.ico",
    "--paths", "src",
    "--add-data", "scripts\save-clipboard-image.ps1;scripts",
    "--add-data", "scripts\set-clipboard-image.ps1;scripts",
    "--add-data", "assets\icons\manna-snips.ico;assets\icons",
    "--add-data", "assets\icons\manna-snips.png;assets\icons",
    "scripts\manna_snips_app.pyw"
)

Write-Output "Building MannaSnips release from $projectRoot"
Write-Output "PyInstaller version: $versionCheck"
Write-Output "Command: py $($pyArgs -join ' ') $($pyInstallerModuleArgs -join ' ') $($pyInstallerArgs -join ' ')"

& py @pyArgs @pyInstallerModuleArgs @pyInstallerArgs
if ($LASTEXITCODE -ne 0) {
    throw "PyInstaller build failed."
}

if (Test-Path $releaseZip) {
    Remove-Item -LiteralPath $releaseZip -Force
}

Compress-Archive -LiteralPath $releaseDir -DestinationPath $releaseZip -Force

$releaseZipHash = (Get-FileHash -LiteralPath $releaseZip -Algorithm SHA256).Hash.ToLowerInvariant()
Set-Content -Path $releaseZipHashPath -Value ("{0} *{1}" -f $releaseZipHash, (Split-Path -Leaf $releaseZip)) -Encoding ascii

Write-Output "Release build complete."
Write-Output "Output: $releaseDir"
Write-Output "Archive: $releaseZip"
Write-Output "SHA256: $releaseZipHashPath"
