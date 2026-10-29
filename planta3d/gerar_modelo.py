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
 # Acabamentos observados nas fotos atuais do quarto; dimensões continuam aproximadas.
 'roupa_cinza':mat('roupa_cama_cinza',(.52,.54,.56),0,.92),
 'branco_frio':mat('armario_quarto_branco',(.91,.91,.89),0,.48),
 'aluminio':mat('trilho_aluminio',(.52,.54,.55),.6,.30),
 'base_cama':mat('cama_marrom_escura',(.10,.075,.065),0,.78),
 'pixel_verde':mat('tecla_rgb_verde',(.04,.65,.22),0,.4),
 'pixel_azul':mat('tecla_rgb_azul',(.06,.21,.85),0,.4),
}

# Texturas compactas, geradas localmente e exportadas junto com o modelo OBJ.
# Não dependem de serviços externos e podem ser substituídas por fotos reais.
def texture(key, filename, fn):
    n=192
    image=bpy.data.images.new(filename, width=n, height=n, alpha=True)
    data=[]
    rng=random.Random(20)
    for y in range(n):
        for x in range(n):
            c=fn(x/n,y/n,rng)
            data.extend((max(0,min(1,c[0])),max(0,min(1,c[1])),max(0,min(1,c[2])),1.0))
    image.pixels.foreach_set(data)
    image.filepath_raw=os.path.join(OUT,filename)
    image.file_format='PNG'
    image.save()
    image.filepath='//'+filename
    nodes=M[key].node_tree.nodes
    tex=nodes.new('ShaderNodeTexImage'); tex.image=image
    M[key].node_tree.links.new(tex.outputs['Color'],nodes.get('Principled BSDF').inputs['Base Color'])

def wood(u,v,r):
    vein=0.5+0.5*math.sin(110*u+3*math.sin(v*12)+1.3*math.sin(v*36))
    noise=(r.random()-.5)*.03
    return (.21+.18*vein+noise,.085+.095*vein+noise,.038+.05*vein+noise)
def granite(u,v,r):
    n=r.random(); grain=.12 if n>.95 else (.04 if n>.78 else 0)
    return (.06+grain,.06+grain,.065+grain)
def blanket(u,v,r):
    band=0.025*math.sin(u*350)+0.02*math.sin(v*320)
    fold=0.06*math.sin(u*15+v*8)
    return (.32+band+fold,.43+band+fold,.20+band*.7+fold*.6)
def woven(u,v,r):
    detail=.025*(math.sin(u*500)+math.sin(v*500))+(r.random()-.5)*.02
    return (.58+detail,.56+detail,.51+detail)
for args in [('madeira','textura_madeira.png',wood),('granito','textura_granito.png',granite),
             ('setupcolcha','textura_coberta.png',blanket),('sofa','textura_sofa.png',woven)]:
    texture(*args)

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
def ring(name,xyz,major,minor,material,scale=(1,1,1),rot=(0,0,0)):
    bpy.ops.mesh.primitive_torus_add(major_radius=major,minor_radius=minor,major_segments=32,minor_segments=10,location=xyz,rotation=rot)
    o=bpy.context.object; o.name=name; o.scale=scale
    bpy.ops.object.transform_apply(location=False,rotation=False,scale=True)
    o.data.materials.append(M[material]); return o

