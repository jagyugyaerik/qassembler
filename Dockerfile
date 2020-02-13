FROM python:3.6.7-stretch

WORKDIR /app

COPY requirements.txt .
RUN pip3 install -r requirements.txt

COPY . .
RUN python3 setup.py install

EXPOSE 80
CMD ["gunicorn", "--bind", "0.0.0.0:80", "qassembler.main:app"]