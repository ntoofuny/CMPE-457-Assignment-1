# Image manipulation
#
# You'll need Python 2.7 and must install these packages:
#
#   numpy, PyOpenGL, Pillow
#
# Note that file loading and saving (with 'l' and 's') do not work on
# Mac OSX, so you will have to change 'imgFilename' below, instead, if
# you want to work with different images.
#
# Note that images, when loaded, are converted to the YCbCr
# colourspace, and that you should manipulate only the Y component of
# each pixel when doing intensity changes.

#foo - imp.load_source('module.name')

import sys, os, numpy, math
import PIL as gl
import numpy as np
try:  # Pillow
    from PIL import Image
except:
    print('Error: Pillow has not been installed.')
    sys.exit(0)

try:  # PyOpenGL
    from OpenGL.GLUT import *
    from OpenGL.GL import *
    from OpenGL.GLU import *

except:
    print('Error: PyOpenGL has not been installed.')
    sys.exit(0)

# Globals

windowWidth = 600  # window dimensions
windowHeight = 800

localHistoRadius = 5  # distance within which to apply local histogram equalization

# Current image

imgDir = 'images'
imgFilename = 'mandrill.png'

currentImage = Image.open(os.path.join(imgDir, imgFilename)).convert('YCbCr').transpose(Image.FLIP_TOP_BOTTOM)
tempImage = None

# File dialog (doesn't work on Mac OSX)

if sys.platform != 'darwin':
    import Tkinter, tkFileDialog

    root = Tkinter.Tk()
    root.withdraw()


# Apply brightness and contrast to tempImage and store in
# currentImage.  The brightness and constrast changes are always made
# on tempImage, which stores the image when the left mouse button was
# first pressed, and are stored in currentImage, so that the user can
# see the changes immediately.  As long as left mouse button is held
# down, tempImage will not change.

def addToPixel(a, pixel):
    return [x + a for x in pixel]


def applyBrightnessAndContrast(brightness, contrast):
    width = currentImage.size[0]
    height = currentImage.size[1]

    srcPixels = tempImage.load()
    dstPixels = currentImage.load()

    # YOUR CODE HERE

    # loop through pixels in image
    for i in range(0,currentImage.width):
        for j in range(0,currentImage.height):#loop through image
            #get intensity and other tuple values from pixel data
            [y, Cr, Cb] = srcPixels[i, j]
            #equations for adjusting brightness and contrast
            y = contrast*y
            y = y + brightness
            #reassign updated tuple with new intensity to dstPixel
            dstPixels[i,j] = tuple([y, Cr, Cb])


    print("adjust brightness = " + str(brightness) + ", contrast = " + str(contrast))


# Perform local histogram equalization on the current image using the given radius.
#http://watkins.cs.queensu.ca/~jstewart/457/notes/05-yuv-histo-notes.txt
def performHistoEqualization(radius):
    #how does the function get called if nto a mouse click?
    pixels = currentImage.load()
    width = currentImage.size[0]
    height = currentImage.size[1]

    pixelTemp = currentImage.load()


    print("perform local histogram equalization with radius:" + str(radius))
    print("width: " + str(width) + "height: " + str(height))


# Scale the tempImage by the given factor and store it in
# currentImage.  Use backward projection.  This is called when the
# mouse is moved with the right button held down.
    intensityArray = [] #create array to hold intensities of pixels
    numPixels = 0
    # loop through image
    for i in range(0, width):
        for j in range(0, height):
            # at every pixel, get the radius pixels
            radX, radY = getNeighborhood(i,j, radius, height, width)
            for pixX in radX: #for every pixel in the radius, perform histogram equalization
                for pixY in radY:
                    [y, Cr, Cb] = pixels[pixX, pixY] #get pixel values from temp image
                    numPixels = numPixels + 1
                    intensityArray.append(y)

            # create dictionary from array of all intensity. This will get rid of duplicate values
            histDict = dict.fromkeys(intensityArray)

            # fill dictionary with pixel coordinate with that frequency
            for key in histDict:
                histDict[key] = getTofR(numPixels, getN_r(intensityArray,  key))

            #get tuple values from reference image version
            [y, Cr, Cb] = pixels[i, j]
            #get T(r) from dictionary and assign as y
            y = int(histDict[y])
            #assign new pixel tuple to temp image version
            pixelTemp[i, j] = tuple([y, Cr, Cb])

            #go through all pixels in the radius area and replace r with T(r)
            #loop through pixels in nested loop to change them within radius
            numRad = 0
            for pixX in radX:
                for pixY in radY:
                    #get the number of pixels in the radius area
                    pixels[pixX, pixY]
                    numRad = numRad + 1


#compute N_r values which is the sum of the all pixels with AT MOST intensity r
def getN_r(intensityArray, r):
    frequency = 0
    for y in intensityArray:
        if y <= r:
            frequency = frequency+1
    return frequency

def getTofR(N, N_r):
    #function for T(r) as outlined in notes
    N = float(N)
    N_r = float(N_r)
    s = ((256/N*N_r))-1
    return s

