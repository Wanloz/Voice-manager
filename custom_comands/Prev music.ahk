﻿#NoEnv  ; Recommended for performance and compatibility with future AutoHotkey releases.
; #Warn  ; Enable warnings to assist with detecting common errors.
SendMode Input  ; Recommended for new scripts due to its superior speed and reliability.
SetWorkingDir %A_ScriptDir%  ; Ensures a consistent starting directory.

Process, Exist, Y.Music.exe
If ErrorLevel = 0
{
; APP IS NOT RUNNING
}
Else
{
; APP IS RUNNING
;MsgBox, Already running
Run C:\Users\Super\AppData\Local\Programs\yaradio-yamusic\YaMusic.app.exe
sleep 100b
J::Send       {Media_Prev}
}
Returnl