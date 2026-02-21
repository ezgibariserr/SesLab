tell application "Finder"
    set currentPath to POSIX path of (container of (path to me) as text)
    set desktopPath to POSIX path of (path to desktop folder)
    
    -- Masaüstüne kısayol oluştur
    make new alias file at desktop to (POSIX file (currentPath & "launch_seslab.command"))
    set name of result to "SesLab"
end tell 