# Build stage
FROM node:20-alpine as builder

# Set working directory
WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy project files
COPY . .

# Development stage
FROM node:20-alpine as development

WORKDIR /app

# Copy package files and install dependencies
COPY package*.json ./
RUN npm install

# Copy project files
COPY . .

# Expose port
EXPOSE 4200

# Start development server
CMD ["npm", "start", "--", "--host", "0.0.0.0", "--poll=2000"]
