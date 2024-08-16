import os
import re
import subprocess
import sys
import importlib
import bpy
import shutil
import platform
import threading
import time

# from bl_i18n_utils import settings as settings_i18n
# from bl_i18n_utils import utils as utils_i18n
# from bl_i18n_utils import utils_languages_menu

class BilingualAddonUtils:
    def __init__(self) -> None:
        pass

    moRelativePath = os.path.join("{}", "LC_MESSAGES", "blender.mo")
    SYSTEM_WINDOWS = "Windows"
    SYSTEM_MACOS = "Darwin"
    SYSTEM_LINUX = "Linux"

    @staticmethod
    def getSystem():
        return platform.system()

    @staticmethod
    def importModule(module_name):
        def installModule(module_name):
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", module_name])
                return True
            except subprocess.CalledProcessError as e:
                print(f"[ERROR]: Failed to install {module_name}: {e}")
                try:
                    subprocess.check_call([sys.executable, "-m", "pip", "install", "-i", "https://pypi.tuna.tsinghua.edu.cn/simple", module_name])
                    return True
                except subprocess.CalledProcessError as e:
                    print(f"[ERROR]: Failed to install {module_name} from https://pypi.tuna.tsinghua.edu.cn/simple: {e}")
                    return False
                
        try:
            importlib.import_module(module_name)
            print(f"[ERROR]: Module {module_name} is already installed.")
        except ImportError:
            print(f"[ERROR]: Module {module_name} is not installed. Installing now...")
            installModule(module_name)

        try:    
            module = __import__(module_name)
            print(f"[SUCCESS]: {module_name} imported [SUCCESSfully.")
            return module
        except ImportError as e:
            print(f"[ERROR]: Failed to import {module_name}: {e}")
            return None
    
    @staticmethod
    def getLanguages(scene, context):
        propGroup = bpy.context.preferences.addons[__package__].preferences.propGroup
        folder_names = [("en", "en", "")]
        for dirs in os.listdir(propGroup.localePath.path):
            full_path = os.path.join(propGroup.localePath.path, BilingualAddonUtils.moRelativePath.format(dirs))
            if os.path.isfile(full_path):
                folder_names.append((dirs, dirs, ""))
        return folder_names
    
    @staticmethod
    def getBilingual():
        propGroup = bpy.context.preferences.addons[__package__].preferences.propGroup
        bilingualList = []
        for dirs in os.listdir(propGroup.savePath.path):
            dirPath = os.path.join(propGroup.savePath.path, dirs)
            filePath = os.path.join(propGroup.savePath.path, BilingualAddonUtils.moRelativePath.format(dirs))
            if os.path.isdir(dirPath) and os.path.isfile(filePath):
                bilingualList.append((dirs, dirPath, ""))
        if len(bilingualList) == 0:
            bilingualList.append(("None", "None", ""))
        return bilingualList

    @staticmethod
    def checkLanguageFile(self):
        file = os.path.join(self.localePath, BilingualAddonUtils.moRelativePath.format(self.language))
        if self.language.startswith("en"):
            return f"[SUCCESS]: '{self.language}' pass"
        elif not os.path.isfile(file):
            return f"[ERROR]: '{file}' not exists!"
        else:
            return f"[SUCCESS]: '{file}' exists"
    
    @staticmethod
    def getLocalePathList():
        localePathList = []
        searchPathList = []
        exclude = ["BLT_translation_Dicts", "scripts"]
        def findFolders(path, target):
            for item in os.listdir(path):
                if item in exclude:
                    continue
                item_path = os.path.join(path, item)
                if os.path.isdir(item_path):
                    if item == target:
                        localePathList.append(os.path.abspath(item_path))
                        # return item_path
                    else:
                        findFolders(item_path, target)
        
        if BilingualAddonUtils.getSystem() == BilingualAddonUtils.SYSTEM_WINDOWS:
            roaming_directory = os.environ['APPDATA']
            roaming_directory = os.path.join(roaming_directory, "Blender Foundation", "Blender")
            searchPathList.append(roaming_directory)
            blender_directory = bpy.app.binary_path
            blender_directory = os.path.dirname(os.path.dirname(blender_directory))
            searchPathList.append(blender_directory)
        elif BilingualAddonUtils.getSystem() == BilingualAddonUtils.SYSTEM_MACOS:
            user_directory = os.environ['HOME']
            user_directory = os.path.join(user_directory, "Library", "Application Support", "Blender")
            searchPathList.append(user_directory)
            blender_directory = bpy.app.binary_path
            blender_directory = os.path.dirname(os.path.dirname(blender_directory))
            searchPathList.append(blender_directory)
        
        for searchPath in searchPathList:
            findFolders(searchPath, "locale")
        return localePathList
    
    @staticmethod
    def getSavePath():
        currentPath = os.path.abspath(__file__)
        currentPath = os.path.dirname(currentPath)
        moPath = os.path.join(currentPath, "locale")
        if not os.path.exists(moPath):
            try:
                os.makedirs(moPath)
            except Exception as e:
                print(f"[ERROR]: Failed to create path '{moPath}': {e}")
        return moPath

    @staticmethod
    def getIcon(msg):
        if msg.startswith("[SUCCESS]"):
            return 'CHECKMARK'
        elif msg.startswith("[ERROR]"):
            return 'ERROR'
        else:
            return 'INFO'

