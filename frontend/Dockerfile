# FROM node:20-alpine

# WORKDIR /app

# COPY package*.json ./

# RUN npm install

# COPY . .

# RUN npm run build

# EXPOSE 3000

# CMD ["npm", "start"]

# ~/enterprise-rag-platform/frontend/Dockerfile
FROM node:20-alpine

WORKDIR /app

# 1. Install dependencies
COPY package*.json ./
RUN npm install

# 2. Copy source code (Leaving out .env via .dockerignore)
COPY . .

# 3. Set production mode flag and build
ENV NODE_ENV=production
RUN npm run build

EXPOSE 3000

# 4. Boot up production server (reads environment variables at runtime)
CMD ["npm", "start"]