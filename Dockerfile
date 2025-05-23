FROM python:3.10-slim
WORKDIR /

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install gunicorn
EXPOSE 80
COPY . .

CMD ["python", "main.py","gunicorn", "--bind", "0.0.0.0:80",]
