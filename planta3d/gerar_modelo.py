import bpy, math, os, random
from mathutils import Vector, Matrix

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
 'painel_caramelo':mat('painel_tv_caramelo',(.48,.28,.14),0,.48),
 'espelhado':mat('vidro_espelhado',(.53,.57,.58),.85,.12),
 'dourado':mat('metal_dourado',(.59,.41,.16),.7,.25),
 'turquesa':mat('tecido_turquesa',(.04,.57,.48),0,.8),
 'branco_xadrez':mat('linhas_manta',(.60,.70,.65),0,.8),
 'relevo_sombra':mat('relevo_sombra',(.82,.82,.80),0,.8),
 'tampo_branco':mat('tampo_branco_jantar',(.91,.93,.92),.05,.20),
 'estofado_jantar':mat('estofado_jantar_marrom',(.13,.105,.09),0,.86),
 'linha_estofado':mat('costura_estofado',(.22,.18,.15),0,.9),
 'toalha_verde':mat('centro_mesa_verde',(.43,.69,.18),0,.85),
 'rejunte_banheiro_real':mat('rejunte_banheiro_bege',(.45,.35,.28),0,.85),
 'pastilhas_cozinha':mat('pastilhas_cozinha_pretas',(.07,.07,.075),.10,.30),
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
def wood_caramel(u,v,r):
    vein=.5+.5*math.sin(95*u+2*math.sin(v*10)+math.sin(v*28))
    noise=(r.random()-.5)*.022
    return (.37+.16*vein+noise,.20+.12*vein+noise,.10+.07*vein+noise)
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
def mosaic(u,v,r):
    # Pastilhas pequenas escuras com linhas claras de rejunte.
    edge=(int(u*192)%12<2 or int(v*192)%32<2)
    if edge: return (.56,.56,.54)
    tile=((int(u*192)//12)*37+(int(v*192)//32)*17)%7
    value=.025+tile*.012+(r.random()-.5)*.008
    return (value,value,value+.005)
for args in [('madeira','textura_madeira.png',wood),('granito','textura_granito.png',granite),
             ('setupcolcha','textura_coberta.png',blanket),('sofa','textura_sofa.png',woven),
             ('painel_caramelo','textura_painel_tv.png',wood_caramel),
             ('pastilhas_cozinha','textura_pastilhas_cozinha.png',mosaic)]:
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

def beam(name,a,b,width,material):
    a,b=Vector(a),Vector(b)
    o=cube(name,(a+b)/2,((b-a).length,width,width),material)
    o.rotation_euler=(b-a).to_track_quat('X','Z').to_euler()
    return o

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
wallx(0,3.30,0); wallx(3.30,6.50,0,(5.55,6.35))
wallx(0,1.80,3.00); wallx(1.80,3.30,3.00,(2.20,3.00))
wallx(0,3.30,4.80,(2.20,3.00))
wallx(0,3.30,7.80,window=(1.0,2.15)); wallx(3.30,6.50,7.80,window=(4.25,5.70))
wally(0,0,3,window=(1.75,2.90)); wally(0,3,4.8,window=(3.62,4.22)); wally(0,4.8,7.8)
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
# Giro de 90 graus horário visto de cima para mover a janela ao lado oeste.
# Centro do quarto aproximado (1.65, 1.50); -0.15 m em X corrige o fato de o quarto ser retangular.
quarto_pivo = Vector((1.65, 1.50, 0))
rotacao_quarto = Matrix.Translation(quarto_pivo) @ Matrix.Rotation(-math.pi / 2, 4, 'Z') @ Matrix.Translation(-quarto_pivo)
def girar_quarto(objetos, dx=0, dy=0):
    trans = Matrix.Translation(Vector((dx, dy, 0))) @ rotacao_quarto
    for obj in objetos:
        obj.matrix_world = trans @ obj.matrix_world
janela_quarto_setup = [obj for obj in bpy.context.scene.objects if obj.name.startswith('janela_setup')]
girar_quarto(janela_quarto_setup, dx=-.15)

# Persiana da janela do outro quarto, com lâminas horizontais visíveis.
for z in [0.81+i*.055 for i in range(8)]:
    box('persiana_quarto',1.02,7.77,z,1.10,.025,.012,'moldura')

# Sala: aparador espelhado junto à entrada, com estrutura preta e tampo espelhado.
box('aparador_estrutura',3.62,.12,.04,.85,.37,.72,'escuro',.01)
for i in range(3):
    box('aparador_painel_espelho',3.64+i*.275,.491,.10,.255,.012,.61,'espelhado')
    box('aparador_montante',3.63+i*.275,.502,.08,.018,.015,.65,'dourado')
box('aparador_tampo',3.60,.10,.76,.89,.41,.035,'espelhado',.008)
box('aparador_passadeira',3.66,.13,.797,.75,.31,.008,'verdeagua')
for i,(x,h) in enumerate(((3.78,.20),(4.03,.27),(4.29,.32))):
    cylinder('vaso_dourado_aparador',(x,.28,.80+h/2),.045,h,'dourado',20)
box('espelho_sala_moldura',3.55,.07,.84,1.04,.035,.44,'escuro')
box('espelho_sala',3.58,.11,.86,.98,.015,.40,'espelhado')
box('sofa_base',3.72,.63,.06,.76,1.84,.29,'sofa',.06)
box('sofa_assento',3.78,.69,.35,.67,1.70,.19,'sofa',.06)
box('sofa_encosto',3.71,.63,.36,.20,1.84,.65,'sofa',.05)
for y in (.63,2.29): box('sofa_braco',3.72,y,.36,.76,.18,.32,'sofa',.04)
for i,y in enumerate((.86,1.34,1.82)):
    o=box('almofada',3.94,y,.56,.18,.30,.28,'mostarda' if i==1 else 'verdeagua',.075)
    o.rotation_euler.y=.14 if i==0 else -.10
for y in (1.03,1.61): box('costura_sofa',3.78,y,.536,.66,.009,.008,'creme')
quilt('manta_sofa',3.84,.71,.56,.56,1.65,'verde',.012)
for y in [.80+i*.17 for i in range(9)]: box('xadrez_manta',3.85,y,.575,.54,.007,.006,'branco_xadrez')
for x in (3.93,4.10,4.27): box('xadrez_manta',x,.72,.575,.007,1.62,.006,'branco_xadrez')
# Relevo triangular branco na parede atrás do sofá.
verts=[]; faces=[]
for y_i in range(15):
    for z_i in range(7):
        y=.63+y_i*.12; z=.19+z_i*.14; k=len(verts)
        verts.extend([(3.357,y,z),(3.357,y+.12,z),(3.357,y+.12,z+.14),(3.357,y,z+.14),(3.378,y+.06,z+.07)])
        faces.extend([(k,k+1,k+4),(k+1,k+2,k+4),(k+2,k+3,k+4),(k+3,k,k+4)])
mesh=bpy.data.meshes.new('relevo_geometrico_sala'); mesh.from_pydata(verts,[],faces); mesh.update()
ob=bpy.data.objects.new('relevo_geometrico_sala',mesh); bpy.context.collection.objects.link(ob); ob.data.materials.append(M['parede'])
box('quadro_verde_moldura',3.383,1.48,.83,.025,.40,.35,'madeira2')
box('quadro_verde',3.409,1.50,.85,.01,.36,.31,'verdeagua')
# Mesa centro e estante da TV.
box('mesa_centro_vidro',4.58,.95,.43,.58,.96,.035,'espelhado',.008)
for x in (4.60,5.12):
    for y in (.97,1.87): box('perna_mesa_centro',x,y,.045,.025,.025,.39,'escuro')
for x in (4.61,5.12):
    beam('diagonal_mesa',(x,.98,.08),(x,1.87,.40),.018,'escuro')
    beam('diagonal_mesa',(x,1.87,.08),(x,.98,.40),.018,'escuro')
for y in (.97,1.87):
    beam('travessa_mesa',(4.61,y,.07),(5.12,y,.07),.018,'escuro')
cylinder('vaso_rosas_mesa',(4.88,1.43,.53),.09,.14,'dourado',20)
for i in range(7):
    xx=4.88+random.uniform(-.075,.075); yy=1.43+random.uniform(-.075,.075)
    cylinder('caule_rosa',(xx,yy,.67),.006,.20,'planta',8)
    sphere('rosa_mesa',(xx,yy,.78),(.035,.035,.04),'vermelho')
box('painel_tv',6.35,.56,.03,.10,1.90,1.85,'painel_caramelo')
for z in (.53,1.59): box('friso_painel_tv',6.345,.58,z,.012,1.86,.012,'dourado')
box('prateleira_superior_tv',6.17,.60,1.64,.20,1.80,.035,'painel_caramelo')
for y in (.75,1.02):
    cylinder('vaso_branco_tv',(6.24,y,1.74),.035,.16,'loucabranca',20)
box('rack_tv_base',6.10,.58,.20,.26,1.86,.31,'painel_caramelo',.015)
box('nicho_tv_centro',6.07,1.14,.25,.03,.73,.21,'escuro')
for yy in (.60,1.93):
    box('rack_porta_clara',6.065,yy,.22,.035,.48,.27,'moldura')
    for i in range(11): box('detalhe_canelado_rack',6.055,yy+i*.043,.23,.012,.012,.25,'creme')
box('moldura_tv_sala',6.27,.80,.78,.075,1.28,.77,'escuro',.01)
box('obj_tv_sala',6.25,.83,.81,.025,1.22,.71,'teladesligada')
box('ps5_centro',6.12,.70,.53,.12,.26,.08,'escuro')
box('ps5_superior',6.11,.68,.62,.14,.30,.025,'moldura')
box('ps5_inferior',6.11,.68,.50,.14,.30,.025,'moldura')
# Pingentes de cristal abaixo da luminária central da sala.
for i in range(11):
    angle=i*2.4; r=.018+.012*(i%3); z=2.34-i*.043
    sphere('gota_lustre',(5.28+math.cos(angle)*r,1.78+math.sin(angle)*r,z),(.018,.018,.025),'espelhado')

# Corredor: móvel lateral baixo com toalha turquesa e quadro, posição aproximada.
box('movel_corredor',3.34,3.17,.03,.34,.72,.67,'madeira2',.008)
box('porta_movel_corredor',3.315,3.22,.10,.025,.42,.53,'creme')
for z in (.17,.34,.51): box('nicho_movel_corredor',3.31,3.66,z,.03,.18,.11,'escuro')
box('toalha_movel_corredor',3.34,3.17,.71,.34,.72,.012,'turquesa')
for y in (3.29,3.50,3.70): cylinder('vaso_corredor',(3.49,y,.79),.045,.15,'dourado',18)
# Moldura apoiada junto ao móvel: sem inventar uma parede que feche a passagem.
box('porta_retrato_moldura',3.32,3.24,.725,.025,.43,.30,'moldura')
for i in range(3): box('foto_retrato',3.305,3.28+i*.12,.775,.012,.09,.10,'espelhado')

# Sala de jantar: tampo branco, pequenos jogos verdes e arranjo de rosas.
box('mesa_jantar',5.08,3.40,.76,1.18,.88,.08,'tampo_branco',.02)
box('base_mesa_jantar',5.40,3.69,.03,.50,.30,.72,'creme',.015)
for i in range(3):
    # Eleva discretamente as peças sobrepostas para evitar superfícies coplanares.
    tapete=cube('centro_mesa_verde',(5.32+i*.30,3.84,.846+i*.010),(.30,.30,.008),'toalha_verde')
    tapete.rotation_euler.z=math.pi/4
cylinder('vaso_jantar',(5.66,3.84,.91),.075,.13,'escuro',20)
for i in range(7):
    a=i*2.4; xx=5.66+math.cos(a)*.045; yy=3.84+math.sin(a)*.045
    cylinder('caule_jantar',(xx,yy,1.03),.006,.22,'planta',8)
    sphere('rosa_jantar',(xx,yy,1.14),(.032,.032,.035),'vermelho')
# As duas cadeiras próximas ao painel conservam o assento na mesma posição;
# o encosto passa para a borda externa, em vez de ficar junto ao tampo.
for x,y in ((5.18,3.14),(5.76,3.14),(5.18,4.32),(5.76,4.32)):
    box('assento_cadeira',x,y,.43,.40,.37,.08,'estofado_jantar',.025)
    for xx in (x+.03,x+.31):
        for yy in (y+.03,y+.28): box('perna_cadeira',xx,yy,.03,.05,.05,.40,'madeira')
    encosto_y=y if y<3.5 else y+.31
    box('encosto_cadeira',x,encosto_y,.50,.40,.06,.46,'estofado_jantar',.025)
    box('moldura_encosto_cadeira',x,encosto_y,.96,.40,.065,.035,'madeira2',.007)
    for k in range(1,4):
        xx=x+.08*k
        beam('costura_encosto',(xx,encosto_y-.004,.55),(min(x+.39,xx+.15),encosto_y-.004,.89),.005,'linha_estofado')
box('cristaleira',5.22,5.05,.04,.72,.40,1.75,'madeira2',.015)
box('cristaleira_frente',5.25,5.02,.35,.66,.025,1.35,'vidro')
for z in (.47,.80,1.13,1.46): box('cristaleira_prateleira',5.25,5.04,z,.66,.36,.025,'madeira')
for z in (.50,.83,1.16,1.49):
    for x in (5.35,5.52,5.69):
        cylinder('louca_cristaleira',(x,5.20,z+.045),.045,.09,'loucabranca',16)
# Prateleiras vazadas e haste metálica junto à divisão com a cozinha.
for z in (1.07,1.45,1.83,2.21):
    box('prateleira_divisoria',4.84,4.86,z,.36,.66,.045,'creme',.008)
cylinder('haste_divisoria',(5.16,4.92,1.64),.018,1.18,'inox',12)
for z in (1.10,1.48,1.86):
    cylinder('vaso_prateleira',(5.02,5.22,z+.05),.045,.10,'dourado',12)
    sphere('planta_prateleira',(5.02,5.22,z+.13),(.07,.07,.08),'planta')

# Cozinha e lavanderia: dois lados de armários com circulação central.
# Posições e medidas estimadas das fotografias, sem objetos temporários.
box('geladeira',3.43,4.97,.03,.63,.64,1.72,'inox',.02)
box('frente_geladeira',4.061,4.99,.07,.015,.60,1.61,'inox',.006)
box('divisao_geladeira',4.08,4.99,.93,.012,.60,.025,'escuro')
box('puxador_geladeira_superior',4.086,5.04,1.01,.025,.49,.023,'escuro',.006)
box('puxador_geladeira_inferior',4.086,5.04,.86,.025,.49,.023,'escuro',.006)
box('aereo_sobre_geladeira',3.39,4.96,1.78,.53,.65,.44,'branco_frio',.008)
box('porta_aereo_geladeira',3.92,4.99,1.81,.018,.59,.38,'branco_frio')
box('perfil_aereo_geladeira',3.94,4.99,1.84,.02,.59,.023,'aluminio')

# Bancada contínua de granito com pia e cooktop; o frontão é de pastilhas.
box('armario_pia',3.43,5.65,.03,.60,1.82,.82,'taupe')
for y in (5.68,6.13,6.58,7.03):
    box('frente_armario_cozinha',4.035,y,.09,.018,.42,.70,'taupe',.006)
    box('puxador_armario_cozinha',4.055,y+.04,.70,.025,.34,.022,'aluminio',.004)
for z in (.24,.39,.54):
    box('linha_gaveta_cozinha',4.057,6.59,z,.008,.40,.010,'aluminio')
box('bancada_cozinha',3.39,5.62,.85,.67,1.88,.05,'granito')
box('pastilhas_cozinha',3.342,5.64,.90,.018,1.85,.64,'pastilhas_cozinha')
box('cuba_cozinha',3.48,5.86,.901,.45,.55,.016,'inox',.035)
box('interior_cuba',3.52,5.90,.919,.37,.47,.006,'escuro',.045)
box('fundo_cuba',3.55,5.93,.922,.31,.41,.005,'inox',.04)
cylinder('torneira_cozinha',(3.47,6.10,1.03),.025,.25,'inox',12)
cylinder('bica_torneira',(3.57,6.10,1.14),.018,.21,'inox',12,(0,math.pi/2,0))
box('escorredor_base',3.48,5.68,.915,.45,.15,.015,'inox')
for yy in [5.69+i*.025 for i in range(6)]: box('escorredor_grade',3.50,yy,.93,.40,.006,.008,'aluminio')
box('cooktop_preto',3.45,6.75,.904,.55,.56,.025,'escuro',.01)
for xx in (3.58,3.87):
    for yy in (6.89,7.15):
        ring('boca_cooktop',(xx,yy,.936),.065,.010,'inox')
        cylinder('centro_cooktop',(xx,yy,.937),.045,.008,'escuro',16)
box('armario_aereo_esquerda',3.40,5.63,1.58,.42,1.88,.78,'branco_frio',.008)
for yy in (5.66,6.11,6.56,7.01):
    box('porta_aereo_esquerda',3.821,yy,1.61,.018,.42,.72,'branco_frio')
    for zz in (1.94,2.26): box('perfil_aereo_esquerda',3.843,yy,zz,.018,.42,.018,'aluminio')
box('coifa_inox',3.44,6.81,1.49,.48,.54,.08,'inox',.01)
box('coifa_escura',3.52,6.86,1.48,.33,.42,.015,'escuro')
box('torradeira',3.49,7.37,.91,.28,.26,.27,'inox',.025)

# Lado direito com armário baixo, aéreo, nichos e micro-ondas.
box('armario_oposto_inferior',6.02,5.35,.03,.44,1.30,.83,'taupe',.008)
box('tampo_oposto',6.00,5.32,.86,.47,1.36,.035,'creme')
for yy in (5.38,6.01):
    box('porta_armario_oposto',6.001,yy,.10,.018,.59,.69,'taupe')
    box('perfil_armario_oposto',5.978,yy+.04,.70,.022,.51,.023,'aluminio')
box('aereo_oposto',6.06,5.32,1.49,.40,1.42,.83,'branco_frio',.008)
for yy in (5.36,5.81,6.26):
    box('porta_aereo_oposto',6.039,yy,1.53,.018,.42,.75,'branco_frio')
    box('perfil_aereo_oposto',6.016,yy,1.57,.020,.42,.022,'aluminio')
for zz in (1.30,1.62,1.94,2.26):
    box('nicho_lateral_oposto',5.86,5.00,zz,.60,.28,.045,'creme',.01)
for zz in (1.35,1.67,1.99):
    cylinder('vaso_nicho_cozinha',(6.12,5.13,zz+.045),.045,.09,'loucabranca',12)
    sphere('planta_nicho_cozinha',(6.12,5.13,zz+.12),(.06,.06,.07),'planta')
box('nicho_microondas',6.04,6.83,1.39,.41,.70,.48,'branco_frio')
box('microondas_inox',6.045,6.88,1.43,.38,.60,.39,'inox',.012)
box('frente_microondas',6.026,6.90,1.47,.012,.45,.30,'escuro',.005)
box('painel_microondas',6.025,7.36,1.47,.012,.10,.30,'aluminio')
box('display_microondas',6.010,7.37,1.68,.006,.075,.04,'pixel_azul')
box('puxador_microondas',6.005,6.94,1.50,.025,.025,.23,'aluminio',.008)

# Lavadora de abertura superior na parede direita, sem inventar tanque.
box('maquina_lavar_superior',5.81,6.88,.03,.63,.66,.88,'loucabranca',.025)
box('tampa_maquina_superior',5.85,6.92,.912,.55,.57,.035,'branco_frio',.018)
box('painel_maquina_superior',5.85,7.36,.95,.55,.13,.045,'creme',.01)
for yy in (7.38,7.42,7.46): cylinder('botao_maquina_superior',(5.97,yy,.999),.016,.012,'escuro',12)
box('abertura_tampa_maquina',5.91,6.94,.949,.43,.40,.009,'vidro',.02)

# Varal branco suspenso diante da janela da lavanderia, sem roupas.
for xx in (4.38,5.65):
    box('suporte_varal',(xx),7.16,2.36,.035,.54,.035,'branco_frio')
for yy in (7.18,7.28,7.38,7.48,7.58,7.68):
    beam('barra_varal',(4.38,yy,2.36),(5.68,yy,2.36),.009,'branco_frio')
for xx in (4.38,5.65):
    for yy in (7.16,7.68): beam('tirante_varal',(xx,yy,2.36),(xx,yy,2.55),.006,'branco_frio')

# Banheiro: olhando da porta para a janela, vaso à esquerda e pia à direita.
# As paredes permanecem as mesmas; detalhes e distâncias são aproximados.
sphere('vaso_base',(.39,3.38,.21),(.23,.19,.19),'loucabranca')
sphere('vaso_taca',(.43,3.38,.35),(.30,.24,.16),'loucabranca')
ring('vaso_assento',(.43,3.38,.47),.16,.025,'loucabranca',scale=(1.38,1.08,1))
sphere('agua_vaso',(.43,3.38,.465),(.16,.12,.008),'vidro')
box('vaso_caixa',.10,3.18,.35,.19,.40,.39,'loucabranca',.02)
for z in (1.01,1.32,1.63):
    box('nicho_banheiro_fundo',.07,3.10,z,.035,.42,.24,'escuro')
    for zz in (z,z+.22): box('nicho_banheiro_moldura',.085,3.10,zz,.11,.42,.025,'branco_frio')
    for yy in (3.10,3.495): box('nicho_banheiro_lateral',.085,yy,z,.11,.025,.24,'branco_frio')
box('bancada_banheiro',.12,4.24,.76,.52,.47,.08,'granito')
box('cuba_banheiro',.16,4.28,.84,.40,.37,.12,'loucabranca',.04)
box('espelho_banheiro',.08,4.28,.97,.025,.38,.50,'espelhado')
cylinder('torneira_banheiro',(.20,4.58,1.02),.018,.20,'inox',12)
box('piso_box',1.05,3.86,.035,.69,.80,.025,'creme')
box('vidro_box',1.04,3.86,.06,.025,.80,1.45,'vidro')
for y in (3.86,4.64): box('perfil_box',1.02,y,.06,.045,.035,1.45,'escuro')
# Azulejo branco e rejunte acastanhado conforme as fotografias.
for z in (.30,.60,.90,1.20): box('rejunte_banheiro',.055,3.05,z,.008,1.68,.005,'rejunte_banheiro_real')
for y in [3.15+i*.30 for i in range(6)]: box('rejunte_banheiro',.055,y,.06,.008,.005,1.22,'rejunte_banheiro_real')
# Chuveiro branco próximo ao box. A posição é aproximada pela foto.
cylinder('chuveiro_haste',(1.42,4.60,1.58),.018,.26,'loucabranca',12,(0,math.pi/2,0))
sphere('chuveiro',(1.30,4.60,1.55),(.13,.13,.035),'loucabranca')

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

# Quarto: os móveis e a janela giram 90 graus no sentido horário, mantendo a porta fixa.
# Guarda-roupa claro: duas portas largas de correr e perfis metálicos.
objetos_antes_roupeiro = set(bpy.context.scene.objects)
box('guarda_roupa_setup',2.70,.16,.03,.53,1.82,2.24,'branco_frio',.012)
for y in (.20,1.10):
    box('porta_de_correr',2.675,y,.08,.035,.87,2.13,'branco_frio',.008)
    box('perfil_vertical_porta',2.649,y+.015,.09,.025,.025,2.10,'aluminio')
for z in (.08,2.21):
    box('trilho_roupeiro',2.64,.18,z,.065,1.78,.035,'aluminio')

# Roda apenas o roupeiro para a parede sul; reancora sem alterar as dimensões.
girar_quarto(set(bpy.context.scene.objects) - objetos_antes_roupeiro, dy=.15)

# Cama com base marrom-escura e roupa de cama cinza; objetos transitórios omitidos.
objetos_antes_cama = set(bpy.context.scene.objects)
box('cama_setup_base',.18,.15,.03,1.40,1.95,.32,'base_cama',.035)
box('cama_setup_colchao',.20,.17,.35,1.36,1.91,.22,'roupa_cinza',.055)
quilt('cama_setup_coberta',.22,.48,.59,1.32,1.43,'roupa_cinza',.027)
for x in (.34,.96):
    box('travesseiro_setup',x,.25,.58,.49,.26,.11,'roupa_cinza',.065)

# Roda a cama para a parede oeste, acompanhando a janela. Os 3 cm adicionais
# mantêm a base afastada da parede da porta no quarto retangular aproximado.
girar_quarto(set(bpy.context.scene.objects) - objetos_antes_cama, dx=-.15, dy=-.03)

# Mesa e duas telas: a tela maior é central, a outra fica angulada à esquerda.
objetos_antes_setup = set(bpy.context.scene.objects)
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
# A TV gira com o setup; seu identificador permanece para as interações.
box('moldura_tv_quarto',1.20,2.86,1.38,.94,.075,.54,'escuro',.008)
box('obj_tv_quarto',1.23,2.84,1.41,.88,.025,.48,'teladesligada')

# Roda o conjunto da parede da porta para a parede leste. A porta não está neste grupo.
objetos_setup_girados = set(bpy.context.scene.objects) - objetos_antes_setup
girar_quarto(objetos_setup_girados, dx=.15)
# O aéreo e nichos ficavam na parede perpendicular. Como o quarto não é quadrado,
# reancoramos esses elementos no canto, evitando que atravessem a parede ou o roupeiro.
for obj in objetos_setup_girados:
    if obj.name.startswith(('armario_aereo_quarto', 'porta_armario_aereo_quarto', 'nicho_quarto_')):
        obj.location.x += .08
        obj.location.y += .15

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
