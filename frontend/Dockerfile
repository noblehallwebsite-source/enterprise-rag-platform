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

# =========================
# Install dependencies
# =========================
COPY package*.json ./
RUN npm install

# =========================
# Copy source code
# =========================
COPY . .

# =========================
# Build Next.js app
# (env vars MUST exist at build time)
# =========================
ARG BACKEND_URL
ARG BACKEND_API_KEY

ENV BACKEND_URL=$BACKEND_URL
ENV BACKEND_API_KEY=$BACKEND_API_KEY

RUN npm run build

# =========================
# Run app
# =========================
EXPOSE 3000

CMD ["npm", "start"]