package com.springboot.springfirstapp.service;

import org.opencv.core.*;
import org.opencv.imgcodecs.Imgcodecs;
import org.opencv.imgproc.Imgproc;
import org.opencv.objdetect.HOGDescriptor;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.mock.web.MockMultipartFile;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.File;
import java.io.IOException;
import java.lang.reflect.Array;
import java.nio.file.Files;
import java.util.Arrays;
import java.util.List;
import java.util.UUID;


//@Service
public class HogService {

    public ResponseEntity ProcessImage(MultipartFile multipartFile) {
        try {
            File imageFile = File.createTempFile(UUID.randomUUID().toString(),".png");
            multipartFile.transferTo(imageFile);
            System.out.println("Start");
            // Load image
            Mat image = Imgcodecs.imread(imageFile.getAbsolutePath()); // will be replaced with request body

            // Convert image to grayscale
            Mat gray = new Mat();
            Imgproc.cvtColor(image, gray, Imgproc.COLOR_BGR2GRAY);

            // Calculate HOG features
            HOGDescriptor hog = new HOGDescriptor();
            hog.setSVMDetector(HOGDescriptor.getDefaultPeopleDetector());
            MatOfRect foundLocations = new MatOfRect();
            MatOfDouble foundWeights = new MatOfDouble();

            hog.detectMultiScale(
                    gray,
                    foundLocations,
                    foundWeights,
                    0,
                    new Size(8,8),
                    new Size(32,32),
                    1.05,
                    2,
                    false);

            List<Rect> rectangles = foundLocations.toList();

            for (int i = 0; i < rectangles.size(); i++) {
                Imgproc.rectangle(image,
                        new Point(rectangles.get(i).x,rectangles.get(i).y),
                        new Point(rectangles.get(i).x + rectangles.get(i).width,
                                rectangles.get(i).y + rectangles.get(i).height),
                        new Scalar (255,0,0), 2, 1, 0);
            }
            // Display HOG features
            // System.out.println(features.dump());
            File result = File.createTempFile( UUID.randomUUID().toString(),".png");
            File persist = new File("/home/tmp/vision_microservice_hog/src/main/resources/result.png");
            Imgcodecs.imwrite(persist.getAbsolutePath(),image);
            Imgcodecs.imwrite(result.getAbsolutePath(), image);
            byte[] content = null;
            try {
                content = Files.readAllBytes(result.toPath());
            } catch (final IOException e) {
            }
            MultipartFile mfResult = new MockMultipartFile( UUID.randomUUID().toString(),
                    UUID.randomUUID().toString(), "image/png", content);
            System.out.println("complete");
            // delete later
            // System.out.println(Arrays.toString(mfResult.getBytes()));


            return ResponseEntity.ok(mfResult.getBytes());
        }catch (Exception e){
            e.printStackTrace();
        }
        return null;
    }
}
