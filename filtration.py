import os
import csv
import shutil
import cv2

'''
    Simple script for manually filtering out invalid images
'''

cams = [2, 7]
recording = '23_57 20_02_2022'


def filter_images():
    corrupt_imgs = 0
    for cam in cams:
        recording_path = os.path.join(
            './recordings', recording, f'camera_{cam}')
        filtered_path = os.path.join(
            './recordings', recording + '_filtered', f'camera_{cam}')
        if not os.path.exists(filtered_path):
            os.makedirs(filtered_path)
        csv_gt = os.path.join(recording_path, 'data.csv')
        csv_filtered = os.path.join(filtered_path, 'data.csv')
        filtered_path_images = os.path.join(filtered_path, 'images')
        if not os.path.exists(filtered_path_images):
            os.makedirs(filtered_path_images)

        with open(csv_gt) as in_file:
            reader = csv.reader(in_file)
            reader_list = list(reader)
            header = reader_list[0]
            images = {row[header.index('ImageName')]: []
                      for row in reader_list[1:]}
            for row in reader_list[1:]:
                img_path = row[header.index('ImageName')]
                images[img_path].append(row)

        rows = []
        object_index = 0
        last_index = -1
        index = 0
        edit_index = 0
        keys = list(images.keys())
        while index < len(keys):
            if object_index >= len(images[keys[index]]):
                index += 1
                continue
            row = images[keys[index]][object_index]
            img_path = keys[index]
            obj_id = row[header.index('ObjectID')]
            img = cv2.imread(img_path)
            if img is not None:
                print(f"{index}/{len(keys)}   {len(rows)}")
                cv2.imshow(f'Object {obj_id} in Camera {cam}?', img)
                key = cv2.waitKey(0)
                if key == 97:  # a
                    print('Image Accepted')
                    if last_index == -1:
                        rows.append(row)
                        index += 1
                        edit_index += 1
                    else:
                        print('Image Replaced')
                        rows[index] = row
                        index = last_index
                        last_index = -1
                        edit_index = len(rows)
                elif key == 114:  # r
                    print('Image Rejected!')
                    index += 1
                    edit_index += 1
                    rows.append(None)
                elif key == 113:  # q
                    cv2.destroyAllWindows()
                    break
                # go one index back and reedit last
                elif key == 110:  # n
                    last_index = index if last_index == -1 else last_index
                    index -= 1 if index > 0 else 0
                    edit_index -= 1 if index > 0 else 0
                cv2.destroyAllWindows()
            else:
                corrupt_imgs += 1
                continue

            if index == len(keys):
                object_index += 1
                index = 0

        with open(csv_gt) as in_file, open(csv_filtered, 'w', newline='') as out_file:
            writer = csv.writer(out_file)
            writer.writerow(header)
            for row in rows:
                if row is None:
                    continue
                img_path = row[header.index('ImageName')]
                shutil.copy2(img_path, filtered_path_images)
                writer.writerow(row)

        print(corrupt_imgs)


if __name__ == '__main__':
    filter_images()
