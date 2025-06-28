import glm
import pygame as pg

FOV = 50  # field of view: degrees
NEAR = 0.1
FAR = 100
SPEED = 0.005 #movement speed

#camera position and movement
class Camera:
    def __init__(self, app, position=(0, -2, -6), up=(0, 1, 0), forward=(0, 0, -1)):
        self.app = app
        self.aspect_ratio = app.WIN_SIZE[0] / app.WIN_SIZE[1]
        self.position = glm.vec3(position) #pos inicial
        self.up = up
        self.forward = forward #direction facing
        
        # Controlar la vista de la camara
        self.perspectiva = True
        
        # view and projection matrix
        self.m_view = self.get_view_matrix()
        self.m_proj = self.get_projection_matrix()
        
        # guardar la posició del zoom
        self.zoom = glm.vec3((0,0,0))
        self.right = glm.vec3((1, 0, 0))
        
        #for smooth velocity and movement
        self.zoom_velocity = glm.vec3((0, 0, 0))  # smooth movement
        self.zoom_friction = 0.97 #friction
    
    #update camera position
    def update(self, position, up, forward):
        self.position = glm.vec3(position) + self.zoom
        self.up = glm.vec3(up)
        self.forward = glm.vec3(forward)
        self.m_view = self.get_view_matrix()
        self.m_proj = self.get_projection_matrix()
    
    #canviar camera basat en keys
    def move(self):
        velocity = SPEED * self.app.delta_time
        keys = pg.key.get_pressed()
        if keys[pg.K_a]:
            self.zoom -= self.right * velocity
        if keys[pg.K_d]:
            self.zoom += self.right * velocity
        if keys[pg.K_q]:
            self.zoom += self.up * velocity
        if keys[pg.K_e]:
            self.zoom -= self.up * velocity
        if keys[pg.K_r]:
            self.zoom = glm.vec3((0,0,0))
            self.zoom_velocity = glm.vec3((0, 0, 0))
            
        #apply zoom velocity for gesture-based zooming:
        self.zoom += self.zoom_velocity
        self.zoom_velocity *= self.zoom_friction
    
    #zoom in per gesture input
    def move_forward(self):
        self.zoom_velocity += self.forward * 0.05 # 0.04 és sensitivity
    
    ##zoom out per gesture input
    def move_backward(self):
        self.zoom_velocity -= self.forward * 0.05 # 0.04 és sensitivity
    
    #reset position per gesture
    def reset_position(self):
        self.zoom = glm.vec3((0,0,0))
        self.zoom_velocity = glm.vec3((0, 0, 0))
        
    def get_view_matrix(self):
        return glm.lookAt(self.position, self.position + self.forward, self.up)
    
    #projection matrix per les dues perspectives
    def get_projection_matrix(self):
        if self.perspectiva:
            return glm.perspective(glm.radians(FOV), self.aspect_ratio, NEAR, FAR)
        else:
            return glm.ortho(-5, 5, -5, 1, NEAR, FAR)
