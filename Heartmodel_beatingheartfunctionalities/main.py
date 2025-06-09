import pygame as pg
import moderngl as mgl
import sys
from model import *
from camera import Camera
from light import Light
from scene import Scene
import cv2


class GraphicsEngine:
    def __init__(self, models_data = [((0, -2, -10), (0, 0, 0), (1, 1, 1), 60, [1])], win_size=(1300, 800)): #1000, 800
        # init pygame modules
        pg.init()
        # window size
        self.WIN_SIZE = win_size
        # set opengl attr
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MAJOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_MINOR_VERSION, 3)
        pg.display.gl_set_attribute(pg.GL_CONTEXT_PROFILE_MASK, pg.GL_CONTEXT_PROFILE_CORE)
        # create opengl context
        pg.display.set_mode(self.WIN_SIZE, flags=pg.OPENGL | pg.DOUBLEBUF)
        # detect and use existing opengl context
        self.ctx = mgl.create_context()
        # self.ctx.front_face = 'cw'
        self.ctx.enable(flags=mgl.DEPTH_TEST | mgl.CULL_FACE)
        # create an object to help track time
        self.clock = pg.time.Clock()
        self.time = 0
        self.delta_time = 0
        # light
        self.light = Light()
        # camera
        self.camera = Camera(self)
        # scene
        self.scene = Scene(self, models_data)
        
        #AFEGIT PER DOBLE VISTA (webcam texture):
        self.latest_camera_frame_data = None
        self.latest_camera_frame_ready = False
        self.webcam_texture = None

    #ADDED METHODS per veure'm a mi en la pantalla: update_camera_frame i update_webcam_texture
    def update_camera_frame(self, frame):
    #processa i guarda cada frame
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) #de BGR a RGB
        rgb = np.flipud(rgb) #flip perque opencv i opengl diff coordinades
        self.latest_camera_frame_data = rgb #guarda resultat
        self.latest_camera_frame_ready = True
        
    def update_webcam_texture(self):
    #carrega el frame a la GPU com a texture
        frame = self.latest_camera_frame_data #agafa frame guardat
        h, w, _ = frame.shape
        
        #crear una opengl texture
        if self.webcam_texture is None or self.webcam_texture.size != (w, h):
            self.webcam_texture = self.ctx.texture((w, h), components=3)
            self.webcam_texture.repeat_x = False
            self.webcam_texture.repeat_y = False
            self.webcam_texture.filter = (mgl.LINEAR, mgl.LINEAR)
        
        #carrega la webcama frame com texture
        self.webcam_texture.write(frame.tobytes())
        self.latest_camera_frame_ready = False

    
    def check_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                pg.quit()
                sys.exit()
                
            elif event.type == pg.KEYDOWN:
                #SPACE FOR STOPPING ENTIRELY THE HEARTBEAT ANIMATION
                elif event.key == pg.K_SPACE:
                    for obj in self.scene.objects:
                        if hasattr(obj, "animate_heartbeat"):
                                obj.animate_heartbeat = False
                                print("Heartbeat paused")
    
    
    def set_max_heartbeat(self): #instead of "j" key = DROP. max heartbeat animation
        for obj in self.scene.objects:
            if hasattr(obj, "ppm"):
                #obj.ppm = min(580, obj.ppm + 100) #a 580 limit and goes +100 each time
                obj.ppm = 500
                print(f"PPM increased to: {obj.ppm}")
    
    def set_min_heartbeat(self): #instead of "k" key = DRAG. min heartbeat animation.
        for obj in self.scene.objects:
            if hasattr(obj, "ppm"):
                obj.ppm = 50
                #obj.ppm = max(0, obj.ppm - 100) #a 0 limit for no negatives and goes -100 each time
                print(f"PPM decreased to: {obj.ppm}")
    
    def reset_heartbeat(self): #if heartbeat stoped or beating max/min go back to normal #"r" key to little finger
        for obj in self.scene.objects:
            if hasattr(obj, "ppm") and hasattr(obj, "animate_heartbeat"):
                obj.ppm = 120
                obj.animate_heartbeat = True
                print(f"PPM reset to normal: {obj.ppm}")
                
    #def stop_heartbeat(self): #space key to stop gesture. Stop the beating entirely.
    #    for obj in self.scene.objects:
    #        if hasattr(obj, "animate_heartbeat"):
    #            obj.animate_heartbeat = False
    #            print("Heartbeat paused")
    
    
    def toggle_perspective_view(self): #instead of "p" key to change perspective, use the gesture action = Double Click
        self.camera.perspectiva = not self.camera.perspectiva
        self.camera.zoom = glm.vec3((0, 0, 0))
    
    def render(self):
        #render the 4 perspectives or 1
        # clear framebuffer
        self.ctx.clear(color=(0.08, 0.16, 0.18))
        
        #ADDED webcam texture
        if self.latest_camera_frame_ready:
            self.update_webcam_texture()
        
        if self.webcam_texture:
            self.render_webcam_quad()

        if self.camera.perspectiva:
            self.ctx.viewport = (0,0,self.WIN_SIZE[0],self.WIN_SIZE[1])
            self.camera.update((0, -2, -6),(0, 1, 0), (0, 0, -1))
            self.camera.move()
            self.scene.render()
        else:
            # Vista Alzado
            self.ctx.viewport = (0, self.WIN_SIZE[1] // 2, self.WIN_SIZE[0] // 2, self.WIN_SIZE[1] // 2)
            if len(self.scene.objects) > 1:
                self.camera.update((0, -2, -7),(0, 1, 0), (0, 0, -1))
            else:
                self.camera.update((0, -2, -7.5),(0, 1, 0), (0, 0, -1))
            self.scene.render()

            # Vista Perfil
            self.ctx.viewport = (0, 0, self.WIN_SIZE[0] // 2, self.WIN_SIZE[1] // 2)
            if len(self.scene.objects) > 1:
                self.camera.update((-3.5, -2, -10), (0, 1, 0), (1, 0, 0))
            else:
                self.camera.update((-2.5, -2, -10), (0, 1, 0), (1, 0, 0))
            self.scene.render()

            # Vista Axonométrica
            self.ctx.viewport = (self.WIN_SIZE[0] // 2, 0, self.WIN_SIZE[0] // 2, self.WIN_SIZE[1] // 2)
            if len(self.scene.objects) > 1:
                self.camera.update((-1.5, -2, -7), (0, 1, 0), glm.normalize(glm.vec3(0, -2, -10) - glm.vec3(-1.5, -2, -7))) 
            else:
                self.camera.update((-1.5, -2, -8), (0, 1, 0), glm.normalize(glm.vec3(0, -2, -10) - glm.vec3(-1.5, -2, -8))) 
            self.scene.render()

            # Vista Planta 
            self.ctx.viewport = (self.WIN_SIZE[0] // 2, self.WIN_SIZE[1] // 2, self.WIN_SIZE[0] // 2, self.WIN_SIZE[1] // 2)
            if len(self.scene.objects) > 1:
                self.camera.update((0, 1.5, -10), (0, 0, -1), (0, -1, 0))
            else:
                self.camera.update((0, 0.5, -10), (0, 0, -1), (0, -1, 0))
            self.scene.render()

        self.scene.animate()
        # swap buffers
        pg.display.flip()
    
    
    
    
    def render_webcam_quad(self):
    #Dibuixar a quad en la pantalla amb la textura mapped= webcam"""
        # Bottom-right corner. crear un quad rectangular
        vertices = np.array([
            0.4, -1.0, 0.0, 0.0, 0.0,
            1.0, -1.0, 0.0, 1.0, 0.0,
            1.0, -0.4, 0.0, 1.0, 1.0,
            0.4, -0.4, 0.0, 0.0, 1.0,
        ], dtype='f4')

        indices = np.array([0, 1, 2, 2, 3, 0], dtype='i4')
        vbo = self.ctx.buffer(vertices.tobytes())
        ibo = self.ctx.buffer(indices.tobytes())
        vao_content = [(vbo, '3f 2f', 'in_vert', 'in_text')]
        
        prog = self.ctx.program(
            vertex_shader='''
                #version 330
                in vec3 in_vert;
                in vec2 in_text;
                out vec2 v_text;
                void main() {
                    gl_Position = vec4(in_vert, 1.0);
                    v_text = in_text;
                }
            ''',
            fragment_shader='''
                #version 330
                uniform sampler2D webcam_tex;
                in vec2 v_text;
                out vec4 f_color;
                void main() {
                    f_color = texture(webcam_tex, v_text);
                }
            ''',
        )

        vao = self.ctx.vertex_array(prog, vao_content, ibo)
        self.webcam_texture.use(location=0)
        prog['webcam_tex'] = 0
        vao.render()


    def get_time(self):
        self.time = pg.time.get_ticks() * 0.001

    def run(self):
        while True:
            self.get_time()
            self.check_events()
            self.render()
            self.delta_time = self.clock.tick(60)

if __name__ == '__main__':
    app = GraphicsEngine()
    app.run()

