from enum import auto
import shutil
from PyQt5 import QtCore
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QMainWindow, QFileDialog, QLabel
# from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtCore import Qt
import numpy as np
import os
from UI import Ui_MainWindow
from opencv_engine import opencv_engine
import cv2
import json
import time
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

        self.root = '/media/waywaybao_cs10/DATASET/RiskBench_Dataset/'

        data_type_list = ["interactive", "non-interactive",
                          "collision", "obstacle"][3:]

        self.ui.combobox_data_type.clear()
        for i in range(len(data_type_list)):
            self.ui.combobox_data_type.insertItem(i, data_type_list[i])
        #basic_scenario_list = os.listdir('../dataset')
        #self.current_data_type = self.ui.combobox_data_type.currentText()

        self.img_width = 1280
        self.img_height = 720
        self.z = 100
        self.color = (0, 0, 255)
        self.alpha = 0.4
        self.draw_line = True
        self.points = []
        self.carla_points = []
        self.points_color = []

        self.updateColor()
        self.set_basic_combobox()

        # set connect
        self.ui.combobox_data_type.currentIndexChanged.connect(
            self.set_basic_combobox)
        self.ui.combobox_basic.currentIndexChanged.connect(
            self.set_variant_combobox)
        self.ui.combobox_variant.currentIndexChanged.connect(
            self.set_frame_combobox)
        self.ui.combobox_frameNum.currentIndexChanged.connect(
            self.variant_action)

        # self.ui.zoom_in.clicked.connect(self.zoom_in)
        # self.ui.zoom_out.clicked.connect(self.zoom_out)
        # self.ui.recover.clicked.connect(self.recover)

        self.ui.slider_videoframe.valueChanged.connect(self.getslidervalue)

        self.ui.nextButton_basic.clicked.connect(self.set_next_basic_index)
        self.ui.nextButton_variant.clicked.connect(self.set_next_variant_index)
        self.ui.nextButton_frame.clicked.connect(self.set_next_frame_index)

        self.ui.backButton_basic.clicked.connect(self.set_back_basic_index)
        self.ui.backButton_variant.clicked.connect(self.set_back_variant_index)
        self.ui.backButton_frame.clicked.connect(self.set_back_frame_index)

        self.ui.image_label.mousePressEvent = self.mouse_press_event

        self.ui.colorR.valueChanged.connect(self.updateColor)
        self.ui.colorG.valueChanged.connect(self.updateColor)
        self.ui.colorB.valueChanged.connect(self.updateColor)

        self.ui.pushButton_add.clicked.connect(self.addZone)
        self.ui.pushButton_clear.clicked.connect(self.clearPoints)
        self.ui.pushButton_save.clicked.connect(self.save_img)
        self.ui.auto_label.clicked.connect(self.auto_label)

    # def zoom_in(self):
    #     self.qpixmap_main_height += 20
    #     self.qpixmap_main_width += 20
    #     self.set_image(self.updated_top_img, self.ui.image_label, scale=True, scale_size=(
    #         self.qpixmap_main_height, self.qpixmap_main_width))

    # def zoom_out(self):
    #     self.qpixmap_main_height -= 20
    #     self.qpixmap_main_width -= 20
    #     self.set_image(self.updated_top_img, self.ui.image_label, scale=True, scale_size=(
    #         self.qpixmap_main_height, self.qpixmap_main_width))

    # def recover(self):
    #     self.qpixmap_main_height = self.img_height
    #     self.qpixmap_main_width = self.img_width
    #     self.set_image(self.updated_top_img, self.ui.image_label, scale=True, scale_size=(
    #         self.qpixmap_main_height, self.qpixmap_main_width))

    def mouse_press_event(self, event):

        # offset = (self.qpixmap_main_height-self.img_height)/2
        x = event.x()//2
        y = event.y()//2

        point = [x, y]
        b, g, r = self.original_top_img[y, x]
        # print([b, g, r])

        if event.button() == 1:  # right clicked
 
            self.points.append(point)
            self.points_color.append([b, g, r])
 
            self.update_image_frame(point)
            self.ui.message_box.setText(f"Note: Select pixel {point} with color {[b, g, r]}")

        elif event.button() == 2:  # left clicked
            world_point = pixel_to_world(np.array([point]), pitch=0, focal_length=548.993771650447, depth=self.z, center=np.array(
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
                    f"Missing frame no.{self.frame_id} information in ego_data.json")

    def save_img(self):

        path = os.path.join(self.root, self.get_current_data_type(),  self.get_current_basic(
        ), 'variant_scenario', self.get_current_variant(), 'obstacle_info2.json')

        if not os.path.isfile(path):
            ref_info = os.path.join(self.root, self.get_current_data_type(),  self.get_current_basic(
            ), 'variant_scenario', self.get_current_variant(), 'obstacle_info.json')
            json_file = open(ref_info)
            data = json.load(json_file)
            json_file.close()
        else:
            json_file = open(path)
            data = json.load(json_file)
            json_file.close()

        if not "other_obstacle_list" in data:
            data["other_obstacle_list"] = {}



        # path_top = os.path.join(path, 'top')
        # path_rgb = os.path.join(path, 'rgb')
        # path_seg = os.path.join(path, 'seg')

        # if not os.path.isdir(path):
        #     os.mkdir(path)
        # if not os.path.isdir(path_top):
        #     os.mkdir(path_top)
        # if not os.path.isdir(path_rgb):
        #     os.mkdir(path_rgb)
        # if not os.path.isdir(path_seg):
        #     os.mkdir(path_seg)

        # cv2.imwrite(os.path.join(path_top, self.get_current_frame()),
        #             self.updated_top_img)
        # cv2.imwrite(os.path.join(path_rgb, self.get_current_frame()),
        #             self.updated_front_img)
        # cv2.imwrite(os.path.join(path_seg, self.get_current_frame()),
        #             self.updated_front_seg)

        # print(self.points_color)
        # print(self.carla_points[0])

        for p, c in zip(self.carla_points[0], self.points_color):
            id = str(256*c[0]+c[1])
            data["other_obstacle_list"][id] = {}
            data["other_obstacle_list"][id]["transform"] = p.tolist()[:2]
            data["other_obstacle_list"][id]["instance_color"] = [int(c[2]),int(c[1]),int(c[0])]

        print(data)

        with open(path, 'w') as f:
            json.dump(data, f, indent=4)

        self.ui.message_box.setText(f"Note: Points save completed")

    def updateColor(self):
        R, G, B = self.ui.colorR.value(), self.ui.colorG.value(), self.ui.colorB.value()

        self.color = (B, G, R)
        self.vis = np.full((100, 50, 3), self.color).astype(np.uint8)

        qimg = QImage(self.vis, 100, 50, 100*3,
                      QImage.Format_RGB888).rgbSwapped()
        self.ui.color_vis.setPixmap(QPixmap.fromImage(qimg))

    def update_image_frame(self, point, world_point=None):
        self.updated_top_img = opencv_engine.draw_point(
            self.updated_top_img, point=point, color=self.color)

        if self.draw_line == False and len(self.points) > 1:
            self.updated_top_img = opencv_engine.draw_line(self.updated_top_img,
                                                           self.points[-2], self.points[-1], color=self.color)

        if world_point is not None:
            x, y, z = world_point[0]
            text = f"{x:.2f} , {y:.2f}"
            self.updated_top_img = opencv_engine.write_text(
                self.updated_top_img, text, loc=(point[0]+5, point[1]+5), color=self.color)

        self.set_image(self.updated_top_img, self.ui.image_label, scale=True, scale_size=(1024, 1024))

    def addZone(self, auto_labeling=False):
        world_points = pixel_to_world(np.array(self.points), depth=self.z, focal_length=548.993771650447, pitch=0, center=np.array(
            (self.img_width//2, self.img_height//2)))

        # # update front view rgb image
        # projection = Projection(self.updated_front_img, np.copy(world_points))
        # self.updated_front_img = projection.bev_to_front(
        #     theta=-90, dx=0, dy=0, dz=0, fov=90, color=self.color)
        # self.set_image(self.updated_front_img, self.ui.image_label3, True)

        # # update front view segmentation image
        # projection_seg = Projection(
        #     self.updated_front_seg, np.copy(world_points))
        # self.updated_front_seg = projection_seg.bev_to_front(
        #     theta=-90, dx=0, dy=0, dz=0, fov=90, color=self.color, alpha=1)
        # self.set_image(self.updated_front_seg, self.ui.image_label2, True)

        # # update top view rgb image
        # self.updated_top_img = opencv_engine.draw_line(self.updated_top_img,
        #                                                self.points[0], self.points[-1], color=self.color)
        # self.updated_top_img = draw_image(
        #     self.updated_top_img, self.points, color=self.color, alpha=self.alpha)
        # self.set_image(self.updated_top_img, self.ui.image_label, True, scale_size=(1024,1024))

        if self.ego_data is not False and not auto_labeling:
            compass, ego_loc = self.ego_data
            carla_point = pixel_to_carla(
                world_points[:, :2], theta=-compass, depth=self.z, ego_loc=ego_loc)

            self.carla_points.append(carla_point)
            # self.points_color.append(self.color)
        else:
            self.ui.message_box.setText(f"No ego data!!!!!!!!!!!!!!!!!!!!!!")
            print(f"No ego data!!!!!!!!!!!!!!!!!!!!!!")

        # self.points = []
        self.ui.message_box.setText(
            f"Note: Add point.")

    def auto_label(self):
        if len(self.carla_points) == 0:
            self.ui.message_box.setText(f"There is no zone to be add.")
            return

        print(f"Note: Auto labeling frame...")

        for i in range(self.ui.combobox_frameNum.count()):
            self.ui.combobox_frameNum.setCurrentIndex(i)
            zone = []
            color = []

            for points, c in zip(self.carla_points, self.points_color):
                if self.ego_data is not False:
                    compass, ego_loc = self.ego_data
                    pixel_points = carla_to_pixel(
                        points[:, :2], theta=compass, ego_loc=ego_loc, depth=self.z, focal_length=548.993771650447, center=np.array((self.img_width//2, self.img_height//2)))
                    zone.append(pixel_points)
                    color.append(c)

                for pixels, c in zip(zone, color):
                    self.points = pixels
                    self.color = c
                    self.addZone(auto_labeling=True)

                self.save_img()
                self.ui.message_box.setText(
                    f"Note: Auto labeling frame {self.get_current_frame()}...")
                print(
                    f"Note: Auto labeling frame {self.get_current_frame()}...")

        self.carla_points = []
        self.points_color = []

    def clearPoints(self):
        path = os.path.join(self.root, self.get_current_data_type(),  self.get_current_basic(
        ), 'variant_scenario', self.get_current_variant(), 'construction_zone')
        if os.path.isdir(path):
            shutil.rmtree(path)

        self.points = []
        self.carla_points = []
        self.points_color = []

        self.updated_top_img = self.original_top_img.copy()
        self.updated_front_img = self.original_front_img.copy()
        self.updated_front_seg = self.original_front_seg.copy()

        self.set_image(self.original_top_img, self.ui.image_label, True, (1024, 1024))
        self.set_image(self.updated_front_seg, self.ui.image_label2, True)
        self.set_image(self.updated_front_img, self.ui.image_label3, True)
        self.ui.message_box.setText(f"Note: Clean all points")

    def set_back_basic_index(self):
        if ((self.ui.combobox_basic.currentIndex()-1) == -1):
            self.ui.combobox_basic.setCurrentIndex(
                self.ui.combobox_basic.count()-1)
        else:
            self.ui.combobox_basic.setCurrentIndex(
                self.ui.combobox_basic.currentIndex()-1)

    def set_next_basic_index(self):
        if (((self.ui.combobox_basic.currentIndex()+1) % self.ui.combobox_basic.count()) == 0):
            self.ui.combobox_basic.setCurrentIndex(0)
        else:
            self.ui.combobox_basic.setCurrentIndex(
                self.ui.combobox_basic.currentIndex()+1)

    def set_back_variant_index(self):
        # self.init_high_level_command()
        if ((self.ui.combobox_variant.currentIndex()-1) == -1):
            self.ui.combobox_variant.setCurrentIndex(
                self.ui.combobox_variant.count()-1)
        else:
            self.ui.combobox_variant.setCurrentIndex(
                self.ui.combobox_variant.currentIndex()-1)

    def set_next_variant_index(self):
        if (((self.ui.combobox_variant.currentIndex()+1) % self.ui.combobox_variant.count()) == 0):
            self.ui.combobox_variant.setCurrentIndex(0)
        else:
            self.ui.combobox_variant.setCurrentIndex(
                self.ui.combobox_variant.currentIndex()+1)

    def set_back_frame_index(self):
        # self.init_high_level_command()
        if ((self.ui.combobox_frameNum.currentIndex()-1) == -1):
            self.ui.combobox_frameNum.setCurrentIndex(
                self.ui.combobox_frameNum.count()-1)
        else:
            self.ui.combobox_frameNum.setCurrentIndex(
                self.ui.combobox_frameNum.currentIndex()-1)

    def set_next_frame_index(self):
        if (((self.ui.combobox_frameNum.currentIndex()+1) % self.ui.combobox_frameNum.count()) == 0):
            self.ui.combobox_frameNum.setCurrentIndex(0)
        else:
            self.ui.combobox_frameNum.setCurrentIndex(
                self.ui.combobox_frameNum.currentIndex()+1)

    def get_current_data_type(self):
        self.current_data_type = self.ui.combobox_data_type.currentText()
        return self.current_data_type

    def get_current_basic(self):
        self.current_basic = self.ui.combobox_basic.currentText()
        return self.current_basic

    def get_current_variant(self):
        self.current_variant = self.ui.combobox_variant.currentText()
        return self.current_variant

    def get_current_frame(self):
        self.current_frame = self.ui.combobox_frameNum.currentText()
        return self.current_frame

    def set_basic_combobox(self):

        list = os.listdir(os.path.join(
            self.root, self.get_current_data_type()))
        list.sort()

        self.init_basic_combobox = True

        self.ui.combobox_basic.clear()
        for i in range(len(list)):
            self.ui.combobox_basic.insertItem(i, list[i])

        self.init_basic_combobox = False
        # print(self.ui.combobox_basic.currentText())

        self.set_variant_combobox()

    def set_variant_combobox(self):

        if self.init_basic_combobox == False:

            path = os.path.join(self.root, self.get_current_data_type(
            ), self.ui.combobox_basic.currentText(), 'variant_scenario')

            list = os.listdir(path)
            list.sort()

            self.init_variant_combobox = True

            self.ui.combobox_variant.clear()
            for i in range(len(list)):
                self.ui.combobox_variant.insertItem(i, list[i])

            self.init_variant_combobox = False

            self.ui.label_basic.setText(
                "{}/{}".format((self.ui.combobox_basic.currentIndex()+1), (self.ui.combobox_basic.count())))

            self.set_frame_combobox()

    def set_frame_combobox(self):

        if self.init_variant_combobox == False:
            self.points = []
            self.carla_points = []
            self.points_color = []
            
            var_path = os.path.join(self.root, self.get_current_data_type(
            ), self.get_current_basic(), 'variant_scenario', self.get_current_variant())
            top_path = os.path.join(var_path, 'rgb/lbc_img')

            list = os.listdir(top_path)
            list.sort()

            self.init_frame_combobox = True

            self.ui.combobox_frameNum.clear()
            for i in range(len(list)):
                self.ui.combobox_frameNum.insertItem(i, list[i])

            self.init_frame_combobox = False

            self.ui.label_varient.setText(
                "{}/{}".format((self.ui.combobox_variant.currentIndex()+1), (self.ui.combobox_variant.count())))
            self.ui.slider_videoframe.setRange(
                0, self.ui.combobox_frameNum.count()-1)

            self.ui.message_box.setText(
                ("Note: Please select the pixel on top view image"))

            self.variant_action()

    def variant_action(self):

        if self.init_frame_combobox == False:

            self.ui.label_frame.setText(
                "{}/{}".format((self.ui.combobox_frameNum.currentIndex()+1), (self.ui.combobox_frameNum.count())))
            self.ui.label_framecnt.setText(
                "{}/{}".format((self.ui.combobox_frameNum.currentIndex()+1), (self.ui.combobox_frameNum.count())))

            self.trigger_button = True
            self.ui.slider_videoframe.setValue(
                self.ui.combobox_frameNum.currentIndex())
            self.trigger_button = False

            var_path = os.path.join(self.root, self.get_current_data_type(
            ), self.get_current_basic(), 'variant_scenario', self.get_current_variant())

            top_path = os.path.join(
                var_path, 'instance_segmentation/top', self.get_current_frame())
            front_path = os.path.join(
                var_path, 'rgb/front', self.get_current_frame())
            front_seg_path = os.path.join(
                var_path, 'instance_segmentation/front', self.get_current_frame())


            self.original_top_img = cv2.imread(top_path)
            # self.original_top_img = cv2.resize(self.original_top_img, (1280, 720), interpolation=cv2.INTER_AREA)
            self.original_front_img = cv2.imread(front_path)
            self.original_front_seg = cv2.imread(front_seg_path)
            self.img_height, self.img_width, _ = self.original_top_img.shape
            # self.qpixmap_main_height, self.qpixmap_main_width = self.img_height, self.img_width

            if self.original_front_img is None or self.original_front_seg is None:
                print(front_path)

            self.updated_top_img = self.original_top_img.copy()
            self.updated_front_img = self.original_front_img.copy()
            self.updated_front_seg = self.original_front_seg.copy()

            self.set_image(self.updated_top_img, 
                            self.ui.image_label, scale=True, scale_size = (1024, 1024))
            self.set_image(self.updated_front_seg,
                           self.ui.image_label2, scale=True)
            self.set_image(self.updated_front_img,
                           self.ui.image_label3, scale=True)

            self.frame_id, self.ego_data = self.get_ego_data()
            self.ui.label_filepath.setText(
                f"Path: {self.root}\n {top_path.split(self.root)[1]}")

    def set_image(self, frame, image_label, scale=False, scale_size=(640, 360)):
        img_size = frame.shape
        qimg = QImage(frame, img_size[1], img_size[0],
                      img_size[1]*3, QImage.Format_RGB888).rgbSwapped()

        self.qpixmap = QPixmap.fromImage(qimg)
        if scale:
            self.qpixmap = self.qpixmap.scaled(
                scale_size[0], scale_size[1], aspectRatioMode=Qt.KeepAspectRatio)

        # if image_label is self.ui.image_label:
        #     print("###", self.qpixmap.height(), self.qpixmap.width())

        image_label.setPixmap(self.qpixmap)

    def getslidervalue(self):
        if self.trigger_button == False:
            self.ui.combobox_frameNum.setCurrentIndex(
                self.ui.slider_videoframe.value())

    def get_ego_data(self):
        ego_data_path = os.path.join(self.root, self.get_current_data_type(
        ), self.get_current_basic(), 'variant_scenario', self.get_current_variant(), 'ego_data.json')
        ego_data = open(ego_data_path)
        data = json.load(ego_data)
        ego_data.close()

        frame_id = int(self.get_current_frame().split('.')[0])

        if "transform" in data[str(frame_id)] and "imu" in data[str(frame_id)] and "compass" in data[str(frame_id)]["imu"]:
            compass = data[str(frame_id)]["imu"]["compass"]
            ego_loc = data[str(frame_id)]["transform"]
            return frame_id, (compass, ego_loc)
        else:
            return frame_id, False
