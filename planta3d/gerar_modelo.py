import bpy, math, os, random
from mathutils import Vector

# Planta aproximada a partir da documentação e das referências fornecidas.
# Coordenadas em metros; X é esquerda/direita e Y segue da entrada para a cozinha.
OUT = os.path.dirname(os.path.abspath(__file__))
random.seed(3)
bpy.ops.object.select_all(action='SELECT'); bpy.ops.object.delete(use_global=False)
for m in bpy.data.materials: bpy.data.materials.remove(m)

def mat(name, color, metallic=0.0, rough=.7, alpha=1):
    m=bpy.data.materials.new(name); m.diffuse_color=(*color,alpha); m.use_nodes=True
    p=m.node_tree.nodes.get('Principled BSDF'); p.inputs['Base Color'].default_value=(*color,alpha)
    p.inputs['Roughness'].default_value=rough; p.inputs['Metallic'].default_value=metallic
    p.inputs['Alpha'].default_value=alpha
    if alpha<1: m.surface_render_method='DITHERED'
    return m

M={
 'piso':mat('ceramica_clara',(.72,.70,.65)), 'rejunte':mat('rejunte',(.46,.46,.44)),
 'parede':mat('parede_gelo',(.88,.88,.85)), 'moldura':mat('moldura_branca',(.94,.94,.91)),
 'porta':mat('porta_branca',(.89,.86,.81)), 'vidro':mat('vidro_fume',(.25,.31,.34),.05,.2,.55),
 'escuro':mat('metal_preto',(.025,.028,.035),.15,.38), 'inox':mat('inox',(.48,.52,.54),.65,.28),
 'madeira':mat('madeira_mogno',(.24,.09,.045),0,.48), 'madeira2':mat('madeira_clara',(.52,.36,.23)),
 'creme':mat('armario_creme',(.75,.71,.63)), 'taupe':mat('cozinha_taupe',(.43,.39,.35)),
 'granito':mat('granito_preto',(.07,.075,.08),.1,.3), 'loucabranca':mat('louca_branca',(.91,.91,.90),.05,.3),
 'sofa':mat('sofa_areia',(.63,.61,.56)), 'verde':mat('manta_verde',(.08,.22,.14)),
 'verdeagua':mat('almofada_verde_agua',(.23,.54,.43)), 'mostarda':mat('almofada_mostarda',(.75,.53,.13)),
 'colcha':mat('colcha_clara',(.78,.74,.71)), 'setupcolcha':mat('colcha_setup',(.45,.57,.26)),
 'vermelho':mat('vermelho',(.67,.055,.045)), 'planta':mat('folhagem',(.09,.29,.10)),
 'teladesligada':mat('tela_desligada',(.012,.018,.025),.05,.25), 'brilho':mat('luminaria',(.97,.94,.78),0,.3),
 'tecido':mat('tecido_cadeira',(.045,.045,.05)), 'rgb':mat('pc_rgb',(.22,.09,.62),.2,.25),
}

def cube(name, xyz, dims, material, bevel=0):
    bpy.ops.mesh.primitive_cube_add(size=1, location=xyz); o=bpy.context.object; o.name=name
    o.dimensions=dims; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(M[material]);
    if bevel:
        mod=o.modifiers.new('bordas','BEVEL'); mod.width=bevel; mod.segments=2
        bpy.context.view_layer.objects.active=o; bpy.ops.object.modifier_apply(modifier='bordas')
    return o
def box(name,x,y,z,dx,dy,dz,material,bevel=0): return cube(name,(x+dx/2,y+dy/2,z+dz/2),(dx,dy,dz),material,bevel)
def cylinder(name,xyz,r,depth,material,vertices=24,rot=None):
    bpy.ops.mesh.primitive_cylinder_add(vertices=vertices,radius=r,depth=depth,location=xyz,rotation=rot or (0,0,0))
    o=bpy.context.object; o.name=name; o.data.materials.append(M[material]); return o
def sphere(name,xyz,scale,material):
    bpy.ops.mesh.primitive_uv_sphere_add(segments=12,ring_count=6,location=xyz); o=bpy.context.object; o.name=name
    o.scale=scale; bpy.ops.object.transform_apply(location=False,rotation=False,scale=True); o.data.materials.append(M[material]); return o

