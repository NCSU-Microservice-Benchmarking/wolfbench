package com.springboot.springfirstapp.configuration;

import com.springboot.springfirstapp.service.*;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;

@Configuration
public class HogServiceConfig {
    @Bean
    public HogService hogBean() {
        System.out.println("Create a HOG service");
        return new HogService();
    }
}
