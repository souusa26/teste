"""Gera imagens alinhadas da planta fixa a partir do Blender editável.

Execute: blender -b ../apartamento_editavel.blend -t 4 --python renderizar.py
As imagens por dispositivo são diferenças positivas para composição em screen.
"""
import bpy, math, os
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view

HERE = os.path.dirname(os.path.abspath(__file__))
s = bpy.context.scene
for o in list(s.objects):
    if o.type in {'CAMERA','LIGHT'}:
        bpy.data.objects.remove(o, do_unlink=True)
world = s.world or bpy.data.worlds.new('Ambiente'); s.world=world
world.use_nodes=True
background=world.node_tree.nodes.get('Background')
background.inputs['Color'].default_value=(0.64,0.70,0.83,1)
background.inputs['Strength'].default_value=.06

def light(name, loc, energy, size=0.1, color=(1,1,1), kind='POINT'):
    data=bpy.data.lights.new(name,kind); data.energy=energy; data.color=color
    if kind=='AREA': data.shape='DISK'; data.size=size
    else: data.shadow_soft_size=size
    ob=bpy.data.objects.new(name,data); s.collection.objects.link(ob); ob.location=loc
    return ob
area=light('Dia', (2,-2,13), 1800, 9, kind='AREA')
area.rotation_euler=(Vector((3.25,3.9,.3))-area.location).to_track_quat('-Z','Y').to_euler()
camera_data=bpy.data.cameras.new('Camera_planta_fixa'); cam=bpy.data.objects.new('Camera_planta_fixa',camera_data); s.collection.objects.link(cam)
cam.location=(-8,-10,14); cam.rotation_euler=(Vector((3.2,3.9,.3))-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.type='ORTHO'; cam.data.ortho_scale=11.7; s.camera=cam
s.render.engine='CYCLES'; s.cycles.samples=12; s.cycles.use_denoising=False
s.render.resolution_x=1000; s.render.resolution_y=1000; s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG'; s.render.film_transparent=True
s.view_settings.view_transform='Standard'; s.view_settings.look='Medium High Contrast'
s.render.image_settings.color_mode='RGBA'

# Desenhos de interface incorporados à tela, não fotografias de pessoas.
def material(name,color,energy=1.2):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,1); m.use_nodes=True
    n=m.node_tree.nodes.get('Principled BSDF'); n.inputs['Base Color'].default_value=(*color,1)
    n.inputs['Emission Color'].default_value=(*color,1); n.inputs['Emission Strength'].default_value=energy
    return m
colors=[material('interface_'+str(i),c) for i,c in enumerate([(0.02,.04,.10),(.16,.31,.52),(.65,.12,.10),(.20,.39,.25),(.45,.18,.48),(.90,.88,.76)])]
ui={'tv_sala':[], 'tv_quarto':[]}
def panel(name,center,scale,axis,mat):
    bpy.ops.mesh.primitive_cube_add(size=1,location=center); ob=bpy.context.object; ob.name=name
    ob.dimensions=scale; ob.data.materials.append(colors[mat]); ob.hide_render=True; ui[axis].append(ob)
    return ob
# Samsung: face virada para X negativo, mosaico horizontal sobre tela.
panel('samsung_fundo',(6.231,1.44,1.16),(.003,1.18,.67),'tv_sala',0)
for i in range(4):
    panel('samsung_miniatura',(6.227,.96+i*.25,1.21),(.004,.205,.25),'tv_sala',i%4+1)
    panel('samsung_app',(6.226,.97+i*.25,.96),(.004,.15,.07),'tv_sala',5 if i==0 else i%4+1)
# Roku: a interface acompanha a posição e a rotação da tela no modelo.
# Os deslocamentos e tamanhos abaixo estão nas coordenadas locais da tela.
tv_quarto = bpy.data.objects['obj_tv_quarto']
tv_matriz = tv_quarto.matrix_world.copy()
def painel_roku_local(nome, deslocamento, dimensoes, cor):
    posicao = tv_matriz @ Vector(deslocamento)
    objeto = panel(nome, posicao, dimensoes, 'tv_quarto', cor)
    objeto.rotation_euler = tv_matriz.to_quaternion().to_euler()
    return objeto
painel_roku_local('roku_fundo', (0, -.0345, 0), (.84,.003,.44), 4)
for i in range(4):
    painel_roku_local('roku_app', (-.30+i*.19, -.0385, .02), (.15,.004,.15), (i%4)+1)

devices={
 'luz_sala_1':('obj_luz_sala_1',(1,1,1),75),
 'luz_sala_2':('obj_luz_sala_2',(1,1,1),75),
 'luz_cozinha':('obj_luz_cozinha',(1,.72,.42),68),
 'luz_corredor':('obj_luz_corredor',(1,1,1),55),
 'luz_quarto':('obj_luz_quarto',(1,.72,.42),68),
 'luz_quarto_1':('obj_luz_quarto_1',(1,.72,.42),68),
 'tv_sala':('obj_tv_sala',(.12,.36,1),10),
 'tv_quarto':('obj_tv_quarto',(1,.32,.06),10),
}
lamps={}
for key,(name,color,energy) in devices.items():
    ob=bpy.data.objects[name]; loc=ob.location.copy()
    if key=='tv_sala': loc.x-=.12
    if key=='tv_quarto': loc += ob.matrix_world.to_3x3() @ Vector((0, -.12, 0))
    if not key.startswith('tv_'): loc.z-=.18
    lamp=light('emissao_'+key,loc,energy,.22,color); lamp.hide_render=True; lamps[key]=lamp

# Projeta pontos de interação para o picture-elements.
bpy.context.view_layer.update()
for key,(name,_,_) in devices.items():
    v=world_to_camera_view(s,cam,bpy.data.objects[name].location)
    print('HOTSPOT',key,round(v.x*100,2),round((1-v.y)*100,2),flush=True)

def render(name):
    s.render.filepath=os.path.join(HERE,name); bpy.ops.render.render(write_still=True)
area.hide_render=False; background.inputs['Strength'].default_value=.30; render('dia.png')
area.hide_render=True; background.inputs['Strength'].default_value=.07; render('noite.png')
for key,lamp in lamps.items():
    lamp.hide_render=False
    for ob in ui.get(key,[]): ob.hide_render=False
    render('_lit_'+key+'.png')
    lamp.hide_render=True
    for ob in ui.get(key,[]): ob.hide_render=True
