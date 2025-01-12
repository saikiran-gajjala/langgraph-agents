FROM python:3.11-slim

WORKDIR /app

COPY . /app   

RUN pip install --no-cache-dir --upgrade -r requirements.txt

EXPOSE 8001

ENV PYTHONPATH="/app/agents:/app"

CMD ["uvicorn", "agents.main:app", "--host", "0.0.0.0", "--port", "8001"]
