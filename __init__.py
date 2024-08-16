# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTIBILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.

bl_info = {
    "name" : "Bilingual generator",
    "author" : "MagicalAs2O3",
    "description" : "Bilingual file generator",
    "blender" : (2, 80, 0),
    "version" : (1, 0, 0),
    "location" : "",
    "warning" : "",
    "category" : "TRANSLATE"
}

import bpy

from .BAView import BilingualAddonView
from .BAProperty import BilingualAddonPropGroup
from .BAOperator import BilingualAddonOperator

classes = [BilingualAddonPropGroup]

def register():
    for cls in BilingualAddonPropGroup.cls:
        print(f"regist {cls.__name__}")
        bpy.utils.register_class(cls)

    for cls in BilingualAddonOperator:
        print(f"regist {cls.__name__}")
        bpy.utils.register_class(cls)

    for cls in classes:
        print(f"regist {cls.__name__}")
        bpy.utils.register_class(cls)   

    for cls in BilingualAddonView:
        print(f"regist {cls.__name__}")
        bpy.utils.register_class(cls)   

    propGroup = bpy.context.preferences.addons[__package__].preferences.propGroup
    propGroup.bilingualCollection.update()
    propGroup.localePathCollection.getDefault()

def unregister():
    for cls in reversed(BilingualAddonPropGroup.cls):
        print(f"unregist {cls.__name__}")
        bpy.utils.unregister_class(cls)
    
    for cls in reversed(BilingualAddonOperator):
        print(f"unregist {cls.__name__}")
        bpy.utils.unregister_class(cls)

    for cls in reversed(classes):
        print(f"unregist {cls.__name__}")
        bpy.utils.unregister_class(cls)

    for cls in reversed(BilingualAddonView):
        print(f"unregist {cls.__name__}")
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()
