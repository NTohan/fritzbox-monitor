FROM python:3.9 

RUN mkdir -p install/logs
RUN mkdir -p install/docs
ADD *.py install
ADD requirements*.txt install
RUN apt update
RUN apt install -y tree catimg vim
RUN pip install requests beautifulsoup4 python-dotenv
RUN pip install -r install/requirements.txt

#CMD ["python", "./install/fritz.py"] 
ENTRYPOINT ["./install/fritz.py"]