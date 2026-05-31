# FROM node:20-alpine

# WORKDIR /app

# COPY package*.json ./

# RUN npm install

# COPY . .

# RUN npm run build

# EXPOSE 3000

# CMD ["npm", "start"]

FROM node:20-alpine

WORKDIR /app

# 1. install deps
COPY package*.json ./
RUN npm install

# 2. copy env FIRST (important for build time)
COPY .env ./

# 3. copy source
COPY . .

# 4. build (uses env at build time)
RUN npm run build

EXPOSE 3000

# 5. runtime env is still available inside container
CMD ["npm", "start"]