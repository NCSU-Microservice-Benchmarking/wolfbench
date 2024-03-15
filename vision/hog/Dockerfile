# Use the official OpenJDK 17 image as the base image
FROM mcr.microsoft.com/openjdk/jdk:17-ubuntu

# Set the working directory inside the container
WORKDIR /app

# Copy src/main/resources/open
COPY src/main/resources/lib/opencv-480.jar /usr/lib
COPY src/main/resources/lib/libopencv_java480.so /usr/lib
ENV LD_LIBRARY_PATH /usr/lib

# Copy the JAR file to the working directory
COPY target/spring-first-app-0.0.1-SNAPSHOT.jar /app


# Expose port 5000
EXPOSE 5000

# Set the entry point for the container
ENTRYPOINT ["java", "-jar", "spring-first-app-0.0.1-SNAPSHOT.jar"]