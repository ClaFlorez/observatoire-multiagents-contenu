# Serveur portable limité au poste local ; aucune modification persistante de Windows.
$ErrorActionPreference = 'Stop'
$taskRoot = Split-Path -Parent $PSScriptRoot
$taskExecutable = Join-Path $taskRoot '.local\ollama\ollama.exe'
if (-not (Test-Path -LiteralPath $taskExecutable)) {
    throw 'Ollama portable absent dans .local\ollama.'
}
$env:OLLAMA_HOST = '127.0.0.1:11434'
$env:OLLAMA_MODELS = Join-Path $taskRoot '.local\models'
$env:OLLAMA_NO_CLOUD = '1'
$env:CUDA_VISIBLE_DEVICES = '-1'
$env:OLLAMA_CONTEXT_LENGTH = '4096'
$env:OLLAMA_NUM_PARALLEL = '1'
$env:OLLAMA_MAX_LOADED_MODELS = '1'
New-Item -ItemType Directory -Path $env:OLLAMA_MODELS -Force | Out-Null
& $taskExecutable serve
if ($LASTEXITCODE -ne 0) { throw "Ollama s'est arrêté avec le code $LASTEXITCODE." }
