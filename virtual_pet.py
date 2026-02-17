from cmu_graphics import *
import random


def onAppStart(app):
    # ---------- Game State ----------
    app.background='lightskyblue'
    app.gameOver = False
    app.steps = 0
    app.lastActionStep = 0
    app.stepsPerSecond = 10
    app.coins = 2000
    app.foodPrice = 10
    app.currency = 'currency.png'
    app.showWarning = False
    app.warningShown = False
    app.flusteredTimer = 0
    app.flusteredDuration = 5
    app.statColor = 'green'

    #------------Pet Info----------------
    app.imageUrls = [f'sprites/eggToot{i}.png' for i in range(6)]
    app.imageIndex = 0
    app.petName = ''
    app.startButtonSize = 30
    app.buttonX = 275
    app.buttonY = 175
    app.painting = 'painting.png'

    app.chickX, app.chickY = 200, 300
    app.onBed = False
    app.chickColors = ['gold','green','red','blue','pink','purple']
    app.colorIndex = 0
    app.currentColors = app.chickColors[app.colorIndex]
    app.blink = False
    app.flustered = False
    app.halo = 'halo.png'
    # ---------- Stats ----------
    app.stats = {'hunger':50,'happiness':50,'energy':50,'toilet':50}
    app.symbols = {'hunger': 'hungerSymbol.png','happiness': 'happinessSymbol.png','energy': 'sleepSymbol.png','toilet': 'toiletSymbol.png'}
    
    app.health = sum(app.stats.values()) / len(app.stats)
    app.heart = 'heart.png'
    app.hearts = []

    # ---------- Buttons ----------
    app.homeButton = 'homeButton.png'
    app.homeButtonCoordinates = (20,20)
    app.informationButtonCoordinates=(50,20)
    app.screenButtonCoordinates = [(50,350),(150,350),(250,350),(350,350)]
    app.screenButtonSymbols = [
        app.symbols['happiness'],
        app.symbols['hunger'],
        app.symbols['toilet'],
        app.symbols['energy']
    ]

    # ---------- Kitchen ----------
    app.exit = 'exitSymbol.png'
    app.shop = 'shopSymbol.png'
    app.foodList = ['carrot.png','banana.png','strawberry.png','apple.png','cookie.png','burger.png']
    app.foodCount = []
    app.foodX, app.foodY = None, None
    app.isFoodPressed = False
    app.foodItem = None

    # ---------- Bedroom ----------
    app.lamp = 'lamp.png'
    app.lampX, app.lampY = 360,250
    app.lightsOut = False

    # ---------- Mini Game ----------
    app.stack = []                 # list of (x, width)
    app.baseWidth = 160
    app.currentWidth = app.baseWidth
    app.currentX = 120
    app.currentY = 80
    app.isdropping = False
    app.dropSpeed = 8
    app.currentY = 80
    app.direction = 1
    app.speed = 4
    app.minigameOver = False
    app.score = 0

#############################################################################
# -------------------------- UTILITY FUNCTIONS ----------------------------#
#############################################################################

def distance(x1,y1,x2,y2):
    return ((x2-x1)**2 +(y2-y1)**2)**0.5

def goHome(app,mouseX,mouseY):
    x,y = app.homeButtonCoordinates
    if distance(mouseX,mouseY,x,y) < 40:
        setActiveScreen('game')
        app.lightsOut = False
def showInformation(app,mouseX,mouseY):
    x,y=app.informationButtonCoordinates
    if distance(mouseX,mouseY,x,y)<10:
        setActiveScreen('information')
def drawInformationButton(app):
    #info button
    x,y=app.informationButtonCoordinates
    drawCircle(x,y,10,fill='navy')
    drawLabel('i',x,y,size=16,fill='white',italic=True)
#############################################################################
# ---------------------------- PET ACTIONS --------------------------------#
#############################################################################

def feeding(app):
    if app.stats['hunger'] < 100:
        if app.foodItem in ['cookie.png','burger.png']:
            gain = 10
        else:
            gain=15
        app.stats['hunger'] = min(app.stats['hunger'] + gain, 100)

def sleeping(app):
    if app.lightsOut == True and app.steps % 5 == True:
        app.stats['energy'] = min(app.stats['energy'] + 3,100)
        app.stats['hunger'] = max(app.stats['hunger']-1,1)
        app.stats['happiness'] = max(app.stats['happiness']-1,1)
    if app.stats['energy'] == 100:
        app.lightsOut = False

def playing(app,mouseX,mouseY):
    if app.steps == app.lastActionStep:
        return
    if app.stats['happiness'] < 100 and app.stats['energy'] > 5:
        app.stats['happiness'] = min(app.stats['happiness']+5,100)
        app.stats['energy'] = max(app.stats['energy']-1,1)
        app.hearts.append((mouseX,mouseY-50))
        app.lastActionStep = app.steps
    app.flustered = True
    app.flusteredTimer = 0

def usingToilet(app):
    app.stats['toilet'] = min(app.stats['toilet']+10,100)
    app.stats['happiness'] = max(app.stats['happiness']-1,1)
    app.flustered = True
    app.flusteredTimer = 0

#############################################################################
# ---------------------------- STATS FUNCTIONS ----------------------------#
#############################################################################

