## FreeCAD Modern-UI
An alternative take on the default FreeCAD UI

![AllMenus](https://user-images.githubusercontent.com/3831435/79070457-b0433580-7cde-11ea-834b-18b5560d7dfa.png)

Youtube Video: [FreeCAD Modern UI](http://www.youtube.com/watch?v=7ruU8Fnd07M)


## Status
Alpha

## Features
* Auto-hide/hidden docks
* (Collapsible) Ribbon menu
* small/large Ribbon menu icons 

## Installation
* Open **Tools** :arrow_forward: **Addon Manager**.
* Select **ModernUI** and click `Install/update selected`.  

* Restart FreeCAD.

## Uninstallation
* Go to ModernUI tab.
* Open **Tools** :arrow_forward: **Addon Manager**.
* Select **Modern UI** and click `Uninstall selected`.
* Restart FreeCAD.
* When you restarted you don't see any toolbar.
* Create a macro.
* Paste this code in to macro.

```
from PySide2 import QtCore, QtGui, QtWidgets
mw = FreeCADGui.getMainWindow()
mw.menuBar().show()

WBList = FreeCADGui.listWorkbenches()
for WB in WBList:
    FreeCADGui.activateWorkbench(WB)
    for tb in mw.findChildren(QtWidgets.QToolBar):
        tb.show()
```
* Execute it.
* Restart FreeCAD.

## Discussion
Feel free to discuss this addon on its [Modern UI](https://forum.freecadweb.org/viewtopic.php?f=34&t=44937)

## License
GPL v3.0 (see [LICENSE](LICENSE))
