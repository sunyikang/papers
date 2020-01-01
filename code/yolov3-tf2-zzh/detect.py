import time
from absl import app, flags, logging
from absl.flags import FLAGS
import cv2
import numpy as np
import tensorflow as tf
from yolov3_tf2.models import (
    YoloV3, YoloV3Tiny
)
from yolov3_tf2.dataset import transform_images
from yolov3_tf2.utils import draw_outputs
import platformer

flags.DEFINE_string('classes', './data/coco.names', 'path to classes file')
flags.DEFINE_string('weights', './checkpoints/yolov3.tf',
                    'path to weights file')
flags.DEFINE_boolean('tiny', False, 'yolov3 or yolov3-tiny')
flags.DEFINE_integer('size', 416, 'resize images to')
flags.DEFINE_string('image', './data/girl.png', 'path to input image')
flags.DEFINE_string('output', './output.jpg', 'path to output image')
flags.DEFINE_integer('num_classes', 80, 'number of classes in the model')

"""
P1: good code explains itself
P2: mess code shall be split
P3: no duplication
P4: related things shall be put together
P5: hide info that is not worth to expose
P6: one level abstraction per level
"""


def _setup_memory_growth():
    if platformer.get_platform() != 'OS X':
        physical_devices = tf.config.experimental.list_physical_devices('GPU')
        if len(physical_devices) > 0:
            tf.config.experimental.set_memory_growth(physical_devices[0], True)

            
def _create_yolo(tiny, num_classes):
    if tiny:
        return YoloV3Tiny(classes=num_classes)
    else:
        return YoloV3(classes=num_classes)

def _load_weight(yolo, weights):
    yolo.load_weights(weights)
    logging.info('weights loaded')
    
    
def _load_class_names(classes):
    class_names = [c.strip() for c in open(classes).readlines()]
    logging.info('classes loaded')
    return class_names
   
    
def _prepare_image(image, size):
    img = tf.image.decode_image(open(image, 'rb').read(), channels=3)
    img = tf.expand_dims(img, 0)
    img = transform_images(img, size)
    return img
    
    
def _yolo_evaluate_image(yolo, img):
    t1 = time.time()
    boxes, scores, classes, nums = yolo(img)
    t2 = time.time()
    logging.info('time: {}'.format(t2 - t1))
    return boxes, scores, classes, nums


def _print_score_boxes_per_class(class_names, scores, boxes):
    logging.info('detections:')
    for i in range(nums[0]):
        logging.info('\t{}, {}, {}'.format(class_names[int(classes[0][i])],
                                           np.array(scores[0][i]),
                                           np.array(boxes[0][i])))

        
def _draw_outputs_on_image_and_save_it(imagepath, (boxes, scores, classes, nums), class_names):
    img = cv2.imread(imagepath)
    img = draw_outputs(img, (boxes, scores, classes, nums), class_names)
    cv2.imwrite(FLAGS.output, img)
    logging.info('output saved to: {}'.format(FLAGS.output))

    
def _prepare_yolo(FLAGS.tiny, FLAGS.num_classes, FLAGS.weights)
    _create_yolo(FLAGS.tiny, FLAGS.num_classes)
    _yolo_load_weight(yolo, FLAGS.weights)
    return yolo


def _output_results(FLAGS.classes, FLAGS.image, boxes, scores, classes, nums):
    class_names = _load_class_names(FLAGS.classes)
    _print_score_boxes_per_class(class_names, scores, boxes)
    _draw_outputs_on_image_and_save_it(FLAGS.image, (boxes, scores, classes, nums), class_names)


def main(_argv):
    _setup_memory_growth()
    
    yolo = _prepare_yolo(FLAGS.tiny, FLAGS.num_classes, FLAGS.weights)
    img = _prepare_image(FLAGS.image, FLAGS.size)
    boxes, scores, classes, nums = _yolo_evaluate_image(yolo, img)
    
    _output_results(FLAGS.classes, FLAGS.image, boxes, scores, classes, nums)
    
if __name__ == '__main__':
    try:
        app.run(main)
    except SystemExit:
        pass
