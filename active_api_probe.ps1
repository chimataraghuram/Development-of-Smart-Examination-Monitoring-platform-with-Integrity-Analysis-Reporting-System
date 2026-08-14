param(
    [Parameter(Mandatory = $true)][string]$Email,
    [Parameter(Mandatory = $true)][string]$Password
)

$ErrorActionPreference = 'Stop'

$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
$body = @{ email = $Email; password = $Password } | ConvertTo-Json -Compress

try {
    $login = Invoke-WebRequest -UseBasicParsing -Method Post -Uri 'http://127.0.0.1:5000/api/login' -ContentType 'application/json' -Body $body -WebSession $session
    Write-Output "LOGIN_HTTP=$($login.StatusCode)"

    $dashboard = Invoke-WebRequest -UseBasicParsing -Uri 'http://127.0.0.1:5000/api/dashboard/student' -WebSession $session
    Write-Output "DASHBOARD_HTTP=$($dashboard.StatusCode)"
    $dashboardPayload = $dashboard.Content | ConvertFrom-Json
    Write-Output "DASHBOARD_EXAM_RUNNING=$($dashboardPayload.exam_running)"
    Write-Output "DASHBOARD_INTEGRITY_SCORE=$($dashboardPayload.integrity_score)"

    $report = Invoke-WebRequest -UseBasicParsing -Uri 'http://127.0.0.1:5000/api/integrity_report' -WebSession $session
    Write-Output "REPORT_HTTP=$($report.StatusCode)"
    $reportPayload = $report.Content | ConvertFrom-Json
    Write-Output "REPORT_SCORE=$($reportPayload.score)"
    Write-Output "REPORT_RISK=$($reportPayload.risk_label)"
    Write-Output "REPORT_STARTED_AT=$($reportPayload.stats.started_at)"
    Write-Output "REPORT_ENDED_AT=$($reportPayload.stats.ended_at)"
    Write-Output "REPORT_EVENT_COUNT=$($reportPayload.events.Count)"
} catch {
    Write-Output "PROBE_ERROR=$($_.Exception.Message)"
    if ($_.Exception.Response) {
        Write-Output "PROBE_HTTP=$([int]$_.Exception.Response.StatusCode)"
    }
    exit 1
}
