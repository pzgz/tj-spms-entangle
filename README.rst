

### 依赖关系
`conda install pipreqs`
`pipreqs entangle # 生成entangle/requirements.txt`

### Docker

* create image: `docker build --force-rm -t spms/entangle .`
* test container: `docker run --rm -v /opt/apps:/app spms/entangle`
* create container: `docker run -d --name entangle-cmd3 -v /opt/apps:/app spms/entangle cmd3`
* view log: `docker logs -f entangle-cmd3`

### 打包
`python -m zipapp src -o entangle.pyz`

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
