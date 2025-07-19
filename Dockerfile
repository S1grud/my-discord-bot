FROM python:3.11-slim

WORKDIR /app

# Копируем requirements.txt и ставим зависимости Python
COPY requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Копируем остальной код
COPY . /app

RUN chmod +x /app/entrypoint.sh

CMD ["/app/entrypoint.sh"]