class BilingualAddonLanguagesBackup(bpy.types.Operator):
    """Backup 'locale' folder as 'locale.bak'"""
    bl_idname = "operator.backup_languages"
    bl_label = "Make Bilingual Mo"

    @classmethod
    def poll(cls, context):
        propGroup = bpy.context.preferences.addons[__package__].preferences.propGroup
        return propGroup.backup.enable
    
    def execute(self, context):
        propGroup = bpy.context.preferences.addons[__package__].preferences.propGroup
        oriFolder = propGroup.localePath.path
        bakFolder = os.path.normpath(propGroup.localePath.path) + ".bak"
        try:
            shutil.copytree(oriFolder, bakFolder)
            propGroup.backup.msg = f"[SUCCESS]: 'Copy from {oriFolder} to {bakFolder}"
            self.report({'INFO'}, f"[SUCCESS]: 'Copy from {oriFolder} to {bakFolder}")
            return {'FINISHED'}
        except Exception as e:
            propGroup.backup.msg = f"[ERROR]: 'Copy from {oriFolder} to {bakFolder} failed: {e}!"
            self.report({'WARNING'}, f"[ERROR]: 'Copy from {oriFolder} to {bakFolder} failed: {e}!")
            return {'CANCELLED'}

class BilingualAddonLanguagesRestore(bpy.types.Operator):
    """Restore 'locale' using the 'locale.bak' folder."""
    bl_idname = "operator.restore_languages"
    bl_label = "Make Bilingual Mo"

    @classmethod
    def poll(cls, context):
        propGroup = bpy.context.preferences.addons[__package__].preferences.propGroup
        return propGroup.restore.enable
    
    def execute(self, context):
        propGroup = bpy.context.preferences.addons[__package__].preferences.propGroup
        oriFolder = propGroup.localePath.path
        bakFolder = os.path.normpath(propGroup.localePath.path) + ".bak"
        try:
            shutil.rmtree(oriFolder)
        except Exception as e:
            propGroup.restore.msg = f"[ERROR]: 'Remove {oriFolder} failed: {e}!"
            self.report({'WARNING'}, f"[ERROR]: 'Remove {oriFolder} failed: {e}!")
            return {'CANCELLED'}
        
        try:
            os.rename(bakFolder, oriFolder)
            propGroup.restore.msg = f"[SUCCESS]: 'Move from {bakFolder} to {oriFolder}"
            self.report({'INFO'}, f"[SUCCESS]: 'Move from {bakFolder} to {oriFolder}")
            return {'FINISHED'}
        except Exception as e:
            propGroup.restore.msg = f"[ERROR]: 'Move from {bakFolder} to {oriFolder} failed: {e}!"
            self.report({'WARNING'}, f"[ERROR]: 'Move from {bakFolder} to {oriFolder} failed: {e}!")
            return {'CANCELLED'}

