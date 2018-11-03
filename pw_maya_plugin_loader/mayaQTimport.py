from pymel.core import *
import maya.OpenMayaUI as omui


#try import PyQt or PySide 1/2
qt_bind = None
try:
    import PyQt4
    from PyQt4.QtGui import *
    from PyQt4.QtCore import *
    from sip import wrapinstance as wrp
    qt_bind = 'pyqt'

    def getMayaWindow():
        ptr = omui.MQtUtil.mainWindow()
        if ptr is not None:
            return wrp(long(ptr), QObject)
except ImportError:
    try:
        from PySide.QtGui import *
        from PySide.QtCore import *
        from shiboken import wrapInstance as wrp
        qt_bind = 'pyside'

        def getMayaWindow():
            ptr = omui.MQtUtil.mainWindow()
            if ptr is not None:
                return wrp(long(ptr), QMainWindow)
    except ImportError:
        try:
            from PySide2.QtGui import *
            from PySide2.QtCore import *
            from PySide2.QtWidgets import *
            from shiboken2 import wrapInstance as wrp
            qt_bind = 'pyside2'

            def getMayaWindow():
                return ui.PyUI('MayaWindow').asQtObject()
        except ImportError:
            raise Exception('Qt binding not defined')

# if not qt:
#     cmds.error('NO PYQT or PYSIDE')
# elif qt ==1:
#     from PyQt4.QtGui import *
#     from PyQt4.QtCore import *
#     from sip import wrapinstance as wrp
#
#     def getMayaWindow():
#         ptr = omui.MQtUtil.mainWindow()
#         if ptr is not None:
#             return wrp(long(ptr), QObject)

# elif qt ==2:
#     from PySide.QtGui import *
#     from PySide.QtCore import *
#     from shiboken import wrapInstance as wrp
#     def getMayaWindow():
#         ptr = omui.MQtUtil.mainWindow()
#         if ptr is not None:
#             return wrp(long(ptr), QMainWindow)
# elif qt == 3
def qControl(mayaName, qobj=None):
    # if qt_bind == 'pyside2':
    #     return ui.PyUI(mayaName).asQtObject()
    if not qobj:
        qobj = QObject
    ptr = omui.MQtUtil.findControl(mayaName)
    if ptr is None:
        ptr = omui.MQtUtil.findLayout(mayaName)
    if ptr is None:
        ptr = omui.MQtUtil.findMenuItem(mayaName)
    return wrp(long(ptr), qobj)

qMaya = getMayaWindow()
qApp = QApplication.instance()
