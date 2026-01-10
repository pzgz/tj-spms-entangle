
# 处理流程

## 外部系统数据同步到科研系统

运行：`python entangle.pyz cmd0`

1. 确定调度，每core.period执行一次
2. 处理entangle下的每个表，根据entangle.*.mode决定执行增量（执行cmd1）还是全量（执行cmd2）
3. 增量时，逐条计算每条记录的md5值，和旧值比较，判断数据是否发生变更，产生增、删、改的json记录，lpush到redis队列(entangle.*.target)
4. 全量时，逐条处理每条记录，生成json，sadd到redis集合(entangle.*.target)；同时设置每条记录的redis hash(entangle.*.taget:*)
5. forward模式时，全部记录生成一条json，根据md5值判断是否发生变化，设置到redis的string值中(entangle.*.target)

## 科研系统数据同步到外部系统

运行：`python entangle.pyz cmd3`



### 依赖关系
`conda install pipreqs`
`pipreqs entangle # 生成entangle/requirements.txt`

### Docker

* create image: `docker build --force-rm -t spms/entangle -f Dockerfile .`
* test container: `docker run --rm -v /Users/duduba/Documents/vsc:/app spms/entangle`
* create container: `docker run -d --name entangle-cmd3 -v /opt/apps:/app spms/entangle cmd3`
* view log: `docker logs -f entangle-cmd3`
* start: `docker-compose start` or `docker-compose start spmsin`
* view logs: `docker-compose logs -f --tail=100`

### 打包
`python -m zipapp src -o entangle.pyz`
`scp -P 8080 entangle.pyz laic@tjspms.laic-tech.com:`

### 运行

* 同步到spms：`python entangle.pyz cmd0`
* 同步到财务： `python entangle.pyz cmd3`


实时调度：全量和增量同步
python -m entangle -c ../etc/config.yml cmd0

处理历史表
python -m entangle -c ../etc/config.yml -s cmd2

增量同步单张表PS_ETC_CW_BUDSTR
python -m entangle -c ../etc/config.yml cmd1 -n PS_ETC_CW_BUDSTR

同步数据到外部系统
python -m entangle -c ../etc/config.yml cmd3


## 最新部署和build方式

* 在生产服务器上checkout代码
* 进入代码目录，使用以下命令打包: `docker build -t spms/entangle .`
* 在`docker-compose.yml`的目录运行: `docker compose up -d`
