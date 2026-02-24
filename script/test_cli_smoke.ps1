param(
    [string]$ExePath = "build_smoke/bin/MyAVLib_Cmd.exe",
    [string]$DataFile = "tests/smoke/test_ids.txt"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Resolve-RepoPath {
    param([string]$BaseDir, [string]$PathLike)
    if (Test-Path $PathLike) {
        return (Resolve-Path $PathLike).Path
    }

    $candidate = Join-Path $BaseDir $PathLike
    if (Test-Path $candidate) {
        return (Resolve-Path $candidate).Path
    }

    throw "Path not found: $PathLike"
}

function Assert-Contains {
    param(
        [string]$Text,
        [string]$Expected,
        [string]$Name
    )
    if ($Text -notmatch [Regex]::Escape($Expected)) {
        throw "Assertion failed [$Name]. Missing text: $Expected"
    }
}

$repoRoot = (Resolve-Path (Join-Path $PSScriptRoot "..")).Path
$exeFullPath = Resolve-RepoPath -BaseDir $repoRoot -PathLike $ExePath
$dataFullPath = Resolve-RepoPath -BaseDir $repoRoot -PathLike $DataFile

$tempDir = Join-Path ([System.IO.Path]::GetTempPath()) ("avlib_cli_smoke_" + [Guid]::NewGuid().ToString("N"))
New-Item -ItemType Directory -Path $tempDir -Force | Out-Null

$exportPath = Join-Path $tempDir "export_ids.txt"
$outputPath = Join-Path $tempDir "cli_output.txt"
$dbName = "smoke_" + (Get-Date -Format "yyyyMMdd_HHmmss") + "_" + (Get-Random -Minimum 100 -Maximum 999)
$dbFileName = "$dbName.sqlite3"

$inputLines = @(
    "3",
    $dbName,
    "5",
    $dataFullPath,
    "2",
    "abc-1234",
    "2",
    "zz-9999",
    "8",
    $exportPath,
    "0"
)
$inputText = ($inputLines -join "`r`n") + "`r`n"

$dbPath = Join-Path (Split-Path -Parent $exeFullPath) ("data/" + $dbFileName)

try {
    $cliOutput = $inputText | & $exeFullPath 2>&1 | Out-String
    Set-Content -Path $outputPath -Value $cliOutput -Encoding utf8

    Assert-Contains -Text $cliOutput -Expected "从文件导入到 [$dbFileName] 完成。 成功: 4。" -Name "import"
    Assert-Contains -Text $cliOutput -Expected "在 [$dbFileName] 中查询完成。 找到: 1个。" -Name "query_hit"
    Assert-Contains -Text $cliOutput -Expected "在 [$dbFileName] 中查询完成。 找到: 0个。 未找到: 1个。" -Name "query_miss"

    if (-not (Test-Path $exportPath)) {
        throw "Assertion failed [export_exists]. File not found: $exportPath"
    }

    $actual = Get-Content $exportPath | Where-Object { $_.Trim().Length -gt 0 } | Sort-Object -Unique
    $expected = @("a123", "abc1234", "abcd1234", "efgh5678") | Sort-Object -Unique
    $diff = Compare-Object -ReferenceObject $expected -DifferenceObject $actual
    if ($null -ne $diff) {
        throw ("Assertion failed [export_content]. Expected: " + ($expected -join ", ") +
               "; Actual: " + ($actual -join ", "))
    }

    Write-Host "CLI smoke test passed."
    Write-Host "Output log: $outputPath"
    Write-Host "Export file: $exportPath"
}
finally {
    if (Test-Path $dbPath) {
        Remove-Item -Path $dbPath -Force
    }
}

