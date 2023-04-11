import os

'''
用于将git的最新代码从本地更新至线上节点的正确位置
因为站点修复、优化、新增、测试等原因需要频繁部署更新代码，但采集节点无法直连gitlab
'''

server_list = {
    # "ia-bw6": "/data/news/site_crawl",
    # "tx-hg": "/data/news/site_crawl",
    # "tx-om": "/data/news/site_crawl",
    # "tx-usa": "/data/news/site_crawl"
}

'''
rsync -avuP /data/news/news_test/* /data/news/new-spider-method-2 --exclude='*shell*'
'''


def push():
    local_path = os.path.abspath(os.path.dirname(os.path.abspath(__file__)))
    for item in server_list.items():
        print(f"+++++++++++开始向{item[0]}推送代码++++++++++++")
        cmd = (f"rsync -avP --checksum {local_path} {item[0]}:{item[1]} "
               f"--exclude='news*.csv' --exclude='.idea' --exclude='*.json' --exclude='*.log*' --exclude='*.html*'"
               f"--exclude='venv' --exclude='settings.py' --exclude='*.git*' --exclude='pipelines.py' --exclude='*.test*.py'")
        os.system(cmd)


if __name__ == '__main__':
        push()

