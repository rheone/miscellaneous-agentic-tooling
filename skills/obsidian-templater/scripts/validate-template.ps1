<#
.SYNOPSIS
  Validates a Templater template file for syntax errors.
.DESCRIPTION
  Checks for balanced <% %> tags, unclosed commands, and unrecognized
  tp.* function names against a known API reference table.
.PARAMETER Path
  Path to the template .md file to validate.
.EXAMPLE
  .\validate-template.ps1 -Path "Templates\daily-note.md"
#>

param(
  [Parameter(Mandatory = $true)]
  [string]$Path
)

if (-not (Test-Path $Path)) {
  Write-Error "File not found: $Path"
  exit 1
}

$content = Get-Content -Path $Path -Raw
$errors = @()

# Known tp.* functions
$knownFunctions = @(
  'tp\.date\.now', 'tp\.date\.tomorrow', 'tp\.date\.yesterday', 'tp\.date\.weekday',
  'tp\.file\.content', 'tp\.file\.create_new', 'tp\.file\.creation_date',
  'tp\.file\.cursor', 'tp\.file\.cursor_append', 'tp\.file\.exists',
  'tp\.file\.find_tfile', 'tp\.file\.folder', 'tp\.file\.include',
  'tp\.file\.last_modified_date', 'tp\.file\.move', 'tp\.file\.path',
  'tp\.file\.rename', 'tp\.file\.selection', 'tp\.file\.tags', 'tp\.file\.title',
  'tp\.frontmatter', 'tp\.hooks\.on_all_templates_executed',
  'tp\.system\.clipboard', 'tp\.system\.prompt', 'tp\.system\.suggester',
  'tp\.system\.multi_suggester', 'tp\.web\.daily_quote', 'tp\.web\.random_picture',
  'tp\.web\.request', 'tp\.obsidian', 'tp\.app', 'tp\.config', 'tp\.user'
)

# Count open/close tags
$openCount = [regex]::Matches($content, '<%[\*\+\-]?').Count
$closeCount = [regex]::Matches($content, '%>').Count

if ($openCount -ne $closeCount) {
  $errors += "UNBALANCED TAGS: $openCount opening vs $closeCount closing tags"
}

# Find all tp.* function calls
$tpCalls = [regex]::Matches($content, 'tp\.\w+(?:\.\w+)*')

foreach ($call in $tpCalls) {
  $matched = $false
  foreach ($known in $knownFunctions) {
    if ($call.Value -match "^$known(\b|$)") {
      $matched = $true
      break
    }
  }
  if (-not $matched) {
    $errors += "UNKNOWN FUNCTION at line $((Get-Content $Path | Select-String $call.Value).LineNumber): $($call.Value)"
  }
}

# Check for unclosed tags (EOF while in a command)
$inTag = $false
$lines = Get-Content $Path
for ($i = 0; $i -lt $lines.Count; $i++) {
  $line = $lines[$i]
  if ($line -match '<%[\*\+\-]?') { $inTag = $true }
  if ($line -match '%>') { $inTag = $false }
  if ($inTag -and ($i -eq $lines.Count - 1)) {
    $errors += "UNCLOSED TAG reaches end of file"
  }
}

if ($errors.Count -eq 0) {
  Write-Host "OK: Template validated successfully ($openCount commands)" -ForegroundColor Green
  exit 0
} else {
  Write-Host "ISSUES FOUND ($($errors.Count)):" -ForegroundColor Yellow
  $errors | ForEach-Object { Write-Host "  $_" -ForegroundColor Red }
  exit 1
}
