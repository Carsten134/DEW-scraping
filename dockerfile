FROM selenium/standalone-firefox

# adding scraper modules and executeable
COPY /project /project
RUN pip install -r /project/requirements.txt

VOLUME [ "/project/data" ]

ENTRYPOINT [ "python3", "/project/main.py" ]