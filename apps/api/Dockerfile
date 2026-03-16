FROM node:22-slim AS base
WORKDIR /app

COPY package.json package-lock.json* ./
RUN npm ci

COPY tsconfig.json ./
COPY src ./src
COPY data ./data
COPY public ./public

RUN npm run build

EXPOSE 8080
CMD ["npm", "start"]
