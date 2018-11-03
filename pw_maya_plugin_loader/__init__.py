'''menuData
act={name:Plugin loader,action:show()}
'''
'''moduleInfo
Load unload plugin
'''

def show():
    from . import pluginLoader
    reload(pluginLoader)
    w = pluginLoader.pluginLoaderClass()
    w.show()
