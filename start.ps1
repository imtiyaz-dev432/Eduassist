# start.ps1
Write-Host "Starting EduAssist with OpenTelemetry Tracing..." -ForegroundColor Green

# Environment variables set karein
$env:OTEL_SERVICE_NAME="eduassist-flask"
$env:OTEL_EXPORTER_OTLP_ENDPOINT="http://127.0.0.1:4318"
$env:OTEL_EXPORTER_OTLP_PROTOCOL="http/protobuf"

# Virtual environment activate karein (agar activate nahi hai toh)
if (-not (Test-Path "Env:VIRTUAL_ENV")) {
    . .\.venv\Scripts\Activate.ps1
}

# App run karein
opentelemetry-instrument --traces_exporter otlp --metrics_exporter none python app.py