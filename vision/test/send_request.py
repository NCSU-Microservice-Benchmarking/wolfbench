import requests
import json
if __name__ == "__main__":
    host = "http://127.0.0.1:5000"
    # send a get request to the greet endpoint
    response = requests.get(host+"/greet")
    # print the response text
    print(response.text)
    # encode the image as a binary string
    image = open("bus.png","rb").read()
    # put the image in a multipart/form-data
    files = {'image': image}
    # send a post request to the detect endpoint
    # response = requests.post(host + '/detections', files=files)
    response = requests.post(host + '/', files=files)
    #response = requests.post(host+"/model-hog-people", "")
    # check the response status code
    print(response.status_code)
    # save the image
    open("result.png","wb").write(response.content)