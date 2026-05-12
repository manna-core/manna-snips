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
if (-not (Test-Path $targetPath)) {
    throw "Image file not found: $targetPath"
}

$sourceImage = [System.Drawing.Image]::FromFile($targetPath)
try {
    $bitmap = New-Object System.Drawing.Bitmap $sourceImage
}
finally {
    $sourceImage.Dispose()
}

try {
    $copied = $false
    for ($attempt = 0; $attempt -lt 15 -and -not $copied; $attempt++) {
        try {
            [System.Windows.Forms.Clipboard]::SetImage($bitmap)
            $copied = $true
        }
        catch {
            if ($attempt -ge 14) {
                throw
            }
            Start-Sleep -Milliseconds 40
        }
    }
}
finally {
    $bitmap.Dispose()
}

Write-Output $targetPath
