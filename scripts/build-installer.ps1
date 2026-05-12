$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent (Split-Path -Parent $MyInvocation.MyCommand.Path)
Set-Location $projectRoot

$packageVersion = & py -3 -c "import pathlib, tomllib; print(tomllib.loads(pathlib.Path('pyproject.toml').read_text(encoding='utf-8'))['project']['version'])"
if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($packageVersion)) {
    throw "Could not read project version from pyproject.toml."
}
$packageVersion = $packageVersion.Trim()

$possibleIsccPaths = @(
    (Join-Path $env:LOCALAPPDATA "Programs\Inno Setup 6\ISCC.exe"),
    "C:\Program Files (x86)\Inno Setup 6\ISCC.exe",
    "C:\Program Files\Inno Setup 6\ISCC.exe"
)

$isccPath = ""
$isccCommand = Get-Command ISCC.exe -ErrorAction SilentlyContinue
if ($isccCommand) {
    $isccPath = $isccCommand.Source
}
else {
    foreach ($candidate in $possibleIsccPaths) {
        if (Test-Path $candidate) {
            $isccPath = $candidate
            break
        }
    }
}

if (-not $isccPath) {
    throw "Inno Setup is not installed. Install it with: winget install --id JRSoftware.InnoSetup -e --accept-source-agreements --accept-package-agreements"
}

$pythonRoot = & py -3 -c "import pathlib, sys; print(pathlib.Path(sys.executable).parent)"
if ($LASTEXITCODE -ne 0 -or [string]::IsNullOrWhiteSpace($pythonRoot)) {
    throw "Could not resolve the local Python runtime root."
}
$pythonRoot = $pythonRoot.Trim()
if (-not (Test-Path $pythonRoot)) {
    throw "Resolved Python runtime root does not exist: $pythonRoot"
}

$installerScript = Join-Path $projectRoot "installer\manna-snips.iss"
$installerStagingRoot = Join-Path $projectRoot "dist\installer-staging"
$stagingDir = Join-Path $installerStagingRoot ("MannaSnips-{0}-source-runtime" -f $packageVersion)
$stagingAppDir = Join-Path $stagingDir "MannaSnips"
$installerOutputDir = Join-Path $projectRoot "dist\installer"
New-Item -ItemType Directory -Path $installerOutputDir -Force | Out-Null

if (Test-Path $stagingDir) {
    Remove-Item -LiteralPath $stagingDir -Recurse -Force
}
New-Item -ItemType Directory -Path $stagingAppDir -Force | Out-Null

function Copy-Tree {
    param(
        [Parameter(Mandatory = $true)]
        [string]$Source,
        [Parameter(Mandatory = $true)]
        [string]$Destination
    )

    if (-not (Test-Path $Source)) {
        throw "Source path not found: $Source"
    }

    New-Item -ItemType Directory -Path $Destination -Force | Out-Null
    Copy-Item -Path (Join-Path $Source "*") -Destination $Destination -Recurse -Force
}

$sourceDirs = @(
    @{ Source = (Join-Path $projectRoot "assets"); Destination = (Join-Path $stagingAppDir "assets") },
    @{ Source = (Join-Path $projectRoot "scripts"); Destination = (Join-Path $stagingAppDir "scripts") },
    @{ Source = (Join-Path $projectRoot "src"); Destination = (Join-Path $stagingAppDir "src") },
    @{ Source = (Join-Path $pythonRoot "DLLs"); Destination = (Join-Path $stagingAppDir "python-runtime\DLLs") },
    @{ Source = (Join-Path $pythonRoot "Lib"); Destination = (Join-Path $stagingAppDir "python-runtime\Lib") },
    @{ Source = (Join-Path $pythonRoot "tcl"); Destination = (Join-Path $stagingAppDir "python-runtime\tcl") }
)

foreach ($entry in $sourceDirs) {
    Copy-Tree -Source $entry.Source -Destination $entry.Destination
}

$sourceFiles = @(
    "LICENSE.txt",
    "python.exe",
    "pythonw.exe",
    "python3.dll",
    "python314.dll",
    "vcruntime140.dll",
    "vcruntime140_1.dll"
)

foreach ($fileName in $sourceFiles) {
    $sourceFile = Join-Path $pythonRoot $fileName
    if (Test-Path $sourceFile) {
        $destinationFile = Join-Path (Join-Path $stagingAppDir "python-runtime") $fileName
        New-Item -ItemType Directory -Path (Split-Path -Parent $destinationFile) -Force | Out-Null
        Copy-Item -LiteralPath $sourceFile -Destination $destinationFile -Force
    }
}

foreach ($projectFile in @("README.md", "PRIVACY.md", "LICENSE")) {
    $sourceFile = Join-Path $projectRoot $projectFile
    if (Test-Path $sourceFile) {
        Copy-Item -LiteralPath $sourceFile -Destination (Join-Path $stagingAppDir $projectFile) -Force
    }
}

$compileArgs = @(
    "/Qp",
    "/DAppVersion=$packageVersion",
    "/DSourceDir=$stagingAppDir",
    "/DOutputDir=$installerOutputDir",
    $installerScript
)

Write-Output "Building Manna Snips installer from $projectRoot"
Write-Output "Inno Setup compiler: $isccPath"
Write-Output "Installer script: $installerScript"
Write-Output "Installer staging: $stagingAppDir"
Write-Output "Bundled Python runtime: $pythonRoot"

& $isccPath @compileArgs
if ($LASTEXITCODE -ne 0) {
    throw "Inno Setup build failed."
}

$setupPath = Join-Path $installerOutputDir ("MannaSnips-{0}-Setup.exe" -f $packageVersion)
$setupHashPath = Join-Path $installerOutputDir ("MannaSnips-{0}-Setup.sha256.txt" -f $packageVersion)
$setupHash = (Get-FileHash -LiteralPath $setupPath -Algorithm SHA256).Hash.ToLowerInvariant()
Set-Content -Path $setupHashPath -Value ("{0} *{1}" -f $setupHash, (Split-Path -Leaf $setupPath)) -Encoding ascii
Write-Output "Installer build complete."
Write-Output "Output: $setupPath"
Write-Output "SHA256: $setupHashPath"