class BilingualAddonMakeMo(bpy.types.Operator):
    """Make bilingual .mo file"""
    bl_idname = "operator.make_bilingual_mo"
    bl_label = "Make Bilingual Mo"
    
    polib = BilingualAddonUtils.importModule('polib')
    gettext = BilingualAddonUtils.importModule('gettext')

    def _openMo(self, language):
        propGroup = bpy.context.preferences.addons[__package__].preferences.propGroup
        moPath = os.path.join(propGroup.localePath.path, f"{language}", "LC_MESSAGES", "blender.mo")
        try:
            moFile = open(moPath, 'rb')
        except Exception as e:
            propGroup.generate.msg = f"[ERROR]: Failed to open '{moPath}': {e}!"
            return None
        
        try:
            mo = self.polib.mofile(moFile.name)
        except Exception as e:
            propGroup.generate.msg = f"[ERROR]: polib.mofile failed: {e}!"
            return None
        return mo

    def _writeMo(self, po):
        language = po.metadata['Language']
        propGroup = bpy.context.preferences.addons[__package__].preferences.propGroup
        currentPath = propGroup.savePath.path

        moPath = os.path.join(f"{currentPath}", BilingualAddonUtils.moRelativePath.format(language))
        moPath = os.path.dirname(moPath)
        poFile = os.path.join(moPath, "blender.po")
        moFile = os.path.join(moPath, "blender.mo")
        propGroup.generate.msg = f"[INFO]: Generating '{moFile}' ..."
        if not os.path.exists(moPath):
            try:
                os.makedirs(moPath)
            except Exception as e:
                propGroup.generate.msg = f"[ERROR]: Failed to create path '{moPath}': {e}"
                return False
        try:
            po.save(poFile)
            po.save_as_mofile(moFile)
            propGroup.generate.msg = f"[SUCCESS]: Generating '{moFile}' completed"
            return True
        except Exception as e:
            propGroup.generate.msg = f"[ERROR]: Generating '{moFile}' failed!"
            return True

    def _regularize(self, msg):
        pattern1 = r'%[+-]?[0-9]*\.?[0-9]*(h|l|ll|j|z|t|L)?[diouxXeEfgGaAcspnr]'
        pattern2 = r'\{[^{}]*\}'
        pattern = f"({pattern1})|({pattern2})"
        # msg = re.sub(pattern, lambda m: f'[{m.group(0)[1:]}]', msg)
        match = re.search(pattern, msg)
        return msg if match is None else None
    
    def _combiningStr(self, msg1, msg2):
        msg2 = self._regularize(msg2)
        if msg2 is None:
            return msg1
        
        if "\n" in msg1:
            msgstr = f"{msg1}\n{msg2}"
        else:
            msgstr = f"{msg1}·{msg2}"
        return msgstr

    def _combin(self):
        if self.l1En:
            mo1 = self._openMo(self.language2)
        else:
            mo1 = self._openMo(self.language1)

        if self.l2En:
            mo2 = self._openMo(self.language1)
        else:
            mo2 = self._openMo(self.language2)

        if mo1 is None or mo2 is None:
            return None

        if len(mo1) <= 0 or len(mo2) <= 0:
            self.propGroup.generate.msg = f"[ERROR]: The lengths of mo1 and mo2 cannot be 0!"
            return None
        
        try:
            po = self.polib.POFile()
        except Exception as e:
            self.propGroup.generate.msg = f"[ERROR]: Create po failed: {e}!"
            return None

        po.metadata = mo2.metadata
        if not self.l1En and not self.l2En:
            po.metadata["Last-Translator"] = mo1.metadata["Last-Translator"] + ' ' + mo2.metadata["Last-Translator"] 
            po.metadata["Language-Team"] = mo1.metadata["Language-Team"] + ' ' + mo2.metadata["Language-Team"] 
        po.metadata["Language"] = self.language1 + '@' + self.language2

        totalNum = len(mo1)
        progress = 0.0
        for index, entry1 in enumerate(mo1):
            newProgress = round(((index + 1) * 100.00) / totalNum, 2)
            if newProgress - progress >= 1.0:
                progress = newProgress
                self.propGroup.generate.msg = "[INFO]: Generating po files {:.2f}%".format(progress)

            if entry1.msgstr is None:
                continue          

            if self.l1En and not self.l2En:
                msg1 = entry1.msgid
                msg2 = entry1.msgstr
                new_msgstr = self._combiningStr(msg1, msg2)
            elif self.l2En and not self.l1En:
                msg1 = entry1.msgstr
                msg2 = entry1.msgid
                new_msgstr = self._combiningStr(msg1, msg2)
            else:
                msg1 = entry1.msgstr
                new_msgstr = msg1

                entry2 = mo2.find(entry1.msgid)
                if entry2 is not None:
                    msg2 = entry2.msgstr
                    new_msgstr = self._combiningStr(msg1, msg2)
            
            new_entry = self.polib.POEntry(
                msgctxt=entry1.msgctxt,
                msgid=entry1.msgid,
                msgstr=new_msgstr,
                occurrences=entry1.occurrences,
                comments=entry1.comment,
                tcomment=entry1.tcomment,
                flags=entry1.flags
            )
            po.append(new_entry)
        return po

    def execute(self, context):
        self.propGroup = bpy.context.preferences.addons[__package__].preferences.propGroup
        self.language1 = self.propGroup.languageList1.language
        self.language2 = self.propGroup.languageList2.language
        self.l1En = False
        self.l2En = False
        if self.language1 == "en" or self.language1 == "en_US":
            self.l1En = True
        if self.language2 == "en" or self.language2 == "en_US":
            self.l2En = True
        
        if self.polib is None:
            self.propGroup.generate.msg = f"[ERROR]: Failed to import polib!"
            return {'CANCELLED'}
                
        if self.language1 == self.language2:
            self.propGroup.generate.msg = f"[ERROR]: Language 1 and 2 cannot be the same!"
            return {'CANCELLED'}
        
        po = self._combin()

        if po is not None:
            self._writeMo(po)
            self.propGroup.bilingualCollection.update()
            return {'FINISHED'}
        else:
            return {'CANCELLED'}

