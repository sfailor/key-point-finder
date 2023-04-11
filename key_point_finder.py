import pyqtgraph as pg
from PyQt5 import QtCore
import numpy as np

# TODO: 
# - Add ability to click on specific targets and delete them, then update the numbering of the remaining targets

           
class ImageView(pg.ViewBox):
       
    def __init__(self, parent, views, color, name, view_names):
        pg.ViewBox.__init__(self, lockAspect=True, enableMouse=True, invertY=True, enableMenu=False,
                                        border=None, name=name, defaultPadding = 0)
                
        self.parent = parent
        self.points = []
        self.high_conf = []
        self.targets = []
        self.color = color
        self.name = name
        self.view_names = view_names
        self.view_index = 0
        self.views = views
        self.current_view = pg.ImageItem()
        self.focused = False
        self.addItem(self.current_view)
        self.update_view()
        self.setBorder(pg.mkPen('black'))
        self.setRange(yRange=[0,self.current_view.image.shape[0]],
                      xRange=[0,self.current_view.image.shape[1]])
        self.label = pg.TextItem(anchor=(0,0))
        self.addItem(self.label)

        # self.setLimits(maxXRange = self.current_view.image.shape[1] * 1.2, maxYRange = self.current_view.image.shape[0] * 1.2)
        
        # Add to parent so .scene() doesn't return 'NoneType'
        self.parent.addItem(self)
        
        self.scene().sigMouseMoved.connect(self.mouseMoved)
        self.sigStateChanged.connect(self.update_label)
    
    def update_view(self):
        self.current_view.setImage(self.views[self.view_index])

    def update_view_index(self,increment):
        if increment:
            self.view_index = (self.view_index + 1) % len(self.views)
        else:
            self.view_index = (self.view_index -1) % len(self.views)

    def get_zoom(self):
        view_range = self.viewRange()
        view_width = np.diff(view_range[1])
        total_width = self.current_view.image.shape[1]
        view_height = np.diff(view_range[0])
        # print(view_height)
        total_height = self.current_view.image.shape[1]
        
        zoom = int(np.round(np.sqrt((total_width*total_height)/(view_width*view_height)),1)*100)
       
        return zoom
    
    def get_pos(self):
        view_range = self.viewRange()
        view_y = int(np.mean(view_range[1]))
        view_x = int(np.mean(view_range[0]))
        return (view_y+10,view_x+10)
    
    def text(self):
        hex = '#%02x%02x%02x' % self.color
        if self.focused:
            text = f'<font size = "+3" color = "{hex}">{self.name} - {self.view_names[self.view_index]}<br>Zoom {self.get_zoom()}%<br>Position {self.get_pos()}</font>'
        else:
            text = f'<font size = "+3" color = "white">{self.name} - {self.view_names[self.view_index]}<br>Zoom {self.get_zoom()}%<br>Position {self.get_pos()}</font>'
        return text
   
    
    def update_label(self):
        self.label.setHtml(self.text())
        
        view_range = self.viewRange()
        # print(view_range)
            
        self.label.setPos(min(view_range[0]),min(view_range[1]))

        
    def update_border(self):
        if self.focused:
            self.setBorder(pg.mkPen(self.color))
        else:
            self.setBorder(None)
      
    def mouseMoved(self,point):
        if self.sceneBoundingRect().contains(point):
            self.setFocus()
            self.focused = True
            self.update_label()
            # self.update_border()
        else:
            self.focused = False
            self.update_label()
            # self.update_border()
            
    def keyPressEvent(self, event):
        # Scroll through views
        if len(self.views)>1:  
            if event.key() == QtCore.Qt.Key_W:
                self.update_view_index(False)
                self.update_view()
                self.update_label()
            elif event.key() == QtCore.Qt.Key_E:
                self.update_view_index(True)
                self.update_view()
                self.update_label()
                
        # D key deletes last placed target/point
        if event.key() == QtCore.Qt.Key_D and len(self.points) > 0:
            self.points.pop()
            self.removeItem(self.targets[-1])
            self.targets.pop()
            self.high_conf.pop()

    # def mouseClickEvent(self, event):
    #     scene_pos = self.mapToScene(event.pos())
        
    #     if self.sceneBoundingRect().contains(scene_pos):
    #         img_pos = self.current_view.mapFromScene(scene_pos)
    #         in_frame = np.min([img_pos.y(),img_pos.x()])>=0 and img_pos.y()<=self.current_view.image.shape[0] and img_pos.x()<=self.current_view.image.shape[1]

    #         if (event.button() == QtCore.Qt.LeftButton) and in_frame:
    #             np.random.seed(len(self.points))
    #             c = list(np.random.choice(range(256), size=3))
    #             c.append(25)
    #             hex = '#%02x%02x%02x' % tuple(c[:3])
    #             tg = pg.TargetItem(pos=img_pos,movable=False, size = 20,
    #                                label = f'{len(self.points)}',
    #                                pen = pg.mkPen(c[:3],width=3),
    #                                brush = c,
    #                                labelOpts={'html' : f'<font size = "+3" color = "{hex}">{len(self.points)}</font>'})
    #             self.points.append((img_pos.y(),img_pos.x()))
    #             self.targets.append(tg)
    #             self.addItem(tg)
    
    def mouseDoubleClickEvent(self, event):
        scene_pos = self.mapToScene(event.pos())
        
        if self.sceneBoundingRect().contains(scene_pos):
            img_pos = self.current_view.mapFromScene(scene_pos)
            in_frame = np.min([img_pos.y(),img_pos.x()])>=0 and img_pos.y()<=self.current_view.image.shape[0] and img_pos.x()<=self.current_view.image.shape[1]

            if in_frame:               
                if event.button() == QtCore.Qt.RightButton:
                    self.high_conf.append(False)
                    tg_symbol = '+'
                elif event.button() == QtCore.Qt.LeftButton:
                    self.high_conf.append(True)
                    tg_symbol = 'star'
                
                np.random.seed(len(self.points))
                c = list(np.random.choice(range(256), size=3))
                c.append(25)
                hex = '#%02x%02x%02x' % tuple(c[:3])
                tg = pg.TargetItem(pos=img_pos,movable=False, size = 20,
                                   label = f'{len(self.targets)}',
                                   pen = pg.mkPen(c[:3],width=3),
                                   symbol = tg_symbol,
                                   brush = c,
                                   labelOpts={'html' : f'<font size = "+3" color = "{hex}">{len(self.targets)}</font>'})
                self.points.append((img_pos.y(),img_pos.x()))  
                self.targets.append(tg)
                self.addItem(tg)                 

                
