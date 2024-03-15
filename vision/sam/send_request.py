import requests
import json

# the server has an api "/tests" that accepts a get request with parameters "task", "host", "port", and "api"

if __name__ == "__main__":
    host = "http://127.0.0.1:5000" # We want to get the "ip or domain name" and the "port" of the service to test from the get requests's "host" and "port" parameter.
    # encode the image as a binary string
    image = open("claypotRice.jpg","rb").read() # For detection and segmentation, we only have this image
    # put the image and mask in a multipart/form-data
    files = {'image': image} 
    # send a post request to the detect endpoint
    response = requests.post(host+"/", files=files) # "/detections" is the API for YOLO. Here we want to let the test server receive an api from a get requests's parameter.
    # the API, as far as I remember, includes "/" and "detections".
    # save response as a png image
    open('sam_results.png', 'wb').write(response.content)
    # TODO: check the response status code

    # TODO: check the format of the response
    # the response should be a PNG image encoded as a binary string
    print(response.json())
    # TODO: response to the request with status code 200 and a JSON
    if response.status_code == 200:
        print("Test successful")
    else:
        print("Test failed")
    # {result: true} if the test is passed
    # {result: false, error: where the request failed the test.} if the test is failed