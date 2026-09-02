<#
.SYNOPSIS
    Remove os relatórios que sobraram da nomenclatura antiga (`_AAAAMMDD`).

.DESCRIPTION
    Até a mudança para `_DD_MM_AAAA_HH_MM_SS`, o nome do arquivo tinha apenas a
    data: uma nova execução no mesmo dia sobrescrevia a anterior. Com o carimbo
    novo isso deixou de acontecer, e os arquivos do formato antigo passaram a
    conviver para sempre com os novos — dois nomes diferentes para o mesmo
    conteúdo.

    Este script apaga apenas o que casa com o padrão ANTIGO:
    `<nome>_AAAAMMDD.csv` ou `.xlsx`. Arquivos no formato novo nunca são
    tocados, porque o carimbo novo tem seis grupos e não oito dígitos seguidos.

    Por segurança ele pede confirmação. Use -WhatIf para apenas listar.

.PARAMETER Path
    Diretório de saída a limpar (padrão: output\ na raiz do repositório).
    Subpastas são incluídas: o Run-AzureEstate.ps1 grava em pastas datadas.

.EXAMPLE
    # Só mostra o que seria apagado
    .\scripts\Remove-LegacyOutput.ps1 -WhatIf

.EXAMPLE
    # Apaga sem perguntar, em outro diretório
    .\scripts\Remove-LegacyOutput.ps1 -Path D:\inventario -Confirm:$false

.NOTES
    Para os arquivos já enviados ao container de Blob, o equivalente é:

      az storage blob delete-batch --account-name <conta> --source <container> `
        --pattern "*_20??????.csv" --auth-mode login --dry-run

    Confira a lista e repita sem --dry-run.
#>
[CmdletBinding(SupportsShouldProcess, ConfirmImpact = 'High')]
param(
    [string] $Path
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if (-not $Path) { $Path = Join-Path (Split-Path -Parent $PSScriptRoot) "output" }
if (-not (Test-Path -LiteralPath $Path)) { throw "Diretorio nao encontrado: '$Path'." }

# Formato antigo: oito digitos colados antes da extensao. O novo carimbo
# (02_09_2026_10_10_34) nao casa, porque seus digitos vem separados por '_'.
$legado = '_\d{8}\.(csv|xlsx)$'

$alvos = @(Get-ChildItem -LiteralPath $Path -File -Recurse |
    Where-Object { $_.Name -match $legado })

if ($alvos.Count -eq 0) {
    Write-Host "Nada a remover em '$Path': nenhum arquivo no formato antigo."
    return
}

$bytes = ($alvos | Measure-Object -Property Length -Sum).Sum
Write-Host ("{0} arquivo(s) no formato antigo, {1:N1} MB:" -f $alvos.Count, ($bytes / 1MB))
$alvos | ForEach-Object { Write-Host "  $($_.FullName)" }

foreach ($alvo in $alvos) {
    if ($PSCmdlet.ShouldProcess($alvo.FullName, "Remover")) {
        Remove-Item -LiteralPath $alvo.FullName -Force
    }
}