class CompareWindow(pg.GraphicsLayoutWidget):
        
    pg.setConfigOptions(imageAxisOrder='row-major')    

    def __init__(self, image_list, size, image_names=None, view_names=None):
        pg.GraphicsLayoutWidget.__init__(self, size=size, title=None, show=True, border=False)
                
        self.p = []
        
        # Give unique colors to each ImageView
        if len(image_list) == 1:
            colors = [(211, 211, 211)]
        if len(image_list) <= 6:
            colors = [(64, 83, 211), (221, 179, 16), (181, 29, 20), (0, 190, 255), (251, 73, 176), (0, 178, 93), (202, 202, 202)]
        elif len(image_list) <= 12:
            colors = [(235, 172, 35), (184, 0, 88), (0, 140, 249), (0, 110, 0), (0, 187, 173), (209, 99, 230), (178, 69, 2), (255, 146, 135), (89, 84, 214), (0, 198, 248), (135, 133, 0), (0, 167, 108), (189, 189, 189)]
        else:
            colors = [list(np.random.choice(range(256), size=3)) for i in range(len(image_list))]
            
        for c,l in enumerate(image_list):
            self.p.append(ImageView(parent = self, views=l, color=colors[c], name=image_names[c], view_names=view_names[c]))
          
          
def compare_images(image_list, image_names = None, view_names = None):
    
    '''
    Takes images, images names, and 'view' names.
        Arguments:
            image_list (list): A list containing 2D numpy arrays or sublists of 2d numpy arrays when providing more than one 'view'
            image_names (list, OPTIONAL): List of image names, length the same as image_list
            view_names (list, OPTIONAL): list of view names. If there is more than one view per image, list should contain sublists for each image equal in length to the number or views. 
        Returns:
            results (dict): 
                            'names' : List of image names
                            'points' : List of matching points from each image
                            'point_high_conf' : Whether the feature match at the selected point is of high confidence
    '''
    
    app = pg.mkQApp()
    app.setQuitOnLastWindowClosed(True)    
        
    screen_resolution = app.desktop().screenGeometry()
    width, height = screen_resolution.width(), screen_resolution.height()

    width = int(width*0.9)
    height = int(width/len(image_list))
    
    # Check a list was provided
    if type(image_list) is not list:
        raise TypeError('image_list must be list')
    
    # Check that views are numpy arrays and they are in a list
    for i in range(len(image_list)):
        if type(image_list[i]) is not list:
            if type(image_list[i]) is np.ndarray:
                image_list[i] = [image_list[i]]
            else:
                raise TypeError('views must be numpy arrays')
        else:
            for v in image_list[i]:
                if type(v) is not np.ndarray:
                    raise TypeError('views must be numpy arrays')
                       
    if image_names == None:
        image_names = [f'Image {i}' for i in range(len(image_list))]
    
    if view_names == None:
        view_names = []
        for i in range(len(image_list)):    
            view_names.append([f'View {v}' for v in range(len(image_list[i]))])   
    
    win = CompareWindow(image_list=image_list, size=(width,height), image_names=image_names, view_names=view_names)

    app.exec()

    names = [win.p[i].name for i in range(len(image_list))]
    points = [win.p[i].points for i in range(len(image_list))]
    point_high_conf = [win.p[i].high_conf for i in range(len(image_list))]

    results = {'names' : names,
               'points' : points,
               'point_high_conf' : point_high_conf}

    return results