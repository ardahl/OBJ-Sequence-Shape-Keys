import bpy
import os
import glob
import re
from bpy_extras.io_utils import (
    ImportHelper,
    orientation_helper,
    axis_conversion)

#Pretty much all of the menu and setting stuff is copied from Stop Motion OBJ (https://github.com/neverhood311/Stop-motion-OBJ)

bl_info = {
    "name": "OBJ Shape Keys",
    "description": "Import a sequence of OBJ (or STL, PLY) files and convert them to an animation using shape keys.",
    "author": "Alex Dahl",
    "version": (1, 0, 0),
    "blender": (3, 2, 0),
    "location": "File > Import > OBJ Shape Keys",
    "category": "Import",
#    "doc_url": "",
#    "tracker_url": "",
    "warning": ""
}

def deselectAll():
    for ob in bpy.context.scene.objects:
        ob.select_set(state=False)
        
def alphanumKey(string):
    """ Turn a string into a list of string and number chunks
        "z23a" -> ["z", 23, "a"]
    """
    return [int(c) if c.isdigit() else c for c in re.split('([0-9]+)', string)]
        

class MeshImporter(bpy.types.PropertyGroup):
    #OBJ settings
    obj_global_scale: bpy.props.FloatProperty(
        name="Scale",
        soft_min=0.001,
        soft_max=1000.0,
        min=1e-6,
        max=1e6,
        default=1.0)
    obj_use_groups_as_vgroups: bpy.props.BoolProperty(name="Poly Groups", description="Import OBJ groups as vertex groups", default=False)
    obj_global_clamp_size: bpy.props.FloatProperty(
        name="Clamp Size",
        description="Clamp bounds under this value (zero to disable)",
        min=0.0,
        max=1000.0,
        soft_min=0.0,
        soft_max=1000.0,
        default=0.0)
    obj_use_split_objects: bpy.props.BoolProperty(name="Split By Object", description="Import each OBJ 'o' as a separate object", default=True)
    obj_use_split_groups: bpy.props.BoolProperty(name="Split By Group", description="Import each OBJ 'g' as a separate object", default=False)
    
    #STL settings
    stl_global_scale: bpy.props.FloatProperty(
        name="Scale",
        soft_min=0.001,
        soft_max=1000.0,
        min=1e-6,
        max=1e6,
        default=1.0)
    stl_use_scene_unit: bpy.props.BoolProperty(name="Scene Unit", description="Apply current scene's unit (as defined by unit scale) to imported data", default=False)
    stl_use_facet_normal: bpy.props.BoolProperty(name="Facet Normals", description="Use imported facet normals", default=False)
    
    #PLY settings
    ply_global_scale: bpy.props.FloatProperty(
        name="Scale",
        soft_min=0.001,
        soft_max=1000.0,
        min=1e-6,
        max=1e6,
        default=1.0)
    ply_use_scene_unit: bpy.props.BoolProperty(name="Scene Unit", description="Apply current scene's unit (as defined by unit scale) to imported data", default=False)
    
    #Shared settings
    axis_forward: bpy.props.StringProperty(name="Axis Forward", default="NEGATIVE_Z")
    axis_up: bpy.props.StringProperty(name="Axis Up", default="Y")
    
    def draw(self):
        pass
    
    def load(self, fileType, filePath):
        if fileType == 'obj':
            self.loadOBJ(filePath)
        elif fileType == 'stl':
            self.loadSTL(filePath)
        elif fileType == 'ply':
            self.loadPLY(filePath)
    
    def loadOBJ(self, filePath):
        if bpy.app.version >= (3, 2, 0):
            forward = self.axis_forward
            if forward[0] == '-':
                forward = 'NEGATIVE_'+forward[1:]
            up = self.axis_up
            if up[0] == '-':
                up = 'NEGATIVE_'+up[1:]
            bpy.ops.wm.obj_import(
                filepath=filePath,
                global_scale=self.obj_global_scale,
                clamp_size=self.obj_global_clamp_size,
                forward_axis=forward,
                up_axis=up,
                use_split_objects=self.obj_use_split_objects,
                use_split_groups=self.obj_use_split_groups,
                import_vertex_groups=self.obj_use_groups_as_vgroups)
                
    def loadSTL(self, filePath):
        if bpy.app.version >= (3, 2, 0):
            forward = self.axis_forward
            if forward[0] == '-':
                forward = 'NEGATIVE_'+forward[1:]
            up = self.axis_up
            if up[0] == '-':
                up = 'NEGATIVE_'+up[1:]
            bpy.ops.wm.stl_import(
                filepath=filePath,
                global_scale=self.stl_global_scale,
                use_scene_unit=self.stl_use_scene_unit,
                use_facet_normal=self.std_use_facet_normal,
                forward_axis=forward,
                up_axis=up)
            
    def loadPLY(self, filePath):
        if bpy.app.version >= (3, 2, 0):
            forward = self.axis_forward
            if forward[0] == '-':
                forward = 'NEGATIVE_'+forward[1:]
            up = self.axis_up
            if up[0] == '-':
                up = 'NEGATIVE_'+up[1:]
            bpy.ops.wm.ply_import(
                filepath=filePath,
                global_scale=self.ply_global_scale,
                use_scene_unit=self.ply_use_scene_unit,
                forward_axis=forward,
                up_axis=up)
    

