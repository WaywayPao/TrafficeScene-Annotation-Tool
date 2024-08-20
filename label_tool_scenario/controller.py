from PyQt5.QtCore import Qt
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QLabel
from UI import Ui_MainWindow
from opencv_engine import opencv_engine
import numpy as np
import os
import cv2
import json
import glob
from projection import Projection, pixel_to_world, draw_image, pixel_to_carla, carla_to_pixel

class MainWindow_controller(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.init_basic_combobox = False
        self.init_variant_combobox = False
        self.init_frame_combobox = False
        self.trigger_button = False

        self.root = "RiskBench"
        self.main_image_path = "map_collection"
        self.focal_length = -1

        self.current_map = ".png"
        self.road_id = ""
        self.img_width = 1280
        self.img_height = 720
        self.z = 100
        self.current_color = (0, 0, 255)
        self.alpha = 0.4
        self.draw_line = True

        self.points = []
        self.points_by_pixel = []
        self.carla_points = []
        self.carla_points_color = []
        self.updated_top_img_list = []

        self.set_map_combobox()
        self.set_color_combobox()

        # set connect
        self.ui.combobox_instance_color.currentIndexChanged.connect(
            self.updateColor)
        self.ui.combobox_map_id.currentIndexChanged.connect(
            self.variant_action)

        self.ui.nextButton_frame.clicked.connect(self.set_next_map_index)
        self.ui.backButton_frame.clicked.connect(self.set_back_map_index)
        self.ui.main_image.mousePressEvent = self.mouse_press_event

        self.ui.pushButton_add.clicked.connect(self.addZone)
        self.ui.pushButton_undo.clicked.connect(self.undo)
        self.ui.pushButton_clean.clicked.connect(self.clean)
        self.ui.pushButton_save.clicked.connect(self.save_img)

    def mouse_press_event(self, event):

        point = [event.x(), event.y()]
        # print(point)

        if event.button() == 1:  # right clicked
            self.points.append(point)
            self.update_image_frame(point)
            self.ui.message_box.setText(f"Note: Select pixel    {point}")

        elif event.button() == 2:  # left clicked
            world_point = pixel_to_world(np.array([point]), pitch=0, focal_length=self.focal_length, depth=self.z, center=np.array(
                (self.img_width//2, self.img_height//2)))

            if self.ego_data is not False:
                compass, ego_loc = self.ego_data
                carla_point = pixel_to_carla(
                    world_point[:, :2], theta=-compass, depth=self.z, ego_loc=ego_loc)

                self.update_image_frame(point, carla_point)
                self.ui.message_box.setText(
                    f"Note: Select global point    {np.around(carla_point, 2)[0]}")

            else:
                self.ui.message_box.setText(
                    f"Missing {self.current_map} information in {self.current_map.split('.')[0]}.json")

    def updateColor(self):
        color = self.get_current_color()
        self.vis = np.full((100, 50, 3), color).astype(np.uint8)
        qimg = QImage(self.vis, 100, 50, 100*3,
                      QImage.Format_RGB888).rgbSwapped()
        self.ui.color_vis.setPixmap(QPixmap.fromImage(qimg))

    def update_image_frame(self, point, world_point=None):
        self.updated_top_img = opencv_engine.draw_point(
            self.updated_top_img, point=point, color=self.current_color)

        if self.draw_line == True and len(self.points) > 1:
            self.updated_top_img = opencv_engine.draw_line(self.updated_top_img,
                                                           self.points[-2], self.points[-1], color=self.current_color)

        if world_point is not None:
            x, y, z = world_point[0]
            text = f"{x:.2f} , {y:.2f}"
            self.updated_top_img = opencv_engine.write_text(
                self.updated_top_img, text, loc=(point[0]+5, point[1]+5), color=self.current_color)


        self.set_image(self.updated_top_img, self.ui.main_image, scale=True, scale_size=(
            self.qpixmap_main_height, self.qpixmap_main_width))

    def addZone(self, auto_labeling=False):
        if len(self.points) < 3:
            self.ui.message_box.setText("Note: Need more than 2 points!")
            return

        world_points = pixel_to_world(np.array(self.points), depth=self.z, focal_length=self.focal_length, pitch=0, center=np.array(
            (self.img_width//2, self.img_height//2)))

        # update top view rgb image
        self.updated_top_img = opencv_engine.draw_line(self.updated_top_img,
                                                       self.points[0], self.points[-1], color=self.current_color)
        self.updated_top_img = draw_image(
            self.updated_top_img, self.points, color=self.current_color, alpha=self.alpha)

        self.updated_top_img_list.append(self.updated_top_img.copy())
        self.set_image(self.updated_top_img, self.ui.main_image)


        if self.ego_data is not False and not auto_labeling:
            compass, ego_loc = self.ego_data
            carla_point = pixel_to_carla(
                world_points[:, :2], theta=-compass, depth=self.z, ego_loc=ego_loc)

            self.carla_points.append(carla_point.tolist())
            self.carla_points_color.append(self.current_color)
            self.points_by_pixel.append(self.points)

        self.points = []
        self.ui.message_box.setText(
            f"Note: Add zone with instance {self.ui.combobox_instance_color.currentText()}")

    def undo(self):
        
        if len(self.updated_top_img_list)<2:
            self.ui.message_box.setText(f"Note: It's original image")
            return 

        self.updated_top_img_list.pop()
        self.carla_points.pop()
        self.carla_points_color.pop()
        self.points_by_pixel.pop()
        

        self.points = []

        self.updated_top_img = self.updated_top_img_list[-1].copy()
        self.set_image(self.updated_top_img, self.ui.main_image)

        self.ui.message_box.setText(f"Note: Undo")

    def clean(self):
        self.updated_top_img_list = []
        self.carla_points = []
        self.carla_points_color = []
        self.points_by_pixel = []

        self.points = []

        path_json = os.path.join(self.main_image_path, 'label', 'top', f'{self.road_id}.json')
        if os.path.isfile(path_json):
            os.remove(path_json)

        path_img = os.path.join(self.main_image_path, 'label', 'top', f'{self.road_id}.png')
        if os.path.isfile(path_img):
            os.remove(path_img)

        self.updated_top_img = self.original_top_img.copy()
        self.updated_top_img_list.append(self.updated_top_img.copy())
        
        self.set_image(self.updated_top_img, self.ui.main_image)
        self.ui.message_box.setText(f"Note: Clean all instance color and delete labeled image")

    def save_img(self):

        path = os.path.join(self.main_image_path, 'label')
        path_top = os.path.join(path, 'top')
        path_json = os.path.join(path_top, f'{self.road_id}.json')

        if not os.path.isdir(path):
            os.mkdir(path)
        if not os.path.isdir(path_top):
            os.mkdir(path_top)

        cv2.imwrite(os.path.join(path_top, self.current_map), self.updated_top_img)

        self.ui.message_box.setText(f"Note: Map {self.current_map} save completed")
        print(f"Save to {path_top}")


        info = {"carla_points": self.carla_points, \
                "carla_points_color":self.carla_points_color, \
                "points_by_pixel":self.points_by_pixel}

        # print(info)

        with open(path_json, "w") as f:
            json.dump(info, f, indent = 4)        


    def set_back_map_index(self):
        if ((self.ui.combobox_map_id.currentIndex()-1) == -1):
            self.ui.combobox_map_id.setCurrentIndex(
                self.ui.combobox_map_id.count()-1)
        else:
            self.ui.combobox_map_id.setCurrentIndex(
                self.ui.combobox_map_id.currentIndex()-1)


    def set_next_map_index(self):
        if (((self.ui.combobox_map_id.currentIndex()+1) % self.ui.combobox_map_id.count()) == 0):
            self.ui.combobox_map_id.setCurrentIndex(0)
        else:
            self.ui.combobox_map_id.setCurrentIndex(
                self.ui.combobox_map_id.currentIndex()+1)


    def get_current_color(self):
        temp = self.ui.combobox_instance_color.currentText().split('(')[1].split(')')[0]
        R, G, B = map(int, temp.split(',')[:3])
        self.current_color = (B, G, R)
        
        return self.current_color


    def set_color_combobox(self):
        self.color_list = {'Corner': (255, 0, 0), 'Road': (0, 255, 0), 'Crosswalk': (0, 0, 255), 'Intersection': (255, 255, 0), 'Lane': (255, 0, 255)}
        
        self.init_color_combobox = True

        self.ui.combobox_instance_color.clear()
        for i, color in enumerate(self.color_list):
            self.color_list[color]
            self.ui.combobox_instance_color.insertItem(i, f"{color}    {self.color_list[color]}")

        self.init_color_combobox = False
        self.updateColor()


    def set_map_combobox(self):

        map_list = glob.glob(os.path.join(self.main_image_path, '*.png'))
        map_list.sort()
        # print(map_list)

        self.init_map_combobox = True
        self.ui.combobox_map_id.clear()
        for i, map in enumerate(map_list):
            self.ui.combobox_map_id.insertItem(i, map.split('/')[-1])
        self.init_map_combobox = False

        self.variant_action()


    def variant_action(self):

        if self.init_map_combobox == False:
            self.points = []
            self.points_by_pixel = []
            self.carla_points = []
            self.carla_points_color = []
    
            self.updated_top_img_list = []

            self.current_map = self.ui.combobox_map_id.currentText()
            self.road_id = self.current_map.split('.')[0]

            map_path = os.path.join(self.main_image_path, self.current_map)
            
            self.labeled_top_path = os.path.join(
                self.main_image_path, 'label', 'top', self.current_map)

            self.original_top_img = cv2.imread(map_path)
            self.img_height, self.img_width, _ = self.original_top_img.shape
            self.qpixmap_main_height, self.qpixmap_main_width = self.img_height, self.img_width

            if os.path.isfile(self.labeled_top_path):
                self.updated_top_img = cv2.imread(self.labeled_top_path)
            else:
                self.updated_top_img = self.original_top_img.copy()

            self.updated_top_img_list.append(self.updated_top_img.copy())
            self.ego_data = self.get_ego_data()

            self.set_image(self.updated_top_img, self.ui.main_image)


    def set_image(self, frame, main_image, scale=False, scale_size=(640, 360)):
        img_size = frame.shape
        qimg = QImage(frame, img_size[1], img_size[0],
                      img_size[1]*3, QImage.Format_RGB888).rgbSwapped()

        self.qpixmap = QPixmap.fromImage(qimg)
        if scale:
            self.qpixmap = self.qpixmap.scaled(
                scale_size[0], scale_size[1], aspectRatioMode=Qt.KeepAspectRatio)

        # if main_image is self.ui.main_image:
        #     print("###", self.qpixmap.height(), self.qpixmap.width())

        main_image.setPixmap(self.qpixmap)


    def get_ego_data(self):
        ego_data_path = os.path.join(self.main_image_path, self.road_id+'.json')
        ego_data = open(ego_data_path)
        data = json.load(ego_data)
        ego_data.close()

        
        if all(x in data.keys() for x in ["compass", "x", "y", "z"]):
            compass = data["compass"]
            ego_loc = {"x":data["x"], "y":data["y"], "z":data["z"]}
            return (compass, ego_loc)
        else:
            return False

