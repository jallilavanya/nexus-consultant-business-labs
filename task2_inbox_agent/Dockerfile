FROM node:22-alpine
WORKDIR /service
COPY task2_inbox_agent/package*.json ./
RUN npm install
COPY task2_inbox_agent/ ./
EXPOSE 8002
CMD ["npm", "start"]
