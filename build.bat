rmdir dist /s /q
rmdir packages\com.vendor.product\data /s /q
pyinstaller --windowed --icon=logo.ico main.py
copy dist\main\Qt5Core.dll dist\main\PyQt5\Qt\bin
mkdir packages\com.vendor.product\data\bin
mkdir packages\com.vendor.product\data\themes
mkdir packages\com.vendor.product\data\sources
mkdir packages\com.vendor.product\data\books
xcopy /E /Y dist\main\* packages\com.vendor.product\data\bin
xcopy /E /Y themes\* packages\com.vendor.product\data\themes
C:\Qt\Tools\QtInstallerFramework\4.5\bin\binarycreator -f -c config/config.xml -p packages EbookCreator-Windows-1.3.1.Setup