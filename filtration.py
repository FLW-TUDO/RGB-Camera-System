import os
import csv
import shutil
import cv2

'''
    Simple script for manually filtering out invalid images
'''

cams = [2, 7]
recording = '22_50 20_02_2022'

def filter_images():
    corrupt_imgs = 0
    for cam in cams:
        recording_path = os.path.join('./recordings', recording, f'camera_{cam}')
        filtered_path = os.path.join('./recordings', recording + '_filtered', f'camera_{cam}')
        if not os.path.exists(filtered_path):
            os.makedirs(filtered_path)
        csv_gt = os.path.join(recording_path, 'data.csv')
        csv_filtered = os.path.join(filtered_path, 'data.csv')
        filtered_path_images = os.path.join(filtered_path, 'images')
        if not os.path.exists(filtered_path_images):
            os.makedirs(filtered_path_images)
        with open(csv_gt) as in_file, open(csv_filtered, 'w', newline='') as out_file:
            reader = csv.reader(in_file)
            reader_list = list(reader)
            writer = csv.writer(out_file)
            header = reader_list[0]
            writer.writerow(header)
            for row in reader_list[1:]:
                img_path = row[header.index('ImageName')]
                obj_id = row[header.index('ObjectID')]
                img = cv2.imread(img_path)
                if img is not None:
                    cv2.imshow(f'Object {obj_id} in Camera {cam}?', img)
                    key = cv2.waitKey(0)
                    if key == 97: #a
                        print('Image Accepted')
                        shutil.copy2(img_path, filtered_path_images)
                        writer.writerow(row)
                    elif key == 114: #r
                        print('Image Rejected!')
                    elif key == 113: #q
                        cv2.destroyAllWindows()
                        break
                    cv2.destroyAllWindows()
                else:
                    corrupt_imgs += 1
                    continue
        print(corrupt_imgs)

if __name__ == '__main__':
    filter_images()
