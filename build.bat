rmdir dist /s /q
rmdir packages\com.vendor.product\data /s /q
pyinstaller main.py
copy dist\main\Qt5Core.dll dist\main\PyQt5\Qt\bin
mkdir packages\com.vendor.product\data\bin
mkdir packages\com.vendor.product\data\themes
mkdir packages\com.vendor.product\data\sources
mkdir packages\com.vendor.product\data\books
xcopy /E /Y dist\main\* packages\com.vendor.product\data\bin
xcopy /E /Y themes\* packages\com.vendor.product\data\themes
copy AppRun.bat packages\com.vendor.product\data
ren packages\com.vendor.product\data\bin\main.exe EbookCreator.exe
C:\Qt\Tools\QtInstallerFramework\3.0\bin\binarycreator -f -c config/config.xml -p packages EbookCreator-Windows-1.0.2.Setup