; Auto-sync clipboard from UNC path
fileToWatch := "\\192.168.50.250\docker\aider\clipboard.txt"
lastModified := ""

SetTimer, CheckClipboardFile, 1000  ; Check every 1 second
return

CheckClipboardFile:
FileGetTime, currentModified, %fileToWatch%, M
if (currentModified != lastModified)
{
    lastModified := currentModified
    FileRead, clipboardContent, %fileToWatch%
    clipboard := clipboardContent
    ToolTip, 📋 Clipboard updated from Aider!
    SetTimer, RemoveTooltip, -1500
}
return

RemoveTooltip:
ToolTip
return
