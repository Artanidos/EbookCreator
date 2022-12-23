function Component()
{
    // default constructor
}

Component.prototype.createOperations = function()
{
    component.createOperations();
    if (systemInfo.productType === "windows") {
        component.addOperation("CreateShortcut", "@TargetDir@/bin/main.exe", "@DesktopDir@/EbookCreator.lnk", "workingDirectory=@TargetDir@");
    }
}