# Lajes e cerâmica com linhas de rejunte discretas.
box('laje',0,0,-.09,6.50,7.80,.09,'parede')
box('piso_ceramico',0,0,0,6.50,7.80,.025,'piso')
for x in [i*.60 for i in range(1,11)]: box('junta_piso',x,0,.026,.006,7.80,.002,'rejunte')
for y in [i*.60 for i in range(1,13)]: box('junta_piso',0,y,.026,6.50,.006,.002,'rejunte')

# Paredes cortadas na altura de 1,30 m, com vãos nas portas e janelas.
# Algumas posições são estimadas e devem ser confirmadas por medidas/fotos.
H=1.30; T=.10
def wallx(x1,x2,y,door=None,window=None):
    spans=[(x1,x2)] if door is None else [(x1,door[0]),(door[1],x2)]
    for a,b in spans:
        if window and a<=window[0] and b>=window[1]:
            for c,d in ((a,window[0]),(window[1],b)):
                if d>c: box('parede',c,y-T/2,.025,d-c,T,H,'parede',.006)
            box('peitoril_parede',window[0],y-T/2,.025,window[1]-window[0],T,.735,'parede')
        elif b>a: box('parede',a,y-T/2,.025,b-a,T,H,'parede',.006)
def wally(x,y1,y2,door=None,window=None):
    spans=[(y1,y2)] if door is None else [(y1,door[0]),(door[1],y2)]
    for a,b in spans:
        if window and a<=window[0] and b>=window[1]:
            for c,d in ((a,window[0]),(window[1],b)):
                if d>c: box('parede',x-T/2,c,.025,T,d-c,H,'parede',.006)
            box('peitoril_parede',x-T/2,window[0],.025,T,window[1]-window[0],.735,'parede')
        elif b>a: box('parede',x-T/2,a,.025,T,b-a,H,'parede',.006)
wallx(0,3.30,0,window=(1.9,3.05)); wallx(3.30,6.50,0,(5.55,6.35))
wallx(0,1.80,3.00); wallx(1.80,3.30,3.00,(2.20,3.00))
wallx(0,3.30,4.80,(2.20,3.00))
wallx(0,3.30,7.80,window=(1.0,2.15)); wallx(3.30,6.50,7.80,window=(4.25,5.70))
wally(0,0,3); wally(0,3,4.8,window=(3.62,4.22)); wally(0,4.8,7.8)
wally(1.80,3,4.8,(3.48,4.28))
wally(3.30,0,3.00); wally(3.30,4.80,7.80); wally(6.50,0,7.80,window=(3.2,4.4))
# Divisória baixa entre a cozinha e a área da cristaleira.
box('meia_parede_cozinha',4.85,4.80,.025,.12,1.45,1.08,'parede',.006)

# Portas simbólicas, abaixo da altura de corte e com pequenas ferragens.
box('porta_entrada',5.58,.03,.03,.77,.045,1.24,'porta')
box('veda_porta',5.58,.012,.03,.77,.025,.04,'vermelho')
box('fechadura_entrada',5.68,.085,.92,.055,.035,.17,'escuro',.008)
box('porta_setup',2.23,3.02,.03,.74,.035,1.23,'porta')
box('porta_quarto_1',2.23,4.76,.03,.74,.035,1.23,'porta')
box('porta_banheiro',1.77,3.50,.03,.035,.74,1.23,'porta')

# Indicação de janelas no topo das paredes cortadas: montantes e vidro.
def window_x(name,x,y,w):
    box(name+'_vidro',x,y-.018,.80,w,.036,.48,'vidro')
    for xx in (x,x+w/2,x+w-.035): box(name+'_perfil',xx,y-.025,.76,.035,.05,.52,'moldura')
    box(name+'_peitoril',x,y-.03,.76,w,.06,.035,'moldura')
def window_y(name,x,y,w):
    box(name+'_vidro',x-.018,y,.80,.036,w,.48,'vidro')
    for yy in (y,y+w/2,y+w-.035): box(name+'_perfil',x-.025,yy,.76,.05,.035,.52,'moldura')
    box(name+'_peitoril',x-.03,y,.76,.06,w,.035,'moldura')
window_x('janela_setup',1.9,0,1.15); window_x('janela_quarto',1.0,7.80,1.15)
window_x('janela_cozinha',4.25,7.80,1.45); window_y('janela_sala',6.50,3.2,1.2)
window_y('janela_banheiro',0,3.62,.6)

