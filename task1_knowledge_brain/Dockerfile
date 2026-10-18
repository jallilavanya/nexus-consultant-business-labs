FROM python:3.12-slim
WORKDIR /service
COPY task1_knowledge_brain/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY task1_knowledge_brain/app ./app
EXPOSE 8001
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8001"]
