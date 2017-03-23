#    Addon info
bl_info = {
    'name': 'IKify',
    'author': 'Aman Gupta',
    'location': 'View3D',
    'category': 'Animation'
    }
    
if "bpy" in locals():
    import imp
    imp.reload(CreateBodyRigOperator)
    imp.reload(rigUI)
    imp.reload(utils)
    imp.reload(ikRig)
    imp.reload(fkRig)
    print("Reloaded multifiles")
else:
    from . import CreateBodyRigOperator, rigUI, utils, ikRig, fkRig
    print("Imported multifiles")

import bpy
from .rig_properties import add_properties
 
def register():
    bpy.utils.register_module(__name__)    
    add_properties()

def unregister():
    bpy.utils.register_module(__name__)

if __name__ == "__main__":
    register()