# Sala: aparador, vaso e sofá com almofadas.
box('aparador_corpo',3.62,.12,.04,.85,.37,.72,'creme',.01)
box('aparador_tampo',3.60,.10,.76,.89,.41,.045,'vidro',.01)
box('espelho_sala',3.64,.075,.83,.78,.025,.42,'inox')
cylinder('vaso_rosas',(4.17,.28,.84),.07,.17,'loucabranca')
for i in range(6):
    xx=4.17+random.uniform(-.06,.06); yy=.28+random.uniform(-.05,.05)
    cylinder('caule',(xx,yy,1.02),.008,.25,'planta',8); sphere('rosa',(xx,yy,1.16),(.045,.045,.045),'vermelho')
box('sofa_base',3.72,.63,.06,.76,1.84,.29,'sofa',.06)
box('sofa_assento',3.78,.69,.35,.67,1.70,.19,'sofa',.06)
box('sofa_encosto',3.71,.63,.36,.20,1.84,.65,'sofa',.05)
for y in (.63,2.29): box('sofa_braco',3.72,y,.36,.76,.18,.32,'sofa',.04)
for i,y in enumerate((.86,1.34,1.82)): box('almofada',3.94,y,.56,.18,.30,.28,'mostarda' if i==1 else 'verdeagua',.045)
box('manta',4.15,1.34,.54,.27,.70,.025,'verde')
# Mesa centro e estante da TV.
box('mesa_centro_base',4.63,1.00,.05,.48,.86,.38,'escuro')
box('mesa_centro_vidro',4.58,.95,.43,.58,.96,.035,'vidro',.01)
box('painel_tv',6.35,.56,.03,.10,1.90,1.85,'madeira')
box('rack_tv',6.10,.58,.04,.26,1.86,.46,'creme',.015)
box('moldura_tv_sala',6.27,.80,.78,.075,1.28,.77,'escuro',.01)
box('obj_tv_sala',6.25,.83,.81,.025,1.22,.71,'teladesligada')
box('ps5_centro',6.12,.70,.53,.12,.26,.08,'escuro')
box('ps5_superior',6.11,.68,.62,.14,.30,.025,'moldura')
box('ps5_inferior',6.11,.68,.50,.14,.30,.025,'moldura')

# Sala de jantar e cristaleira.
box('mesa_jantar',5.08,3.40,.76,1.18,.88,.08,'madeira2',.02)
box('toalha_jantar',5.14,3.44,.84,1.06,.80,.012,'vermelho')
for x in (5.18,6.10):
    for y in (3.49,4.11): box('perna_mesa',x,y,.03,.07,.07,.73,'madeira')
for x,y in ((5.18,3.14),(5.76,3.14),(5.18,4.32),(5.76,4.32)):
    box('assento_cadeira',x,y,.43,.40,.37,.07,'madeira2',.015)
    for xx in (x+.03,x+.31):
        for yy in (y+.03,y+.28): box('perna_cadeira',xx,yy,.03,.05,.05,.40,'madeira')
    box('encosto_cadeira',x,y+.31,.50,.40,.06,.45,'madeira')
box('cristaleira',5.22,5.05,.04,.72,.40,1.75,'madeira2',.015)
box('cristaleira_frente',5.25,5.02,.35,.66,.025,1.35,'vidro')
for z in (.47,.80,1.13,1.46): box('cristaleira_prateleira',5.25,5.04,z,.66,.36,.025,'madeira')

# Cozinha e lavanderia: armários, bancada, eletrodomésticos.
box('geladeira',3.43,4.97,.03,.63,.64,1.72,'inox',.02)
box('porta_geladeira',3.41,4.99,.09,.025,.60,1.05,'inox')
box('geladeira_puxador',3.37,5.08,.75,.04,.05,.49,'escuro',.006)
box('armario_pia',3.43,5.72,.03,.60,1.05,.82,'taupe')
box('bancada_cozinha',3.39,5.69,.85,.67,1.11,.05,'granito')
box('cuba_cozinha',3.48,5.90,.90,.45,.55,.018,'inox')
cylinder('torneira_cozinha',(3.47,6.10,1.03),.025,.25,'inox',12)
box('armario_aereo',3.42,5.75,1.45,.38,.98,.62,'taupe')
for yy in (5.78,6.25): box('porta_armario',3.40,yy,1.48,.03,.42,.56,'creme')
box('fogao_corpo',3.44,6.90,.03,.60,.55,.82,'loucabranca',.015)
box('fogao_tampo',3.43,6.89,.85,.62,.57,.04,'granito')
for xx in (3.58,3.89):
    for yy in (7.04,7.30): cylinder('boca_fogao',(xx,yy,.90),.075,.015,'escuro',16)
