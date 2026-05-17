import pyglet,math
from pyglet.window import key
import numpy as np
import json

window = pyglet.window.Window(width=1000,height=1000)
keys=key.KeyStateHandler()
window.push_handlers(keys)
batch = pyglet.graphics.Batch()

layers = [pyglet.graphics.Group(order=0),pyglet.graphics.Group(order=1),pyglet.graphics.Group(order=2)]

@window.event
def on_draw():
    window.clear()
    batch.draw()

@window.event
def on_mouse_press(x, y, buttons, modifiers):
    if buttons == 1:
        road.createPoint((x,y))
    if buttons == 4:
        road.checkDotsCollision((x,y))
        road.dragDot((x,y))

@window.event
def on_mouse_drag(x, y,dx,dy, buttons, modifiers):
    if buttons == 4:
        road.dragDot((x,y))

@window.event
def on_mouse_release(x, y, buttons, modifiers):
    if buttons == 4:
        road.held_point=None

@window.event
def on_key_press(symbol,modifiers):
    if symbol ==key.F3:
        road.save("./saves/","save")
    if symbol ==key.F4:
        road.load("./saves/","save")
    if symbol == key.TAB:
        road.switch()


class Road:
    def __init__(self,):
        self.points = []
        self.dots = []
        self.lines= []
        self.curves = None
        self.held_point = None
        self.is_closed = False

    def createDots(self):
        for i in range(len(self.points)):
            new_dot = pyglet.shapes.Circle(radius=5,
                batch=batch,
                color=(100,100,255),
                x=self.points[i][0],
                y=self.points[i][1],
                group=layers[2])
            
            self.dots.append(new_dot)

    def createLines(self):
        if len(self.points) < 2: return

        new_lines_coord = []

        new_lines_coord.append((self.points[0],self.points[1]))
        new_lines_coord.append((self.points[-1],self.points[-2]))

        for i in range(2,len(self.points)-3):
            if (i-1) % 3 == 0: continue
            new_lines_coord.append((self.points[i],self.points[i+1]))
            
        for i in new_lines_coord:
            new_line = pyglet.shapes.Line(
                    x=i[0][0],
                    y=i[0][1],
                    x2=i[1][0],
                    y2=i[1][1],
                    batch=batch,
                    color=(255,255,255),
                    thickness=5,
                    group=layers[1])
            self.lines.append(new_line)

    def createCurves(self):
        if len(self.points) < 4 : return 

        self.curve=pyglet.shapes.BezierCurve(
            *self.points,
            thickness=50,
            color=(100,100,100),
            batch=batch,
            group=layers[0],
            segments=len(self.points)*100)

    def update(self):
        if len(self.points)==0:
            return
        self.dots.clear()
        self.lines.clear()
        self.createDots()
        self.createLines()
        self.createCurves()
        
    
    def createPoint(self,coord):
        if len(self.points)==0:        
            self.points.append(coord)
        elif len(self.points) == 1:
            delta = (
                coord[0]
                -self.points[0][0],
                coord[1]
                -self.points[0][1])
            self.points.append((self.points[0][0]+delta[0]//3,self.points[0][1]+delta[1]//3))
            self.points.append((self.points[0][0]+delta[0]//3*2,self.points[0][1]+delta[1]//3*2))
            self.points.append(coord)
        else: 
            delta = (self.points[-2][0]-self.points[-1][0],self.points[-2][1]-self.points[-1][1])
            new_point =(self.points[-1][0]-delta[0],self.points[-1][1]-delta[1])
            self.points.append(new_point)

            delta = (
                coord[0]
                -self.points[-1][0],
                coord[1]
                -self.points[-1][1])
            self.points.append((self.points[-1][0]+delta[0]//3,self.points[-1][1]+delta[1]//3))
            self.points.append(coord)

    def checkDotsCollision(self,coord):
        for i in range(1,len(self.points)-1):
            if i % 3 == 0: continue
            if (coord[0]-self.points[i][0])**2+(coord[1]-self.points[i][1])**2 <= 10**2:
                self.held_point = i

    def dragDot(self,coord):
        if not self.held_point: return
        self.points[self.held_point] = coord
    
    def save(self,path,name):
        save = {"points":self.points,"is_closed":1 if self.is_closed else 0}
        with open(path+name+".json","w") as save_file:
            json.dump(save,save_file)
    
    def load(self,path,name):
        self.points.clear()
        with open(path+name+".json","r") as save_file:
            save = json.load(save_file)
            for i in save["points"]:
                self.points.append((i[0],i[1]))
            self.is_closed=save["is_closed"]
    
    def close(self):
        if self.is_closed: return
        self.is_closed = True

        delta_coord = [
            (
                self.points[-2][0] - self.points[-1][0],
                self.points[-2][1] - self.points[-1][1]
            ),
            (
                self.points[1][0] - self.points[0][0],
                self.points[1][1] - self.points[0][1]
            )]

        new_points = [
            (
                self.points[-1][0] - delta_coord[0][0],
                self.points[-1][1] - delta_coord[0][1]
            ),
            (
                self.points[0][0] - delta_coord[1][0],
                self.points[0][1] - delta_coord[1][1]
            ),
            (
                self.points[0][0],
                self.points[0][1]
            )
        ]
        for i in new_points:
            self.points.append(i)
    
    def open(self):
        if not self.is_closed: return
        self.is_closed = False
        for i in range(3):
            self.points.pop()

    def switch(self):
        if self.is_closed: self.open()
        else: self.close()

road = Road()

def update(data):
    road.update()

pyglet.clock.schedule_interval(update,1/60.0)

pyglet.app.run()