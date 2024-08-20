import numpy as np
import os
import cv2

labeled_path = 'label/top'
data_path = 'mini_dataset/data_collection/interactive'
save_path = 'labedled_mask'     # {variant_scenario}/{weather}/{labedled_mask}
view = ['front', 'left', 'right', 'lbc_img'][3]

### user optional
######################################################
test_scenario = "5_i-1_0_b_l_f_1_0/variant_scenario/CloudyNoon_high_"
check_mask_path = f"{data_path}/{test_scenario}/{save_path}/{view}"
check_rgb_path = f"{data_path}/{test_scenario}/rgb/{view}"
check_frame = "00000072.npy"
######################################################

def check_mask(mask_path, rgb_front_path, check_frame=""):
    if check_frame != "":
        file_list = [check_frame]
    else:
        file_list = os.listdir(mask_path)

    for mask_name in file_list:
        frame_id = int(mask_name.split('.')[0])

        mask = np.load(os.path.join(mask_path, mask_name))
        img = cv2.imread(os.path.join(rgb_front_path, f'{frame_id:08d}.png'))

        for m in mask:
            new_m = np.zeros((m.shape[0], m.shape[1], 3)).astype('uint8')
            m[m!=0] = 255
            new_m[:, :, 0] = 0
            new_m[:, :, 1] = m
            new_m[:, :, 2] = m
            

            mask_image = cv2.bitwise_and(img, ~new_m)
            
            print(f'{mask_path}/{frame_id:08d}.png')
            cv2.imshow(
                f'{mask_path}/{frame_id:08d}.png', mask_image)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

def auto_test():

    for basic in os.listdir(data_path):
        basic_path = os.path.join(
            data_path, basic, 'variant_scenario')

        for variant in os.listdir(basic_path):
            variant_path = os.path.join(basic_path, variant)
           
            mask_path = os.path.join(
                variant_path, save_path, view)
            rgb_front_path = os.path.join(
                variant_path, 'rgb', view)

            if not os.path.isdir(mask_path):
                continue

            check_mask(mask_path, rgb_front_path)


if __name__ == '__main__':

    if test_scenario != "":
        check_mask(check_mask_path, check_rgb_path, check_frame)
    else:
        auto_test()