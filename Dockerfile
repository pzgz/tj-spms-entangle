FROM python:3.7.1-slim

LABEL vendor="LAIC" \
    maintainer="ly.deng@gmail.com"

RUN echo "deb http://mirrors.aliyun.com/debian-archive/debian stretch main contrib non-free" > /etc/apt/sources.list && \
    echo "deb http://mirrors.aliyun.com/debian-archive/debian-security stretch/updates main contrib non-free" >> /etc/apt/sources.list

RUN apt-get update && apt-get -y --allow-unauthenticated install \
#    net-tools \
#    iputils-ping \
    bsdtar \
    libaio1 \
    wget && \
    rm -rf /var/lib/apt/lists/* && \
    echo "Asia/Shanghai" > /etc/timezone && \
    ln -sf /usr/share/zoneinfo/Asia/Shanghai  /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata

ENV ORACLE_HOME=/usr/local/instantclient
ENV PATH=$ORACLE_HOME:$PATH \
    LD_LIBRARY_PATH=$ORACLE_HOME:$LD_LIBRARY_PATH \
    NLS_LANGE="SIMPLIFIED CHINESE_CHINA.UTF8"

COPY instantclient-basiclite-linux.x64-12.2.0.1.0.zip /tmp/

RUN bsdtar -xvf /tmp/instantclient-basiclite-linux.x64-12.2.0.1.0.zip -C /usr/local && \
    rm /tmp/instantclient-basiclite-linux.x64-12.2.0.1.0.zip && \
    ln -s /usr/local/instantclient_12_2 /usr/local/instantclient && \
    ln -s /usr/local/instantclient/libclntsh.so.* /usr/local/instantclient/libclntsh.so && \
    ln -s /usr/local/instantclient/libocci.so.* /usr/local/instantclient/libocci.so
    
COPY requirements.txt /tmp/

ARG PIP_INDEX_URL=https://mirror.sjtu.edu.cn/pypi/web/simple
ARG PIP_EXTRA_INDEX_URL=https://pypi.mirrors.ustc.edu.cn/simple/
RUN pip config set global.index-url "${PIP_INDEX_URL}" && \
    pip config set global.extra-index-url "${PIP_EXTRA_INDEX_URL}" && \
    pip config set global.trusted-host "pypi.mirrors.ustc.edu.cn,mirror.sjtu.edu.cn"

RUN python -m pip install -U pip && \
    pip --version

RUN pip install --no-cache-dir -r /tmp/requirements.txt

WORKDIR /app/entangle/

ENTRYPOINT ["python", "entangle.pyz"]
CMD ["--help"]
