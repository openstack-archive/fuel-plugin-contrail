FROM python:2

RUN  apt-get update -qq &&  \
apt-get install -q -y \
    python-dev \
    libvirt-dev \
    # xvfb \
    # iceweasel \
    # libav-tools \
    && \
apt-get clean  && \
rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

WORKDIR /opt/app

COPY . /opt/app/

ENV OSLO_PACKAGE_VERSION=1.8

RUN pip install -e . -r requirements.txt

ENV OS_USERNAME=admin
ENV OS_PASSWORD=admin
ENV VIRTUAL_DISPLAY=1
ENV OS_FAULTS_CLOUD_DRIVER=fuel
ENV OS_FAULTS_CLOUD_DRIVER_KEYFILE=/opt/app/cloud.key

ENTRYPOINT ["py.test", "-v", "--junit-xml=test_reports/report.xml"]
CMD ["vapor"]
