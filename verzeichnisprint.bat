@echo off
chcp 65001 > nul
set "AUSGABE_DATEI=verzeichnisstruktur.txt"

echo Erstelle Verzeichnisstruktur...
tree /F /A > "%AUSGABE_DATEI%"

echo Fertig! Die Struktur wurde in %AUSGABE_DATEI% gespeichert.
pause
