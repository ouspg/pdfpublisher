# -----------------------------------------------
# INITIAL DRAFT FOR POWERPOINT 2 PDF TRANSFORMATION
# FOR WINDOWS-BASED SYSTEMS WITH POWERSHELL ENABLED
# INITIAL CODE VERSION FROM COPILOT WITH SMALL MANUAL CHANGES.
# TO BE (RE)STARTED MANUALLY OR BY TASK MANAGER
# -----------------------------------------------

# -----------------------------------------------
# READ TARGET FOLDERS FROM THE PDFPUBLISHER SETTINGS.INI
# -----------------------------------------------
$iniPath = "settings.ini"

# --- Check 1: Does the file exist? ---
if (-not (Test-Path $iniPath)) {
    Write-Error "settings.ini not found at: $iniPath. Aborting script."
    exit 1
}

# Read all lines
$lines = Get-Content $iniPath

# Keys we care about
$keys = @("lecture_slides_dir", "course_slides_dir")

# Extract directories
$folders = foreach ($line in $lines) {
    foreach ($key in $keys) {
        if ($line -match "^\s*$key\s*=\s*(.+)$") {
            $matches[1].Trim()
        }
    }
}

# Remove empty entries
$folders = $folders | Where-Object { $_ -and $_.Trim() -ne "" }

# --- Check 2: Did we find any folders? ---
if ($folders.Count -eq 0) {
    Write-Error "No valid folder paths found in settings.ini. Please add course_slides_dir and lecture_slides_dir keys for directories to monitor. Aborting script."
    exit 1
}

Write-Host "Monitoring the following folders:"
$folders


# -----------------------------------------------
# CONFIGURATION
# -----------------------------------------------
# Sleep time between loops (in seconds)
$sleepSeconds = 300   # 5 minutes


# -----------------------------------------------
# MAIN LOOP
# -----------------------------------------------

Write-Host "Starting PPTX → PDF monitor..."

while ($true) {

    Write-Host "Scanning folders at $(Get-Date)..."

    # Start PowerPoint once per loop for efficiency
    $ppApp = New-Object -ComObject PowerPoint.Application
    $ppApp.Visible = $false

    foreach ($folder in $folders) {
        if (-not (Test-Path $folder)) {
            Write-Warning "Folder not found: $folder"
            continue
        }
        Write-Host "Scanning folder ${$folder}..."

        # Get all PPTX files in the folder (non-recursive)
        $pptxFiles = Get-ChildItem -Path $folder -Filter *.pptx -File

        foreach ($pptx in $pptxFiles) {

            $pdf = [System.IO.Path]::ChangeExtension($pptx.FullName, ".pdf")

            $needsUpdate = $false

            if (-not (Test-Path $pdf)) {
                # PDF does not exist → must create
                $needsUpdate = $true
            }
            else {
                # Compare timestamps
                $pptTime = (Get-Item $pptx.FullName).LastWriteTime
                $pdfTime = (Get-Item $pdf).LastWriteTime

                if ($pptTime -gt $pdfTime) {
                    $needsUpdate = $true
                }
            }

            if ($needsUpdate) {
                Write-Host "Updating PDF for: $($pptx.Name)"

                try {
                    $presentation = $ppApp.Presentations.Open($pptx.FullName, $false, $false, $false)
                    $presentation.SaveAs($pdf, 32)   # 32 = PDF
                    $presentation.Close()
                }
                catch {
                    Write-Error "Failed to convert $($pptx.FullName): $_"
                }
            }
        }
    }

    # Close PowerPoint for this loop
    $ppApp.Quit()

    Write-Host "Sleeping for $sleepSeconds seconds..."
    Start-Sleep -Seconds $sleepSeconds
}
