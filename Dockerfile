FROM python:3.7.1-slim

LABEL vendor="LAIC" \
    maintainer="ly.deng@gmail.com"

RUN apt-get update && apt-get -y install \
#    net-tools \
#    iputils-ping \
    bsdtar \
    libaio1 \
    wget && \
    rm -rf /var/lib/apt/lists/* && \
    echo "Asia/Shanghai" > /etc/timezone && \
    ln -sf /usr/share/zoneinfo/Asia/Shanghai  /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata

ENV ORACLE_HOME /usr/local/instantclient
ENV PATH=$ORACLE_HOME:$PATH \
    LD_LIBRARY_PATH=$ORACLE_HOME:$LD_LIBRARY_PATH \
    NLS_LANGE="SIMPLIFIED CHINESE_CHINA.UTF8"

RUN wget -qO- https://github.com/iDuduba/resources/raw/master/instantclient-basiclite-linux.x64-12.2.0.1.0.zip | bsdtar -xvf- -C /usr/local && \
    ln -s /usr/local/instantclient_12_2 /usr/local/instantclient && \
    ln -s /usr/local/instantclient/libclntsh.so.* /usr/local/instantclient/libclntsh.so && \
    ln -s /usr/local/instantclient/libocci.so.* /usr/local/instantclient/libocci.so

COPY requirements.txt /tmp/

RUN pip install --no-cache-dir -r /tmp/requirements.txt

WORKDIR /app/entangle/

COPY src/ /app/entangle/src/

RUN python -m zipapp src -o entangle.pyz && rm -rf src/

ENTRYPOINT ["python", "entangle.pyz"]
CMD ["--help"]
