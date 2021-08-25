import sys
from numpy.core.fromnumeric import shape
import cv2
from PIL.Image import ImageTransformHandler
import argparse
from camera import Camera
import time
from demo.predictor import VisualizationDemo
from detectron2.config import get_cfg
from detectron2.utils.logger import setup_logger


def get_parser():
    parser = argparse.ArgumentParser(
        description="Detectron2 demo for builtin configs")
    parser.add_argument(
        "--config-file",
        default="/home/athos/detectron2/configs/quick_schedules/mask_rcnn_R_50_FPN_inference_acc_test.yaml",
        metavar="FILE",
        help="path to config file",
    )

    parser.add_argument(
        "--confidence-threshold",
        type=float,
        default=0.5,
        help="Minimum score for instance predictions to be shown",
    )
    parser.add_argument(
        "--opts",
        help="Modify config options using the command-line 'KEY VALUE' pairs",
        default=[],
        nargs=argparse.REMAINDER,
    )
    return parser


def setup_cfg(args):
    # load config from file and command-line arguments
    cfg = get_cfg()
    # To use demo for Panoptic-DeepLab, please uncomment the following two lines.
    # from detectron2.projects.panoptic_deeplab import add_panoptic_deeplab_config  # noqa
    # add_panoptic_deeplab_config(cfg)
    cfg.merge_from_file(args.config_file)
    cfg.merge_from_list(args.opts)
    # Set score_threshold for builtin models
    cfg.MODEL.RETINANET.SCORE_THRESH_TEST = args.confidence_threshold
    cfg.MODEL.ROI_HEADS.SCORE_THRESH_TEST = args.confidence_threshold
    cfg.MODEL.PANOPTIC_FPN.COMBINE.INSTANCES_CONFIDENCE_THRESH = args.confidence_threshold
    cfg.freeze()
    return cfg


if __name__ == '__main__':
    cam = Camera(0)
    setup_logger(name="fvcore")
    logger = setup_logger()
    parser = get_parser()
    args = parser.parse_args()
    logger.info("Arguments: " + str(args))
    while True:
        image = cam.getImage()
        if image is None:
            continue
        image = cv2.flip(image, 0)
        image = cv2.flip(image, 1)
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image_resized = cv2.resize(image, (int(2592 / 2), int(2048 / 2)))
        image_resized[0], image_resized[1] = image_resized[1], image_resized[0]
        print(shape(image_resized))

        cfg = setup_cfg(args)
        demo = VisualizationDemo(cfg)
        start_time = time.time()
        predictions, visualized_output = demo.run_on_image(image_resized)
        logger.info(
            "{} in {:.2f}s".format(
                "detected {} instances".format(len(predictions["instances"]))
                if "instances" in predictions
                else "finished",
                time.time() - start_time,
            )
        )
        cv2.imshow('cam_pred', visualized_output.get_image()[:, :, ::-1])
        if cv2.waitKey(1) == 27:  # esc
            cv2.destroyAllWindows()
            break
    cam.close()
