import glm
import numpy as np
import moderngl as mgl
import pywavefront
import pygame as pg

# heart class to represent a 3D heart model
class Heart:
    def __init__(self, app, pos=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1), ppm=100, mask=[1]*100):
        self.app = app
        self.ctx = app.ctx
        self.pos = pos
        #treballarem amb aquest self.rot per fer les rotacions del cor
        self.rot = glm.vec3([glm.radians(a) for a in rot])
        self.scale = scale
        
        #shader program
        self.program = self.get_program('default')
        #3D vertex data
        self.vertex_data = self.get_vertex_data('objects/heart/base.obj')
        #imatge texture
        self.texture = self.get_texture('objects/heart/texture_diffuse.png')
        
        #Vertex Buffer Object i Vertex Array Object
        self.vbo = self.ctx.buffer(self.vertex_data)
        self.format = '2f 3f 3f'
        self.attribs = ['in_texcoord_0', 'in_normal', 'in_position']
        self.vao = self.ctx.vertex_array(self.program, [(self.vbo, self.format, *self.attribs)])
        
        #model matrix i camera
        self.m_model = self.get_model_matrix()
        self.camera = self.app.camera

        #variables per rotació del cor
        self.rotation_velocity = glm.vec2(0.0, 0.0)  # velocitat de rotacio en x i y
        self.rotation_friction = 0.985  #friccio per desaccelerar i parar el cor. 
        
        #si vols tornar a la posicio original que no vols rotar: R
        self.return_key = pg.K_r  # LA R

        # Animation vertex per steps
        self.start_vertices = self.vertex_data
        self.end_vertices_step1 = self.get_vertex_data('objects/heart/updated_abaix.obj')
        self.end_vertices_step2 = self.get_vertex_data('objects/heart/updated_ventricula.obj')
        self.end_vertices_step3 = self.get_vertex_data('objects/heart/updated_arterias.obj')

        # Animation progress
        self.animation_progress_1 = 0.0
        self.animation_progress_2 = 0.0
        self.animation_progress_3 = 0.0
        self.tempo = 0

        # Heart beat animation
        self.ppm = ppm
        self.beat_mask = mask
        self.animate_heartbeat = True #animation control beating or not.
        
        #afegir beating sound:
        self.heartbeat_sound_slow = pg.mixer.Sound("Bateg_Cor.wav") #50 ppm
        self.heartbeat_sound_normal = pg.mixer.Sound("Bateg_Cor_normal.wav") #150 ppm
        self.heartbeat_sound_fast = pg.mixer.Sound("Bateg_Cor_fast2.wav") #250 ppm
        #set volume
        self.heartbeat_sound_slow.set_volume(0.6)
        self.heartbeat_sound_normal.set_volume(0.6)
        self.heartbeat_sound_fast.set_volume(0.6)
        #fer servir un canal audio diferent per no juntar amb background music
        self.heartbeat_channel = pg.mixer.Channel(1)

        self.on_init()
            
    def update_rotation(self):
        #no mes control amb keyboard: y,u,i,o... ara amb gestures
        #les funcions rotate_left, right, up, down gestionen els canvis de self.rotation_velocity.y .x;  + o -. Aquesta funcio es standard per totes: friccio i actualitzar
        
        # Aplicar fricció
        self.rotation_velocity *= self.rotation_friction
        
        # Actualitzar rotació
        self.rot.y += glm.radians(self.rotation_velocity.x)
        self.rot.x += glm.radians(self.rotation_velocity.y)
    
    #funcions pels gestures canviar la rotació
    #1.1 es la rotation_speed
    def rotate_left(self): #gesture action = swipe left
        self.rotation_velocity.x -= 1.1

    def rotate_right(self): #gesture action = swipe right
        self.rotation_velocity.x += 1.1

    def rotate_up(self): #gesture action = swipe up
        self.rotation_velocity.y += 1.1

    def rotate_down(self): #gesture action = swipe down
        self.rotation_velocity.y -= 1.1
    
    #reset rotation a normal: tornar a pos inicial abans rotacio
    def reset_rotation(self): #gesture action = click
        self.rotation_velocity = glm.vec2(0.0, 0.0) #tornar velocitat a 0
        self.rot = glm.vec3(0, 0, 0) #tornar rotació a 0
    
    #model transform matrix (translation, rotation, scale)
    def get_model_matrix(self):
        m_model = glm.mat4()
        # translate
        m_model = glm.translate(m_model, self.pos)
        # rotate
        m_model = glm.rotate(m_model, self.rot.z, glm.vec3(0, 0, 1))
        m_model = glm.rotate(m_model, self.rot.y, glm.vec3(0, 1, 0))
        m_model = glm.rotate(m_model, self.rot.x, glm.vec3(1, 0, 0))
        #additional rotation around Y-axis
        rotation_y = getattr(self, 'rotation_y', 0.0) 
        m_model = glm.rotate(m_model, rotation_y, glm.vec3(0, 1, 0))
        # scale
        m_model = glm.scale(m_model, self.scale)
        return m_model
    
    #load vertex dara de .obj file
    def get_vertex_data(self, obj_file):
        objs = pywavefront.Wavefront(obj_file, parse=True)
        obj = objs.materials.popitem()[1]
        vertex_data = obj.vertices
        vertex_data = np.array(vertex_data, dtype='f4')
        return vertex_data    
    
    #texture per render
    def get_texture(self, path):
        texture = pg.image.load(path).convert()
        texture = pg.transform.flip(texture, flip_x=False, flip_y=True)
        texture = self.ctx.texture(size=texture.get_size(), components=3,
                                   data=pg.image.tostring(texture, 'RGB'))
        # mipmaps
        texture.filter = (mgl.LINEAR_MIPMAP_LINEAR, mgl.LINEAR)
        texture.build_mipmaps()
        # AF
        texture.anisotropy = 32.0
        return texture
    
    #load shader program
    def get_program(self, shader_program_name):
        with open(f'/Users/carlotacortes/Desktop/Heartmodel/shaders/{shader_program_name}.vert') as file:
            vertex_shader = file.read()

        with open(f'/Users/carlotacortes/Desktop/Heartmodel/shaders/{shader_program_name}.frag') as file:
            fragment_shader = file.read()

        program = self.ctx.program(vertex_shader=vertex_shader, fragment_shader=fragment_shader)
        return program

    def on_init(self):
        # texture
        self.program['u_texture_0'] = 0
        self.texture.use()
        # mvp
        self.program['m_proj'].write(self.camera.m_proj)
        self.program['m_view'].write(self.camera.m_view)
        self.program['m_model'].write(self.m_model)
        # light
        #self.program['light.position'].write(self.app.light.position)
        self.program['light.Ia'].write(self.app.light.Ia)
        self.program['light.Id'].write(self.app.light.Id)
        self.program['light.Is'].write(self.app.light.Is)

    def update_animation_params(self, ppm, mask):
        self.ppm = ppm
        self.beat_mask = mask
    
    #vertex updates per heartbeat animació: interpolació vertexs.
    def update_vertex(self, factor_1=0.0167, factor_2=0.0067):
        self.animation_progress_1 += (self.ppm * factor_1) / 60
        if self.animation_progress_1 >= 1.0:
             self.animation_progress_1 = 0.0
             self.tempo += 1
             if self.tempo == len(self.beat_mask):
                self.tempo = 0
             if not self.heartbeat_channel.get_busy():
                if self.ppm >= 150: #fast
                    self.heartbeat_channel.play(self.heartbeat_sound_fast)
                elif self.ppm >= 75: #normal
                    self.heartbeat_channel.play(self.heartbeat_sound_normal)
                else: #slow
                    self.heartbeat_channel.play(self.heartbeat_sound_slow)
        
        #blend progressiu
        if self.animation_progress_1 >= 0.5:
            if self.animation_progress_2 < 1.0:
                self.animation_progress_2 += (self.ppm * factor_2) / 60
        else:
            if self.animation_progress_2 > 0.0:
                self.animation_progress_2 -= (self.ppm * factor_2) / 60

        if self.animation_progress_1 >= 0.75:
            if self.animation_progress_3 < 1.0:
                self.animation_progress_3 += (self.ppm * factor_1) / 60
        else:
            if self.animation_progress_3 > 0.0:
                self.animation_progress_3 -= (self.ppm * factor_1) / 60
                

        # Interpolació per cada pas
        interpolated_vertices_step1 = ((1 - self.animation_progress_1 * self.beat_mask[self.tempo]) * self.start_vertices) + (self.animation_progress_1 * self.beat_mask[self.tempo] * self.end_vertices_step1)
        interpolated_vertices_step2 = ((1 - self.animation_progress_2 * self.beat_mask[self.tempo]) * self.start_vertices) + (self.animation_progress_2 * self.beat_mask[self.tempo] * self.end_vertices_step2)
        interpolated_vertices_step3 = ((1 - self.animation_progress_3 * self.beat_mask[self.tempo]) * self.start_vertices) + (self.animation_progress_3 * self.beat_mask[self.tempo] * self.end_vertices_step3)

        # mix ponderada dels passos
        blend_factor_step2 = min(self.animation_progress_2 * 2, 1.0)
        blend_factor_step3 = min(self.animation_progress_3 * 2, 1.0)  
        p1 = (1 - blend_factor_step2 - blend_factor_step3) * interpolated_vertices_step1
        p2 = blend_factor_step2 * interpolated_vertices_step2
        p3 = blend_factor_step3 * interpolated_vertices_step3
        blended_vertices = p1 + p2 + p3

        # actualitzar vertexs model
        self.vbo.write(np.array(blended_vertices, dtype='f4'))

    def update(self):
        self.texture.use()
        self.program['camPos'].write(self.camera.position)
        self.program['m_view'].write(self.camera.m_view)
        self.m_model = self.get_model_matrix()  # Recalculate model matrix
        self.program['m_model'].write(self.m_model)
        
    def render(self):
        self.update()
        self.vao.render()
    
    #actualitzar animacio i rotacio cada frame
    def animate(self):
        if self.animate_heartbeat and self.ppm > 0: #if beating=true animate.
            self.update_vertex()
        self.update_rotation()
    
    #netejar GPU resources
    def destroy(self):
        self.vbo.release()
        self.texture.release()
        self.program.release()