def drawStatsBar(app,x,y,symbol,amount):
    symbolX = x-15
    symbolY = y+5
    fillColor = 'red' if amount<30 else 'green'
    drawRect(x,y,105,22,fill='darkgrey',border='gold')
    drawRect(x+2,y+3,amount,17,fill=fillColor)
    drawImage(symbol,symbolX,symbolY,width=40,height=40,align='center')

def updateStats(app):
    # Give coins if health is good
    if app.health >= 80 and app.steps%10 == 0:
        app.coins += 2
    if app.showWarning:
        return
    # Decay stats every 200 steps
    if app.steps > 0 and app.steps % 200 == 0 and not app.lightsOut:
        for stat in app.stats:
            app.stats[stat] = max(app.stats[stat] - 5, 1)

def updateChickExpression(app):
    if app.lightsOut:
        app.blink = True
    elif app.steps % 15 == 0:
        app.blink = True
    else:
        app.blink = False

def updateFlustered(app):
    if app.flustered:
        app.flusteredTimer += 1
        if app.flusteredTimer > app.flusteredDuration:
            app.flustered = False
            app.flusteredTimer = 0

def updateTime(app):
    if app.showWarning:
        updateChickExpression(app)
        return
    app.steps += 1
    updateStats(app)
    app.health = sum(app.stats.values()) / len(app.stats)
    updateChickExpression(app)
    checkLose(app)
    checkWin(app)
    updateFlustered(app)

    if app.health < 25 and not app.showWarning and not app.warningShown:
        app.showWarning = True

def resetGame(app):
    app.stats = {'hunger':50, 'energy':50, 'toilet':50, 'happiness':50}
    app.coins = 2000
    app.health = 50
    app.steps = 0
    app.lightsOut = False
    app.hearts = []
    app.foodCount = []
    app.isFoodPressed = False
    app.foodItem = None
    app.foodX, app.foodY = None, None
    app.petName = ''
    app.gameOver = False
    app.showWarning = False
    app.flustered = False
    app.blink = False

def checkLose(app):
    for stat in app.stats:
        if app.stats[stat] <= 1 and not app.gameOver:
            setActiveScreen('lose')
            app.gameOver = True

def checkWin(app):
    if app.coins >= 3000 and not app.gameOver:
        setActiveScreen('win')
        app.gameOver = True

#############################################################################
# ---------------------------- PET DRAWING --------------------------------#
#############################################################################

def drawToot(app,x,y):
    # Body
    drawOval(x, y, 95, 110, fill=app.currentColors)
    drawOval(x, y+10, 105, 90, fill=app.currentColors)
    # Beak & feet
    drawOval(x, y-12, 12, 10, fill='orange')
    drawRect(x-25, y+45, 20, 12, fill='orange', align='center')
    drawRect(x+25, y+45, 20, 12, fill='orange', align='center')
    # Wings
    drawOval(x-45, y+10, 30, 50, fill=app.currentColors, rotateAngle=25)
    drawOval(x+45, y+10, 30, 50, fill=app.currentColors, rotateAngle=-25)
    # Flustered blush/eyes
    if app.flustered:
        drawOval(x-22,y-5,20,10,fill='lightcoral',opacity=80)
        drawOval(x+22,y-5,20,10,fill='lightcoral',opacity=80)
        drawLine(x-30,y-25,x-10,y-20,lineWidth=3)
        drawLine(x-30,y-15,x-10,y-20,lineWidth=3)
        drawLine(x+30,y-25,x+10,y-20,lineWidth=3)
        drawLine(x+30,y-15,x+10,y-20,lineWidth=3)
    if app.health<25:
        drawOval(x-22,y-5,20,10,fill='lightcoral',opacity=80)
        drawOval(x+22,y-5,20,10,fill='lightcoral',opacity=80)
    if not app.flustered:
        if not app.blink:
            drawCircle(x+20, y-20, 10)
            drawCircle(x-20, y-20, 10)
            drawCircle(x+18, y-25, 4, fill='white')
            drawCircle(x-18, y-25, 4, fill='white')
        else:
            drawLine(x-10, y-20, x-30, y-20, lineWidth=3)
            drawLine(x+10, y-20, x+30, y-20, lineWidth=3)
    # Feather tuft
    drawOval(x, y-57, 12, 18, fill=app.currentColors, rotateAngle=35)



#############################################################################
#start screen 
#############################################################################
def start_onStep(app):
    # Increase the image index to display the next image in the sequence
    # Mod by len(app.imageUrls) to wrap around at the end of the list
    app.imageIndex = (app.imageIndex + 1) % len(app.imageUrls)

def start_redrawAll(app):
    drawLabel('Name your pet to start!',200,100,size=25,fill='white',bold=True)
    drawOval(200,300,120,110,fill='White')
    drawOval(150,320,100,90,fill='White')
    drawOval(250,320,100,90,fill='White')
    drawCircle(110,350,35,fill='white')
    drawOval(290,330,100,80,fill='white')
    drawCircle(125,370,30,fill='white')
    drawOval(170,365,90,80,fill='white')
    drawOval(260,360,120,70,fill='white')
    drawCircle(220,365,35,fill='white')
    drawOval(200,335,80,30,opacity=30)
    drawImage(app.imageUrls[app.imageIndex],200,300,align='center')
    drawRect(70,150,150,25,fill='honeydew',border='black',opacity=50)
    #draws pet's name
    drawLabel(app.petName,75,160,align='left',size=15)
    drawCircle(app.buttonX,app.buttonY,app.startButtonSize,fill='purple')
    drawLabel('Start',app.buttonX,app.buttonY,fill='white',bold=True,align='center')

