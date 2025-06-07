import pygame as pg
import moderngl as mgl
import sys
from model import *
from camera import Camera
from light import Light
from scene import Scene


class GraphicsEngine:
    def __init__(self, models_data = [((0, -2, -10), (0, 0, 0), (1, 1, 1), 60, [1])], win_size=(1000, 800)):
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

    def check_events(self):
        for event in pg.event.get():
            if event.type == pg.QUIT or (event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE):
                pg.quit()
                sys.exit()
    
    def toggle_perspective_view(self): #instead of "p" key to change perspective, use the gesture action = Double Click
        self.camera.perspectiva = not self.camera.perspectiva
        self.camera.zoom = glm.vec3((0, 0, 0))
    
    def render(self):
        #render the 4 perspectives or 1
        # clear framebuffer
        self.ctx.clear(color=(0.08, 0.16, 0.18))

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