box('maquina_lavar',4.22,7.06,.03,.62,.61,.89,'loucabranca',.02)
cylinder('porta_maquina',(4.54,7.045,.53),.20,.025,'escuro',24,(math.pi/2,0,0))
box('tanque',4.93,7.13,.03,.60,.55,.83,'loucabranca')
box('cuba_tanque',4.99,7.18,.86,.47,.42,.025,'inox')

# Banheiro: vaso, nichos, bancada e box.
box('vaso_base',.17,3.82,.03,.38,.52,.34,'loucabranca',.07)
box('vaso_assento',.19,3.78,.37,.34,.48,.06,'loucabranca',.05)
box('vaso_caixa',.10,4.21,.35,.32,.18,.39,'loucabranca',.02)
for z in (.95,1.17,1.39): box('nicho_banheiro',.06,3.80,z,.20,.50,.08,'creme')
box('bancada_banheiro',.12,3.12,.76,.52,.48,.08,'granito')
box('cuba_banheiro',.16,3.16,.84,.40,.38,.12,'loucabranca',.04)
box('espelho_banheiro',.08,3.15,.97,.025,.40,.50,'inox')
box('piso_box',1.05,3.86,.035,.69,.80,.025,'creme')
box('vidro_box',1.04,3.86,.06,.025,.80,1.45,'vidro')
for y in (3.86,4.64): box('perfil_box',1.02,y,.06,.045,.035,1.45,'escuro')

# Quarto do vídeo: cama, cabeceira, roupa de cama e guarda-roupa.
box('guarda_roupa_quarto_1',.12,5.11,.03,.53,2.35,2.08,'creme',.01)
for i in range(6):
    y=5.15+i*.375; box('porta_roupeiro_quarto_1',.65,y,.10,.018,.36,1.90,'moldura')
    box('puxador_roupeiro',.67,y+.29,1.0,.02,.025,.11,'inox')
box('cama_quarto_1',1.75,5.50,.03,1.40,1.85,.35,'madeira')
box('colchao_quarto_1',1.77,5.52,.38,1.36,1.81,.22,'colcha',.035)
box('coberta_quarto_1',1.78,5.55,.60,.98,1.75,.025,'colcha')
box('cabeceira_quarto_1',3.07,5.48,.03,.10,1.90,1.05,'madeira')
for y in (5.73,6.59): box('travesseiro_quarto_1',2.77,y,.63,.25,.56,.10,'vermelho',.04)

# Quarto setup: guarda-roupa à esquerda de quem entra, cama junto à janela.
box('guarda_roupa_setup',.12,.16,.03,.53,2.65,2.10,'creme',.01)
for i in range(5):
    y=.20+i*.51; box('porta_roupeiro_setup',.65,y,.10,.018,.49,1.90,'moldura')
    box('puxador_setup',.67,y+.40,1.01,.02,.025,.12,'inox')
box('cama_setup_base',1.72,.15,.03,1.40,1.95,.32,'creme')
box('cama_setup_colchao',1.74,.17,.35,1.36,1.91,.22,'colcha',.035)
box('cama_setup_coberta',1.76,.48,.57,1.32,1.43,.025,'setupcolcha')
box('cabeceira_setup',1.72,.10,.03,1.40,.08,.80,'madeira2')
for x in (1.90,2.52): box('travesseiro_setup',x,.25,.60,.49,.26,.11,'colcha',.035)
box('mesa_setup',1.06,2.36,.73,1.15,.52,.045,'escuro')
for x in (1.10,2.12): box('perna_mesa_setup',x,2.40,.03,.05,.44,.70,'escuro')
for x in (1.10,1.64):
    box('monitor_setup',x,2.68,.89,.48,.045,.32,'escuro',.01)
    box('pe_monitor',x+.19,2.61,.77,.10,.13,.12,'escuro')
