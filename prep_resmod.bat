@echo off
REM ModPack を入れた後の res_mods 使用準備用 batch file.
REM -----------------------------------------------------------------
set VER=0.9.19.1.2
REM -----------------------------------------------------------------
set Store=Y:\Games\World_of_Tanks_Mods
set RES=C:\Games\World_of_Tanks\res_mods
set MOD=%RES%\%VER%
set SZIP=D:\Program Files\7-Zip\7z.exe
set PACK=%Store%\res_mods.7z
set RMC=C:\Games\World_of_Tanks\res_mods\%VER%\scripts\client\gui\scaleform\daapi\view\battle
set LocalMODS=D:\Users\HRM.Delphinus\WoT\MODS
set SiteHome=%RES%\%VER%\gui\scaleform
set CHHome=%LocalMODS%\[CrossHair] J1mB0_s_Crosshair_Mod_v1.58\%Ver%\gui\scaleform
REM -----------------------------------------------------------------
REM Move to Drive C !
C:
REM -----------------------------------------------------------------
cd "%RES%"
mkdir configs\xvm
mkdir mods
REM
cd "%MOD%"
mkdir vehicles\american\Tracks
mkdir vehicles\french\Tracks
mkdir vehicles\german\Tracks
mkdir vehicles\russian\Tracks
mkdir gui\flash
mkdir gui\maps\icons\tankmen\icons\barracks
mkdir gui\maps\icons\tankmen\icons\big
mkdir gui\maps\icons\tankmen\icons\small
mkdir gui\scaleform
mkdir scripts\client\gui\mods
mklink /J "%RES%\LocalMODS" "%LocalMODS%"
REM -----------------------------------------------------------------
cd "%RES%"
"%SZIP%" x -wD:\var\spool\7z "%PACK%"
REM copy /Y "%Store%\RadialMenu.xml" "%RMC%"
REM copy /Y "%CHHome%\crosshair_panel_strategic.swf" "%SiteHome%"
REM copy /Y "%CHHome%\crosshair_sniper.swf" "%SiteHome%"
REM copy /Y "D:\Users\HRM.Delphinus\WoT\battleLoading.xc" "%RES%\configs\xvm\Aslain"
REM -----------------------------------------------------------------
REM All done. go back to home.
D:
REM pause
