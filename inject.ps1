param(
    [Parameter(Position=0, Mandatory=$true)]
    [string]$Device,
    [Parameter(Position=1, Mandatory=$false)]
    [string]$Image,
    [Parameter(ValueFromRemainingArguments=$true)]
    [string[]]$RemainingArgs
)

$ErrorActionPreference = "Stop"

$env:PYTHONPATH = "$PWD;$PWD\injector;$env:PYTHONPATH"

$Cmd = @("injector\inject.py", $Device)
if ($Image) {
    $Cmd += $Image
}
if ($RemainingArgs) {
    $Cmd += $RemainingArgs
}

python @Cmd
