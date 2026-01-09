FROM python:3.9-slim-bullseye

LABEL vendor="LAIC" \
    maintainer="ly.deng@gmail.com"

RUN sed -i 's|deb.debian.org|mirror.sjtu.edu.cn|g' /etc/apt/sources.list && \
    sed -i 's|security.debian.org/debian-security|mirror.sjtu.edu.cn/debian-security|g' /etc/apt/sources.list && \
    apt-get update && apt-get -y install \
#    net-tools \
#    iputils-ping \
    libarchive-tools \
    libaio1 \
    gcc \
    python3-dev && \
    rm -rf /var/lib/apt/lists/* && \
    echo "Asia/Shanghai" > /etc/timezone && \
    ln -sf /usr/share/zoneinfo/Asia/Shanghai  /etc/localtime && \
    dpkg-reconfigure -f noninteractive tzdata

ENV ORACLE_HOME=/usr/local/instantclient
ENV PATH=$ORACLE_HOME:$PATH \
    LD_LIBRARY_PATH=$ORACLE_HOME \
    NLS_LANGE="SIMPLIFIED CHINESE_CHINA.UTF8"

COPY instantclient-basiclite-linux.x64-12.2.0.1.0.zip /tmp/

RUN bsdtar -xvf /tmp/instantclient-basiclite-linux.x64-12.2.0.1.0.zip -C /usr/local && \
    rm /tmp/instantclient-basiclite-linux.x64-12.2.0.1.0.zip && \
    ln -s /usr/local/instantclient_12_2 /usr/local/instantclient && \
    ln -s /usr/local/instantclient/libclntsh.so.* /usr/local/instantclient/libclntsh.so && \
    ln -s /usr/local/instantclient/libocci.so.* /usr/local/instantclient/libocci.so

COPY requirements.txt /tmp/

RUN pip install --no-cache-dir -i https://mirror.sjtu.edu.cn/pypi/web/simple/ -r /tmp/requirements.txt

WORKDIR /app/entangle/

COPY src/ /app/entangle/src/

RUN python -m zipapp src -o entangle.pyz && rm -rf src/

ENTRYPOINT ["python", "entangle.pyz"]
CMD ["--help"]
