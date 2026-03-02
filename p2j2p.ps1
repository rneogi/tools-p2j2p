param(
    [Parameter(Mandatory = $true, Position = 0)]
    [string]$InputPdf
)

$python = "C:/Users/raja.neogi/AppData/Local/Programs/Python/Python312/python.exe"

if (-not (Test-Path $python)) {
    $python = "python"
}

& $python "tools/p2j2p.py" $InputPdf
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}