def start_onKeyPress(app, key):
    if len(key)==1 and len(app.petName)<10:
        app.petName+=key
        print(app.petName)
    if key=='backspace':
        app.petName=app.petName[:-1]
    if key=='enter':
        setActiveScreen('tutorial')

def start_onMousePress(app,mouseX,mouseY):
    dist=distance(mouseX,mouseY,app.buttonX,app.buttonY)
    if dist<30:
        setActiveScreen('tutorial')

#############################################################################
#Tutorial
#############################################################################
def tutorial_onStep(app):
    pass
def tutorial_redrawAll(app):

    drawLabel('How To Play',200,30,size=24, bold=True)
    for i in range(4):
        y=80+50*i
        symbol=app.screenButtonSymbols[i]
        drawImage(symbol,60,y,align='center',width=40,height=40)
    drawLabel("Mini Game - Earn coins & boost happiness",210,80)
    drawLabel("Kitchen - Buy food and feed your pet",210,130)
    drawLabel("Bathroom - Tap stomach to use restroom",210,180,)
    drawLabel("Bedroom - Click on lamp to sleep.",210,230)
    drawCircle(60,270,10,fill='navy')
    drawLabel('i',60,270,size=16,fill='white',italic=True)
    drawLabel("Provides information on pet and rooms",210,270)
    drawLabel("Win - earn 3000 coins and keep pet healthy",200,300)
    drawLabel("<>Change pet color - Click left and right arrows",200,320)
    drawLabel("Press ENTER to Start",200,370,size=16,italic=True)

def tutorial_onKeyPress(app,key):
    if key=='enter':
        setActiveScreen('game')
###########################################################################################
#Information tab
###########################################################################################
def information_onStep(app):
    pass
def information_redrawAll(app):
    drawLabel('How To Play',200,30,size=24, bold=True)
    for i in range(4):
        y=80+50*i
        symbol=app.screenButtonSymbols[i]
        drawImage(symbol,60,y,align='center',width=40,height=40)
    drawLabel("Mini Game - Earn coins & boost happiness",210,80)
    drawLabel("Kitchen - Buy food and feed your pet",210,130)
    drawLabel("Bathroom - Tap stomach to use restroom",210,180)
    drawLabel("Bedroom - Click on lamp to sleep.",210,230)
    drawLabel("<> Change pet color - Click left and right arrows",200,270)
    drawLabel("Win - earn 3000 coins and keep pet healthy",200,300)
    homeX,homeY=app.homeButtonCoordinates
    drawImage(app.homeButton,homeX,homeY,align='center',width=30,height=30)
    drawInformationButton(app)

def information_onMousePress(app,mouseX,mouseY):
    goHome(app,mouseX,mouseY)






###########################################################################################
#Game screen
###########################################################################################
def drawHearts(app):
    newHearts=[]
    for x,y in app.hearts:
        if y>200:
            newHearts.append((x,y-15))
    app.hearts=newHearts
    

def game_onStep(app):
    updateTime(app)
    drawHearts(app)

   
def game_redrawAll(app):
    drawRect(0,0,400,300,fill='honeydew')
    drawRect(0,250,400,150,fill=gradient('burlywood','peru',start='left'))
    for x in range(0,400,50):
        drawLine(x,250,x,400,fill='sienna',opacity=30)
    drawImage(app.painting,90,90,width=80,height=80,align='center',opacity=90)
# backrest
    drawRect(20,135,25,55,fill=rgb(154,39,35))
    drawRect(40,135,100,80,fill=rgb(174,57,57))

# side of couch
    drawRect(0,275,50,60,fill=rgb(142,36,34),align='left-bottom')

# left armrest and leg
    drawRect(0,190,65,25,fill=rgb(113,29,23))
    drawRect(50,215,30,60,fill=rgb(216,62,71))
    drawCircle(61,210,20,fill=rgb(216,62,71))

# cushion
    drawRect(80,215,80,35,fill=rgb(174,57,57))
 # couch shadow
    drawOval(55,255,120,12,fill='black',opacity=15)
      
# bottom part (now sits right on the floor)
    drawRect(50,250,110,25,fill=rgb(216,62,71))
    drawLine(80,250,160,250,fill='darkred')