def quilt(name,x,y,z,w,d,material,wrinkle=.018):
    # Superfície com pequenas dobras e UV próprio, para evitar uma colcha em bloco.
    nx,ny=16,24
    vertices=[]; faces=[]
    for j in range(ny+1):
        for i in range(nx+1):
            u=i/nx; v=j/ny
            h=wrinkle*(.45*math.sin(u*17+v*8)+.35*math.sin(v*24-u*3)+.2*math.sin(u*31+v*15))
            vertices.append((x+w*u,y+d*v,z+h))
    for j in range(ny):
        for i in range(nx):
            a=j*(nx+1)+i; faces.append((a,a+1,a+nx+2,a+nx+1))
    mesh=bpy.data.meshes.new(name); mesh.from_pydata(vertices,[],faces); mesh.update()
    o=bpy.data.objects.new(name,mesh); bpy.context.collection.objects.link(o); o.data.materials.append(M[material])
    uv=mesh.uv_layers.new(name='UVMap')
    for polygon in mesh.polygons:
        for li in polygon.loop_indices:
            vi=mesh.loops[li].vertex_index; uv.data[li].uv=((vi%(nx+1))/nx,(vi//(nx+1))/ny)
    for polygon in mesh.polygons: polygon.use_smooth=True
    solid=o.modifiers.new('espessura','SOLIDIFY'); solid.thickness=.012
    bpy.context.view_layer.objects.active=o; bpy.ops.object.modifier_apply(modifier='espessura')
    return o

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
wallx(0,3.30,0,window=(.25,1.40)); wallx(3.30,6.50,0,(5.55,6.35))
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
window_x('janela_setup',.25,0,1.15); window_x('janela_quarto',1.0,7.80,1.15)
window_x('janela_cozinha',4.25,7.80,1.45); window_y('janela_sala',6.50,3.2,1.2)
window_y('janela_banheiro',0,3.62,.6)
# Janela de alumínio e persiana horizontal do quarto fotografado.
box('janela_setup_vidro_escuro',.29,.012,.80,1.07,.02,.46,'teladesligada')
for z in [.84+i*.045 for i in range(10)]:
    box('janela_setup_persiana',.82,-.015,z,.56,.025,.018,'aluminio')
box('janela_setup_trilho_central',.815,-.028,.78,.035,.06,.50,'aluminio')
# Persiana da janela do outro quarto, com lâminas horizontais visíveis.
for z in [0.81+i*.055 for i in range(8)]:
    box('persiana_quarto',1.02,7.77,z,1.10,.025,.012,'moldura')

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
for i,y in enumerate((.86,1.34,1.82)):
    o=box('almofada',3.94,y,.56,.18,.30,.28,'mostarda' if i==1 else 'verdeagua',.075)
    o.rotation_euler.y=.14 if i==0 else -.10
for y in (1.03,1.61): box('costura_sofa',3.78,y,.536,.66,.009,.008,'creme')
quilt('manta_sofa',4.13,1.32,.56,.30,.72,'verde',.025)
for y in (1.42,1.55,1.68,1.81,1.94): box('xadrez_manta',4.14,y,.576,.28,.008,.006,'verdeagua')
# Mesa centro e estante da TV.
box('mesa_centro_base',4.63,1.00,.05,.48,.86,.38,'escuro')
box('mesa_centro_vidro',4.58,.95,.43,.58,.96,.035,'vidro',.01)
for x in (4.60,5.08):
    for y in (.97,1.85): box('perna_mesa_centro',x,y,.045,.035,.035,.37,'inox',.008)
box('painel_tv',6.35,.56,.03,.10,1.90,1.85,'madeira')
box('rack_tv',6.10,.58,.04,.26,1.86,.46,'creme',.015)
for y in [0.62+i*.045 for i in range(40)]: box('detalhe_canelado_rack',6.075,y,.08,.018,.016,.35,'moldura',.004)
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
for z in (.50,.83,1.16,1.49):
    for x in (5.35,5.52,5.69):
        cylinder('louca_cristaleira',(x,5.20,z+.045),.045,.09,'loucabranca',16)

# Cozinha e lavanderia: armários, bancada, eletrodomésticos.
box('geladeira',3.43,4.97,.03,.63,.64,1.72,'inox',.02)
box('porta_geladeira',3.41,4.99,.09,.025,.60,1.05,'inox')
box('geladeira_puxador',3.37,5.08,.75,.04,.05,.49,'escuro',.006)
box('armario_pia',3.43,5.72,.03,.60,1.05,.82,'taupe')
for y in (5.75,6.26):
    box('frente_armario_cozinha',4.032,y,.10,.018,.47,.68,'taupe',.006)
    box('puxador_armario_cozinha',4.055,y+.10,.69,.035,.25,.025,'inox',.007)
box('bancada_cozinha',3.39,5.69,.85,.67,1.11,.05,'granito')
box('cuba_cozinha',3.48,5.90,.901,.45,.55,.016,'inox',.035)
box('interior_cuba',3.52,5.94,.919,.37,.47,.006,'escuro',.045)
box('fundo_cuba',3.55,5.97,.922,.31,.41,.005,'inox',.04)
cylinder('torneira_cozinha',(3.47,6.10,1.03),.025,.25,'inox',12)
cylinder('bica_torneira',(3.57,6.10,1.14),.018,.21,'inox',12,(0,math.pi/2,0))
box('armario_aereo',3.42,5.75,1.45,.38,.98,.62,'taupe')
for yy in (5.78,6.25): box('porta_armario',3.40,yy,1.48,.03,.42,.56,'creme')
box('fogao_corpo',3.44,6.90,.03,.60,.55,.82,'loucabranca',.015)
box('fogao_tampo',3.43,6.89,.85,.62,.57,.04,'granito')
box('porta_forno',4.045,6.93,.18,.02,.45,.48,'escuro',.01)
box('puxador_forno',4.075,6.98,.69,.025,.36,.025,'inox',.006)
for xx in (3.58,3.89):
    for yy in (7.04,7.30): cylinder('boca_fogao',(xx,yy,.90),.075,.015,'escuro',16)
box('maquina_lavar',4.22,7.06,.03,.62,.61,.89,'loucabranca',.02)
cylinder('porta_maquina',(4.54,7.045,.53),.20,.025,'escuro',24,(math.pi/2,0,0))
cylinder('vidro_maquina',(4.54,7.025,.53),.145,.018,'vidro',24,(math.pi/2,0,0))
for x in (4.30,4.40,4.51): cylinder('botao_maquina',(x,7.035,.82),.018,.015,'escuro',12,(math.pi/2,0,0))
box('tanque',4.93,7.13,.03,.60,.55,.83,'loucabranca')
box('cuba_tanque',4.99,7.18,.86,.47,.42,.025,'inox')

# Banheiro: vaso, nichos, bancada e box.
sphere('vaso_base',(.35,4.05,.21),(.19,.23,.19),'loucabranca')
sphere('vaso_taça',(.35,3.99,.35),(.24,.30,.16),'loucabranca')
ring('vaso_assento',(.35,3.98,.47),.16,.025,'loucabranca',scale=(1.08,1.38,1))
sphere('agua_vaso',(.35,3.98,.465),(.12,.16,.008),'vidro')
box('vaso_caixa',.10,4.21,.35,.32,.18,.39,'loucabranca',.02)
for z in (.95,1.17,1.39): box('nicho_banheiro',.06,3.80,z,.20,.50,.08,'creme')
box('bancada_banheiro',.12,3.12,.76,.52,.48,.08,'granito')
box('cuba_banheiro',.16,3.16,.84,.40,.38,.12,'loucabranca',.04)
box('espelho_banheiro',.08,3.15,.97,.025,.40,.50,'inox')
box('piso_box',1.05,3.86,.035,.69,.80,.025,'creme')
box('vidro_box',1.04,3.86,.06,.025,.80,1.45,'vidro')
for y in (3.86,4.64): box('perfil_box',1.02,y,.06,.045,.035,1.45,'escuro')
# Faixas de rejunte sugerem os azulejos do banheiro, conforme o vídeo.
for z in (.30,.60,.90,1.20): box('rejunte_banheiro',.055,3.05,z,.008,1.68,.005,'rejunte')
for y in [3.15+i*.30 for i in range(6)]: box('rejunte_banheiro',.055,y,.06,.008,.005,1.22,'rejunte')
cylinder('chuveiro_haste',(.24,4.57,1.57),.018,.25,'inox',12)
sphere('chuveiro',(.24,4.57,1.46),(.10,.10,.04),'inox')

# Quarto do vídeo: cama, cabeceira, roupa de cama e guarda-roupa.
box('guarda_roupa_quarto_1',.12,5.11,.03,.53,2.35,2.08,'creme',.01)
for i in range(6):
    y=5.15+i*.375; box('porta_roupeiro_quarto_1',.65,y,.10,.018,.36,1.90,'moldura')
    box('puxador_roupeiro',.67,y+.29,1.0,.02,.025,.11,'inox')
box('cama_quarto_1',1.75,5.50,.03,1.40,1.85,.35,'madeira')
box('colchao_quarto_1',1.77,5.52,.38,1.36,1.81,.22,'colcha',.035)
quilt('coberta_quarto_1',1.78,5.55,.61,.98,1.75,'colcha',.025)
box('cabeceira_quarto_1',3.07,5.48,.03,.10,1.90,1.05,'madeira')
for y in (5.73,6.59): box('travesseiro_quarto_1',2.77,y,.63,.25,.56,.10,'vermelho',.04)

# Quarto: esquerda de quem entra corresponde à parede +X.
# As posições de paredes, porta e TV permanecem no lugar previamente aprovado.
# Guarda-roupa claro: duas portas largas de correr e perfis metálicos.
box('guarda_roupa_setup',2.70,.16,.03,.53,1.82,2.24,'branco_frio',.012)
for y in (.20,1.10):
    box('porta_de_correr',2.675,y,.08,.035,.87,2.13,'branco_frio',.008)
    box('perfil_vertical_porta',2.649,y+.015,.09,.025,.025,2.10,'aluminio')
for z in (.08,2.21):
    box('trilho_roupeiro',2.64,.18,z,.065,1.78,.035,'aluminio')

# Cama com base marrom-escura e roupa de cama cinza; objetos transitórios omitidos.
box('cama_setup_base',.18,.15,.03,1.40,1.95,.32,'base_cama',.035)
box('cama_setup_colchao',.20,.17,.35,1.36,1.91,.22,'roupa_cinza',.055)
quilt('cama_setup_coberta',.22,.48,.59,1.32,1.43,'roupa_cinza',.027)
for x in (.34,.96):
    box('travesseiro_setup',x,.25,.58,.49,.26,.11,'roupa_cinza',.065)

# Mesa e duas telas: a tela maior é central, a outra fica angulada à esquerda.
box('mesa_setup',1.06,2.31,.73,1.15,.57,.045,'escuro',.008)
for x in (1.10,2.12): box('perna_mesa_setup',x,2.35,.03,.05,.50,.70,'escuro')
for x,w,h in ((1.08,.46,.32),(1.58,.57,.38)):
    box('monitor_setup',x,2.67,.88,w,.045,h,'escuro',.01)
    box('tela_monitor',x+.012,2.655,.895,w-.024,.008,h-.03,'teladesligada')
    box('pe_monitor',x+w/2-.05,2.61,.77,.10,.12,.11,'escuro')
box('teclado',1.31,2.34,.785,.57,.18,.025,'escuro',.01)
for i in range(12):
    for j in range(3): box('tecla_rgb',1.33+i*.043,2.36+j*.045,.81,.033,.033,.008,'pixel_verde' if (i+j)%2 else 'pixel_azul',.003)
sphere('mouse',(1.98,2.40,.80),(.045,.075,.025),'escuro')
box('tapete_mouse',1.86,2.33,.78,.24,.22,.006,'tecido')
box('pc_gabinete',2.13,2.44,.78,.24,.40,.49,'escuro',.015)
box('lateral_vidro_pc',2.115,2.47,.82,.012,.30,.38,'vidro')
for z in (.88,1.02,1.16): cylinder('ventoinha_rgb',(2.105,2.53,z),.047,.02,'rgb',16,(0,math.pi/2,0))

# Armário aéreo na parede à direita da TV (perpendicular), com nichos abertos.
box('armario_aereo_quarto',2.91,1.96,1.84,.33,.90,.45,'branco_frio',.008)
for i in range(3):
    box('porta_armario_aereo_quarto',2.887,1.98+i*.29,1.86,.025,.28,.40,'branco_frio',.005)
box('nicho_quarto_tampo',2.88,2.03,1.40,.33,.82,.035,'branco_frio')
box('nicho_quarto_base',2.88,2.03,1.08,.33,.82,.035,'branco_frio')
for y in (2.03,2.44,2.83): box('nicho_quarto_divisoria',2.88,y,1.08,.33,.025,.35,'branco_frio')

# Pequena bancada lateral e impressora 3D com carretel, conforme a foto.
box('armario_impressora',2.32,2.04,.03,.46,.52,.63,'escuro',.012)
box('bancada_impressora',2.30,2.02,.66,.50,.55,.04,'branco_frio',.008)
box('impressora_base',2.34,2.08,.71,.38,.38,.045,'branco_frio')
for x in (2.36,2.68): box('impressora_coluna',x,2.34,.75,.035,.035,.42,'aluminio')
box('impressora_travessa',2.36,2.34,1.16,.35,.035,.035,'aluminio')
box('impressora_cabecote',2.48,2.28,.91,.10,.10,.10,'branco_frio',.005)
box('impressora_mesa',2.39,2.11,.79,.25,.22,.018,'escuro')
ring('carretel_impressora',(2.73,2.17,.94),.105,.022,'escuro',rot=(0,math.pi/2,0))

# Cadeira gamer preta; detalhes vermelhos da versão anterior não aparecem nas fotos.
box('cadeira_assento',1.72,1.83,.45,.48,.48,.12,'tecido',.08)
box('cadeira_encosto',1.72,1.85,.57,.48,.12,.68,'tecido',.07)
cylinder('cadeira_base',(1.96,2.07,.24),.04,.42,'escuro',12)
for dx,dy in ((-.22,-.16),(.22,-.16),(-.22,.16),(.22,.16)):
    cylinder('rodinha_cadeira',(1.96+dx,2.07+dy,.05),.045,.07,'escuro',12,(math.pi/2,0,0))
for x in (1.65,2.18):
    box('braco_cadeira',x,1.90,.66,.07,.38,.06,'tecido',.025)
    box('apoio_cadeira',x+.02,2.06,.50,.035,.04,.16,'escuro')
# A TV mantém posição, eixo e identificador para não quebrar iluminação e interação.
box('moldura_tv_quarto',1.20,2.86,1.38,.94,.075,.54,'escuro',.008)
box('obj_tv_quarto',1.23,2.84,1.41,.88,.025,.48,'teladesligada')

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
