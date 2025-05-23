FROM python:3.10-slim
WORKDIR /

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
EXPOSE 80
COPY . .

CMD ["python", "main.py"]
