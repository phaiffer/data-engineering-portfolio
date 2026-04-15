FROM node:20-alpine AS build

WORKDIR /app

COPY dashboard/package.json dashboard/package-lock.json ./

RUN npm ci

COPY dashboard/ ./

ARG VITE_API_BASE_URL=http://127.0.0.1:5002
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL}

RUN npm run build

FROM node:20-alpine AS runtime

WORKDIR /app

RUN npm install --global serve

COPY --from=build /app/dist ./dist

EXPOSE 4173

CMD ["serve", "-s", "dist", "-l", "4173"]
