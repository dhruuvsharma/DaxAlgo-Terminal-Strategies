# Packages each strategy as a .daxplugin — the integrity-verified format DaxAlgo Terminal's Plugin
# Manager installs (Plugins -> Manage strategy plugins... -> Install plugin...). A package is a zip of
# the plugin files plus a package.json integrity index (per-file sha256 + the main assembly name); the
# host verifies every file BEFORE any trust gate sees the content. Works in Windows PowerShell 5.1 and pwsh.
#
#   ./pack-plugin.ps1                                       # pack all 9 strategies -> dist/
#   ./pack-plugin.ps1 -Name TradingTerminal.Strategies.SigmaIcFlow   # pack one
param(
    [string]$Configuration = "Release",
    [string]$Name = ""
)
$ErrorActionPreference = "Stop"

# Strategies carrying a PRIVATE HelixToolkit.Wpf dependency the host does NOT provide — it must ship
# inside the package. Everything else the strategy links (TradingTerminal.*/DaxAlgo.Sdk*/MahApps/
# ScottPlot/CommunityToolkit) is host-provided; shipping a copy would break type identity, so those
# are deliberately NOT packed.
$helix = @(
    "TradingTerminal.Strategies.OrderFlowCube",
    "TradingTerminal.Strategies.OrderFlowSurfaceSpike",
    "TradingTerminal.Strategies.ImbalanceHeatFront",
    "TradingTerminal.Strategies.IndexKScoreSurface"
)

Add-Type -AssemblyName System.IO.Compression.FileSystem
$srcRoot = Join-Path $PSScriptRoot "src"
$outRoot = Join-Path $PSScriptRoot "dist"
New-Item -ItemType Directory -Force $outRoot | Out-Null

$projects = Get-ChildItem $srcRoot -Directory
if ($Name) {
    $projects = $projects | Where-Object { $_.Name -eq $Name }
    if (-not $projects) { throw "No strategy folder named '$Name' under src/." }
}

foreach ($proj in $projects) {
    $sName = $proj.Name
    $csproj = Join-Path $proj.FullName "$sName.csproj"
    dotnet build $csproj -c $Configuration | Out-Host
    if ($LASTEXITCODE -ne 0) { throw "Build failed: $sName" }

    $targetDirOutput = @(dotnet msbuild $csproj -nologo -p:Configuration=$Configuration -getProperty:TargetDir)
    if ($LASTEXITCODE -ne 0) { throw "Could not evaluate TargetDir: $sName" }
    $bin = [string]($targetDirOutput | Where-Object { -not [string]::IsNullOrWhiteSpace($_) } | Select-Object -Last 1)
    $bin = $bin.Trim()
    if (-not [IO.Path]::IsPathRooted($bin)) { throw "MSBuild returned an invalid TargetDir for ${sName}: '$bin'" }

    $stage = Join-Path ([IO.Path]::GetTempPath()) ("daxplugin-" + [guid]::NewGuid().ToString("N"))
    New-Item -ItemType Directory $stage | Out-Null
    try {
        $ship = @("$sName.dll", "plugin.json", "$sName.pdb", "$sName.deps.json")
        if ($helix -contains $sName) { $ship += "HelixToolkit.Wpf.dll" }
        foreach ($f in $ship) {
            $s = Join-Path $bin $f
            if (Test-Path $s) { Copy-Item $s $stage }
        }
        if (-not (Test-Path (Join-Path $stage "$sName.dll"))) { throw "Build output not found under $bin." }

        # Integrity index — must match the host's reader: forward-slash keys, hex sha256.
        $files = @{}
        Get-ChildItem $stage -Recurse -File | ForEach-Object {
            $relative = $_.FullName.Substring($stage.Length + 1).Replace('\', '/')
            $files[$relative] = (Get-FileHash $_.FullName -Algorithm SHA256).Hash
        }
        @{ formatVersion = 1; mainAssembly = "$sName.dll"; files = $files } |
            ConvertTo-Json -Depth 5 | Set-Content (Join-Path $stage "package.json") -Encoding utf8

        $output = Join-Path $outRoot "$sName.daxplugin"
        Remove-Item $output -ErrorAction SilentlyContinue
        [IO.Compression.ZipFile]::CreateFromDirectory($stage, $output)
        Write-Host "Packaged -> $output"
    }
    finally { Remove-Item $stage -Recurse -Force -ErrorAction SilentlyContinue }
}
Write-Host "Install via DaxAlgo Terminal: Plugins -> Manage strategy plugins... -> Install plugin..."
