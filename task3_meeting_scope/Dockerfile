
FROM python:3.12-slim

WORKDIR /service

COPY task3_meeting_scope/requirements.txt ./requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY task3_meeting_scope/app ./app

EXPOSE 8003

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8003}"]