class BilingualAddonBilingualCollectionUpdate(bpy.types.Operator):
    """Update bilingual list"""
    bl_idname = "operator.update_collection"
    bl_label = "Apply Bilingual Mo"

    def execute(self, context):
        propGroup = bpy.context.preferences.addons[__package__].preferences.propGroup
        propGroup.bilingualCollection.update()
        bilingualList = propGroup.bilingualCollection._getList()
        propGroup.bilingualCollection.msg = f"[SUCCESS]: Update {bilingualList}"
        return {'FINISHED'}
    
class BilingualAddonBilingualCollectionDelete(bpy.types.Operator):
    """Delete bilingual file"""
    bl_idname = "operator.delete_collection"
    bl_label = "Apply Bilingual Mo"

    def execute(self, context):
        propGroup = bpy.context.preferences.addons[__package__].preferences.propGroup
        checkList = propGroup.bilingualCollection._getCheck()
        for item in checkList:
            path = item[1]
            try:
                shutil.rmtree(path)
            except Exception as e:
                propGroup.bilingualCollection.msg = f"[ERROR]: 'Remove {path} failed: {e}!"
                return {'CANCELLED'}
        propGroup.bilingualCollection.msg = f"[SUCCESS]: Detele {[item[0] for item in checkList]}"
        propGroup.bilingualCollection.update()
        return {'FINISHED'}

