FROM python:3.7.2-alpine3.7

COPY requirements.txt /tmp/
COPY bot.py /tmp/
COPY bot /tmp/bot
RUN pip install -r /tmp/requirements.txt

CMD ["python3", "/tmp/bot.py"]
