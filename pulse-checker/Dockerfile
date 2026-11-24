FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY probe.py tracker.py checker.py ./
CMD ["python", "checker.py"]
