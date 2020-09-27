FROM python:3.8

WORKDIR /covid19

COPY ./requirements.txt .

RUN pip install -r requirements.txt

COPY ./*.py /covid19/
COPY ./*.json /covid19/
COPY ./apps/*.py /covid19/apps/

EXPOSE 8051:8051

RUN chmod +x /covid19/index.py

CMD ["python", "/covid19/index.py"]

