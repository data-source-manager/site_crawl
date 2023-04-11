### 项目结构及目录说明
> apps:每个爬虫网站对应的基础信息及对应的解析方法  
> resource\package 日志对应的包 直接pip install whl包路径(日志依赖包不能遗忘)   
> site_crawl\spider  basic_spider.py 核心爬虫 通过app中的网站基础信息调度对应的解析规则
> site_crawl\spider\parser 每个网站对应的解析规则文件  
> requirements.txt 项目依赖 直接使用pip install 安装即可(项目依赖)    
<font color="red">```注意```</font> dockerfile及docker-compose.yaml 别轻易动  
> start_master.py 主要是将Url推送到redis 以供抓取,也可以更改逻辑只推送
> start_slaver.py 项目启动文件
### 框架依赖安装：
> pip install -r requirement.txt -i http://pypi.douban.com/simple/  
> 

###git提交流程
<font color="red">注意事项如下</font>
>1、站点开发的时候一定要在自己的分支上开发 不要在主分支开发 默认main分支为主分支  
> 2、如果是必须使用一些不属于框架的第三方库一定要告知(尽量别使用除requirement.txt里以外的第三方库)  
3、主分支出现代码冲突的时候一定要切换到其他分支去解决冲突，禁止在主分支解决

step1:

>主分支更新代码到最新、保持当前代码和线上仓库代码同步  
git pull 


step2
> git checkout -b feature/20220921-[具体的事(开发|修复|更新)]

step3:
> 只允许提交app.py、site_crawl/spiders/parser/__init__.py、site_crawl/spiders/parser/country_domain.py三个文件   
git add xxxx

step4
>提交的操作  
Update: 更新xxxx  
Add:新增xxxx  
Delete:删除xxxx  
Fix：修复xxx  
提交示例  
git commit -m "Update:更新xxxx"  

step5：
>推送操作  
git push origin 当前创建的分支名

### 线下站点开发测试：
  
在项目根目录下新建一个xxxx_test.py文件作为线下爬虫测试使用

```python
from util.push_urls import Master

# =========================== TEST ==============================
m = Master()
m.push_urls(90)
```
setting.py
> 

### 部署
```text
docker run -d --name container_name  -v /data/news/site_crawl/site_crawl:/home/site_crawl   --restart=always  image_id
```