class BilingualAddonBilingualCollectionApply(bpy.types.Operator):
    """Apply bilingual file"""
    bl_idname = "operator.apply_collection"
    bl_label = "Apply Bilingual Mo"

    @classmethod
    def poll(cls, context):
        propGroup = bpy.context.preferences.addons[__package__].preferences.propGroup
        return propGroup.bilingualCollection.applyEnable

    def execute(self, context):
        propGroup = bpy.context.preferences.addons[__package__].preferences.propGroup

        languagesPath = os.path.join(os.path.normpath(propGroup.localePath.path) + ".bak", "languages")
        coverPath = os.path.join(propGroup.localePath.path, "languages")
        
        try:
            shutil.copy(languagesPath, coverPath)
        except Exception as e:
            propGroup.bilingualCollection.msg = f"[ERROR]: 'Copy failed: {e}"
            return {'CANCELLED'}

        try:
            languagesFile = open(coverPath, "r+")
        except Exception as e:
            propGroup.bilingualCollection.msg = f"[ERROR]: 'Open {coverPath} failed: {e}!"
            return {'CANCELLED'}
        
        maxId = None
        pattern = r'^\s*(\d+):.*$'
        lines = languagesFile.readlines()
        for line in lines:
            match = re.match(pattern, line)
            if match:
                idStr = match.group(1)
                currentId = int(idStr)
                if maxId is None or currentId > maxId:
                    maxId = currentId

        languagesFile.seek(0, os.SEEK_END)
        languagesFile.write("\n#\n")
        languagesFile.write("0:Bilingual:\n")

        checkList = propGroup.bilingualCollection._getCheck()
        for item in checkList:
            maxId += 1
            name = item[0]
            savePath = os.path.join(propGroup.savePath.path, name)
            coverPath = os.path.join(propGroup.localePath.path, name)
            try:
                if os.path.exists(coverPath):
                    shutil.rmtree(coverPath)
                shutil.copytree(savePath, coverPath)
            except Exception as e:
                propGroup.bilingualCollection.msg = f"[ERROR]: Copy from {savePath} to {coverPath} failed: {e}!"
                self.report({'WARNING'}, f"[ERROR]: Copy from {savePath} to {coverPath} failed: {e}!")
                return {'CANCELLED'}
            languagesFile.write(f"{maxId}:{name} ({name}):{name}\n")
        languagesFile.close()
        propGroup.bilingualCollection.msg = f"[SUCCESS]: Apply {[item[0] for item in checkList]}"
        return {'FINISHED'}
    
