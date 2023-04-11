### 框架依赖安装：
> pip install -r requirement.txt -i http://pypi.douban.com/simple/  
> 


### 部署
```text
docker run -d --name container_name  -v /data/news/site_crawl/site_crawl:/home/site_crawl   --restart=always  image_id
```
