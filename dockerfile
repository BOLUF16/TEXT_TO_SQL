FROM python:3.11.9

ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY requirements.txt app/requirements.txt
COPY . /app

RUN pip install -r requirements.txt

EXPOSE 5000

ENTRYPOINT ["streamlit","run"]

CMD ["streamlit.py"]