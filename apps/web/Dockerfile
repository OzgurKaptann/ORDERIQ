FROM node:20-alpine

WORKDIR /app

# Install dependencies (cached layer)
COPY package.json package-lock.json* ./
RUN npm install

# Copy source (overridden by bind mount in local dev)
COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev"]
