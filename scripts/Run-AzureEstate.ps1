<#
.SYNOPSIS
    Executa o Azure Estate de forma não assistida (Tarefa Agendada do Windows),
    usando a identidade gerenciada da VM e enviando os relatórios ao Storage
    Account.

.DESCRIPTION
    Pensado para rodar sem nenhum usuário logado: não há 'az login', não há
    segredo em disco. A credencial vem do IMDS da VM (AZE_AUTH_MODE=managed-identity).

    Cada execução:
      1. gera o relatório em uma subpasta datada (execuções concorrentes ou
         interrompidas não se sobrepõem);
      2. envia os .xlsx e .csv para o File Share;
      3. registra tudo em logs\azure-estate_<data>.log;
      4. remove execuções locais mais antigas que -RetentionDays.

.PARAMETER Report
    Nome do relatório (padrão: resource_details). 'all' roda todos.

.PARAMETER SkipUpload
    Gera os arquivos sem enviar ao Storage Account.

.PARAMETER UploadTarget
    Destino do envio: 'blob' (container de Blob Storage) ou 'share' (Azure File
    Share). Padrao: o valor de AZE_UPLOAD_TARGET no .env.

.PARAMETER Format
    Formato de saida: 'xlsx', 'csv' ou 'both'. Padrao: o valor de
    AZE_OUTPUT_FORMAT no .env (que por sua vez tem 'both' como padrao).

.EXAMPLE
    .\scripts\Run-AzureEstate.ps1 -Report resource_details -UploadTarget blob
#>
[CmdletBinding()]
param(
    [string] $Report = "resource_details",
    [string] $OutputRoot,
    [int]    $RetentionDays = 30,
    [switch] $SkipUpload,
    [ValidateSet("blob","share")]
    [string] $UploadTarget,
    [ValidateSet("xlsx","csv","both")]
    [string] $Format
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$root = Split-Path -Parent $PSScriptRoot
if (-not $OutputRoot) { $OutputRoot = Join-Path $root "output" }

$python = Join-Path $root ".venv\Scripts\python.exe"
if (-not (Test-Path -LiteralPath $python)) {
    throw "Interpretador nao encontrado em '$python'. Crie o venv e instale requirements.txt."
}

$stamp   = Get-Date -Format "yyyyMMdd-HHmmss"
$runDir  = Join-Path $OutputRoot $stamp
$logDir  = Join-Path $root "logs"
$logFile = Join-Path $logDir ("azure-estate_{0}.log" -f (Get-Date -Format "yyyyMMdd"))

New-Item -ItemType Directory -Force -Path $runDir, $logDir | Out-Null

function Write-Log {
    param([string] $Message)
    $line = "{0} {1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $Message
    Write-Output $line
    Add-Content -LiteralPath $logFile -Value $line -Encoding UTF8
}

# A tarefa agendada nao herda o ambiente de um usuario interativo; o modo de
# autenticacao e fixado aqui para que uma variavel ausente nao faca o processo
# procurar silenciosamente por um 'az login' que nunca existira.
if (-not $env:AZE_AUTH_MODE) { $env:AZE_AUTH_MODE = "managed-identity" }

Write-Log "=== Inicio | relatorio='$Report' | auth='$($env:AZE_AUTH_MODE)' | saida='$runDir' ==="

$exitCode = 0
try {
    $arguments = @("main.py", "--report", $Report, "--output", $runDir)
    if ($Format) { $arguments += @("--format", $Format) }
    if (-not $SkipUpload) {
        $arguments += "--upload"
        if ($UploadTarget) { $arguments += @("--upload-target", $UploadTarget) }
    }

    Push-Location $root
    try {
        # O stderr vai para um arquivo em vez de ser unido ao stdout no pipeline:
        # com '2>&1' o PowerShell embrulha a primeira linha de stderr em um
        # NativeCommandError ruidoso (e, sob ErrorActionPreference='Stop', corta
        # o traceback na primeira linha).
        $stderrFile = Join-Path $runDir "stderr.txt"
        # Sem isto o Python emite cp1252 e os acentos chegam corrompidos ao log.
        $env:PYTHONIOENCODING = "utf-8"

        # 'Continue' e obrigatorio mesmo redirecionando para arquivo: o stderr de
        # um processo nativo passa pelo fluxo de erro do PowerShell e, sob
        # ErrorActionPreference='Stop', a primeira linha vira erro terminante e
        # corta o traceback logo em "Traceback (most recent call last):".
        $anterior = $ErrorActionPreference
        $ErrorActionPreference = "Continue"
        try {
            & $python @arguments 2>$stderrFile | ForEach-Object { Write-Log $_ }
            $exitCode = $LASTEXITCODE
        }
        finally { $ErrorActionPreference = $anterior }

        if (Test-Path -LiteralPath $stderrFile) {
            Get-Content -LiteralPath $stderrFile -Encoding UTF8 |
                Where-Object { $_ -ne "" } |
                ForEach-Object { Write-Log "  $_" }
            Remove-Item -LiteralPath $stderrFile -Force
        }
    }
    finally { Pop-Location }

    if ($exitCode -ne 0) {
        Write-Log "[ERRO] main.py terminou com codigo $exitCode."
    }
    else {
        $files = @(Get-ChildItem -LiteralPath $runDir -File -ErrorAction SilentlyContinue |
            Where-Object { $_.Extension -in @(".xlsx", ".csv") })
        # Codigo de saida 0 sem nenhum arquivo e uma falha silenciosa: a tarefa
        # apareceria como bem-sucedida no agendador para sempre.
        if ($files.Count -eq 0) {
            Write-Log "[ERRO] Nenhum .xlsx/.csv foi gerado em '$runDir'."
            $exitCode = 2
        }
        else {
            Write-Log ("Gerado(s) {0} arquivo(s): {1}" -f $files.Count, ($files.Name -join ", "))
        }
    }
}
catch {
    Write-Log "[ERRO] $($_.Exception.Message)"
    $exitCode = 1
}

# Limpeza das execucoes locais antigas (o destino permanente e o Storage Account).
try {
    $limite = (Get-Date).AddDays(-$RetentionDays)
    Get-ChildItem -LiteralPath $OutputRoot -Directory -ErrorAction SilentlyContinue |
        Where-Object { $_.Name -match '^\d{8}-\d{6}$' -and $_.LastWriteTime -lt $limite } |
        ForEach-Object {
            Remove-Item -LiteralPath $_.FullName -Recurse -Force
            Write-Log "Removida execucao antiga: $($_.Name)"
        }
    Get-ChildItem -LiteralPath $logDir -Filter "azure-estate_*.log" -File -ErrorAction SilentlyContinue |
        Where-Object { $_.LastWriteTime -lt $limite } |
        Remove-Item -Force
}
catch {
    Write-Log "[AVISO] Falha na limpeza: $($_.Exception.Message)"
}

Write-Log "=== Fim | codigo de saida $exitCode ==="
exit $exitCode
