import pyglet,math
from pyglet.window import key
import numpy as np

window = pyglet.window.Window(width=1000,height=1000,style=pyglet.window.Window.WINDOW_STYLE_BORDERLESS)
keys=key.KeyStateHandler()
window.push_handlers(keys)
batch = pyglet.graphics.Batch()

worldObjects = []

class Car:
    def __init__(self,x,y,objList):
        image = pyglet.image.load("./sprites/car.png")
        image.anchor_x=image.width//2
        image.anchor_y=image.height//2
        self.sprite = pyglet.sprite.Sprite(
            image,
            x=x,
            y=y,
            batch=batch,
        )

        self.sprite.scale=0.15

        objList.append(self.sprite)
        
        self.vector = np.zeros(2)

        self.rotation_speed=0

        self.speed = 0
        self.max_speed=10
        self.isDriving=False
        
    def Break(self):
        delta_speed = self.speed * 0.05
        if delta_speed < 0.03: delta_speed=0.03
        self.speed-=delta_speed
        if self.speed < 0: self.speed=0

    def Gas(self):
        self.isDriving=True
        if self.speed < self.max_speed:
            self.speed += 0.5
        
        return
    def Rotate(self,direction):
        self.sprite.rotation +=self.rotation_speed * -1 if direction == "left" else self.rotation_speed

        if self.sprite.rotation >= 360: self.sprite.rotation-=360
        elif self.sprite.rotation < 0: self.sprite.rotation+=360

        rad = math.radians(self.sprite.rotation)
        vector_x = round(math.sin(rad),3)
        vector_y = round(math.cos(rad),3)
        self.vector = (vector_x,vector_y)
    def Update(self):
        self.sprite.x += self.vector[0] * self.speed
        self.sprite.y += self.vector[1] * self.speed
        if not self.isDriving and self.speed > 0:
            self.speed -= 0.1
        self.rotation_speed = self.speed * 0.6
        self.isDriving=False
        return

class Camera:
    def __init__(self,objList):
        self.objList=objList
        
    def Move(self,delta):
        for i in self.objList:
            i.x-=delta[0]
            i.y-=delta[1]
            
cam = Camera(worldObjects)
car = Car(500,500,worldObjects)
@window.event
def on_draw():
    window.clear()
    batch.draw()

@window.event
def on_mouse_motion(x, y, dx, dy):
    cam.Move((dx,dy))

@window.event
def on_activate():
    window.set_exclusive_mouse(True)

@window.event
def on_deactivate():
    window.set_exclusive_mouse(False)

def update(data):
    if keys[key.D] or keys[key.RIGHT]:
        car.Rotate("right")
    elif keys[key.A] or keys[key.LEFT]:
        car.Rotate("left")
    if keys[key.S]  or keys[key.DOWN]:
        car.Break()
    elif keys[key.W] or keys[key.UP]:
        car.Gas()

    
    car.Update()


pyglet.clock.schedule_interval(update,1/60.0)


pyglet.app.run()