# right leg
    drawRect(140,190,35,25,fill=rgb(113,29,23))
    drawRect(160,215,30,60,fill=rgb(216,62,71))
    drawCircle(180,210,20,fill=rgb(216,62,71))

    drawRect(75,215,85,5,fill=rgb(216,62,71))
    
    drawRect(40,280,320,100,fill='darkOliveGreen')
    drawRect(60,300,280,60,fill=None,border='olive')
    
    #lamp
    drawCircle(370,130,70,fill='gold',opacity=10)
    drawLine(170,160,285,160,fill='saddlebrown',lineWidth=8)
    drawOval(370,250,50,20,fill=rgb(254,186,81))
    drawOval(370,60,60,10,fill=rgb(249,197,136))
    drawPolygon(340,60,400,60,390,30,350,30,fill='darkOliveGreen')
    drawLine(370,250,370,60,fill='peru')
    

    #tv
    drawLine(300,200,285,180,fill='cadetblue',lineWidth=3)
    drawLine(300,200,315,180,fill='cadetblue',lineWidth=3)
    drawCircle(300,200,10,fill='red',border='black')
    drawRect(250,200,100,60,fill='orange',border='gold',borderWidth=5)
    drawRect(260,210,60,40,fill='lightskyblue',border='black',borderWidth=5)
    drawLine(323,200,323,260,fill='chocolate',lineWidth=2)
    drawLine(325,200,325,260,lineWidth=2)
    drawCircle(335,220,6,fill='plum',border='black',borderWidth=1)
    drawCircle(335,240,6,fill='green',border='black',borderWidth=1)

    drawRect(175,52,105,110,fill=None, border='peru',borderWidth=10)
    for x in range(2):
        for y in range(2):
            cx=180+45*x
            cy=60+45*y
            drawLine(cx+40,cy+5,cx+5,cy+45,fill=rgb(193,238,254),lineWidth=10)
            drawRect(cx,cy,50,50,fill='lightblue',opacity=80,border='saddlebrown',borderWidth=5)

    
    drawLabel(f'{app.coins}',365,12,size=16,fill='black',bold=True)
    drawImage(app.currency,330,15,width=40,height=40,align='center')
    
    if len(app.petName)==0:
        petName='Toot Toot'
    else:
        petName=app.petName
    drawLabel(f'Meet your pet {petName}',200,25,fill='Black',size=20,bold=True)
    drawToot(app,app.chickX,app.chickY)
    for coordinates in app.screenButtonCoordinates:
        x,y=coordinates
        drawCircle(x,y,20,fill='gold')
    
    for i in range(4):
        x,y=app.screenButtonCoordinates[i]
        symbol=app.screenButtonSymbols[i]
        drawImage(symbol,x,y,align='center',width=40,height=40)
    
   
    
    for cor in app.hearts:
        x,y=cor
        drawImage(app.heart,x,y,width=30,height=30,align='center')
    
    
    y=75 
    for stat in app.stats:
        drawStatsBar(app,30,y,app.symbols[stat],app.stats[stat])
        y+=50
    
    if app.showWarning == True and app.health<25:
        drawRect(200, 200, 350, 300, align='center', fill='white', opacity=90, border='red')
        drawLabel("Oh no! Your pet's health is extremely low", 200, 100, size=14, bold=True)
        drawLabel("They require treatment in order to restore its health", 200, 130, size=14, bold=True)

        # Vet buttons
        drawRect(120, 300, 100, 25, fill='green', border='gold', align='center')
        drawLabel('1000', 120, 300, fill='gold', bold=True)
    
        drawRect(280, 300, 100, 25, fill='darkRed', border='gold', align='center')
        drawLabel('Ignore', 280, 300, fill='gold')

        # Display currency
        drawImage(app.currency, 100, 300, align='center', width=25, height=25)
    drawInformationButton(app)

def findCircle(app,mouseX,mouseY):  
    if app.showWarning:
        return  
    chosenCircle=None
    for coordinates in app.screenButtonCoordinates:
        x,y=coordinates
        if distance(x,y,mouseX,mouseY)<20:
            chosenCircle=x,y
    if chosenCircle==(150,350):
        setActiveScreen("kitchen")
    elif chosenCircle==(250,350):
        setActiveScreen("bathroom")
    elif chosenCircle==(350,350):
        setActiveScreen("bedroom")
    elif chosenCircle==(50,350):
        setActiveScreen("miniGame")
    
def vetVisit(app, mouseX, mouseY):
    if not app.showWarning or app.health > 25:
        return

    # Only check clicks inside the warning box
    if not (25 < mouseX < 375 and 150 < mouseY < 350):
        return

    if distance(120, 300, mouseX, mouseY) < 50:  # Visit vet button
        if app.coins >= 1000:
            app.coins -= 1000
            for stat in app.stats:
                app.stats[stat] = min(app.stats[stat] + 40, 100)
        app.showWarning = False
        app.warningShown = False  # reset so the warning can appear later if health drops again

    elif distance(280, 300, mouseX, mouseY) < 50:  # Ignore button
        app.showWarning = False
        app.warningShown = True  # mark it ignored so it won't immediately pop back


def game_onKeyPress(app, key):
    if key == 'right':
        app.colorIndex = (app.colorIndex + 1) % len(app.chickColors)

    elif key == 'left':
        app.colorIndex = (app.colorIndex - 1) % len(app.chickColors)

    app.currentColors = app.chickColors[app.colorIndex]


def game_onMousePress(app, mouseX, mouseY):
    vetVisit(app, mouseX, mouseY)  # Call vetVisit when a click occurs
    findCircle(app, mouseX, mouseY)
    if distance(mouseX, mouseY, app.chickX, app.chickY) < 40:
        playing(app, mouseX, mouseY)
    showInformation(app,mouseX,mouseY)
       


        
#######################################################################
#mini game
#######################################################################
# -------------------------------
# MINI GAME: STACK THE CAKE
# -------------------------------

PASTEL_COLORS = ['pink', 'lightblue', 'lavender', 'peachpuff']

# ---------- Game Setup ----------
def miniGame_onScreenActivate(app):
    app.stack = []  # list of (x, width, y, color)
    app.baseWidth = 160
    app.currentWidth = app.baseWidth
    app.currentX = 120
    app.currentY = 100
    app.currentColor = random.choice(PASTEL_COLORS)
    app.direction = 1
    app.speed = 10
    app.minigameOver = False
    app.score = 0
    app.dropping = False
    app.landingFrame = 0
    

    # first pancake base at bottom
    baseY = 350
    app.stack.append((120, 160, baseY, 'goldenrod'))



