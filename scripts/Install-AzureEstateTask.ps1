<#
.SYNOPSIS
    Registra (ou atualiza) a Tarefa Agendada do Windows que executa o Azure
    Estate periodicamente na VM.

.DESCRIPTION
    A tarefa roda como SYSTEM, com "executar mesmo sem usuario logado", porque a
    identidade gerenciada vem do IMDS da VM (169.254.169.254) e nao de nenhuma
    sessao de usuario. Nenhuma senha e armazenada.

    Precisa ser executado em um PowerShell elevado (Administrador).

.EXAMPLE
    # Diariamente as 03:00
    .\scripts\Install-AzureEstateTask.ps1 -At 03:00

.EXAMPLE
    # Toda segunda-feira as 06:30, relatorio 'all'
    .\scripts\Install-AzureEstateTask.ps1 -At 06:30 -Weekly Monday -Report all

.EXAMPLE
    # Diariamente as 03:00, enviando para um container de Blob Storage
    .\scripts\Install-AzureEstateTask.ps1 -At 03:00 -UploadTarget blob
#>
[CmdletBinding()]
param(
    [string]   $TaskName = "AzureEstate-ResourceDetails",
    [datetime] $At = "03:00",
    [ValidateSet("Monday","Tuesday","Wednesday","Thursday","Friday","Saturday","Sunday")]
    [string]   $Weekly,
    [string]   $Report = "resource_details",
    [ValidateSet("blob","share")]
    [string]   $UploadTarget,
    [string]   $User = "SYSTEM"
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$identity = [Security.Principal.WindowsIdentity]::GetCurrent()
if (-not ([Security.Principal.WindowsPrincipal]$identity).IsInRole(
        [Security.Principal.WindowsBuiltInRole]::Administrator)) {
    throw "Execute este script em um PowerShell elevado (Administrador)."
}

$root   = Split-Path -Parent $PSScriptRoot
$runner = Join-Path $PSScriptRoot "Run-AzureEstate.ps1"
if (-not (Test-Path -LiteralPath $runner)) {
    throw "Runner nao encontrado: $runner"
}

$argumento = '-NoProfile -NonInteractive -ExecutionPolicy Bypass -File "{0}" -Report {1}' -f $runner, $Report
if ($UploadTarget) { $argumento += " -UploadTarget $UploadTarget" }

$action = New-ScheduledTaskAction `
    -Execute "$env:SystemRoot\System32\WindowsPowerShell\v1.0\powershell.exe" `
    -Argument $argumento `
    -WorkingDirectory $root

if ($Weekly) {
    $trigger = New-ScheduledTaskTrigger -Weekly -DaysOfWeek $Weekly -At $At
}
else {
    $trigger = New-ScheduledTaskTrigger -Daily -At $At
}

# SYSTEM alcanca o IMDS e nao expira senha. RunLevel Highest evita bloqueios de
# escrita na pasta do projeto.
$principal = New-ScheduledTaskPrincipal -UserId $User -LogonType ServiceAccount -RunLevel Highest

$settings = New-ScheduledTaskSettingsSet `
    -StartWhenAvailable `
    -DontStopOnIdleEnd `
    -MultipleInstances IgnoreNew `
    -ExecutionTimeLimit (New-TimeSpan -Hours 4) `
    -RestartCount 2 `
    -RestartInterval (New-TimeSpan -Minutes 15)

Register-ScheduledTask `
    -TaskName $TaskName `
    -Action $action `
    -Trigger $trigger `
    -Principal $principal `
    -Settings $settings `
    -Description "Azure Estate: inventario do Azure via identidade gerenciada, enviado ao Storage Account." `
    -Force | Out-Null

Write-Host "Tarefa '$TaskName' registrada."
Write-Host "Testar agora:      Start-ScheduledTask -TaskName '$TaskName'"
Write-Host "Ver resultado:     Get-ScheduledTaskInfo -TaskName '$TaskName'"
Write-Host "Log:               $root\logs\"
