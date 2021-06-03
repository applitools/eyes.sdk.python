FROM tutorial_python:latest
ARG repo=tutorial-selenium-python-ultrafastgrid
ARG package
ENV REPOSITORY_NAME=$repo
RUN cd home/project \
    && git clone https://github.com/applitools/${REPOSITORY_NAME}.git \
    && cd ${REPOSITORY_NAME} \
    && sed -i 's/"APPLITOOLS_API_KEY"/os.getenv("APPLITOOLS_API_KEY")/g' ultrafastgrid_tutorial.py

COPY ./ultrafastgrid/start.sh /
COPY package/ /

RUN cd home/project/${REPOSITORY_NAME} \
    && pip install -r requirements.txt

RUN pip install ./$package

CMD ./start.sh ${REPOSITORY_NAME}
