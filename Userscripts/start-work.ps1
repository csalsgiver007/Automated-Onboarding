# --- Lumon Administrative Bridge v4.0 ---
# Optimized for Local Terminal (PowerShell 7 / VS Code)

$LEAD_GROUP_ID = "REDACTED"
$RG            = "rg-mdr-production"
$IMAGE         = "lumonregistry.azurecr.io/mdr-terminal:v12" 

Write-Host "`n[Lumon Infrastructure] Connecting..." -ForegroundColor Cyan

# 1. Identity Verification
try {
    $userContext = az ad signed-in-user show --query "{id:id, name:displayName}" -o json | ConvertFrom-Json
    $userObjectId = $userContext.id
    $currentUser  = $userContext.name
} catch {
    Write-Error "Failed to authenticate. Please run 'az login' as your refiner identity."
    exit
}

Write-Host "[Identity] Verifying permissions for $currentUser..." -ForegroundColor Cyan

# 2. Role Determination
$isLead = az ad group member check --group $LEAD_GROUP_ID --member-id $userObjectId --query value -o tsv
$ROLE = if ($isLead -eq "true") { "LEAD" } else { "WORKER" }

# 3. Retrieve Managed Identity Context (Hardened Fail-Safe Path)
# Bypasses Azure API lookup latency for newly created/synchronized security objects
$MSI_ID = "REDACTED"

# 4. Provisioning (Hardened Variable Handling)
$cleanName = $currentUser.Replace(" ","").ToLower()
$containerName = "mdr-session-$cleanName"

# Double check that we actually have a name before proceeding
if ([string]::IsNullOrWhiteSpace($containerName) -or $containerName -eq "mdr-session-") {
    Write-Error "Container name could not be determined. Check your 'az login' status."
    exit
}

Write-Host "[Provisioning] Initializing $ROLE terminal session for $containerName..." -ForegroundColor Green

# Create the container
az container create `
  --resource-group $RG `
  --name $containerName `
  --image $IMAGE `
  --os-type Linux `
  --cpu 1 --memory 1.5 `
  --vnet vnet-mdr --subnet prod `
  --restart-policy Never `
  --assign-identity $MSI_ID `
  --acr-identity $MSI_ID `
  --environment-variables LUMON_ROLE=$ROLE REFINER_NAME="$currentUser" > $null 

# Polling Logic with explicit variable reference
Write-Host "[Provisioning] Waiting for VNet attachment and pull..." -ForegroundColor Yellow
do {
    # We use -o tsv to ensure we get a clean string for comparison
    $status = az container show --resource-group $RG --name "$containerName" --query "provisioningState" -o tsv
    Write-Host "." -NoNewline
    Start-Sleep -Seconds 3
} while ($status -ne "Succeeded")

# 5. The Interactive Injection
Write-Host "`n[Lumon] Connecting to workstation terminal session..." -ForegroundColor Cyan
az container exec --resource-group $RG --name $containerName --exec-command "/bin/bash"

# 6. Post-Shift Decommissioning
Write-Host "`n[Lumon] Work shift ended. Decommissioning terminal..." -ForegroundColor Yellow

 az container delete --resource-group $RG --name $containerName --yes