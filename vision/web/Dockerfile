# Use the official Node.js image as the base image
FROM node:20 as build

# Set the working directory
WORKDIR /usr/src/app

# Copy package.json and package-lock.json to the working directory
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy the entire project to the working directory
COPY . .

# Build the React app
RUN npm run build

# Use a smaller, nginx-based image for the production environment
FROM nginx:alpine

# Copy the build output to serve with Nginx
COPY --from=build /usr/src/app/build /usr/share/nginx/html

# Copy the custom Nginx configuration file
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port 80
EXPOSE 80

# # Start Nginx when the container launches
CMD ["nginx", "-g", "daemon off;"]
