param(
    [Parameter(Mandatory = $true)][string]$Email,
    [Parameter(Mandatory = $true)][string]$Password,
    [Parameter(Mandatory = $true)][int]$UserId
)

$ErrorActionPreference = 'Stop'
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
$body = @{ email = $Email; password = $Password } | ConvertTo-Json -Compress

try {
    $login = Invoke-WebRequest -UseBasicParsing -Method Post -Uri 'http://127.0.0.1:5000/api/login' -ContentType 'application/json' -Body $body -WebSession $session
    Write-Output "LOGIN_HTTP=$($login.StatusCode)"

    $report = Invoke-WebRequest -UseBasicParsing -Uri ("http://127.0.0.1:5000/api/integrity_report/{0}" -f $UserId) -WebSession $session
    $payload = $report.Content | ConvertFrom-Json
    Write-Output "COMPLETED_REPORT_HTTP=$($report.StatusCode)"
    Write-Output "COMPLETED_REPORT_USER_ID=$($payload.user.id)"
    Write-Output "COMPLETED_REPORT_SCORE=$($payload.score)"
    Write-Output "COMPLETED_REPORT_RISK=$($payload.risk_label)"
    Write-Output "COMPLETED_REPORT_EVENT_COUNT=$($payload.events.Count)"
} catch {
    Write-Output "PROBE_ERROR=$($_.Exception.Message)"
    if ($_.Exception.Response) { Write-Output "PROBE_HTTP=$([int]$_.Exception.Response.StatusCode)" }
    exit 1
}
