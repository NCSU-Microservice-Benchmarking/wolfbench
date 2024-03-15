package com.springboot.springfirstapp.controller;
import com.springboot.springfirstapp.service.HogService;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import io.swagger.v3.oas.annotations.Operation;
//import io.swagger.v3.oas.annotations.media.Content;
//import io.swagger.v3.oas.annotations.media.Schema;
//import io.swagger.v3.oas.annotations.media.SchemaProperties;
//import io.swagger.v3.oas.annotations.parameters.RequestBody;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;
//import io.swagger.v3.oas.annotations.responses.ApiResponse;

@RestController
public class HOGController {
    
    @Autowired
    private HogService myHogService;

    @RequestMapping("/hello")
    public String hello() {
        return "Hello World";
    }

    @RequestMapping("/health-check")
    public String healthCheck() {
        return "healthy";
    }

    @PostMapping("/model-hog-people")
    @Operation(summary = "Returns the detected image",
            description = "Receives an image and returns the detected result")
    public ResponseEntity HogMethod(@RequestParam("image") MultipartFile files) {
        System.out.println("Hello this is the requestbody: ");
        return myHogService.ProcessImage(files);
    }
}
