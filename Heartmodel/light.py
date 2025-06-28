import glm

#a point light source
class Light:
    def __init__(self, position=(0, 30, 10), color=(1, 1, 1)):
        self.position = glm.vec3(position)
        self.color = glm.vec3(color)
        # intensities
        self.Ia = 0.06 * self.color  # ambient: low-intensity
        self.Id = 0.8 * self.color  # diffuse: directional light
        self.Is = 1.0 * self.color  # specular: reflective highlight