class BilingualAddonLocalePathCollectionAdd(bpy.types.Operator):
    """Add a folder path to the list"""
    bl_idname = "operator.add_locale_path"
    bl_label = "Add Folder Path"

    directory: bpy.props.StringProperty(subtype='DIR_PATH')

    def execute(self, context):
        propGroup = bpy.context.preferences.addons[__package__].preferences.propGroup
        item = propGroup.localePathCollection.collection.add()
        item.path = self.directory
        return {'FINISHED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}

class BilingualAddonLocalePathCollectionRemove(bpy.types.Operator):
    """Remove an item from the list"""
    bl_idname = "operator.remove_locale_path"
    bl_label = "Remove the selected item"

    @classmethod
    def poll(cls, context):
        propGroup = bpy.context.preferences.addons[__package__].preferences.propGroup
        return propGroup.localePathCollection.collection

    def execute(self, context):
        propGroup = bpy.context.preferences.addons[__package__].preferences.propGroup
        propGroup.localePathCollection.collection.remove(propGroup.localePathCollection.index)
        return {'FINISHED'}
    
class BilingualAddonLocalePathCollectionRefresh(bpy.types.Operator):
    """Refresh the list with new data"""
    bl_idname = "operator.refresh_locale_path"
    bl_label = "Refresh"

    def execute(self, context):
        propGroup = bpy.context.preferences.addons[__package__].preferences.propGroup
        propGroup.localePathCollection.getDefault()
        return {'FINISHED'}

class BackgroundWorker(threading.Thread):
    def __init__(self, callback):
        super().__init__()
        self.callback = callback
        self.progress = 0
        self.polib = BilingualAddonUtils.importModule('polib')
        self.gettext = BilingualAddonUtils.importModule('gettext')
        self.propGroup = bpy.context.preferences.addons[__package__].preferences.propGroup

    def _openMo(self, language):
        moPath = os.path.join(self.propGroup.localePath.path, f"{language}", "LC_MESSAGES", "blender.mo")
        try:
            moFile = open(moPath, 'rb')
        except Exception as e:
            self.callback(f"[ERROR]: Failed to open '{moPath}': {e}!")
            return None
        
        try:
            mo = self.polib.mofile(moFile.name)
        except Exception as e:
            self.callback(f"[ERROR]: polib.mofile failed: {e}!")
            return None
        return mo

    def _writeMo(self, po):
        language = po.metadata['Language']
        currentPath = self.propGroup.savePath.path

        moPath = os.path.join(f"{currentPath}", BilingualAddonUtils.moRelativePath.format(language))
        moPath = os.path.dirname(moPath)
        poFile = os.path.join(moPath, "blender.po")
        moFile = os.path.join(moPath, "blender.mo")
        self.callback(f"[INFO]: Generating mo file...")
        if not os.path.exists(moPath):
            try:
                os.makedirs(moPath)
            except Exception as e:
                self.callback(f"[ERROR]: Failed to create path '{moPath}': {e}")
                return False
        try:
            # po.save(poFile)
            po.save_as_mofile(moFile)
            self.callback(f"[SUCCESS]: Generation Completed: '{moFile}'")
            return True
        except Exception as e:
            self.callback(f"[ERROR]: Generating '{moFile}' failed!")
            return True

    def _regularize(self, msg):
        pattern1 = r'%[+-]?[0-9]*\.?[0-9]*(h|l|ll|j|z|t|L)?[diouxXeEfgGaAcspnr]'
        pattern2 = r'\{[^{}]*\}'
        pattern = f"({pattern1})|({pattern2})"
        # msg = re.sub(pattern, lambda m: f'[{m.group(0)[1:]}]', msg)
        match = re.search(pattern, msg)
        return msg if match is None else None
    
    def _combiningStr(self, msg1, msg2):
        msg2 = self._regularize(msg2)
        if msg2 is None:
            return msg1
        
        if "\n" in msg1:
            msgstr = f"{msg1}\n{msg2}"
        else:
            msgstr = f"{msg1}·{msg2}"
        return msgstr

    def _combin(self):
        if self.l1En:
            mo1 = self._openMo(self.language2)
        else:
            mo1 = self._openMo(self.language1)

        if self.l2En:
            mo2 = self._openMo(self.language1)
        else:
            mo2 = self._openMo(self.language2)

        if mo1 is None or mo2 is None:
            return None

        if len(mo1) <= 0 or len(mo2) <= 0:
            self.callback(f"[ERROR]: The lengths of mo1 and mo2 cannot be 0!")
            return None
        
        try:
            po = self.polib.POFile()
        except Exception as e:
            self.callback(f"[ERROR]: Create po failed: {e}!")
            return None

        po.metadata = mo2.metadata
        if not self.l1En and not self.l2En:
            po.metadata["Last-Translator"] = mo1.metadata["Last-Translator"] + ' ' + mo2.metadata["Last-Translator"] 
            po.metadata["Language-Team"] = mo1.metadata["Language-Team"] + ' ' + mo2.metadata["Language-Team"] 
        po.metadata["Language"] = self.language1 + '@' + self.language2

        totalNum = len(mo1)
        progress = 0.0
        for index, entry1 in enumerate(mo1):
            newProgress = round(((index + 1) * 100.00) / totalNum, 2)
            if newProgress - progress >= 1.0:
                progress = newProgress
                self.callback("[INFO]: Generating po file {:.2f}%...".format(progress))

            if entry1.msgstr is None:
                continue          

            if self.l1En and not self.l2En:
                msg1 = entry1.msgid
                msg2 = entry1.msgstr
                new_msgstr = self._combiningStr(msg1, msg2)
            elif self.l2En and not self.l1En:
                msg1 = entry1.msgstr
                msg2 = entry1.msgid
                new_msgstr = self._combiningStr(msg1, msg2)
            else:
                msg1 = entry1.msgstr
                new_msgstr = msg1

                entry2 = mo2.find(entry1.msgid)
                if entry2 is not None:
                    msg2 = entry2.msgstr
                    new_msgstr = self._combiningStr(msg1, msg2)
            
            new_entry = self.polib.POEntry(
                msgctxt=entry1.msgctxt,
                msgid=entry1.msgid,
                msgstr=new_msgstr,
                occurrences=entry1.occurrences,
                comments=entry1.comment,
                tcomment=entry1.tcomment,
                flags=entry1.flags
            )
            po.append(new_entry)
        return po

    def run(self):
        self.language1 = self.propGroup.languageList1.language
        self.language2 = self.propGroup.languageList2.language
        self.l1En = False
        self.l2En = False
        if self.language1 == "en" or self.language1 == "en_US":
            self.l1En = True
        if self.language2 == "en" or self.language2 == "en_US":
            self.l2En = True
        
        if self.polib is None:
            self.callback(f"[ERROR]: Failed to import polib!")
            return {'CANCELLED'}
                
        if self.language1 == self.language2:
            self.callback(f"[ERROR]: Language 1 and 2 cannot be the same!")
            return {'CANCELLED'}
        
        po = self._combin()

        if po is not None:
            self._writeMo(po)
            self.propGroup.bilingualCollection.update()
            return {'FINISHED'}
        else:
            return {'CANCELLED'}

class BilingualAddonMakeMoAsyn(bpy.types.Operator):
    """Example asynchronous operator with progress update"""
    bl_idname = "operator.make_bilingual_mo_asyn"
    bl_label = "Make Bilingual Mo"

    _timer = None
    _worker = None
    msg = ""

    @classmethod
    def poll(cls, context):
        propGroup = bpy.context.preferences.addons[__package__].preferences.propGroup
        return propGroup.generate.enable

    def modal(self, context, event):
        if event.type == 'TIMER':
            propGroup = bpy.context.preferences.addons[__package__].preferences.propGroup
            if propGroup.generate.msg != self.msg:
                propGroup.generate.msg = self.msg
                print(f"BilingualAddonMakeMoAsyn: {self.msg}")
            if self._worker is not None and not self._worker.is_alive():
                bpy.context.window_manager.event_timer_remove(self._timer)
                propGroup.generate.enable = True
                return {'FINISHED'}
        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        self._timer = context.window_manager.event_timer_add(0.5, window=context.window)
        context.window_manager.modal_handler_add(self)

        self._worker = BackgroundWorker(self.callback)

        propGroup = bpy.context.preferences.addons[__package__].preferences.propGroup
        self._worker.start()
        propGroup.generate.enable = False
        self.msg = "[INFO]: Start Generation"

        return {'RUNNING_MODAL'}
    
    def callback(self, msg):
        self.msg = msg

BilingualAddonOperator = [
    BilingualAddonLanguagesBackup,
    BilingualAddonLanguagesRestore,
    BilingualAddonMakeMo,
    BilingualAddonMakeMoAsyn,
    BilingualAddonBilingualCollectionUpdate,
    BilingualAddonBilingualCollectionDelete,
    BilingualAddonBilingualCollectionApply,
    BilingualAddonLocalePathCollectionAdd,
    BilingualAddonLocalePathCollectionRemove,
    BilingualAddonLocalePathCollectionRefresh,
]