from AggregationProcessor import Processor

# Main function to capture vicon and camera data from an object


def main():
    # the selected cameras out of [0, 1, 2, 3, 4, 5, 6, 7]
    camera_ids = [0, 1, 2, 3, 4, 5, 6, 7]
    object_ids = ["KLT_34_neu"]

    processor = Processor(camera_ids, object_ids)
    processor.record()


if __name__ == "__main__":
    main()
