from posixpath import split
from PIL import Image, ImageDraw
import numpy as np
import math

class TriangleClass: 
    def __init__(self, RGBColor, Position, v0v1, v0v2, Normal):   
        self.RGBColor = RGBColor
        self.Position = Position
        self.v0v1 = v0v1
        self.v0v2 = v0v2
        self.Normal = Normal

class ScreenDimension:
    def __init__(self, Width, Height):
        self.Width = Width
        self.Height = Height

class DistenceCalc:
    def __init__(self, Distence, Colour):
        self.Distence = Distence
        self.Colour = Colour

class Light:
    def __init__(self, position, RGBColor, brightness):
        self.position = position
        self.RGBColor = RGBColor
        self.brightness = brightness

def normalise(vector): 
    vector = vector / math.sqrt(vector.dot(vector))
    return vector 

def CrossProduct(vec1, vec2):
    return np.array([vec1[1] * vec2[2] - vec1[2] * vec2[1], vec1[2] * vec2[0] - vec1[0] * vec2[2], vec1[0] * vec2[1] - vec1[1] * vec2[0]]) 

def Clamp(Var, Low, max):

    Var = np.where(Var<Low, Low, Var)
    Var = np.where(Var>max, max, Var)
    return Var

def RayTraceTriangle(Object, Origin, Direction):   

    ### Start Code mostly from https://www.scratchapixel.com/lessons/3d-basic-rendering/ray-tracing-rendering-a-triangle/moller-trumbore-ray-triangle-intersection ###
    
    #scalar triple Product
    pvec = CrossProduct(Direction, Object.v0v2) 
    det = Object.v0v1.dot(pvec)

    # det equivelenat to normal.dot(direction). If det = 0 then these are parralel meaning ray will never hit 
    if(det<0):
        return [False]

    # instead of dividing by det we can now * invdet and get same result
    if(det == 0):
        invDet = 0
    else:
        invDet = 1/det

    #Crammer's rule for u
    tvec = Origin - Object.Position[0]
    u = tvec.dot(pvec) * invDet
    if(u<0 or u > 1):
        return [False]

    #Crammer's rule for v
    qvec = CrossProduct(tvec, Object.v0v1)
    v = Direction.dot(qvec) * invDet
    if(v<0 or u + v >1 or v>1):
        return [False]

    t = Object.v0v2.dot(qvec) * invDet
    
    ### End ###
    
    p = Origin + ( t * Direction )

    return [True, p, u, v]


def ShadowRay(Object, Lpos, IntersectionPoint):

    RayDirection = normalise((-Lpos) - IntersectionPoint)

    for i in range(len(Object)):

        RayTraceResult = RayTraceTriangle(Object[i], IntersectionPoint, -RayDirection)

        if (RayTraceResult[0] == False): 
            continue
        else:
            RayVector = IntersectionPoint - RayTraceResult[1]
            RayLength = math.sqrt(RayVector.dot(RayVector))
            if(RayLength < 0.1):
                return True
                
    return False

def Lighting(IntersectionPoint, light, Object, Normal):

    PointLightVector = (-light.position) - IntersectionPoint         

    incidentLight = Clamp(light.RGBColor*light.brightness/(PointLightVector.dot(PointLightVector)), 0, 255) 

    PointLightVector = normalise(PointLightVector)
    
    Normal = normalise(Normal)

    Diffuse = Clamp( abs(Normal.dot(PointLightVector)) , 0, 1 )
    
    Diffuse = Clamp( ((incidentLight) * Diffuse) / 255 , 0, 255 )            

    PixelColour = (Diffuse*Object.RGBColor) + (0.25*Object.RGBColor)

    return PixelColour


