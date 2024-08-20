import os
import cv2
import math
import numpy as np
from math import pi
from scipy.spatial import ConvexHull
from shapely.geometry import LineString, Polygon, MultiLineString

points = []
if not os.path.isdir('output'):
    os.mkdir('output')


class Projection(object):

    def __init__(self, image_path, world_points=[]):
        self.image_path = image_path
        if type(image_path) != 'str':
            self.image = image_path
        else:
            self.image = cv2.imread(image_path)

        self.height, self.width, self.channels = self.image.shape
        self.world_points = world_points + np.array([0, 2.31671180725, 0])

    def bev_to_front(self, theta=0, phi=0, gamma=0, dx=0, dy=0, dz=0, fov=90, img_name='projection.png', color=(0, 0, 255), alpha=0.4):

        rtheta, rphi, rgamma = self.get_rad(theta, phi, gamma)
        self.focal_w = self.width / (2 * math.tan(fov * math.pi / 360))
        self.focal_h = self.focal_w
        # self.focal_h = self.height / (2 * math.tan(fov * math.pi / 360))/scale
        # print(f'Focal length: {self.focal_w}, {self.focal_h} ')

        M, _, extrinsic = self.M(rtheta, rphi, rgamma, dx=0, dy=0, dz=0)

        # check image boundary
        a = LineString([(-500, 0), (500, 0)])
        poly = Polygon(self.world_points[:, :2])
        multi_line = MultiLineString([a])
        line_poly = multi_line.convex_hull

        clockwise = np.cross(self.world_points[0], self.world_points[1])[2]

        if (clockwise < 0 and self.world_points[0][1]<0) or (clockwise>0 and self.world_points[0][1]>0):
            # counter-clockwise point
            intersection = np.array(poly.intersection(line_poly).coords)
        else:
            # clockwise point
            intersection = np.flipud(
                np.array(poly.intersection(line_poly).coords))


        idx = -1
        new_pixels = []
        n = len(self.world_points)

        for p, i in zip(self.world_points.copy(), range(n)):
            if p[1] > 0:
                if len(intersection) == 0:
                    p[0], p[1] = 0, -0.01
                else:
                    if idx < len(intersection)-1 and (self.world_points[(i+1) % n][1] < 0 or idx == -1):
                        idx += 1
                    p[0], p[1] = intersection[idx][0], -0.01

            world_point = np.array([p[0], p[1], 1.61697903275, 1]).T
            new_pixel = M @ world_point

            new_pixel = ((new_pixel/new_pixel[2])+0.5).astype(int)
            new_pixels.append([new_pixel[0], new_pixel[1]])

            cv2.circle(self.image,
                       (new_pixel[0], new_pixel[1]), 1, color, -1)

        return draw_image(self.image, new_pixels, img_name, color, alpha)

    def M(self, theta=0, phi=0, gamma=0, dx=0, dy=0, dz=0):
        w, h = self.width, self.height
        f_w, f_h = self.focal_w, self.focal_h

        RX = np.array([[1, 0, 0],
                       [0, np.cos(theta), -np.sin(theta)],
                       [0, np.sin(theta), np.cos(theta)]])

        RY = np.array([[np.cos(phi), 0, np.sin(phi)],
                       [0, 1, 0],
                       [-np.sin(phi), 0, np.cos(phi)]])

        RZ = np.array([[np.cos(gamma), -np.sin(gamma), 0],
                       [np.sin(gamma), np.cos(gamma), 0],
                       [0, 0, 1]])

        RT = np.zeros((3, 4))
        RT[:3, :3] = RX@RY@RZ
        RT[:3, 3] = np.array([dx, dy, dz]).T
        # print(dx, dy, dz)
        extrinsic = RT
        intrinsic = np.array([[f_w, 0, w/2],
                              [0, f_h, h/2],
                              [0, 0, 1]])

        return intrinsic@extrinsic, intrinsic, extrinsic

    def get_rad(self, theta, phi, gamma):
        return (self.deg_to_rad(theta),
                self.deg_to_rad(phi),
                self.deg_to_rad(gamma))

    def get_deg(self, rtheta, rphi, rgamma):
        return (self.rad_to_deg(rtheta),
                self.rad_to_deg(rphi),
                self.rad_to_deg(rgamma))

    def deg_to_rad(self, deg):
        return deg * pi / 180.0

    def rad_to_deg(self, rad):
        return rad * 180.0 / pi


