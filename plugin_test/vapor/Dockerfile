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
ENV OS_PASSWORD=workshop
ENV OS_TENANR_NAME=admin
ENV OS_AUTH_URL=http://172.16.10.254:35357/v3
ENV VIRTUAL_DISPLAY=1
ENV OS_FAULTS_CLOUD_DRIVER=tcpcloud
ENV OS_FAULTS_CLOUD_DRIVER_KEYFILE=/opt/app/cloud.key
ENV OS_FAULTS_CLOUD_DRIVER_ADDRESS=192.168.10.100
ENV OS_FAULTS_CLOUD_DRIVER_USERNAME=root
ENV CONTRAIL_ROLES_DISTRIBUTION_YAML=roles_mk22_qa_lab01.yaml

ENTRYPOINT ["py.test", "-v", "--junit-xml=test_reports/report.xml", \
            "--html=test_reports/report.html"]
