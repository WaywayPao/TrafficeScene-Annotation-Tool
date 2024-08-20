from hashlib import new
import os
import cv2
import math
import numpy as np
from math import pi
from shapely.geometry import LineString, Polygon, MultiLineString

points = []
if not os.path.isdir('output'):
    os.mkdir('output')


class Projection(object):

    def __init__(self, image_shape=(720, 1280, 3), fov=90):
        self.height, self.width, self.channels = image_shape

        self.focal_w = self.width / (2 * math.tan(fov * math.pi / 360))
        self.focal_h = self.focal_w

    def bev_to_front(self, image, theta=0, phi=0, gamma=0, sensor_h=1.61697903275, world_points=[], color=(0, 0, 255), instance_id=0, show_img=False):

        rtheta, rphi, rgamma = self.get_rad(theta, phi, gamma)
        self.M, intrisic, extrinsic = self.tranformation_matrix(
            rtheta, rphi, rgamma)

        # check image boundary
        if sensor_h != 100:   # non-LBC
            a = LineString([(-500, 0), (500, 0)])

            poly = Polygon(world_points[:, :2])
            multi_line = MultiLineString([a])
            line_poly = multi_line.convex_hull

            if np.cross(world_points[0], world_points[1]) < 0:
                # counter-clockwise point
                intersection = np.array(poly.intersection(line_poly).coords)
            else:
                # clockwise point
                intersection = np.flipud(
                    np.array(poly.intersection(line_poly).coords))

        idx = -1
        new_pixels = []
        n = len(world_points)

        for p, i in zip(world_points, range(n)):
            if sensor_h != 100 and p[1] > 0:
                if len(intersection) == 0:
                    p[0], p[1] = 0, -0.01
                else:
                    if idx < len(intersection)-1 and (world_points[(i+1) % n][1] < 0 or idx == -1):
                        idx += 1
                    p[0], p[1] = intersection[idx][0], -0.01

            world_point = np.array([p[0], p[1], sensor_h, 1]).T
            new_pixel = self.M @ world_point

            new_pixel = ((new_pixel/new_pixel[2])+0.5).astype(int)
            new_pixels.append([new_pixel[0], new_pixel[1]])

        new_img = None
        if show_img:
            new_img = cv2.fillPoly(
                image.copy(), [np.array(new_pixels).astype(int)], color)
            cv2.imshow(f'instance id: {instance_id}, class: ...', new_img)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

        mask = np.zeros((self.height, self.width))
        updated_mask = (cv2.fillPoly(
            mask.copy(), [np.array(new_pixels).astype(int)], instance_id)).astype('uint8')

        if (updated_mask == mask).all():
            updated_mask = None

        return new_img, updated_mask

    def tranformation_matrix(self, theta=0, phi=0, gamma=0, dx=0, dy=0, dz=0):
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


def related_distance(points, theta=0, ego_loc={"x": 0., "y": 0.}):
    theta = theta*pi/180.0

    # clockwise
    R = np.array([[np.cos(theta), np.sin(theta)],
                  [-np.sin(theta), np.cos(theta)]])

    points = points-np.array([ego_loc["x"], ego_loc["y"]])
    world_dis = (R@points.T).T

    return np.array(world_dis)  # (N*2)


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
    points = np.append(points, np.array(
        [[focal_length]*len(points)]).reshape(-1, 1), axis=1)

    world_points = (points*depth/focal_length)@R.T

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


def carla_to_pixel(points, theta=0, ego_loc={"x": 0., "y": 0.}, depth=100, focal_length=640, center=np.array([640, 360])):
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
    scenario_id = ""

    front_rgb = f"{scenario_id}/rgb/front/{frame}"
    bev_rgb = f"{scenario_id}/rgb/top/{frame}"
    bev_depth = f"{scenario_id}/depth/depth_front/{frame}"

    img = cv2.imread(bev_rgb, 1)
    cv2.imshow('image', img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()

    world_points = pixel_to_world(
        np.array(points), pitch=0)

    projection = Projection(front_rgb, world_points)
    projection.bev_to_front(
        theta=pitch_ang, dx=0, dy=0, dz=0, fov=90, img_name=frame)
