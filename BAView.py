import bpy

from .BAOperator import BilingualAddonUtils as BAUtils
from .BAProperty import BilingualAddonPropGroup

class LocalePathList(bpy.types.UIList):
    def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index):
        custom_icon = 'FOLDER_REDIRECT'

        # Make sure your code supports all 3 layout types
        if self.layout_type in {'DEFAULT', 'COMPACT'}:
            layout.label(text=item.path, icon=custom_icon)
        elif self.layout_type in {'GRID'}:
            layout.alignment = 'CENTER'
            layout.label(text=item.path, icon=custom_icon)

class BilingualAddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    propGroup: bpy.props.PointerProperty(type=BilingualAddonPropGroup)

    def view(self, context):
        layout = self.layout

        layout.label(text="Select locale folder:")
        localePathCollection = self.propGroup.localePathCollection
        row = layout.row()
        col = row.column()
        col.template_list("LocalePathList", "", localePathCollection, "collection", localePathCollection, "index")
        col = row.column()
        row = col.row()
        col = row.column(align=True)
        col.scale_x = 1.0
        col.operator("operator.add_locale_path", text="", icon='ADD')
        col.operator("operator.remove_locale_path", text="", icon='REMOVE')
        col.separator()
        row = col.row()
        col = row.column(align=True)
        col.scale_x = 1.0
        col.operator("operator.refresh_locale_path", text="", icon='FILE_REFRESH')

        layout.label(text="1. Manage locale folder:")
        box = layout.box()
        localePath = self.propGroup.localePath
        row = box.row()
        row.enabled = False
        row.prop(localePath, "path")
        box.label(text=localePath.msg, icon=BAUtils.getIcon(localePath.msg))
        savePath = self.propGroup.savePath
        row = box.row()
        row.enabled = False
        row.prop(savePath, "path")
        box.label(text=savePath.msg, icon=BAUtils.getIcon(savePath.msg))
        split = box.split(factor=0.5, align=True)
        col = split.column(align=True)
        backup = self.propGroup.backup
        col.operator("operator.backup_languages", text="Backup")
        col.label(text=backup.msg, icon=BAUtils.getIcon(backup.msg))
        col = split.column(align=True)
        restore = self.propGroup.restore
        col.operator(restore.operator, text=restore.name)
        col.label(text=restore.msg, icon=BAUtils.getIcon(restore.msg))

        layout.label(text="2. Select the language 1 and 2, then click on the Generate:")
        box = layout.box()
        languageList1 = self.propGroup.languageList1
        box.prop(languageList1, "language")
        box.label(text=languageList1.msg, icon=BAUtils.getIcon(languageList1.msg))
        languageList2 = self.propGroup.languageList2
        box.prop(languageList2, "language")
        box.label(text=languageList2.msg, icon=BAUtils.getIcon(languageList2.msg))
        generate = self.propGroup.generate
        # box.operator("operator.make_bilingual_mo", text="Generate")
        box.operator("operator.make_bilingual_mo_asyn", text="Generate")
        box.label(text=generate.msg, icon=BAUtils.getIcon(generate.msg))

        layout.label(text="3. Select bilingual translation, then click on the Apply:")
        box = layout.box()
        bilingualCollection = self.propGroup.bilingualCollection
        for i, item in enumerate(bilingualCollection.collection):
            row = box.row()
            if item.name == "None":
                row.enabled = False
            row.prop(item, "checked", text=item.name)
        split = box.split(factor=0.333, align=True)
        col = split.column(align=True)
        col.operator("operator.update_collection", text="Update")
        col = split.column(align=True)
        col.operator("operator.delete_collection", text="Delete")
        col = split.column(align=True)
        col.operator("operator.apply_collection", text="Apply")
        box.label(text=bilingualCollection.msg, icon=BAUtils.getIcon(bilingualCollection.msg))

    def draw(self, context):
        layout = self.layout

        if bpy.context.preferences.addons[__package__].preferences is None:
            layout.label(text="preferences is None")
            msg = "[ERROR]: Preferences is None"
            layout.label(text=msg, icon=BAUtils.getIcon(msg))
        elif not bpy.app.build_options.international:
            msg = "[ERROR]: This version of Blender does not support internationalization!"
            layout.label(text=msg, icon=BAUtils.getIcon(msg))
        else:
            self.view(context)

BilingualAddonView = [
    LocalePathList,
    BilingualAddonPreferences,
]