class SequenceImportSettings(bpy.types.PropertyGroup):
    fileNamePrefix: bpy.props.StringProperty(name='File Name')
    fileFormat: bpy.props.EnumProperty(
        items = [('obj', 'OBJ', 'Wavefront OBJ'),
                 ('stl', 'STL', 'StereoLithography'),
                 ('ply', 'PLY', 'Stanford PLY')],
        name = 'File Format',
        default = 'obj')
        
        
def loadSequence(dir, file, fileExt, fileImporter):
    full_dir = bpy.path.abspath(dir)
    full_path = os.path.join(full_dir, file+'*.'+fileExt)
    unsorted_files = glob.glob(full_path)
    if len(unsorted_files) == 0:
        return (0, None)
    import_files = sorted(unsorted_files, key=alphanumKey)
    #setup progress
    wm = bpy.context.window_manager
    wm.progress_begin(0, 2*len(import_files))
    
    
    deselectAll()
    objSizes = []
    fileImporter.load(fileExt, import_files[0])
    baseObjs = bpy.context.selected_objects # get newly imported object
    count = 0
    for baseObj in  baseObjs:
        verts = baseObj.data.vertices # get vertices obj
        if len(verts) == 0:
            return (-1, "Imported object %d in %s has 0 vertices" % (count+1, import_files[0]))
        objSizes.append(len(verts))
        sk_basis = baseObj.shape_key_add(name='Basis', from_mix=False) # create base shape key
        sk_basis.interpolation = 'KEY_LINEAR'
        baseObj.data.shape_keys.use_relative = True
    import_files.pop(0) # remove first element

    deselectAll()
    #for each remaining file, import and create shape key
    frame = 1
    for f in import_files:
        #import object
        fileImporter.load(fileExt, f)
        frameObjs = bpy.context.selected_objects
        for ind, obj in enumerate(frameObjs):
            new_verts = obj.data.vertices
            if len(new_verts) == 0:
                return (-1, "Imported object %d in %s has 0 vertices" % (ind+1, f))
            if len(new_verts) != objSizes[ind]:
                return (-2, "Imported object %d in %s has difference vertex number (%d) than base object (%d)" % (ind+1, f, len(new_verts), objSizes[ind]))
            # create new shake key
            sk = baseObjs[ind].shape_key_add(name='Frame '+str(frame), from_mix=False)
            sk.interpolation = 'KEY_LINEAR'
            #for each vertex, update data in shape key
            for i in range(len(new_verts)):
                sk.data[i].co = new_verts[i].co
        #delete object
        deselectAll()
        for obj in frameObjs:
            obj.select_set(state=True)
        bpy.ops.object.delete()
        frame += 1
        wm.progress_update(frame)
    
    #add keyframes for shape keys for each frame
    for i in range(frame): # loop over each frame
        for obj in baseObjs:
            for j, sk in enumerate(obj.data.shape_keys.key_blocks): # for each shape key, need to set keyframe value
                if sk.name == 'Basis':
                    continue
                value = 0.0  #shape key evaluation amount (0.0 for inactive, 1.0 for active)
                if i == j:
                    value = 1.0
                sk.value = value
                sk.keyframe_insert('value', frame=i+1)
        wm.progress_update(frame+i)
    wm.progress_end()
    return (frame, baseObjs)


@orientation_helper(axis_forward='-Z', axis_up='Y')
class ImportObjShapeKeys(bpy.types.Operator, ImportHelper):
    """Load a mesh sequence as shape keys"""
    bl_idname = "objsk.import_sequence"
    bl_label = "Select Folder"
    bl_options = {'UNDO'}
    
    importSettings: bpy.props.PointerProperty(type=MeshImporter)
    sequenceSettings: bpy.props.PointerProperty(type=SequenceImportSettings)
    
    filter_glob: bpy.props.StringProperty(default="*.obj;*.mtl;*.stl;*.ply")
    directory: bpy.props.StringProperty(subtype='DIR_PATH')
    
    axis_forward: bpy.props.StringProperty(default='-Z')
    axis_up: bpy.props.StringProperty(default='Y')
    
    def resetToDefault(self):
        self.sequenceSettings.fileNamePrefix = ""
        self.filepath = ""
        self.axis_forward = "-Z"
        self.axis_up = "Y"
    
    def execute(self, context):
        #import first file as base
        if context.mode != 'OBJECT':
            self.report({'ERROR'}, "You may import only while in Object mode")
            return {'CANCELLED'}
        self.importSettings.axis_forward = self.axis_forward
        self.importSettings.axis_up = self.axis_up
        
        global_matrix = axis_conversion(from_forward=self.axis_forward, from_up=self.axis_up).to_4x4()
        
        #load sequence
        meshCount, seqObjs = loadSequence(self.directory, self.sequenceSettings.fileNamePrefix, self.sequenceSettings.fileFormat, self.importSettings)
        self.resetToDefault()
        if meshCount == 0:
            self.report({'ERROR'}, "No matching files found. Make sure the Root Folder, File Name, and File Format are correct.")
            return {'CANCELLED'}
        if meshCount < 0:
            #use the other return as the string, bit of a hack
            self.report({'ERROR'}, seqObjs)
            return {'CANCELLED'}
        
        for seqObj in seqObjs:
            seqObj.matrix_world = global_matrix
            #update name
            meshName = os.path.splitext(seqObj.name)[0].rstrip('._0123456789')
            seqObj.name = meshName + '_shapekeys'
        #set the frame to the start
        context.scene.frame_set(1)
        
        return {'FINISHED'}
    
    def draw(self, context):
        pass
        

