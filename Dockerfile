FROM python:3.9
EXPOSE 8051
WORKDIR /app
COPY . ./
RUN pip3.9 install -r requirements.txt
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8501", "--server.enableCORS=false", "--server.enableXsrfProtection=false"]