# ---------- Game Step ----------
def miniGame_onStep(app):
    if app.minigameOver:
        return

    if not app.dropping:
        # move pancake horizontally at top
        app.currentX += app.speed * app.direction
        if app.currentX <= 0 or app.currentX + app.currentWidth >= 400:
            app.direction *= -1
    else:
        # vertical falling
        lastX, lastWidth, lastY, _ = app.stack[-1]
        targetY = lastY - 2  # 20px height + 2px gap

        if app.currentY + 20 < targetY:
            app.currentY += 10  # fall speed
    
        else:
            # landing finished
            app.dropping = False
            app.landingFrame = 0

            # calculate overlap
            overlapLeft = max(app.currentX, lastX)
            overlapRight = min(app.currentX + app.currentWidth,
                                lastX + lastWidth)
            overlapWidth = overlapRight - overlapLeft

            if overlapWidth <= 0:
                app.minigameOver = True
                return

            # keep only overlap part
            app.currentWidth = overlapWidth
            app.currentX = overlapLeft

            # add to stack (store y + color)
            app.stack.append((app.currentX, app.currentWidth, app.currentY, app.currentColor))
            app.score += 1

            # reset next pancake at top
            app.currentX = 120
            app.currentY = 100
            app.currentWidth = app.baseWidth
            app.currentColor = random.choice(PASTEL_COLORS)


# ---------- Mouse Press ----------
def miniGame_onMousePress(app, mouseX, mouseY):
    if app.minigameOver:

    # Play Again
        if 120 <= mouseX <= 280 and 230 <= mouseY <= 270:
            miniGame_onScreenActivate(app)

    # Home
        if 120 <= mouseX <= 280 and 290 <= mouseY <= 330:
            setActiveScreen('game')

    # start dropping
    app.dropping = True


# ---------- Draw ----------
def miniGame_redrawAll(app):
    drawRect(0,0,400,400,fill='lightSalmon')
    drawLabel("Stack the Cake!", 200, 30, size=20, bold=True)
    drawLabel(f"Score: {app.score}", 200, 55)

    # draw stacked pancakes
    for x, width, y, color in app.stack:
        drawRect(x, y, width, 20, fill=color, border='bisque',borderWidth=1)
    

    # draw moving pancake
    if not app.minigameOver:
        drawRect(app.currentX-1, app.currentY+20, app.currentWidth+2, 4, fill='gray', opacity=30)  # shadow
        drawRect(app.currentX, app.currentY, app.currentWidth, 20, fill=app.currentColor, border='pink',borderWidth=1)
        

    if app.minigameOver:
        drawRect(0, 0, 400, 400, fill='black', opacity=60)

        drawLabel("GAME OVER", 200, 150, size=36, bold=True, fill='white')
        drawLabel(f"Final Score: {app.score}", 200, 190, size=20, fill='white')

        drawRect(120, 230, 160, 40, fill='lightGreen')
        drawLabel("Play Again", 200, 250)

        drawRect(120, 290, 160, 40, fill='lightCoral')
        drawLabel("Home", 200, 310)



###################################################################
#kitchen
######################################################################
def kitchen_onStep(app):
    updateTime(app)

def findNumOfItem(app,foodType,y):
    amount=0
    for item in app.foodCount:
        if item==foodType:
            amount+=1
    drawLabel(str(amount),60,y,fill='black',bold=True)
    
def drawNumOfItems(app):
    runs=0
    for food in app.foodList:
        y=125+50*runs
        runs+=1
        findNumOfItem(app,food,y)
        drawImage(food,30,y,align='center')

def findItemFed(app, mouseX, mouseY):
    for i, food in enumerate(app.foodList):
        Y = 125 + 50*i
        if distance(mouseX, mouseY, 30, Y) < 15:  # slightly bigger click radius
            if food in app.foodCount:
                app.foodItem = food
                app.isFoodPressed = True
                app.foodX = mouseX
                app.foodY = mouseY
                break  # stop after finding the clicked food


def deductFood(app): 
    if app.foodItem in app.foodCount:
        app.foodCount.remove(app.foodItem)

