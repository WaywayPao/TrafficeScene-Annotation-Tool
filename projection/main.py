import numpy as np
import json
import os
import cv2
from utils import Projection, related_distance

# user optional
######################################################
"""
    variable:
        labeled_path
            labeled data path by label_tool_hank_4k

        data_path
            carla dataset path

        save_path
            save path of the mask .npy file
            e.g. {variant_scenario}/{weather}/{hank_tool}
  
        view
            ego-view type, this program only supports running one view at a time

        verbose
            print the process of generating the mask

        color_list
            {class name: (label color, class number), ...}

"""
labeled_path = 'label/top'
data_path = 'mini_dataset/data_collection/interactive'
save_path = 'hank_tool'
view = ['front', 'left', 'right', 'lbc_img'][3]
verbose = True
color_list = {'Corner': ([255, 0, 0], 0), 'Road': ([0, 255, 0], 1), 'Crosswalk': ([0, 0, 255], 2),
              'Intersection': ([255, 255, 0], 3), 'Lane': ([255, 0, 255], 4), 'Route': ([125, 125, 125], 5)}
######################################################


if view == 'lbc_img':
    image_shape = (512, 512, 3)
    fov = 50
    theta = 0
    sensor_h = 100
else:   # ego view
    image_shape = (720, 1280, 3)
    fov = 90
    theta = -90
    sensor_h = 1.61697903275

P = Projection(image_shape=image_shape, fov=fov)


def read_json(json_path):
    """
        return:
            carla_points
                shape ZxPx3 list, world(global) point transform(x, y, z) in carla

            carla_points_color
                shape Z list, rgb color of the zone

            points_by_pixel
                pixel on map_collection image

            Z: zone number
            P: points number of zone
    """
    f = open(json_path)
    info = json.load(f)
    f.close()

    carla_points = info['carla_points']
    carla_points_color = info['carla_points_color']
    points_by_pixel = info['points_by_pixel']

    return carla_points, carla_points_color, points_by_pixel


def get_ego_data(ego_data_path):

    ego_data = open(ego_data_path)
    data = json.load(ego_data)
    ego_data.close()

    ego_info = {}

    for frame_id in data.keys():
        if "transform" in data[frame_id] and "imu" in data[frame_id] and "compass" in data[frame_id]["imu"]:
            compass = data[frame_id]["imu"]["compass"]
            ego_loc = data[frame_id]["transform"]

            ego_info[int(frame_id)] = (compass, ego_loc)

    return ego_info


def get_intance_id(ins_id_list_path, labeled_file, color):

    # total instance number {labeled_file}
    ins_num_list = [0]*len(color_list)

    if not os.path.isfile(ins_id_list_path):
        info = {}
        # total instance number for all labeled_file
        total_ins_num_list = [0]*len(color_list)
    else:
        f = open(ins_id_list_path)
        info = json.load(f)
        f.close()
        if labeled_file in info.keys():
            return None

        total_ins_num_list = info['total_instance_number']

    ins_id_list = []
    for c in color:
        for cls in color_list.keys():
            if color_list[cls][0] == c:
                ins_num_list[color_list[cls][1]] += 1
                total_ins_num_list[color_list[cls][1]] += 1

                ins_id = color_list[cls][1]*32+ins_num_list[color_list[cls][1]]
                break

        ins_id_list.append(ins_id)

    info[labeled_file] = ins_num_list
    info['total_instance_number'] = total_ins_num_list

    with open(ins_id_list_path, 'w') as f:
        json.dump(info, f)

    return ins_id_list


def save_mask(new_mask, variant_path, view, frame_id):
    """
        parameter:
            variant_path
                save the mask to the {variant_path}/{hank_tool}/{view}
            mask
                (NxHxW) ndarray, N is number of total instance
    """
    mask_path = os.path.join(variant_path, save_path, view)
    if not os.path.isdir(mask_path):
        os.mkdir(os.path.join(variant_path, save_path))
        os.mkdir(mask_path)

    mask_path = os.path.join(mask_path, f'{frame_id:08d}.npy')
    if os.path.isfile(mask_path):
        old_mask = np.load(mask_path)
        new_mask = np.concatenate((old_mask, new_mask), axis=0)

    np.save(mask_path, new_mask)


def make_mask(map_scenario, p_carla, p_color, labeled_file):

    for basic in map_scenario:
        basic_path = os.path.join(
            data_path, basic, 'variant_scenario')

        for variant in os.listdir(basic_path):
            variant_path = os.path.join(basic_path, variant)
            ins_id_list_path = os.path.join(variant_path, 'instance_set.json')

            instance_id_list = get_intance_id(
                ins_id_list_path, labeled_file, p_color)
            if instance_id_list is None:
                continue

            ego_info = get_ego_data(os.path.join(
                variant_path, 'ego_data.json'))
            rgb_front_path = os.path.join(
                variant_path, 'rgb', view)

            for img_name in os.listdir(rgb_front_path):
                frame_id = int(img_name.split('.')[0])

                if frame_id not in ego_info.keys():
                    continue

                img = cv2.imread(os.path.join(
                    rgb_front_path, img_name))
                all_mask = np.zeros(
                    (len(p_carla), image_shape[0], image_shape[1])).astype('uint8')

                ins_cnt = 0
                for idx, (points, color) in enumerate(zip(p_carla, p_color)):

                    compass = ego_info[frame_id][0]
                    ego_loc = ego_info[frame_id][1]

                    pts = related_distance(
                        np.array(points)[:, :2], theta=compass, ego_loc=ego_loc)  # np.array([0, 2.31671180725, 0])
                    new_img, mask = P.bev_to_front(
                        img, theta=theta, phi=0, gamma=0, sensor_h=sensor_h, world_points=pts, color=color, instance_id=instance_id_list[idx], show_img=False)

                    if mask is not None:
                        all_mask[ins_cnt] = mask
                        ins_cnt += 1

                if ins_cnt > 0:
                    save_mask(all_mask[:ins_cnt], variant_path, view, frame_id)
                    if verbose:
                        print(
                            f"Saved mask {basic}/{variant}/{view}/{frame_id:08d}.npy")


def main():

    for labeled_file in os.listdir(labeled_path):
        if labeled_file.endswith('.json'):
            p_carla, p_color, p_pixel = read_json(
                os.path.join(labeled_path, labeled_file))

            map_scenario = [basic for basic in os.listdir(
                data_path) if basic[0] == labeled_file[0]]

            make_mask(map_scenario, p_carla, p_color,
                      labeled_file.split('.')[0])


if __name__ == '__main__':
    main()
