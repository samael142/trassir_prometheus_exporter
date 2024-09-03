FROM python:3.11
ADD *.py .
ADD requirements.txt .
RUN pip install -r requirements.txt
CMD ["hypercorn"  , "-b", "0.0.0.0:5000", "wsgi:asgi_app"]