def kitchen_redrawAll(app):
    
    drawRect(0,0,400,290,fill='ghostWhite')
    drawRect(0,290,400,120,fill=gradient('burlywood','peru',start='left')) 
    for x in range(0,400,40): 
        drawLine(x,290,x,400,fill='sienna',opacity=30) 
    #window
    drawRect(175,52,105,110,fill=None, border='peru',borderWidth=10)
    for x in range(2):
        for y in range(2):
            cx=180+45*x
            cy=60+45*y
            drawLine(cx+40,cy+5,cx+5,cy+45,fill=rgb(193,238,254),lineWidth=10)
            drawRect(cx,cy,50,50,fill='lightblue',opacity=80,border='saddlebrown',borderWidth=5)

    drawLine(170,160,285,160,fill='saddlebrown',lineWidth=8)
    
   
    #fridge
    dx = -40
    drawRect(40+dx,300,40,15,fill='orchid',borderWidth=1) 
    drawRect(80+dx,305,108,10,fill='orchid',borderWidth=1) 
    drawLine(80+dx,90,80+dx,310,fill='orange',lineWidth=3) 
    drawPolygon(40+dx,100, 80+dx,90, 80+dx,310, 40+dx,310, fill=gradient('plum','mediumorchid',start='top-right')) 
    drawRect(80+dx,89,108,221,fill='steelblue') 
    drawRect(85+dx,90,100,80, fill=gradient('skyblue','powderBlue',start='left-bottom'), border='cornflowerblue',borderWidth=2) 
    drawRect(85+dx,172,100,135, fill=gradient('skyblue','powderBlue',start='left-bottom'), border='cornflowerblue',borderWidth=2) 
    drawLine(85+dx,170,182+dx,170,lineWidth=2,) 
    drawRect(95+dx,110,20,50,fill='coral',opacity=90) 
    drawRect(95+dx,180,20,50,fill='coral',opacity=90) 
    drawLine(104+dx,115,104+dx,155,fill='orangeRed',lineWidth=4,opacity=70) 
    drawLine(106+dx,115,106+dx,120,fill='red',lineWidth=2) 
    drawLine(106+dx,150,106+dx,155,fill='red',lineWidth=2) 
    drawLine(108+dx,115,108+dx,155,fill='grey',lineWidth=3) 
    drawLine(104+dx,187,104+dx,225,fill='orangeRed',lineWidth=4,opacity=70) 
    drawLine(106+dx,187,106+dx,193,fill='red',lineWidth=2) 
    drawLine(106+dx,220,106+dx,225,fill='red',lineWidth=2) 
    drawLine(108+dx,187,108+dx,225,fill='grey',lineWidth=3) 
    drawOval(160+dx,115,30,10,fill='midnightblue') 
    #counters
 
    for x in range(200,400,100):
        drawRect(x,195,100,115,fill='skyblue')
        drawRect(x+10,200,80,100,fill='aliceblue')
        drawPolygon(x+10,200,x+10,300,x+90,300,fill='gainsboro',opacity=50)
    drawCircle(280,260,6,fill='coral')
    drawCircle(320,260,6,fill='coral')
    drawLine(200,195,400,195,fill='mediumorchid',lineWidth=8)
    drawLine(200,310,400,310,fill='mediumorchid',lineWidth=6)
    drawRect(200,180,200,15,fill='mediumorchid',opacity=40)
    
    #shelf 
    drawRect(290,60,100,6,fill='indigo',opacity=20) 
    drawRect(290,52,100,10,fill='mediumorchid')
    drawRect(310,60,8,10,fill='mediumorchid')
    drawRect(370,60,8,10,fill='mediumorchid')
    drawRect(310,65,8,10,fill='orchid')
    drawRect(370,65,8,10,fill='orchid')
    #mug
    drawRect(330,30,20,25,fill='hotPink')
    drawRect(345,35,10,12,fill=None,border='hotpink')
    drawLine(334,33,347,33,fill='mediumvioletred')
    drawToot(app,app.chickX,app.chickY)
    #table
    

# tabletop
    drawRect(70,310,290,55,fill='skyblue',border='deepskyblue',borderWidth=2)

# table legs (straight, chunky, readable)
    drawRect(95,365,20,45,fill='skyblue')
    drawRect(315,365,20,45,fill='skyblue')

# front trim 
    drawRect(70,350,290,10,fill='deepskyblue',opacity=60)

    drawInformationButton(app)
    
    drawNumOfItems(app)
    drawStatsBar(app,30,75,app.symbols['hunger'],app.stats['hunger'])
    x,y=app.homeButtonCoordinates
    drawImage(app.homeButton,x,y,width=45,height=45,align='center')
    drawImage(app.shop,380,20,width=50,height=50,align='center')
    if app.isFoodPressed==True:
        drawImage(app.foodItem,app.foodX,app.foodY,align='center')
    
def kitchen_onMousePress(app,mouseX,mouseY):
    if app.stats['hunger']<100:
        findItemFed(app,mouseX,mouseY)
    goHome(app,mouseX,mouseY)
    if distance(mouseX,mouseY,380,20)<50:
        setActiveScreen('shop')
    showInformation(app,mouseX,mouseY)

def kitchen_onMouseDrag(app,mouseX,mouseY):
    if app.isFoodPressed==True:
        app.foodX=mouseX
        app.foodY=mouseY
            
            
def kitchen_onMouseRelease(app,mouseX,mouseY):
    if app.isFoodPressed and distance(mouseX,mouseY,app.chickX,app.chickY)<40:
        feeding(app)
        deductFood(app)
        app.isFoodPressed=False
##############################################################################################
#shop
#############################################################################################
def shop_onStep(app):
    pass

def shop_redrawAll(app):
    drawRect(20,50,360,300,fill='white',opacity=70)
    drawImage(app.currency,300,70,align='center')
    drawLabel(f'{app.coins}',330,70,fill='black',bold=True)
    drawImage(app.exit,380,20,align='center')

    for y in range(2):
        for x in range(3):
            X=100+100*x
            Y=200+100*y
            foodItem=(x+y)+2*y
            drawImage(app.foodList[foodItem],X,Y-50,align='center',width=100,height=100)
            drawRect(X,Y,50,25,fill='green',border='gold',align='center')
            drawImage(app.currency,X-10,Y,width=25,height=25,align='center')
            drawLabel(app.foodPrice,X+5,Y,fill='yellow')

def findItemBought(app, mouseX, mouseY):
    for y in range(2):
        for x in range(3):
            X = 100 + 100*x
            Y = 200 + 100*y
            item_index = x + 3*y  # corrected index for 2x3 grid
            if distance(mouseX, mouseY, X, Y) < 50 and app.coins >= app.foodPrice:
                item = app.foodList[item_index]
                app.foodCount.append(item)
                app.coins -= app.foodPrice

           