def raytracer(x, y, f, Object, camera, light):
    
    RayDirection = normalise(np.array([x, y, f]))
    ColDis = DistenceCalc(None, [0, 0, 0])
    pixelPosition = camera + np.array([x, y, f])
    
    for i in range(len(Object)):

        #BackFace Culling
        NormalNorm = normalise(Object[i].Normal)
        if (NormalNorm.dot(normalise(RayDirection)) > -0.00000000000001):
            continue
            
        RayTraceResult = RayTraceTriangle(Object[i], pixelPosition, RayDirection)

        if (RayTraceResult[0] == False):

            continue

        else:

            IntersectionPoint = RayTraceResult[1]
            PointCameraVector = IntersectionPoint - camera
            length = math.sqrt(PointCameraVector.dot(PointCameraVector))                   

            if(ColDis.Distence == None):
                ColDis.Distence = length
            
            if(length <= ColDis.Distence):

                # set ==0 for plain shading
                if(1==1):
                    ref2 = Lighting(IntersectionPoint, light, Object[i], Object[i].Normal)

                    # comment out for no shadows
                    if (ShadowRay(Object, np.array(light.position), IntersectionPoint) == True):
                        ref2= ref2/ 4

                    ref2 = Clamp(ref2, 0, 255)

                    ColDis.Colour = [int(ref2[0]), int(ref2[1]), int(ref2[2])]

                else:
                    ColDis.Colour = [int(255), int(255), int(255)]

                ColDis.Distence = length

            else:
                continue

    return ColDis.Colour

def render(Screen, scene, light, im, d):

    f=500 
    camera = np.array([0, 0, 120])
    ScreenLocationX = Screen.Width/2 
    ScreenLocationY = Screen.Height/2
    
    for y in range(Screen.Height):
        print(y)
        if(y%10 == 0):

            im.show()

        for x in range(Screen.Width):

            colourValve = raytracer(-(x-ScreenLocationX), -(y-ScreenLocationY), f, scene, camera, light) #, light
            d.point([x, y], fill = (colourValve[0], colourValve[1], colourValve[2]) )
    
    return(im)


def FileRead():

    scene = []
    
    with open("objectLite.txt", "r") as file1:
        ### Start Based of https://stackoverflow.com/questions/44975599/reading-floats-from-file-with-python ###
        VertList = [float(i) for line in file1 for line in line.split() for i in line.split(',')]
        ### End ###
        file1.close()

    x = 0    
    while x < len(VertList):
        point0 = np.array([VertList[x],VertList[x+1],VertList[x+2]])
        point1 = np.array([VertList[x+3],VertList[x+4],VertList[x+5]])
        point2 = np.array([VertList[x+6],VertList[x+7],VertList[x+8]])

        Normal = CrossProduct( (point1 - point0) , (point2 - point0) )

        if(Normal.dot(Normal) == 0 ):
            x+=9
        else:
            # TriangleClass = (Obj Colour, vert Position, edge 1, edge 2, Normal)
            scene.append(TriangleClass(np.array([255,255,255]), [ point0, point1, point2], (point1 - point0), (point2 - point0), Normal)) # 
            x += 9     

    return scene 

def RenderTriangle():

    point0 = np.array([5,0,100])
    point1 = np.array([-5,0,100])
    point2 = np.array([0,5,100])
    Normal = Normal = CrossProduct( (point1 - point0) , (point2 - point0) )
    
    # TriangleClass = (Obj Colour, vert Position, edge 1, edge 2, Normal)
    Triangle = TriangleClass(np.array([255,255,255]), [ point0, point1, point2], (point1 - point0), (point2 - point0), Normal)

    return Triangle

def Scene_Creation(Screen, im, d):

    scene = FileRead()
    
    ### Render Triangle ###
    #Triangle = RenderTriangle()
    #scene = [[Triangle], [Triangle]]

    # LightClass = (Location, Colour, Brightness)
    light = Light(np.array([100, 150, -100]), np.array([255,255,255]), 10000)

    return render(Screen, scene, light, im, d)


def main():

    Screen = ScreenDimension(300, 300)

    im = Image.new("RGB", (Screen.Width, Screen.Height), "black")
    d = ImageDraw.Draw(im)

    im = Scene_Creation(Screen, im, d)

    im.show()
    im.save("image.jpeg")


if __name__ == "__main__":
    main()