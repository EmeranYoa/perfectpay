FROM python:3.9

WORKDIR /perfectpay

COPY ./requirements.txt /perfectpay/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /perfectpay/requirements.txt

COPY . /perfectpay/

# COPY .env /perfectpay/app/.env

WORKDIR /perfectpay/app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80", "--reload"]