from mayaQTimport import *
from pymel.core import *
try:
    import pluginLoader_UIs as ui
except:
    import pluginLoader_UI as ui
reload(ui)
import os
import json

appData = os.getenv('APPDATA')
settingsFile = os.path.join(appData,'loadPluginSettings.json')
mel.source('pluginWin.mel')

class pluginLoaderClass(QMainWindow, ui.Ui_pluginLoader):
    def __init__(self):
        super(pluginLoaderClass, self).__init__(qMaya)
        self.setupUi(self)
        self.setObjectName('pluginLoaderWindow')
        self.setWindowTitle('Plug-in loader v1.5 | PaulWinex')
        self.executer, self.command_ted = self.getScriptEditor()
        self.scriptEditor_ly.addWidget(self.command_ted)
        self.eval_btn.setText('')
        self.eval_btn.setIcon(QIcon(':/executeAll.png'))
        ### settings
        self.settingsData = self.loadSettings()
        paletteLoaded = self.reload_btn.palette()
        paletteLoaded.setColor(QPalette.Button, QColor(60,90,70))
        paletteUnloaded = self.reload_btn.palette()
        paletteUnloaded.setColor(QPalette.Button, QColor(90,60,60))
        self.btnPalette = {'on':paletteLoaded, 'off':paletteUnloaded}
        ### variables
        self.plugin = ''
        self.scene = ''
        self.command = ''
        self.sceneHistory = []
        if self.settingsData:
            self.setPlugin(self.settingsData[0]['name'])
            if self.settingsData[0]['scenes']:
                self.setScene(self.settingsData[0]['scenes'][0])
            self.sceneHistory = self.settingsData[0]['scenes']
        else:
            self.setPlugin()
        ### connectcs
        self.sceneBrowse_btn.clicked.connect(self.browseScene)
        self.pluginBrowse_btn.clicked.connect(self.browsePlugin)
        self.load_btn.clicked.connect(self.loadPlugin)
        self.unload_btn.clicked.connect(self.unloadPlugin)
        self.reload_btn.clicked.connect(self.reloadPlugin)
        self.pluginRemove_btn.clicked.connect(self.removePlugin)
        self.sceneremove_btn.clicked.connect(self.removeScene)
        self.pluginPath_led.returnPressed.connect(self.checkPluginName)
        self.setCurrentScene_btn.clicked.connect(self.setCurrentScene)

        ### menu
        self.pluginPath_led.setContextMenuPolicy(Qt.CustomContextMenu)
        self.pluginPath_led.customContextMenuRequested.connect(self.pluginMenu)
        self.scenePath_led.setContextMenuPolicy(Qt.CustomContextMenu)
        self.scenePath_led.customContextMenuRequested.connect(self.sceneMenu)
        self.pluginInfo_btn.clicked.connect(self.showPluginInfo)
        #self.command_ted.textChanged.connect(self.commandChanged)
        #self.scenePath_led.editingFinished.connect(self.saveScene)
        self.eval_btn.clicked.connect(self.evalScript)
        self.openSettings_act.triggered.connect(self.openSettingsFile)


        ### start
        self.isLoaded()

    def closeEvent(self, event):
        self.commandChanged()
        self.saveLoaderState()
        event.accept()
        super(pluginLoaderClass, self).closeEvent(event)

    def evalScript(self):
        self.commandChanged()
        self.saveLoaderState()
        #cmd =str(self.command_ted.toPlainText())
        #print cmd
        #eval(cmd)
        cmds.cmdScrollFieldExecuter(self.executer, e=1, executeAll=1)

    def openSettingsFile(self, *args):
        #import subprocess
        #subprocess.Popen('notepad '+settingsFile)
        import webbrowser
        webbrowser.open(settingsFile)

    def commandChanged(self):
        self.command = str(self.command_ted.toPlainText())
        for plg in self.settingsData:
            if plg['name'] == self.plugin:
                plg['command'] = self.command
        #self.saveLoaderState()

    def browseScene(self):
        if self.scene:
            path = os.path.dirname(self.scene)
        else:
            path = ''
        path = QFileDialog.getOpenFileName(self, 'Open scene', path,"Maya scene (*.ma *.mb)")
        if path[0]:
            self.setScene(path[0])
            self.saveLoaderState()
            self.saveSettings()

    def browsePlugin(self):
        if self.plugin:
            path = os.path.dirname(self.plugin)
        else:
            path = os.environ['MAYA_PLUG_IN_PATH'].split(';')[0]
        path = QFileDialog.getOpenFileName(self, 'Open Plugin', path,"Maya Plugin (*.py *.mll)")
        if path[0]:
            self.setPlugin(path[0])

    def setScene(self, path=None):
        if path:
            self.scene = path
            self.scenePath_led.setText ( os.path.basename ( path ) )
        else:
            self.scene = ''
            self.scenePath_led.setText ('')
        self.saveLoaderState()

    def setPlugin(self, path=None):
        #self.blockSignals(True)
        if path and os.path.exists(path):
            self.commandChanged()
            self.plugin = path
            self.pluginPath_led.setText(os.path.basename(path))
            for plg in self.settingsData:
                if plg['name'] == path:
                    self.sceneHistory = plg['scenes']
                    if self.sceneHistory:
                        self.setScene(self.sceneHistory[0])
                    else:
                        self.scene = ''
                        self.scenePath_led.setText('')
                    self.setCommand(plg.get('command', ''))
                    return
            self.sceneHistory = []
            self.scene = ''
            self.setCommand('')
            self.scenePath_led.setText('')
            for btn in self.load_btn, self.unload_btn, self.reload_btn,self.pluginInfo_btn:
                btn.setEnabled(1)
        else:
            self.plugin = ''
            self.scene = ''
            self.command = ''
            self.sceneHistory = []
            self.scenePath_led.setText('')
            self.pluginPath_led.setText('')
            for btn in self.load_btn, self.unload_btn, self.reload_btn, self.pluginInfo_btn:
                btn.setEnabled(0)
        self.saveLoaderState()
        self.isLoaded()
        #self.blockSignals(False)

    def setCommand(self, cmd):
        self.command = cmd
        self.command_ted.setText(cmd)

    def checkSceneName(self):
        name = str(self.scenePath_led.text())
        if os.path.isabs(name) and os.path.exists(name):
            self.setScene(name)
            return True
        if self.scene:
            if not name == os.path.basename(self.scene):
                new = os.path.join(os.path.dirname(self.scene), name)
                if os.path.exists(new):
                    self.setScene(new)
                    return True
                else:
                    cmds.error('Scene not found')
                    return False
        return True

    def checkPluginName(self):
        name = str(self.pluginPath_led.text())
        if os.path.isabs(name) and os.path.exists(name):
            self.setPlugin(name)
            return True
        if not name == os.path.basename(self.plugin):
            new = os.path.join(os.path.dirname(self.plugin), name)
            if os.path.exists(new):
                self.setPlugin(new)
                return True
            else:
                self.setPlugin(self.plugin)
                cmds.error('Plugin not found')
                return False
        return True

    def showPluginInfo(self):
        if self.plugin:
            if os.path.exists(self.plugin):
                try:
                    mel.displayPluginInfo(self.plugin)
                except:
                    warning('Error open info, try to load plugin before')

    def loadPlugin(self):
        if self.checkPluginName():
            if os.path.exists(self.plugin):
                cmds.loadPlugin(self.plugin)
            self.isLoaded()
            self.loadScene()

    def loadScene(self):
        if self.loadScene_cbx.isChecked():
            if os.path.exists(self.scene):
                cmds.file(self.scene,o=1,f=1)

    def unloadPlugin(self):
        self.unloadScene()
        pluginName = os.path.splitext(os.path.basename(self.plugin))[0]
        if  cmds.pluginInfo(pluginName,q=1,l=1):
            cmds.unloadPlugin(pluginName)
        self.isLoaded()

    def unloadScene(self):
        cmds.file(new=1,f=1)

    def reloadPlugin(self):
        self.unloadPlugin()
        self.loadPlugin()

    def isLoaded(self):
        pluginName = os.path.splitext(os.path.basename(self.plugin))[0]
        if  cmds.pluginInfo(pluginName,q=1,l=1):
            self.statusbar.showMessage('LOADED')
            for btn in self.load_btn, self.unload_btn, self.reload_btn:
                btn.setPalette(self.btnPalette['on'])
                btn.setAutoFillBackground(True)
            self.pluginInfo_btn.setEnabled(1)
        else:
            for btn in self.load_btn, self.unload_btn, self.reload_btn:
                btn.setPalette(self.btnPalette['off'])
                btn.setAutoFillBackground(True)
            self.pluginInfo_btn.setEnabled(0)
            self.statusbar.showMessage('UNLOADED')

    def loadSettings(self):
        if os.path.exists(settingsFile):
            data = json.load(open(settingsFile, 'r'))
            result =[]
            for plug in data:
                if os.path.exists(plug['name']):
                    result.append(plug)
            return result
        else:
            return []

    def saveSettings(self):
        for s in self.settingsData:
            s['name'] = self.normPath(s['name'])
            s['scenes'] = [self.normPath(x) for x in s['scenes']]
        json.dump(self.settingsData, open(settingsFile, 'w'), indent=4)

    def normPath(self, path):
        return path.replace('\\','/').replace('//','/')

    def saveLoaderState(self):
        if self.plugin:
            if os.path.exists(self.plugin):
                if not self.plugin in [x['name'] for x in self.settingsData]: #new plugin
                    plg = {'name':self.plugin}
                    if self.scene:
                        plg['scenes'] = [self.scene]
                    else:
                        plg['scenes'] = []
                    #plg['command'] = self.command
                    self.sceneHistory = plg['scenes']
                    self.settingsData.insert(0,plg)
                else:
                    if self.scene:
                        for plg in self.settingsData:
                            if plg['name'] == self.plugin:
                                if self.scene in plg['scenes']:
                                    plg['scenes'].remove(self.scene)
                                plg['scenes'].insert(0, self.scene)
                                self.sceneHistory = plg['scenes']
                                break
                    #for plg in self.settingsData:
                    #        if plg['name'] == self.plugin:
                                #plg['command'] = self.command
        self.saveSettings()

    def removePlugin(self):
        self.unloadPlugin()
        for plg in self.settingsData:
            if plg['name'] == self.plugin:
                self.settingsData.remove(plg)
        if self.settingsData:
            self.setPlugin(self.settingsData[0]['name'])
        else:
            self.setPlugin()

    def removeScene(self):
        for plg in self.settingsData:
            if plg['name'] == self.plugin:
                if self.scene in plg['scenes']:
                    plg['scenes'].remove(self.scene)
                if plg['scenes']:
                    self.setScene(plg['scenes'][0])
                else:
                    self.setScene()

    def pluginMenu(self):
        menu = QMenu(self)
        if self.settingsData:
            for plug in self.settingsData:
                path = plug['name']
                scenes = plug['scenes']
                act = QAction(path, self)
                act.setData(scenes)
                menu.addAction(act)

            a = menu.exec_(QCursor().pos())
            if a:
                self.setPlugin(a.text())
                self.sceneHistory = a.data()
                if self.sceneHistory:
                    self.setScene(self.sceneHistory[0])
                self.isLoaded()
        else:
            act = QAction('Empty', self)
            act.setEnabled(0)
            menu.addAction(act)
            menu.exec_(QCursor().pos())

    def sceneMenu(self):
        menu = QMenu(self)
        if self.sceneHistory:
            for s in self.sceneHistory:
                act = QAction(s, self)
                menu.addAction(act)
            a = menu.exec_(QCursor().pos())
            if a:
                scene = a.text()
                self.setScene(scene)
        else:
            act = QAction('Empty', self)
            act.setEnabled(0)
            menu.addAction(act)
            menu.exec_(QCursor().pos())

    def setCurrentScene(self):
        if self.plugin:
            scene = cmds.file(q=1, sn=1)
            if scene:
                self.setScene(scene)

    def getScriptEditor(self):
        cmds.window()
        cmds.columnLayout()
        executer = cmds.cmdScrollFieldExecuter(sourceType="python",commandCompletion=False,showTooltipHelp=False)
        qtObj = qControl(executer, QTextEdit)
        return executer, qtObj