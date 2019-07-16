rm -r dist/*
rm -r packages/com.vendor.product/data/*
pyinstaller main.py
mkdir packages/com.vendor.product/data/bin
mkdir packages/com.vendor.product/data/themes
mkdir packages/com.vendor.product/data/sources
mkdir packages/com.vendor.product/data/books
cp -r dist/main/* packages/com.vendor.product/data/bin
cp -r themes/* packages/com.vendor.product/data/themes
cp AppRun packages/com.vendor.product/data
mv packages/com.vendor.product/data/bin/main packages/com.vendor.product/data/bin/EbookCreator
/home/art/Qt/Tools/QtInstallerFramework/3.1/bin/binarycreator -f -c config/config.xml -p packages EbookCreator-Linux-1.0.2.Setup

