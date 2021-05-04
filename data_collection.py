import csv
import numpy as np
import json
import os
import cv2
from pyquaternion import Quaternion

objects_ids = {"KLT_15_neu": 0}
index = 0


def get_obj_to_cam_transform(obj_to_world_trans, obj_to_world_rot_quat, cam_id):
    obj_to_world_rot_quat_2 = Quaternion(
        obj_to_world_rot_quat[3],
        obj_to_world_rot_quat[0],
        obj_to_world_rot_quat[1],
        obj_to_world_rot_quat[2],
    )  # w,x,y,z
    obj_to_world_rot = obj_to_world_rot_quat_2.rotation_matrix

    cam_to_world_trans = camera_data["cam" + str(cam_id)]["trans"]
    cam_to_world_rot = camera_data["cam" + str(cam_id)]["rot"]
    obj_to_cam_trans = [
        (cam_to_world_trans[i] - obj_to_world_trans[i])
        for i in range(len(obj_to_world_trans))
    ]
    obj_to_cam_rot = obj_to_world_rot * np.transpose(cam_to_world_rot)
    return obj_to_cam_trans, obj_to_cam_rot


def string_to_numpy(string):
    new_string = string.replace("[", "").replace("]", "")
    array = np.fromstring(new_string, sep=",")
    return array


def update(
    index, objectName, cameraID, image, obj_to_world_trans, obj_to_world_rot_quat
):
    with open("annotation_data.csv", "a", newline="") as f:
        writer = csv.writer(f)

        if index == 0:
            writer.writerow(
                [
                    "objectID",
                    "camerID",
                    "imageName",
                    "CamToObjTrans",
                    "CamToObjRot",
                    "ObjToWorldTrans",
                    "symmetry",
                ]
            )

        # get the object id
        objectID = objects_ids[objectName]
        # save the image to file
        imageName = os.path.join(".", "images", "data", f"image_{index}.png")
        print(imageName)
        cv2.imwrite(imageName, image)
        # get camera - object relation
        obj_to_cam_trans, obj_to_cam_rot = get_obj_to_cam_transform(
            obj_to_world_trans, obj_to_world_rot_quat, cameraID
        )
        # final assembly
        data = [
            objectID,
            cameraID,
            imageName,
            list(obj_to_cam_trans),
            [list(array) for array in obj_to_cam_rot],
            list(obj_to_world_trans),
            0,
        ]
        writer.writerow(data)


with open("cam_poses.json", "r") as f:
    camera_data = json.load(f)

with open("data.csv") as f:
    reader = csv.reader(f)

    print("Press q for accepting and r for rejecting the image!")

    for iteration, row in enumerate(reader):

        print(f"Object name: {row[0]}, image id: {row[1]}")

        obj_to_world_trans = string_to_numpy(row[2])
        obj_to_world_rot_quat = string_to_numpy(row[3])

        for camID in range(8):
            fileName = os.path.join("images", f"camera_{camID}", f"{row[1]}.npy")
            if not os.path.isfile(fileName):
                print(f"Not image found for camera {camID}")
                continue
            image = np.load(fileName)
            cv2.imshow("Camera View", image)

            key = cv2.waitKey(0)
            # accept #
            if key == ord("q"):
                update(
                    index,
                    row[0],
                    camID,
                    image,
                    obj_to_world_trans,
                    obj_to_world_rot_quat,
                )
                index += 1
            # reject #
            elif key == ord("r"):
                print(f"IMAGE {fileName} was rejected")
                continue
