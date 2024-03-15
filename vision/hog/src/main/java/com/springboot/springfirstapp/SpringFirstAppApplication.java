package com.springboot.springfirstapp;

import org.opencv.core.Core;
import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

import org.opencv.core.CvType;
import org.opencv.core.Mat;

@SpringBootApplication
public class SpringFirstAppApplication {
	public static void main(String[] args) {
		System.loadLibrary(Core.NATIVE_LIBRARY_NAME);
//		 Mat mat = Mat.eye(3, 3, CvType.CV_8UC1);
//		 System.out.println("mat = " + mat.dump());
		Mat m = new Mat();
		System.out.println(System.getProperty("java.library.path"));
		SpringApplication.run(SpringFirstAppApplication.class, args);
	}
}
