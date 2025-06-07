import glm
import numpy as np
import moderngl as mgl
import pywavefront
import pygame as pg


class Heart:
    def __init__(self, app, pos=(0, 0, 0), rot=(0, 0, 0), scale=(1, 1, 1), ppm=60, mask=[1]):
        self.app = app
        self.ctx = app.ctx
        self.pos = pos
        #treballarem amb aquest self.rot per fer les rotacions del cor
        self.rot = glm.vec3([glm.radians(a) for a in rot])
        self.scale = scale

        self.program = self.get_program('default')
        self.vertex_data = self.get_vertex_data('HeartModel_ENTREGA_FINAL/objects/heart/base.obj')
        self.texture = self.get_texture('HeartModel_ENTREGA_FINAL/objects/heart/texture_diffuse.png')
        
        self.vbo = self.ctx.buffer(self.vertex_data)
        self.format = '2f 3f 3f'
        self.attribs = ['in_texcoord_0', 'in_normal', 'in_position']
        self.vao = self.ctx.vertex_array(self.program, [(self.vbo, self.format, *self.attribs)])

        self.m_model = self.get_model_matrix()
        self.camera = self.app.camera

        #variables per rotació del cor
        self.last_mouse_pos = None  # ultima posicio del mouse en (x,y)
        self.rotation_velocity = glm.vec2(0.0, 0.0)  # velocitat de rotacio en x i y
        self.rotation_friction = 0.985  #friccio per desaccelerar i parar el cor. 
        self.sensitivity_threshold = 5  #umbral sensibilitat diagonal perque si tiro cap a dalt i no es totalment recte que no sigui loko

        #si vols tornar a la posicio original que no vols rotar: R
        self.return_key = pg.K_r  # LA R

        # Animation vertex
        self.start_vertices = self.vertex_data
        self.end_vertices_step1 = self.get_vertex_data('HeartModel_ENTREGA_FINAL/objects/heart/updated_abaix.obj')
        self.end_vertices_step2 = self.get_vertex_data('HeartModel_ENTREGA_FINAL/objects/heart/updated_ventricula.obj')
        self.end_vertices_step3 = self.get_vertex_data('HeartModel_ENTREGA_FINAL/objects/heart/updated_arterias.obj')

        # Animation progress
        self.animation_progress_1 = 0.0
        self.animation_progress_2 = 0.0
        self.animation_progress_3 = 0.0
        self.tempo = 0

        # Animation heart beat
        self.ppm = ppm

        # Animation 
        self.beat_mask = mask

        self.on_init()
            
    def update_rotation(self):
        #actualitza rotació basada en el mouse
        mouse_pos = pg.mouse.get_pos() #agafar pos x,y

        if self.last_mouse_pos is None:
            self.last_mouse_pos = mouse_pos

        #detectar direcció moviment mouse. si s'ha mogut
        if mouse_pos != self.last_mouse_pos:
            #vector de canvi en pos actual i ultima: indica direcció i magnitud en els eixos x,y
            delta = glm.vec2(mouse_pos[0] - self.last_mouse_pos[0], mouse_pos[1] - self.last_mouse_pos[1] )

            # si principalment horitzonal o diagonal. evitar diagonals petites
            if abs(delta.x) > abs(delta.y) + self.sensitivity_threshold:
                delta.y = 0  # moviment horitzonal, fora el vertical/y
            elif abs(delta.y) > abs(delta.x) + self.sensitivity_threshold:
                delta.x = 0  #moviment vertical, fora el horitzontal/x

            self.rotation_velocity += delta * 0.01  # velocitat basada en el mouse
            self.last_mouse_pos = mouse_pos

        # aplicar friccio per parar a la velocitat
        self.rotation_velocity *= self.rotation_friction
        
        # actualitzar els angles de rotació radians amb velocitat
        self.rot.y += glm.radians(self.rotation_velocity.x)  # horitzontal
        self.rot.x += glm.radians(self.rotation_velocity.y)  # vertical

        # si presiono r, tornar a posició inicial 
        keys = pg.key.get_pressed()
        if keys[self.return_key]:
            self.rotation_velocity = glm.vec2(0.0, 0.0)
            self.rot.y = 0
            self.rot.x = 0

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

    def get_vertex_data(self, obj_file):
        objs = pywavefront.Wavefront(obj_file, parse=True)
        obj = objs.materials.popitem()[1]
        vertex_data = obj.vertices
        vertex_data = np.array(vertex_data, dtype='f4')
        return vertex_data    

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

    def get_program(self, shader_program_name):
        with open(f'/Users/carlotacortes/Desktop/HeartModel_ENTREGA_FINAL/shaders/{shader_program_name}.vert') as file:
            vertex_shader = file.read()

        with open(f'/Users/carlotacortes/Desktop/HeartModel_ENTREGA_FINAL/shaders/{shader_program_name}.frag') as file:
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

    def update_vertex(self, factor_1=0.0167, factor_2=0.0067):
        self.animation_progress_1 += (self.ppm * factor_1) / 60
        if self.animation_progress_1 >= 1.0:
             self.animation_progress_1 = 0.0
             self.tempo += 1
             if self.tempo == len(self.beat_mask):
                self.tempo = 0

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
                

        # Interpolación para cada paso
        interpolated_vertices_step1 = ((1 - self.animation_progress_1 * self.beat_mask[self.tempo]) * self.start_vertices) + (self.animation_progress_1 * self.beat_mask[self.tempo] * self.end_vertices_step1)
        interpolated_vertices_step2 = ((1 - self.animation_progress_2 * self.beat_mask[self.tempo]) * self.start_vertices) + (self.animation_progress_2 * self.beat_mask[self.tempo] * self.end_vertices_step2)
        interpolated_vertices_step3 = ((1 - self.animation_progress_3 * self.beat_mask[self.tempo]) * self.start_vertices) + (self.animation_progress_3 * self.beat_mask[self.tempo] * self.end_vertices_step3)

        # Mezcla ponderada de los pasos
        blend_factor_step2 = min(self.animation_progress_2 * 2, 1.0)
        blend_factor_step3 = min(self.animation_progress_3 * 2, 1.0)  
        p1 = (1 - blend_factor_step2 - blend_factor_step3) * interpolated_vertices_step1
        p2 = blend_factor_step2 * interpolated_vertices_step2
        p3 = blend_factor_step3 * interpolated_vertices_step3
        blended_vertices = p1 + p2 + p3

        # Actualizar los vértices en el modelo
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

    def animate(self):
        self.update_vertex()
        self.update_rotation() 

    def destroy(self):
        self.vbo.release()
        self.texture.release()
        self.program.release()