def shop_onMousePress(app,mouseX,mouseY):
    findItemBought(app,mouseX,mouseY)
    if distance(mouseX,mouseY,380,20)<50:
        setActiveScreen('kitchen')

#######################################################################
#bathroom
#######################################################################
def bathroom_onStep(app):
    updateTime(app)
    
def bathroom_redrawAll(app):
    drawRect(0,300,400,120,fill=gradient('tan','sandybrown',start='left'))
    for x in range(0,400,40):
        drawLine(x,300,x,400,fill='sienna',opacity=30)
    drawRect(0,0,400,150,fill='aliceblue')
    for x in range(8):
        for y in range(3):
            fill=None
            if (x+y)%2==0:
                fill='Turquoise'
            else:
                fill='paleTurquoise'
            drawRect(0+50*x,150+50*y,50,50,fill=fill,opacity=70)
    drawRect(0,295,400,10,fill='gray',opacity=15)
    #mirror
    drawOval(200,120,80,100,fill='lightskyblue',border='dimgray',opacity=80)
    drawLine(225,85,165,140,fill='white',lineWidth=8,opacity=60)
    drawLine(235,95,170,155,fill='white',opacity=60)
    drawOval(200,120,90,110,fill=None,border='gold',borderWidth=8,opacity=80)
    
    #bathmat
    drawOval(100,360,170,50,fill='coral',opacity=85)
    drawOval(100,360,150,35,fill='lightsalmon',opacity=85)

# tub shadow
    drawOval(100,330,200,25,fill='sienna',opacity=25)

# tub body
    drawPolygon(15,255,35,330,165,330,185,255,
            fill=rgb(200,235,232),border='dimgray')

# tub top
    drawOval(100,245,190,50,fill=rgb(221,250,248),border='dimgray')
    drawOval(100,245,150,28,fill='aliceblue',border='dimgray')
    drawArc(100,240,180,50,200,140,fill='white',opacity=40)

    # sink (RIGHT)
    drawRect(335,205,8,25,align='center',fill='dimgray')
    drawRect(331,195,15,5,align='center',fill='dimgray')
    drawArc(335,205,90,80,180,180,fill=rgb(221,250,248),border='dimgray')

# cabinet shadow
    drawRect(278,315,125,20,fill='dimgray',opacity=20)

# cabinet legs
    drawRect(290,315,15,10,fill='dimgray',border='dimgray')
    drawRect(365,315,15,10,fill='dimgray',border='dimgray')

# cabinet
    drawRect(280,230,110,90,fill=rgb(25,184,171),border='dimgray')
    drawLine(335,230,335,320,fill='dimgray')

    drawRect(290,245,40,60,fill='teal',border='dimgray')
    drawCircle(320,270,5,fill=rgb(28,206,191),border='saddlebrown')

    drawRect(340,245,40,60,fill='teal',border='dimgray')
    drawCircle(350,270,5,fill=rgb(28,206,191),border='saddlebrown')

    #toilet
    drawPolygon(app.chickX-35,app.chickY+55,app.chickX+35,app.chickY+55,app.chickX+42,app.chickY+100,app.chickX-40,app.chickY+100,
            fill='snow',border='dimgray')
    
    # neck
    drawRect(app.chickX,app.chickY-15,70,30,align='center',fill='mintCream',border='dimgray')
    # body
    drawCircle(app.chickX,app.chickY+30,45,fill='mintcream',border='dimgray')
    drawOval(app.chickX,app.chickY+15,110,60,fill='mintcream',border='dimgray')
    drawOval(app.chickX,app.chickY+15,90,40,fill='mintcream',border='dimgray')

    # head
    drawRect(app.chickX,app.chickY-55,90,80,align='center',fill='mintcream',border='dimgray')

    # top
    drawRect(app.chickX,app.chickY-92,90,10,align='center',fill='mintcream',border='dimgray')

    # detail
    drawCircle(app.chickX+35,app.chickY-80,5,fill='mintcream',border='dimgray')
    drawInformationButton(app)
    
    drawToot(app,app.chickX,app.chickY)
    drawStatsBar(app,30,100,app.symbols['toilet'],app.stats['toilet'])
    x,y=app.homeButtonCoordinates
    drawImage(app.homeButton,x,y,width=45,height=45,align='center')
    
def bathroom_onMousePress(app,mouseX,mouseY):
    goHome(app,mouseX,mouseY)
    if distance(mouseX,mouseY,app.chickX,app.chickY)<40 and app.stats['toilet']<100:
        usingToilet(app)
    showInformation(app,mouseX,mouseY)

########################################################################
#bedroom
#########################################################################
def bedroom_onStep(app):
    updateTime(app)
    sleeping(app)
   

