FROM python:3.9.4
ENV DEBIAN_FRONTEND noninteractive
ENV TZ=Asia/Shanghai
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo  > /etc/timezone
ENV LANG C.UTF-8

COPY ./resource /home/site_crawl/resource
WORKDIR /home/site_crawl

COPY resource/apt/sources.list /etc/apt/sources.list
RUN apt-key adv --recv-keys --keyserver keyserver.ubuntu.com 3B4FE6ACC0B21F32 \
    && apt-key adv --recv-keys --keyserver keyserver.ubuntu.com 7EA0A9C3F273FCD8

# ubuntu系统安装中文字体
RUN cp ./resource/zhcn/simsun.ttc /usr/share/fonts/ \
    && cd /usr/share/fonts/ \
    && chmod 644 simsun.ttc \
    && fc-cache -fsv \
    && cd /home/site_crawl \
    && echo 'simsun.ttc ok'

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y sudo \
    && apt-get install -y openssl \
    && sudo apt-get install -y curl


# pip update
RUN pip install --upgrade pip \
    && pip install -r ./deploy/requirements.txt -i https://mirrors.aliyun.com/pypi/simple/

COPY . .

CMD ["python", "./cmd/start_crawl.py"]
# CMD ["python", "test.py"]