def click_event(event, x, y, flags, params):
    # checking for left mouse clicks
    if event == cv2.EVENT_LBUTTONDOWN:

        print(x, ' ', y)

        points.append([x, y])

        font = cv2.FONT_HERSHEY_SIMPLEX
        # cv2.putText(img, str(x) + ',' + str(y), (x+5, y+5), font, 0.5, (0, 0, 255), 1)
        cv2.circle(img, (x, y), 3, (0, 0, 255), -1)
        cv2.imshow('image', img)

    # checking for right mouse clicks
    if event == cv2.EVENT_RBUTTONDOWN:

        print(x, ' ', y)

        font = cv2.FONT_HERSHEY_SIMPLEX
        b = img[y, x, 0]
        g = img[y, x, 1]
        r = img[y, x, 2]
        # cv2.putText(img, str(b) + ',' + str(g) + ',' + str(r), (x, y), font, 1, (255, 255, 0), 2)
        cv2.imshow('image', img)

    cv2.imwrite('output/original_bev.png', img)


def draw_image(ori_img, new_pixels, img_name='projection.png', color=(0, 0, 255), alpha=0.4):

    new_image = cv2.fillPoly(
        ori_img.copy(), [np.array(new_pixels).astype(int)], color)
    new_image = cv2.addWeighted(
        new_image, alpha, ori_img, (1 - alpha), 0)

    # new_pixels_idx = ConvexHull(new_pixels).vertices
    # new_pixels = [new_pixels[idx] for idx in new_pixels_idx]
    # cv2.fillConvexPoly(ori_img, np.array(new_pixels), color)

    # cv2.imshow(
    #     f'BEV to front view Projection {img_name}', ori_img)
    # cv2.imwrite(f'output/{img_name}', ori_img)
    # cv2.waitKey(0)
    # cv2.destroyAllWindows()
    return new_image


def pixel_to_world(points, pitch, depth=28.6080905795, focal_length=640, center=np.array([640, 360])):
    points = points - center
    theta, phi, gamma = pitch*pi/180.0, 0, 0

    RX = np.array([[1, 0, 0],
                   [0, np.cos(theta), -np.sin(theta)],
                   [0, np.sin(theta), np.cos(theta)]])

    RY = np.array([[np.cos(phi), 0, np.sin(phi)],
                   [0, 1, 0],
                   [-np.sin(phi), 0, np.cos(phi)]])

    RZ = np.array([[np.cos(gamma), -np.sin(gamma), 0],
                   [np.sin(gamma), np.cos(gamma), 0],
                   [0, 0, 1]])
    R = RX@RY@RZ
    # print(R)
    points = np.append(points, np.array(
        [[focal_length]*len(points)]).reshape(-1, 1), axis=1)
    # print(points)

    # world_points = (points*depth/focal_length) * \
    #     [1, 1/(np.sin(72*pi/180.))**2, 1]
    world_points = (points*depth/focal_length)@R.T
    # print(world_points)

    # [0, 2.31671180725, 0]
    return world_points+np.array([0, 0, 0])    # (N*3)


def pixel_to_carla(points, theta=0, ego_loc={"x": 0., "y": 0.}, depth=28.6080905795):

    theta = theta*pi/180.0

    # clockwise
    R = np.array([[np.cos(theta), np.sin(theta)],
                  [-np.sin(theta), np.cos(theta)]])

    world_points = R@points.T
    world_points = world_points.T+np.array([ego_loc["x"], ego_loc["y"]])
    world_points = np.append(world_points, np.array(
        [[depth]*len(world_points)]).reshape(-1, 1), axis=1)

    return world_points  # (N*3)


def carla_to_pixel(points, theta=0, ego_loc={"x": 0., "y": 0.}, depth=28.6080905795, focal_length=640, center=np.array([640, 360])):
    theta = theta*pi/180.0

    # clockwise
    R = np.array([[np.cos(theta), np.sin(theta)],
                  [-np.sin(theta), np.cos(theta)]])

    points = points-np.array([ego_loc["x"], ego_loc["y"]])
    pixels = R@points.T
    pixels = (pixels.T*focal_length/depth)+center
    return np.array(pixels)  # (N*2)


if __name__ == "__main__":

    pitch_ang = -90
    frame = "00000160.png"
    scenario_id = "obstacle/10_s-6_1_f_sl/CloudyNoon_none_"

    front_rgb = f"{scenario_id}/rgb/front/{frame}"
    bev_rgb = f"{scenario_id}/rgb/top/{frame}"
    bev_depth = f"{scenario_id}/depth/depth_front/{frame}"

    img = cv2.imread(bev_rgb, 1)
    cv2.imshow('image', img)
    cv2.setMouseCallback('image', click_event)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    # points = [[630, 178], [655, 178], [630, 385], [655, 385]]
    world_points = pixel_to_world(
        np.array(points), pitch=0)
    # print(world_points)

    projection = Projection(front_rgb, world_points)
    projection.bev_to_front(
        theta=pitch_ang, dx=0, dy=0, dz=0, fov=90, img_name=frame)