def bedroom_redrawAll(app):
 
    drawRect(0,290,400,120,fill=gradient('burlywood','peru',start='left')) 
    drawRect(0,0,400,300,fill='mintcream')
    for x in range(50,400,100):
        for y in range(20,300,100):
            
            size=random.randint(10,15)
            drawStar(x,y,size,4,fill='lightSeaGreen',opacity=50)
    for x in range(0,400,40): 
        drawLine(x,290,x,400,fill='sienna',opacity=50) 
    
    medals=['gold','silver','chocolate']
    for i in range(3):
        x=80*i
        drawLine(125,30,125,85,fill='sienna',lineWidth=10)
        drawLine(245,30,245,85,fill='sienna',lineWidth=10)
        drawLine(135+20*i,30,140+20*i,70,fill=rgb(150-50*i,190,115),lineWidth=10)
        drawLine(145+20*i,30,150+20*i,70,fill=rgb(175,0,50+50*i),lineWidth=10)
        drawLine(125,70,245,70,lineWidth=10,fill='sienna')

        drawPolygon(105+x,140,90+x,100,120+x,100,105+x,140,fill=None,border='navy',borderWidth=8,opacity=90)
        drawCircle(105+x,102,3,fill='maroon',opacity=80)
        drawCircle(105+x,140,15,fill=medals[i],opacity=100)
    
    # back of bed
    drawRect(190,230,260,120,fill='maroon',align='center',opacity=90)
    drawRect(190,200,250,40,fill='firebrick',align='center',opacity=90)
    drawRect(190,260,250,60,fill='firebrick',align='center',opacity=90)

    # back bed posts
    drawRect(50,220,20,150,fill='maroon',align='center',opacity=95)
    drawRect(320,220,20,150,fill='maroon',align='center',opacity=95)
    drawLine(35,145,65,145,fill='orange',lineWidth=10,opacity=95)
    drawLine(305,145,335,145,fill='orange',lineWidth=10,opacity=95)
    #nightstand and lamp
    drawRect(335,380,10,15,fill='seagreen')
    drawRect(360,290,80,10,fill='lightgreen',align='center')
    drawRect(365,340,75,90,fill='seaGreen',align='center')
    drawRect(370,315,65,20,fill='lightgreen',align='center')
    drawRect(370,360,65,20,fill='lightgreen',align='center')
    drawCircle(375,315,4,fill='seagreen')
    drawCircle(375,360,4,fill='seagreen')
    drawCircle(360,250,30,fill='yellow',opacity=30)
    drawImage(app.lamp,360,250,width=100,height=100,align='center')
    
    
    

    # pillows
    drawRect(130,245,70,35,fill='snow',align='center')
    drawRect(230,245,70,35,fill='snow',align='center')
    drawRect(180,248,60,45,fill='seagreen',align='center')
    
    # top of mattress
    drawPolygon(28,290,332,290,288,260,73,260,fill='gold')
    drawOval(180,270,235,50,fill='gold')
    drawToot(app,200,250)
    # bottom part of mattress
    drawRect(180,330,305,80,fill='goldenrod',align='center')

    # front frame of bed
    drawRect(180,360,300,80,fill='maroon',align='center')
    drawRect(180,360,280,60,fill='firebrick',align='center')

    # front bed posts
    drawRect(10,300,20,100,fill='firebrick')
    drawRect(330,300,20,100,fill='firebrick')
    drawLine(5,300,35,300,fill='darkorange',lineWidth=10)
    drawLine(325,300,355,300,fill='darkorange',lineWidth=10)

    drawLine(10,397,350,397,lineWidth=5,fill='tomato',opacity=60)
    drawInformationButton(app)
    
    
    drawStatsBar(app,30,100,app.symbols['energy'],app.stats['energy'])
    x,y=app.homeButtonCoordinates
    drawImage(app.homeButton,x,y,width=45,height=45,align='center')
    #info button
    drawInformationButton(app)
    
    if app.lightsOut==True:
        drawRect(0,0,400,400,fill='black',opacity=50)
        
def bedroom_onMousePress(app,mouseX,mouseY):
    goHome(app,mouseX,mouseY)
    
    if distance(mouseX,mouseY,app.lampX,app.lampY)<40 and app.stats['energy']<100:
        app.lightsOut=not app.lightsOut
    showInformation(app,mouseX,mouseY)
        
##################
#win or lose screens
#################

def lose_onStep(app):
    app.blink=True
    app.flustered=False
def lose_redrawAll(app):
    drawRect(0,0,400,400,fill='lightcyan')
    drawLabel('Your pet has died',200,50,size=20,fill='midnightblue',bold=True)
    drawLabel('press restart button to play again',200,290,size=12,fill='midnightblue')
    drawCircle(200,350,40,fill='midnightblue')
    drawLabel('Restart',200,350,bold=True,fill='aliceblue')
    drawToot(app,200,180)
    drawOval(200,130,130,30,fill=None,border='gold')
def lose_onMousePress(app,mouseX,mouseY):
    if distance(mouseX,mouseY,200,350)<40:
        resetGame(app)
        setActiveScreen('start')

def win_onStep(app):
    app.blink=False
    app.flustered=True
def win_redrawAll(app):
    drawRect(0,0,400,400,fill='lightcyan')
    drawLabel('You Won! ',200,30,size=20,fill='midnightblue',bold=True)
    drawLabel('Congratulations on taking care of your pet!',200,60,fill='midnightblue',bold=True)
    drawLabel('Press the restart button to play again',200,300,size=12,fill='midnightblue')
    drawToot(app,200,200)
    drawCircle(200,350,40,fill='midnightblue')
    drawLabel('Restart',200,350,bold=True,fill='aliceblue')
def win_onMousePress(app,mouseX,mouseY):
    if distance(mouseX,mouseY,200,350)<40:
        resetGame(app)
        setActiveScreen('start')
def main():
    runAppWithScreens('start')
main()