# Vision

A computer vision service website that hosts models including:
- [YOLOv8](https://docs.ultralytics.com/models/yolov8/) for object detection, implemented with Flask. Model comes from Ultralytics.
- Histogram oriented gradients (HOG) for people detection, implemented with Spring Boot.
- [Segment Anything Model](https://docs.ultralytics.com/models/sam/) for instance segmentation, implemented with Flask. Model comes from Ultralytics.
- [LaMa](https://github.com/advimman/lama) for image inpainting (under development), implemented with Flask. Model comes from [simple-lama-inpainting](https://pypi.org/project/simple-lama-inpainting/) packege.

## Pre-requisites
- A [Kubernetes](https://kubernetes.io/) cluster.
- [Nginx Ingress Controller](https://kubernetes.github.io/ingress-nginx/) installed in the cluster.
- [Jaeger](https://www.jaegertracing.io/) installed in the cluster for distributed tracing.
- [Prometheus](https://prometheus.io/) installed in the cluster for monitoring.

## Installation
1. Replace the host of ingress in `vision.yaml` with the domain name of your website.
2. Execute the following command to deploy the service to the cluster.
    ```
    kubectl create -f vision.yaml
    ```

## Usage
1. Access the website with the domain name of your website and port 30000.
2. Use the API to interact with the models.
- YOLOv8 object detection: `<your_host_address>/vision/model-yolov8/detections`
- HOG people detection: `<your_host_address>/vision/model-hog-people/`
- Segment Anything Model: `<your_host_address>/vision/model-sam/`