def getNeighborhood(x,y, radius, height, width):

    radX = range(x-radius, radius + x)
    radX = [item for item in radX if  0<=item<width] #don't let the radius go out of image range

    radY = range(y-radius, radius + y)
    radY = [item for item in radY if 0<=item<height]


    return radX, radY

def scaleImage(factor):

#consider the image as a matrix and perform a matrix transformation
#use im.transform

    width = currentImage.size[0]
    height = currentImage.size[1]

    srcPixels = tempImage.load()
    dstPixels = currentImage.load()

    # YOUR CODE HERE
# Set up the display and draw the current image

    for i in range(0, currentImage.width):
        for j in range(0, currentImage.height):  # loop through image
            # use back projection to set the destination pixels to the factored source coordinates
            #I would have preferred to use an if-then clause to assign pixel values but I could not figure out
            #the proper boundary conditional so I used a try-except because it also works
            try:
                dstPixels[i, j] = srcPixels[i/factor, j/factor]
            # if the pixel in the reference image is out of range, replace the pixels with white
            except:
                dstPixels[i, j] = (255, 128, 128)



def display():
    # Clear window

    glClearColor(1, 1, 1, 0)
    glClear(GL_COLOR_BUFFER_BIT)

    # rebuild the image

    img = currentImage.convert('RGB')

    width = img.size[0]
    height = img.size[1]

    # Find where to position lower-left corner of image

    baseX = (windowWidth - width) / 2
    baseY = (windowHeight - height) / 2

    glWindowPos2i(baseX, baseY)

    # Get pixels and draw

    imageData = numpy.array(list(img.getdata()), numpy.uint8)

    glDrawPixels(width, height, GL_RGB, GL_UNSIGNED_BYTE, imageData)

    glutSwapBuffers()


# Handle keyboard input

def keyboard(key, x, y):
    global localHistoRadius

    if key == '\033':  # ESC = exit
        sys.exit(0)

    elif key == 'l':
        if sys.platform != 'darwin':
            path = tkFileDialog.askopenfilename(initialdir=imgDir)
            if path:
                loadImage(path)

    elif key == 's':
        if sys.platform != 'darwin':
            outputPath = tkFileDialog.asksaveasfilename(initialdir='.')
            if outputPath:
                saveImage(outputPath)

    elif key == 'h':
        performHistoEqualization(localHistoRadius)

    elif key in ['+', '=']:
        localHistoRadius = localHistoRadius + 1
        print
        'radius =', localHistoRadius

    elif key in ['-', '_']:
        localHistoRadius = localHistoRadius - 1
        if localHistoRadius < 1:
            localHistoRadius = 1
        print
        'radius =', localHistoRadius

    else:
        print
        'key =', key  # DO NOT REMOVE THIS LINE.  It will be used during automated marking.

    glutPostRedisplay()


# Load and save images.
#
# Modify these to load to the current image and to save the current image.
#
# DO NOT CHANGE THE NAMES OR ARGUMENT LISTS OF THESE FUNCTIONS, as
# they will be used in automated marking.


def loadImage(path):
    global currentImage

    currentImage = Image.open(path).convert('YCbCr').transpose(Image.FLIP_TOP_BOTTOM)


def saveImage(path):
    global currentImage

    currentImage.transpose(Image.FLIP_TOP_BOTTOM).convert('RGB').save(path)


# Handle window reshape


def reshape(newWidth, newHeight):
    global windowWidth, windowHeight

    windowWidth = newWidth
    windowHeight = newHeight

    glutPostRedisplay()


# Mouse state on initial click

button = None
initX = 0
initY = 0


# Handle mouse click/release

def mouse(btn, state, x, y):
    global button, initX, initY, tempImage

    if state == GLUT_DOWN:
        tempImage = currentImage.copy()
        button = btn
        initX = x
        initY = y
    elif state == GLUT_UP:
        tempImage = None
        button = None

    glutPostRedisplay()


# Handle mouse motion

def motion(x, y):
    if button == GLUT_LEFT_BUTTON:

        diffX = x - initX
        diffY = y - initY

        applyBrightnessAndContrast(255 * diffX / float(windowWidth), 1 + diffY / float(windowHeight))

    elif button == GLUT_RIGHT_BUTTON:

        initPosX = initX - float(windowWidth) / 2.0
        initPosY = initY - float(windowHeight) / 2.0
        initDist = math.sqrt(initPosX * initPosX + initPosY * initPosY)
        if initDist == 0:
            initDist = 1

        newPosX = x - float(windowWidth) / 2.0
        newPosY = y - float(windowHeight) / 2.0
        newDist = math.sqrt(newPosX * newPosX + newPosY * newPosY)

        scaleImage(newDist / initDist)

    glutPostRedisplay()


# Run OpenGL
glutInit()
glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
glutInitWindowSize(windowWidth, windowHeight)
glutInitWindowPosition(50, 50)
glutCreateWindow('imaging')
glutDisplayFunc(display)
glutKeyboardFunc(keyboard)
glutReshapeFunc(reshape)
glutMouseFunc(mouse)
glutMotionFunc(motion)

glutMainLoop()
scaleImage(5)
