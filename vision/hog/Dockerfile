# Use the official OpenJDK 17 image as the base image
FROM mcr.microsoft.com/openjdk/jdk:17-ubuntu

# Set the working directory inside the container
WORKDIR /app

# Copy src/main/resources/open
COPY src/main/resources/lib/opencv-480.jar /usr/lib
COPY src/main/resources/lib/libopencv_java480.so /usr/lib
ENV LD_LIBRARY_PATH /usr/lib

# Copy the JAR file to the working directory
COPY target/spring-first-app-0.0.1-SNAPSHOT.jar .
COPY opentelemetry-javaagent.jar .

# # Tracing
# ENV OTEL_TRACES_EXPORTER zipkin
# ENV OTEL_METRICS_EXPORTER none
# ENV OTEL_LOGS_EXPORTER none
# ENV OTEL_EXPORTER_ZIPKIN_ENDPOINT http://jaeger-with-cassandra-and-kafka-collector.observability.svc.cluster.local:9411/api/v2/spans

# # If testing locally with a Jaeger container, uncomment the following line
# # ENV OTEL_EXPORTER_ZIPKIN_ENDPOINT http://host.docker.internal:9411/api/v2/spans
# ENV JAVA_TOOL_OPTIONS="-javaagent:/app/opentelemetry-javaagent.jar -Dotel.exporter.otlp.protocol=http/protobuf"
# ENV OTEL_SERVICE_NAME="vision-hog"

# Expose port 5000
EXPOSE 5000

# Set the entry point for the container
ENTRYPOINT ["java", "-jar", "spring-first-app-0.0.1-SNAPSHOT.jar"]