box('pc_gabinete',2.13,2.48,.78,.24,.37,.48,'escuro',.015)
for z in (.86,1.00,1.14): cylinder('ventoinha_rgb',(2.14,2.53,z),.047,.02,'rgb',16,(0,math.pi/2,0))
box('cadeira_assento',1.44,1.80,.45,.48,.48,.12,'tecido',.05)
box('cadeira_encosto',1.44,1.82,.57,.48,.12,.68,'tecido',.05)
box('cadeira_detalhe',1.49,1.79,.73,.38,.025,.36,'vermelho')
cylinder('cadeira_base',(1.68,2.04,.24),.04,.42,'escuro',12)
box('moldura_tv_quarto',1.20,2.86,1.38,.94,.075,.54,'escuro',.008)
box('obj_tv_quarto',1.23,2.84,1.41,.88,.025,.48,'teladesligada')
cylinder('vaso_planta',(2.71,2.56,.20),.14,.35,'creme')
cylinder('tronco_planta',(2.71,2.56,.67),.025,.70,'madeira',10)
for i in range(15):
    angle=i*2.4; r=.13+(i%3)*.055
    sphere('folha_planta',(2.71+math.cos(angle)*r,2.56+math.sin(angle)*r,.90+(i%4)*.105),(.12,.07,.16),'planta')

# Luminárias visíveis e clicáveis; altura aproximada do teto preserva foco de luz.
for name,x,y in [('obj_luz_sala_1',5.28,1.78),('obj_luz_sala_2',5.42,3.55),('obj_luz_cozinha',4.35,6.30),('obj_luz_corredor',2.55,3.91),('obj_luz_quarto',1.65,1.43),('obj_luz_quarto_1',1.65,6.23)]:
    cylinder(name,(x,y,2.42),.13,.075,'brilho',24)

# Guarda uma versão editável com os móveis como objetos separados.
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,'apartamento_editavel.blend'))

# Junta peças decorativas por material para diminuir o número de objetos, preservando IDs do card.
protected={'obj_luz_sala_1','obj_luz_sala_2','obj_luz_cozinha','obj_luz_corredor','obj_luz_quarto','obj_luz_quarto_1','obj_tv_sala','obj_tv_quarto'}
for material in M.values():
    objs=[o for o in bpy.context.scene.objects if o.type=='MESH' and o.name not in protected and o.data.materials and o.data.materials[0]==material]
    if len(objs)>1:
        bpy.ops.object.select_all(action='DESELECT')
        for o in objs: o.select_set(True)
        bpy.context.view_layer.objects.active=objs[0]; bpy.ops.object.join(); objs[0].name='decor_'+material.name

# Exporta a geometria antes de criar luzes e câmera de prévia.
bpy.ops.wm.obj_export(filepath=os.path.join(OUT,'apartamento.obj'), export_materials=True, forward_axis='NEGATIVE_Z', up_axis='Y', export_selected_objects=False)
# O card pressupõe X/Z positivos para enquadrar o modelo corretamente.
# A exportação converte Y do Blender em Z negativo; transladar não altera formas.
obj_path=os.path.join(OUT,'apartamento.obj')
with open(obj_path,encoding='utf-8') as f: lines=f.readlines()
verts=[list(map(float,line.split()[1:4])) for line in lines if line.startswith('v ')]
min_x=min(v[0] for v in verts); min_z=min(v[2] for v in verts)
with open(obj_path,'w',encoding='utf-8') as f:
    for line in lines:
        if line.startswith('v '):
            x,y,z=map(float,line.split()[1:4]); line=f'v {x-min_x:.6f} {y:.6f} {z-min_z:.6f}\n'
        f.write(line)

# Render demonstrativo sem simulação dos estados do Home Assistant.
world=bpy.context.scene.world; world.color=(.34,.34,.34)
def area(name,loc,power,size):
    bpy.ops.object.light_add(type='AREA', location=loc); o=bpy.context.object; o.name=name; o.data.energy=power; o.data.shape='DISK'; o.data.size=size
    o.rotation_euler=(Vector((3.25,3.9,.3))-o.location).to_track_quat('-Z','Y').to_euler()
area('sol_preview',(2,-2,13),2300,8); area('suave_preview',(9,8,9),1200,7)
bpy.ops.object.camera_add(location=(11,-10,14)); cam=bpy.context.object
cam.rotation_euler=(Vector((3.2,3.9,.3))-cam.location).to_track_quat('-Z','Y').to_euler()
cam.data.type='ORTHO'; cam.data.ortho_scale=11.7
s=bpy.context.scene; s.camera=cam; s.render.engine='CYCLES'; s.cycles.samples=16; s.cycles.use_denoising=False
s.render.resolution_x=1200; s.render.resolution_y=1200; s.render.resolution_percentage=100
s.render.image_settings.file_format='PNG'; s.render.filepath=os.path.join(OUT,'previa_modelo.png')
s.world.color=(.24,.24,.24); s.view_settings.view_transform='AgX'
if os.environ.get('SKIP_RENDER') != '1':
    bpy.ops.render.render(write_still=True)
