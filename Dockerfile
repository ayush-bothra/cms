# ---- Build stage ----
FROM node:22-bookworm-slim AS build
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 make g++ git ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /opt/app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
ENV NODE_ENV=production
RUN npm run build

# ---- Runtime stage ----
FROM node:22-bookworm-slim
ENV NODE_ENV=production
WORKDIR /opt/app

COPY --from=build /opt/app/node_modules ./node_modules
COPY --from=build /opt/app/package.json ./package.json
COPY --from=build /opt/app/build ./build
COPY --from=build /opt/app/public ./public
COPY --from=build /opt/app/src ./src
COPY --from=build /opt/app/config ./config
COPY --from=build /opt/app/favicon.png ./favicon.png

RUN groupadd -r strapi && useradd -r -g strapi strapi \
    && chown -R strapi:strapi /opt/app
USER strapi

EXPOSE 1337
CMD ["npm", "run", "start"]
