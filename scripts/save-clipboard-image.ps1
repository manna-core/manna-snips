param(
    [Parameter(Mandatory = $true)]
    [string]$Path
)

if ([Threading.Thread]::CurrentThread.GetApartmentState() -ne [Threading.ApartmentState]::STA) {
    throw "Clipboard access requires an STA PowerShell process."
}

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$targetPath = [System.IO.Path]::GetFullPath($Path)
$targetDir = Split-Path -Parent $targetPath

if ($targetDir -and -not (Test-Path $targetDir)) {
    New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
}

$image = [System.Windows.Forms.Clipboard]::GetImage()
if (-not $image) {
    throw "No image is currently available in the clipboard."
}

try {
    $image.Save($targetPath, [System.Drawing.Imaging.ImageFormat]::Png)
}
finally {
    $image.Dispose()
}

Write-Output $targetPath