class SKO_PT_FileImportSettingsPanel(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = 'File Settings'
    bl_parent_id = 'FILE_PT_operator'
    
    @classmethod
    def poll(cls, context):
        return context.space_data.active_operator.bl_idname == "OBJSK_OT_import_sequence"
    
    def draw(self, context):
        op  = context.space_data.active_operator
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        layout.row().prop(op.sequenceSettings, "fileFormat")
        
        if op.sequenceSettings.fileFormat == 'obj':
            layout.prop(op.importSettings, 'obj_global_scale')
            layout.prop(op.importSettings, 'obj_global_clamp_size')
            col = layout.column()
            col.prop(op.importSettings, 'obj_use_groups_as_vgroups')
            col.prop(op.importSettings, 'obj_use_split_objects')
            col.prop(op.importSettings, 'obj_use_split_groups')
        elif op.sequenceSettings.fileFormat == 'stl':
            layout.row().prop(op.importSettings, 'stl_global_scale')
            layout.row().prop(op.importSettings, 'stl_use_scene_unit')
            layout.row().prop(op.importSettings, 'stl_use_facet_normal')
        elif op.sequenceSettings.fileFormat == 'ply':
            layout.row().prop(op.importSettings, 'ply_global_scale')
            layout.row().prop(op.importSettings, 'ply_use_scene_unit')
    
    
class SKO_PT_TransformSettingsPanel(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = 'Transform'
    bl_parent_id = 'FILE_PT_operator'
    
    @classmethod
    def poll(cls, context):
        return context.space_data.active_operator.bl_idname == "OBJSK_OT_import_sequence"
    
    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        
        op = context.space_data.active_operator
        layout.prop(op, 'axis_forward')
        layout.prop(op, 'axis_up')
    

class SKO_PT_SequenceImportSettingsPanel(bpy.types.Panel):
    bl_space_type = 'FILE_BROWSER'
    bl_region_type = 'TOOL_PROPS'
    bl_label = 'Sequence Settings'
    bl_parent_id = 'FILE_PT_operator'
    
    @classmethod
    def poll(cls, context):
        return context.space_data.active_operator.bl_idname == "OBJSK_OT_import_sequence"
    
    def draw(self, context):
        op = context.space_data.active_operator
        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False
        col = layout.column(align=False)
        
        row = col.row()
        if op.sequenceSettings.fileNamePrefix == "":
            row.alert = True
        row.prop(op.sequenceSettings, 'fileNamePrefix')


def menu_func_import_sequence(self, context):
    self.layout.operator(ImportObjShapeKeys.bl_idname, text="Obj Shape Keys")


def register():
    bpy.utils.register_class(MeshImporter)
    #add option to import menu
    bpy.types.TOPBAR_MT_file_import.append(menu_func_import_sequence)
    #add in order to be drawn
    bpy.utils.register_class(SKO_PT_FileImportSettingsPanel)
    bpy.utils.register_class(SKO_PT_TransformSettingsPanel)
    bpy.utils.register_class(SKO_PT_SequenceImportSettingsPanel)
    bpy.utils.register_class(SequenceImportSettings)
    bpy.utils.register_class(ImportObjShapeKeys)

    
def unregister():
    bpy.utils.unregister_class(MeshImporter)
    bpy.types.TOPBAR_MT_file_import.remove(menu_func_import_sequence)
    bpy.utils.unregister_class(SKO_PT_FileImportSettingsPanel)
    bpy.utils.unregister_class(SKO_PT_TransformSettingsPanel)
    bpy.utils.unregister_class(SKO_PT_SequenceImportSettingsPanel)
    bpy.utils.unregister_class(SequenceImportSettings)
    bpy.utils.unregister_class(ImportObjShapeKeys)
    

if __name__ == '__main__':
    register()