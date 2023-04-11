# Name: 站点(law.moj.gov.tw)解析器
# Date: 2023-02-06
# Author: liyun
# Desc: None

import re
from urllib.parse import urljoin

from site_crawl.spiders.parser.base_parser import BaseParser


class TwLaw_mojParser(BaseParser):
    name = 'law_moj'

    # 板块字段
    
    # 站点id
    site_id = "977938df-cbdc-4044-8984-51dba60bc927"
    # 站点名
    site_name = "全国法规资料库"
    # 板块信息
    channel = [
        {
            # 板块默认字段(站点id, 站点名, 站点地区)
            **{"site_id": "977938df-cbdc-4044-8984-51dba60bc927", "source_name": "全国法规资料库", "direction": "tw", "if_front_position": False}, 
            # (板块id, 板块名, 板块URL, 板块类型)
            **{"board_id": board_id, "site_board_name": board_name, "url": board_url, "board_theme": board_theme}
        }
        for board_id, board_name, board_url, board_theme in [
            ("0a856f48-b811-4a91-967f-3a5b466bc11d", "中央法规", "", "政治"),
            ("a86d0730-45d7-400a-81d9-4bcf094c7565", "中央法规/司法", "", "政治"),
            ("aa94acb5-fb71-4789-9058-19debe9a81e9", "中央法规/司法/惩戒法院", "", "政治"),
            ("2177703d-ba72-4645-bc32-b32132f6cd82", "中央法规/司法/惩戒法院/公惩目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=06002001", "政治"),
            ("8c65f57a-c7e8-43b8-8ee5-54b451b6de0c", "中央法规/司法/院本部", "", "政治"),
            ("58746594-f219-4796-aa7a-30ce09f1cb2d", "中央法规/司法/院本部/一般行政目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=06001009", "政治"),
            ("88d6b3db-89cc-4027-a4f7-b4b45c156bee", "中央法规/司法/院本部/刑事目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=06001004", "政治"),
            ("803a8fbb-307c-45e6-b5e7-8a833dec0b7f", "中央法规/司法/院本部/司法人事目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=06001008", "政治"),
            ("6fc82ada-25f5-4176-b678-c826e301ad5a", "中央法规/司法/院本部/司法行政目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=06001007", "政治"),
            ("bd401488-605a-4a78-8caf-03a36e18c1cb", "中央法规/司法/院本部/少年及家事目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=06001006", "政治"),
            ("c6156fb7-9b33-4b74-86f8-2c18c035e22d", "中央法规/司法/院本部/民事目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=06001003", "政治"),
            ("ac848419-6194-480d-b29f-9d6e96eb7fee", "中央法规/司法/院本部/组织目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=06001001", "政治"),
            ("d88b370a-d78b-4952-9326-f753ce6062bd", "中央法规/司法/院本部/行惩及智财目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=06001005", "政治"),
            ("80a7f53f-c5c8-4a63-8bae-d23572d76206", "中央法规/司法/院本部/释宪目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=06001002", "政治"),
            ("b6e6b0d2-5337-4393-a981-33a09f0ceeca", "中央法规/国民大会", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=02000000", "政治"),
            ("3b26a1ac-cedb-4a78-8880-8b585ca73289", "中央法规/宪法", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=01000000", "政治"),
            ("aed92dc3-cf9a-4bda-ba94-8f9f38c17587", "中央法规/废止法规", "", "政治"),
            ("4f0a3d35-e6b4-4d42-a873-fbd0623842b9", "中央法规/废止法规/中央选举委员会", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04028000&fei=1", "政治"),
            ("d0772ba0-7a1d-4d2d-9701-454f8598a99f", "中央法规/废止法规/中央银行", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04026000&fei=1", "政治"),
            ("4c38c878-b67d-4c1f-916e-7f6e529dff26", "中央法规/废止法规/交通部", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04052000&fei=1", "政治"),
            ("bd157fcf-89db-421c-9e80-90cda0f71474", "中央法规/废止法规/侨务委员会", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04020000&fei=1", "政治"),
            ("a67f6d8b-1bad-40fc-ad37-cac8dcbb6699", "中央法规/废止法规/公务人员保障暨培训委员会", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=07004000&fei=1", "政治"),
            ("b92cc826-f1b0-4c92-aa0b-a50045b2dd94", "中央法规/废止法规/公平交易委员会", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04029000&fei=1", "政治"),
            ("cb57e395-9aea-4dd7-8f7f-33c02eb04452", "中央法规/废止法规/内政院", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04051000&fei=1", "政治"),
            ("04b086c6-8213-4baf-aafd-6d4b4faa3c61", "中央法规/废止法规/劳动部", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04010000&fei=1", "政治"),
            ("a137b40b-d194-4c59-8da5-3edaa285b2e1", "中央法规/废止法规/卫生福利部", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04012000&fei=1", "政治"),
            ("e5c9aac6-bf44-4c1b-84b1-25b01f0ce532", "中央法规/废止法规/原住民族委员会", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04022000&fei=1", "政治"),
            ("bfefffc2-d42e-41be-832a-adacd18f755a", "中央法规/废止法规/台湾省政府", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04032000&fei=1", "政治"),
            ("3593e105-e57c-4f41-9be8-235c96f54c20", "中央法规/废止法规/司法院", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=06001000&fei=1", "政治"),
            ("2ef1032d-1681-458b-9822-72ba92d15e40", "中央法规/废止法规/国军退除役官兵辅导委员会", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04021000&fei=1", "政治"),
            ("47455ed5-a606-4916-9c0c-9bfa91794570", "中央法规/废止法规/国家发展委员会", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04016000&fei=1", "政治"),
            ("9ce3a0bd-8248-497d-8358-85d144ddade8", "中央法规/废止法规/国家安全会议", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=03002000&fei=1", "政治"),
            ("5adfea00-e734-4ec8-bc24-3b95382b48e7", "中央法规/废止法规/国家运输安全调查委员会", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04031000&fei=1", "政治"),
            ("18810c01-5dee-4af6-b204-939870b0c05c", "中央法规/废止法规/国家通讯传播委员会", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04030000&fei=1", "政治"),
            ("c24b9c39-3ef4-4430-8341-e8b5c6f2aeaf", "中央法规/废止法规/国立故宫博物院", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04027000&fei=1", "政治"),
            ("8a1b67b1-c43b-45fb-8cdc-6f5579d6cbf5", "中央法规/废止法规/国防部", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04004000&fei=1", "政治"),
            ("73598861-4e70-4ba4-8acc-e9bccfd77efc", "中央法规/废止法规/外交院", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04003000&fei=1", "政治"),
            ("690c4a58-ba71-4cce-8407-5e596591b16d", "中央法规/废止法规/大陆委员会", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04017000&fei=1", "政治"),
            ("ebc0ce90-2815-4277-a613-a4a2164aa128", "中央法规/废止法规/审计部", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=08002000&fei=1", "政治"),
            ("5a0b2bb2-392b-4c5a-9398-885681d821d3", "中央法规/废止法规/客家委员会", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04023000&fei=1", "政治"),
            ("57810cdc-fa28-4770-aa73-9485d5268277", "中央法规/废止法规/宪法", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=01000000&fei=1", "政治"),
            ("8ec96a52-a24f-4344-b3a4-31ed87d5023c", "中央法规/废止法规/总统府", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=03001000&fei=1", "政治"),
            ("ee1c8bc4-78be-432a-b5cd-c62683b73288", "中央法规/废止法规/惩戒法院", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=06002000&fei=1", "政治"),
            ("bdeffcce-3f99-4e5d-9954-1e2564f49ed6", "中央法规/废止法规/教育部", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04006000&fei=1", "政治"),
            ("0a25c77b-3c2d-431a-98c4-7db47a4a09c3", "中央法规/废止法规/文化部", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04014000&fei=1", "政治"),
            ("58011fdf-0360-46c0-b725-e1358b1ff382", "中央法规/废止法规/民大会", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=02000000&fei=1", "政治"),
            ("14dff040-66c0-4212-ada5-b8e1c345bc74", "中央法规/废止法规/法务部", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04007000&fei=1", "政治"),
            ("78e239eb-df3e-41d0-a5b8-4db125040a26", "中央法规/废止法规/海洋委员会", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04019000&fei=1", "政治"),
            ("baa3780e-8e4f-4217-a2c6-b17dc6c8ee8f", "中央法规/废止法规/监察院", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=08001000&fei=1", "政治"),
            ("efe5e259-91a9-45a4-a938-96cea4e8aa05", "中央法规/废止法规/科技部", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04080000&fei=1", "政治"),
            ("2222f782-185d-4d3b-9017-0ee04f8fdf19", "中央法规/废止法规/立法院", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=05000000&fei=1", "政治"),
            ("9685c262-a26b-47b2-ac80-4d116e144fef", "中央法规/废止法规/经济部", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04057000&fei=1", "政治"),
            ("37a5238b-b568-4882-a8d2-80f26ed68b99", "中央法规/废止法规/考试院", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=07001000&fei=1", "政治"),
            ("59a66cb8-555e-4665-bf70-083a43596876", "中央法规/废止法规/考选部", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=07002000&fei=1", "政治"),
            ("bba17812-ba75-42f0-a44c-df547a61cd8e", "中央法规/废止法规/蒙藏委员会", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04079000&fei=1", "政治"),
            ("061c80ab-15d8-41ad-a29f-761fa549dfd6", "中央法规/废止法规/行政机构人事行政总处", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04025000&fei=1", "政治"),
            ("1371b9d2-e43a-49dc-b982-7b5600edff66", "中央法规/废止法规/行政院", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04001000&fei=1", "政治"),
            ("c97d9077-ef62-4719-8c56-a871faa69825", "中央法规/废止法规/行政院921震灾灾后重建推动委员会", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04058000&fei=1", "政治"),
            ("6e01e810-14de-4005-9aaa-ac3a9404a5c1", "中央法规/废止法规/行政院主计处", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04063000&fei=1", "政治"),
            ("7135e3a7-2275-4113-b073-fa97508f54d7", "中央法规/废止法规/行政院主计总处", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04024000&fei=1", "政治"),
            ("ccd6ce69-9ccf-4819-8f3f-d009bd0ca04b", "中央法规/废止法规/行政院人事行政局", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04059000&fei=1", "政治"),
            ("803b76bd-9b76-4fa7-95c4-832caf87dcce", "中央法规/废止法规/行政院体育委员会", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04078000&fei=1", "政治"),
            ("0a6fcff1-6b1b-40a9-962c-ecbe11b6316b", "中央法规/废止法规/行政院公共工程委员会", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04053000&fei=1", "政治"),
            ("d9346171-c6f2-480c-bbf9-89e90e70cb59", "中央法规/废止法规/行政院农业委员会", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04055000&fei=1", "政治"),
            ("07da356a-1a7f-44f2-a0cf-041f3a374e86", "中央法规/废止法规/行政院劳工委员会", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04074000&fei=1", "政治"),
            ("0aa22ede-a612-4d70-af16-cfc9939f0e00", "中央法规/废止法规/行政院卫生署", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04077000&fei=1", "政治"),
            ("205665b6-f57c-41cb-acae-d751eda416c3", "中央法规/废止法规/行政院原住民族委员会", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04068000&fei=1", "政治"),
            ("7383fbfb-cf72-496e-a6f0-a9abef4b1a4f", "中央法规/废止法规/行政院原子能委员会", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04054000&fei=1", "政治"),
            ("06325e72-63b5-43b6-a497-521c6de70b4d", "中央法规/废止法规/行政院台军退除役官兵辅导委员会", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04071000&fei=1", "政治"),
            ("e691ae1e-ad26-4c1e-9d60-98ba80d8c3d7", "中央法规/废止法规/行政院国家科学委员会", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04072000&fei=1", "政治"),
            ("676d9495-778b-426f-91e8-1f653756c522", "中央法规/废止法规/行政院大陆委员会", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04060000&fei=1", "政治"),
            ("9b14a845-5601-49a0-b48c-2bd27d5ec528", "中央法规/废止法规/行政院文化建设委员会", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04062000&fei=1", "政治"),
            ("5568595d-2bca-4e6c-99d1-4d95143949b3", "中央法规/废止法规/行政院新闻局", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04075000&fei=1", "政治"),
            ("9d87f9a7-c72d-41b3-b005-a48212585887", "中央法规/废止法规/行政院海岸巡防署", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04070000&fei=1", "政治"),
            ("e66266fd-209a-4523-9fa9-daefe652b908", "中央法规/废止法规/行政院消费者保护委员会", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04069000&fei=1", "政治"),
            ("4af622b9-2eef-4ba1-89d5-735d13bcdc7c", "中央法规/废止法规/行政院环境保护署", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04056000&fei=1", "政治"),
            ("f19d0c68-03e9-4f8d-b0a7-908a1c8e998f", "中央法规/废止法规/行政院研究发展考核委员会", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04066000&fei=1", "政治"),
            ("2cc79aba-de28-4582-8871-613ec322da48", "中央法规/废止法规/行政院经济建设委员会", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04076000&fei=1", "政治"),
            ("f81339c3-3d9b-4bb5-8e01-ca165bf85f1b", "中央法规/废止法规/行政院莫拉克台风灾后重建推动委员会", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04073000&fei=1", "政治"),
            ("474be910-c060-46de-b22c-4657c5f2cea1", "中央法规/废止法规/行政院金融监督管理委员会", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04064000&fei=1", "政治"),
            ("a742cdab-77c8-4efc-8306-c6eb5810f7c2", "中央法规/废止法规/行政院青年辅导委员会", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04065000&fei=1", "政治"),
            ("39d28ee4-4b24-441a-bc07-01294d2ed294", "中央法规/废止法规/行政院飞航安全委员会", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04067000&fei=1", "政治"),
            ("bd04e113-8c3f-45a0-80e0-508f7269cadc", "中央法规/废止法规/财政部", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04005000&fei=1", "政治"),
            ("478d94eb-7dbc-4be3-bd13-144b6aef6c32", "中央法规/废止法规/金融监督管理委员会", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04018000&fei=1", "政治"),
            ("9486d7be-9a46-4503-b828-72aa4de78477", "中央法规/废止法规/铨叙部", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=07003000&fei=1", "政治"),
            ("f1dafe92-4375-43ce-b229-02cd3760b294", "中央法规/总统", "", "政治"),
            ("02a4bf05-03f1-4714-a25f-d18b4f4b0d1d", "中央法规/总统/国家安全会议", "", "政治"),
            ("8b203737-e954-4c45-893c-7202323e8e94", "中央法规/总统/国家安全会议/情报工作目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=03002003", "政治"),
            ("09046ded-b5f6-4746-8c31-3652f990b1f8", "中央法规/总统/国家安全会议/特种勤务目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=03002004", "政治"),
            ("ef388554-8fd2-4ec8-81bc-281d3248e372", "中央法规/总统/国家安全会议/组织目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=03002001", "政治"),
            ("6d3db316-8da8-47c1-9b98-04e55a350a43", "中央法规/总统/国家安全会议/议事目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=03002002", "政治"),
            ("d6982783-8805-44a9-8552-0dd7fe5f0bab", "中央法规/总统/国家安全会议/诉愿会议目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=03002005", "政治"),
            ("fdd264f3-99aa-47b3-b25b-0c315ce410ec", "中央法规/总统/国家安全会议/资讯公开目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=03002006", "政治"),
            ("62fd5d90-fae2-440b-b978-e7dafdf6fa49", "中央法规/总统/总统府", "", "政治"),
            ("9cf29763-d62c-4552-bb91-f284390ec55e", "中央法规/总统/总统府/中央研究院目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=03001002", "政治"),
            ("99f89a45-d24b-4e85-ad3e-f7ed04ea8f61", "中央法规/总统/总统府/咨询公开目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=03001005", "政治"),
            ("e715d048-85b1-4fd6-8414-2c0e7f440108", "中央法规/总统/总统府/国史馆目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=03001003", "政治"),
            ("d98cdd19-af13-4c78-bbe6-49b16d1445d5", "中央法规/总统/总统府/组织目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=03001001", "政治"),
            ("3e5dd47b-8b89-4f9e-91a9-82e04ba708c2", "中央法规/总统/总统府/诉愿委员会目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=03001006", "政治"),
            ("6c90b331-77ac-4da3-96c7-060b95f48d7a", "中央法规/总统/总统府/资政国策顾问目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=03001004", "政治"),
            ("a5f4b740-95c9-4aa5-b968-1864e457104b", "中央法规/总统/总统府/通用目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=03001007", "政治"),
            ("9e65e6d9-049a-4865-b3a9-d6a03f080a70", "中央法规/监察", "", "政治"),
            ("099d5a55-21d7-4057-82bb-f192a06b74c2", "中央法规/监察/审计部", "", "政治"),
            ("3f36e8c2-35cc-4436-8a57-f79cc722425d", "中央法规/监察/审计部/审计目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=08002002", "政治"),
            ("b4e7730e-fcf9-4bfb-b3a4-71c259467a1d", "中央法规/监察/审计部/组织目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=08002001", "政治"),
            ("a7abf640-6f93-4b7f-b324-8bb7e3e6ce62", "中央法规/监察/院本部", "", "政治"),
            ("ded5df54-1d36-4926-9c4b-42d7da336289", "中央法规/监察/院本部/审计目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=08001003", "政治"),
            ("0b067ab1-14d2-4a1b-b4eb-834f021c946c", "中央法规/监察/院本部/政献目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=08001004", "政治"),
            ("ea5ad6b4-9009-4472-94ab-27fc909d0eec", "中央法规/监察/院本部/监察目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=08001002", "政治"),
            ("7b0a297c-d60b-4a1e-9f25-8c863b81e03a", "中央法规/监察/院本部/组织目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=08001001", "政治"),
            ("83c8993b-5da4-430e-bd42-6738894d540a", "中央法规/监察/院本部/院（处）务目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=08001005", "政治"),
            ("abc74cae-8cd6-4b0f-a663-2b817dc2f9be", "中央法规/立法", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=05000000", "政治"),
            ("68581ee0-6e11-44d7-ab03-9ee1abee01e9", "中央法规/考试", "", "政治"),
            ("d5aeec40-51e7-4e22-91d7-449256cf9efc", "中央法规/考试/公务人员保障暨培训委员会", "", "政治"),
            ("b62838d1-5d37-401f-91ee-32c2fd45c088", "中央法规/考试/公务人员保障暨培训委员会/保障目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=07004002", "政治"),
            ("00f3266f-0ad7-48af-bf0b-7bd8a8d2c759", "中央法规/考试/公务人员保障暨培训委员会/培训目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=07004003", "政治"),
            ("c4a6db82-0b15-46e1-906e-58054c86f2ed", "中央法规/考试/公务人员保障暨培训委员会/组织目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=07004001", "政治"),
            ("5accc70d-c735-4705-b561-f46f35300659", "中央法规/考试/公务人员退休抚卹基金监理委员会", "", "政治"),
            ("5accc71d-c735-4705-b561-f46f35300659", "中央法规/考试/公务人员退休抚卹基金监理委员会/组织目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=07005001", "政治"),
            ("78aa63d1-d2d6-4966-8bd0-1d45532056b4", "中央法规/考试/考选部", "", "政治"),
            ("c335ba80-a4b2-4726-9598-7c9f94e88811", "中央法规/考试/考选部/一般性考试目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=07002002", "政治"),
            ("ce5e6d67-f45f-411a-821b-f89c12626a37", "中央法规/考试/考选部/专门职业及技术人员考试目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=07002004", "政治"),
            ("64db439f-ad84-4d58-9d08-6663b8320572", "中央法规/考试/考选部/公务人员考试目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=07002003", "政治"),
            ("61188a93-8016-4d77-ad4e-d2bce13a9636", "中央法规/考试/考选部/组织目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=07002001", "政治"),
            ("8e3dfa53-3b20-45e4-874c-9aa80a9e3f17", "中央法规/考试/铨叙部", "", "政治"),
            ("329087ce-3b4c-427e-b12f-e307a676241c", "中央法规/考试/铨叙部/人事管理目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=07003006", "政治"),
            ("f4073110-2408-44ea-a479-df9579711965", "中央法规/考试/铨叙部/任用目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=07003002", "政治"),
            ("0c4871de-2a4f-4b7a-b654-c74dce37990b", "中央法规/考试/铨叙部/保险目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=07003008", "政治"),
            ("014bd2f1-52ad-43f2-9fc2-905372fda22f", "中央法规/考试/铨叙部/俸给目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=07003003", "政治"),
            ("4257cd5c-7a35-4544-a94e-ef2d70ffc098", "中央法规/考试/铨叙部/公务人员协会目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=07003013", "政治"),
            ("91335ad2-51c9-445b-a664-6d4107e6bd65", "中央法规/考试/铨叙部/奖惩目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=07003005", "政治"),
            ("4f429342-74d5-4c6a-aebd-ff04c39ce75e", "中央法规/考试/铨叙部/抚卹目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=07003009", "政治"),
            ("cd3aaff0-c682-43d7-bd36-dac40a2fbcd7", "中央法规/考试/铨叙部/登记目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=07003010", "政治"),
            ("2c1741d7-28af-4a24-b57b-81d4b340c663", "中央法规/考试/铨叙部/组织目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=07003001", "政治"),
            ("37820e87-d27c-4ee9-bf4d-c040fcc6eeb4", "中央法规/考试/铨叙部/考绩目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=07003004", "政治"),
            ("2fbaa115-6588-4482-89c4-96962e2a9597", "中央法规/考试/铨叙部/考试分发目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=07003011", "政治"),
            ("aa43d7da-3c86-4c78-b650-29c0be7d02ef", "中央法规/考试/铨叙部/考试目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=07003012", "政治"),
            ("b67c6614-b70a-4241-8078-3b11e413093b", "中央法规/考试/铨叙部/退休目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=07003007", "政治"),
            ("58573d8a-cca2-4f98-bb0f-61df7909e295", "中央法规/考试/院本部", "", "政治"),
            ("75dfb096-dfb3-4615-af4c-ca69e2354bfc", "中央法规/考试/院本部/组织目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=07001001", "政治"),
            ("6448c2a1-bef2-4b6f-8671-da36ee35362c", "中央法规/考试/院本部/通用目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=07001002", "政治"),
            ("98d98068-f796-4c91-bf88-f8819ce00eab", "中央法规/行政", "", "政治"),
            ("0a325b3a-e9fc-4fdf-97b8-26b796ad176f", "中央法规/行政/不当党产处理委员会", "", "政治"),
            ("8730a139-270a-4293-b653-a83456153922", "中央法规/行政/不当党产处理委员会/党产目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04034002", "政治"),
            ("4cf236ac-39eb-4124-a7cc-eaa825264831", "中央法规/行政/不当党产处理委员会/组织目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04034001", "政治"),
            ("6957df75-916a-460a-afca-0d4bc22ee83d", "中央法规/行政/中央选举委员会", "", "政治"),
            ("94c4b0f4-2182-4425-ac8a-6348fa25fd5e", "中央法规/行政/中央选举委员会/公投行政目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04028003", "政治"),
            ("99d826bc-754c-44ea-8684-3ad5fe220f43", "中央法规/行政/中央选举委员会/组织目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04028001", "政治"),
            ("01745a58-a783-47cf-98eb-3640a93a1a2b", "中央法规/行政/中央选举委员会/选举行政目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04028002", "政治"),
            ("e73c70b3-ef8e-48f4-aa2c-57f8dba7332a", "中央法规/行政/中央银行", "", "政治"),
            ("51b7f37c-01c0-4f99-a55e-1ed31d75debb", "中央法规/行政/中央银行/业务目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04026003", "政治"),
            ("3fd06817-53e9-4c28-a261-ff2840211018", "中央法规/行政/中央银行/发行目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04026004", "政治"),
            ("a28499c7-78e8-4515-ae8e-a88730748bff", "中央法规/行政/中央银行/外汇目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04026005", "政治"),
            ("12993ba8-a7dc-4f3c-87f9-72a2590330fc", "中央法规/行政/中央银行/总纲目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04026001", "政治"),
            ("18bbc486-479d-4a0c-aab3-12dc7fe8e55d", "中央法规/行政/中央银行/组织目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04026002", "政治"),
            ("1f973e15-c93c-4c7d-a924-029f83b4c6bf", "中央法规/行政/交通部", "", "政治"),
            ("b190e224-63ee-4739-bdb5-790de5632d6a", "中央法规/行政/交通部/交通通用目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04052003", "政治"),
            ("01f8cf42-3dd1-4b50-b3d0-bee525a002fb", "中央法规/行政/交通部/公路目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04052005", "政治"),
            ("2147c2e0-fe94-4f70-bbc9-a01014403475", "中央法规/行政/交通部/处务目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04052002", "政治"),
            ("9b735b12-8968-488a-beab-0c5c52f69016", "中央法规/行政/交通部/捷运目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04052012", "政治"),
            ("d71f768a-97e2-4dde-9dfa-2356b989b8eb", "中央法规/行政/交通部/气象目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04052010", "政治"),
            ("8058b3df-286e-4750-a732-9089ab0f7889", "中央法规/行政/交通部/港务目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04052008", "政治"),
            ("9961c34d-d94d-47c6-a9b2-0692f1264688", "中央法规/行政/交通部/组织目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04052001", "政治"),
            ("a8e03658-2d55-4fc1-a4cb-190e5f1e42c3", "中央法规/行政/交通部/航政目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04052007", "政治"),
            ("f20817cc-f256-4a26-a6a9-1ea3de8660fb", "中央法规/行政/交通部/航空目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04052009", "政治"),
            ("2487bda6-3ffc-448c-85de-7dbd7a7c27b9", "中央法规/行政/交通部/观光目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04052011", "政治"),
            ("213caa85-bf11-48be-ad64-9d2cdae301e3", "中央法规/行政/交通部/邮政目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04052006", "政治"),
            ("e1f4ab56-d359-4b06-afbc-7584607cbdfb", "中央法规/行政/交通部/铁路目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04052004", "政治"),
            ("88c542a6-b5f4-490c-9299-aaa017ccedfa", "中央法规/行政/侨务委员会", "", "政治"),
            ("7256603f-f672-4f1a-a222-253d9aa7dc5f", "中央法规/行政/侨务委员会/一般业务目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04020005", "政治"),
            ("720e5d79-0a77-4b20-ac5b-9a654c960f65", "中央法规/行政/侨务委员会/侨民教育目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04020004", "政治"),
            ("a713eb3b-fa2f-44b3-bf59-08109b5e8afd", "中央法规/行政/侨务委员会/侨民权益目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04020003", "政治"),
            ("47db23ab-d19d-48da-b112-e18d09bf9d81", "中央法规/行政/侨务委员会/组织目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04020001", "政治"),
            ("7ecd1e02-7f22-433f-a25c-5b11c64a9a40", "中央法规/行政/侨务委员会/综合规划目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04020002", "政治"),
            ("87072374-3bc9-4f0d-ac9c-a23390af70bf", "中央法规/行政/內政部", "", "政治"),
            ("9467035e-2604-4651-940b-56680bccf841", "中央法规/行政/內政部/合作及人民团体目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04051006", "政治"),
            ("1c11d49e-d925-41c5-9b6f-6f95731a56d3", "中央法规/行政/內政部/地政目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04051007", "政治"),
            ("8c8d7b6c-bfbf-4819-9e70-cabeed7f683f", "中央法规/行政/內政部/处务目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04051002", "政治"),
            ("0953f932-d6f5-401b-8676-110725002c9a", "中央法规/行政/內政部/役政目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04051005", "政治"),
            ("443ab4d2-b05f-4e22-bb24-df6be7c298ef", "中央法规/行政/內政部/户政目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04051004", "政治"),
            ("ecdc0721-2d81-4fb0-8c1e-3294bdac1cbd", "中央法规/行政/內政部/民政目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04051003", "政治"),
            ("1e90095f-5969-4087-b686-4f786fbe48bf", "中央法规/行政/內政部/消防目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04051010", "政治"),
            ("55a0a5e5-28b7-4b6c-9cdf-cb4cea698fa0", "中央法规/行政/內政部/移民目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04051011", "政治"),
            ("c6ec3467-5b2d-4eb7-8ab4-30a5324bdacc", "中央法规/行政/內政部/组织目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04051001", "政治"),
            ("a5abed76-678d-4dd3-babb-05e064437ab8", "中央法规/行政/內政部/营建目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04051008", "政治"),
            ("2e7e7946-ccdf-49ee-9bd3-133b26397a16", "中央法规/行政/內政部/警政目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04051009", "政治"),
            ("d946868a-aa93-4020-946e-4d712b56e6e5", "中央法规/行政/公平交易委员会", "", "政治"),
            ("b6611016-51db-4061-bd9c-8e38ca2f15e9", "中央法规/行政/公平交易委员会/公平交易目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04029002", "政治"),
            ("2840c584-6b7c-4ba4-ad42-50c4725b891e", "中央法规/行政/公平交易委员会/组织目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04029001", "政治"),
            ("981bc8ec-c368-47cb-a14f-286ca4f90b17", "中央法规/行政/劳动部", "", "政治"),
            ("8f35bca7-3148-46fe-9665-006b9af53cfb", "中央法规/行政/劳动部/其他目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04010010", "政治"),
            ("823269ed-43e0-41da-9b28-21e027b6a2d5", "中央法规/行政/劳动部/劳动保险目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04010003", "政治"),
            ("a03866ba-97f1-48d5-8fa2-0fdcfee06a34", "中央法规/行政/劳动部/劳动关系目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04010002", "政治"),
            ("5e3db1a2-320e-45dd-b633-25ea586a274c", "中央法规/行政/劳动部/劳动条件及就业平等目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04010005", "政治"),
            ("8f273a33-ecfd-4999-aeeb-3dbd796554cc", "中央法规/行政/劳动部/劳动检查目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04010007", "政治"),
            ("d51519d0-7a55-4679-85cb-9b1ad89e8496", "中央法规/行政/劳动部/劳动福祉退休目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04010004", "政治"),
            ("c1d4b4f8-26f4-4987-a71a-cf7d75b3cfec", "中央法规/行政/劳动部/就业服务目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04010009", "政治"),
            ("c68e96b6-678e-4881-831b-7bb3bb51bb19", "中央法规/行政/劳动部/组织目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04010001", "政治"),
            ("02d39488-0234-44f6-abea-47aa879cbafb", "中央法规/行政/劳动部/职业安全卫生目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04010006", "政治"),
            ("a9a4fda0-4944-4591-8fa1-f595b786b3c7", "中央法规/行政/劳动部/职业训练目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04010008", "政治"),
            ("28cb1bf3-489d-4cf3-998f-52896b2bb94b", "中央法规/行政/卫生福利部", "", "政治"),
            ("ddba8a06-af44-44db-bad4-e3008ad0f3a0", "中央法规/行政/卫生福利部/中医药目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04012009", "政治"),
            ("5495c7d9-fa6e-4acc-9b71-74b73315ebe1", "中央法规/行政/卫生福利部/中央健康保险目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04012013", "政治"),
            ("4766b3a9-4bc4-49fe-8f70-4a2e53cd1261", "中央法规/行政/卫生福利部/人事目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04012016", "政治"),
            ("8bffce44-72dd-4b85-98b6-fc291e1e78a0", "中央法规/行政/卫生福利部/会计目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04012017", "政治"),
            ("059df727-d001-4f2b-b0ac-06401a0ca365", "中央法规/行政/卫生福利部/保护服务目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04012006", "政治"),
            ("b25ec2dd-3acf-4521-b6a8-a6146a889f86", "中央法规/行政/卫生福利部/医事目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04012007", "政治"),
            ("beba840f-f790-49f7-8a63-5c820271de14", "中央法规/行政/卫生福利部/口腔健康目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04012024", "政治"),
            ("b71364c4-7af1-432d-b387-e9e7e2e8292b", "中央法规/行政/卫生福利部/品药物管理目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04012011", "政治"),
            ("27fae797-f09e-4d50-a2f9-de9f8bafcff5", "中央法规/行政/卫生福利部/国民健康目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04012012", "政治"),
            ("c77d82ab-2fda-4019-81b7-bf3e35c54276", "中央法规/行政/卫生福利部/心里健康目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04012008", "政治"),
            ("70ebb173-ec38-43d1-b9b6-ad0c44298e73", "中央法规/行政/卫生福利部/护理及健康照护目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04012005", "政治"),
            ("ca614fed-2296-4cd8-9c58-af92da7de700", "中央法规/行政/卫生福利部/法规目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04012023", "政治"),
            ("de20e99b-5ca5-4179-8411-ad57b04586f6", "中央法规/行政/卫生福利部/疾病管制目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04012010", "政治"),
            ("a0ffd24e-5cdc-45f1-9ce5-1dc670160480", "中央法规/行政/卫生福利部/社会保险目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04012003", "政治"),
            ("e7037315-d96f-4d5f-b7ef-d9cd332e08b1", "中央法规/行政/卫生福利部/社会及家庭目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04012014", "政治"),
            ("b905d225-5dd3-4651-a3f6-adef58451798", "中央法规/行政/卫生福利部/社会救助及社工目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04012004", "政治"),
            ("8982fca9-b8d6-499d-8038-1a1028616b71", "中央法规/行政/卫生福利部/科技发展目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04012019", "政治"),
            ("ae42ce2b-2dec-443d-afdb-5b931051baca", "中央法规/行政/卫生福利部/秘书目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04012015", "政治"),
            ("a21c8af5-ade0-41a5-af27-662664195f9a", "中央法规/行政/卫生福利部/组织目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04012001", "政治"),
            ("50eee3a8-891f-4414-aa2a-0b2bf1b4d870", "中央法规/行政/卫生福利部/统计目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04012020", "政治"),
            ("d19bd519-e436-42b7-92f4-3bd14bf801c8", "中央法规/行政/卫生福利部/综合规划目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04012002", "政治"),
            ("6f916d00-1b50-4716-b2b3-12be849c2247", "中央法规/行政/卫生福利部/资讯目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04012022", "政治"),
            ("5245c10b-397c-4c28-9d21-8e21a1fe3357", "中央法规/行政/卫生福利部/长期照顾目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04012021", "政治"),
            ("1f821217-8128-4d21-b50d-9345832b864c", "中央法规/行政/卫生福利部/附属医疗及社会福利机构管理目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04012018", "政治"),
            ("33854fa7-7e43-446a-93f4-c4ad10f01045", "中央法规/行政/原住民族委员会", "", "政治"),
            ("e34f09de-c7a8-41db-ba6f-794c1aaf35c3", "中央法规/行政/原住民族委员会/公共建设目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04022007", "政治"),
            ("10c8ce74-02d4-4243-91c7-c650d6605dd6", "中央法规/行政/原住民族委员会/土地管理目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04022006", "政治"),
            ("aa693a82-2848-418a-aef4-33613957f72f", "中央法规/行政/原住民族委员会/教育文化目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04022003", "政治"),
            ("7837504e-0580-4afd-812c-daf11ec240cb", "中央法规/行政/原住民族委员会/文化园区目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04022008", "政治"),
            ("e107ecf3-662a-4748-8932-c37df913fd92", "中央法规/行政/原住民族委员会/社会福利目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04022004", "政治"),
            ("c3a997da-2b64-4d58-8fc3-c6e0d7e03933", "中央法规/行政/原住民族委员会/组织目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04022001", "政治"),
            ("bf988c0e-e6e2-47ac-aee5-38fd6c5c9977", "中央法规/行政/原住民族委员会/经济发展目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04022005", "政治"),
            ("2002cc9f-f287-4c39-a9ec-4c9f6d7f5a90", "中央法规/行政/原住民族委员会/综合规划目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04022002", "政治"),
            ("3cafb7fe-f2f6-4f5d-ae90-d3bf19bf3204", "中央法规/行政/台湾省政府", "", "政治"),
            ("50b29b71-3203-4927-b379-5ed1d0c3cb45", "中央法规/行政/台湾省政府/组织目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04032001", "政治"),
            ("ddab0f8b-9809-4425-8536-99cc8ddc92b7", "中央法规/行政/台湾省政府/通用目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04032002", "政治"),
            ("e0557bac-0e44-4014-8f6e-02f44a21c725", "中央法规/行政/国军退除役官兵辅导委员会", "", "政治"),
            ("f60b9e0b-bd59-4d87-b635-a9fe54f5a419", "中央法规/行政/国军退除役官兵辅导委员会/处务目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04021002", "政治"),
            ("2b4802d5-0a36-4e07-958b-45d674df3a63", "中央法规/行政/国军退除役官兵辅导委员会/就业目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04021006", "政治"),
            ("60ac4c28-bbc7-44cb-ab38-06e933a20834", "中央法规/行政/国军退除役官兵辅导委员会/就养目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04021004", "政治"),
            ("bd1af645-ba99-4a2a-8689-dcb711376cb6", "中央法规/行政/国军退除役官兵辅导委员会/就医目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04021007", "政治"),
            ("bf5e838a-60f1-4ae3-b377-0e05f7d8f376", "中央法规/行政/国军退除役官兵辅导委员会/就学目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04021005", "政治"),
            ("345a4792-11b6-481f-b359-c617464a7ea2", "中央法规/行政/国军退除役官兵辅导委员会/组织目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04021001", "政治"),
            ("4af9b805-baaa-4c0f-824a-c3bb221fcb80", "中央法规/行政/国军退除役官兵辅导委员会/辅导管理目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04021003", "政治"),
            ("ffa8d432-9708-439b-b513-ca38a99d4a5f", "中央法规/行政/国家发展委员会", "", "政治"),
            ("70814f8d-9013-41fc-a981-e22d310f2803", "中央法规/行政/国家发展委员会/人事管理目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04016006", "政治"),
            ("7f30586e-c52d-444e-b217-134bd29488ae", "中央法规/行政/国家发展委员会/国营经济事业目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04016004", "政治"),
            ("7f4c1c20-ba77-42ba-9422-3d9e506b9fc1", "中央法规/行政/国家发展委员会/组织目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04016001", "政治"),
            ("b0c0817b-ee9b-4db2-8a47-c6e29d9e0b61", "中央法规/行政/国家发展委员会/通用目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04016003", "政治"),
            ("3b728362-011d-4583-add1-d00560458171", "中央法规/行政/国家发展委员会/院（处）务目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04016002", "政治"),
            ("d27c39ff-7b3a-4893-a943-e70e97e1ac4a", "中央法规/行政/国家科学及技术委员会", "", "政治"),
            ("9d234508-2f57-4292-8517-823db74de1a2", "中央法规/行政/国家科学及技术委员会/园区目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04015003", "政治"),
            ("30a126d2-f32e-41e5-bef3-0828064c1359", "中央法规/行政/国家科学及技术委员会/科学技术目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04015002", "政治"),
            ("d630c988-dfeb-4c11-b6e1-86417d7f58f9", "中央法规/行政/国家科学及技术委员会/组织目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04015001", "政治"),
            ("3bf18dbc-244e-473f-9003-57081aa438de", "中央法规/行政/国家运输安全调查委员会", "", "政治"),
            ("b8160514-77bb-4af1-b1a5-c52504d47d94", "中央法规/行政/国家运输安全调查委员会/组织目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04031001", "政治"),
            ("36874c20-fa77-477d-8634-726d741fa629", "中央法规/行政/国家运输安全调查委员会/航空目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04031002", "政治"),
            ("6cd0db61-1799-45a1-8e24-b23c58d2adb5", "中央法规/行政/国家通讯传播委员会", "", "政治"),
            ("c6e1a453-961c-42eb-8751-9b1ce50a3731", "中央法规/行政/国家通讯传播委员会/主计业务目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04030009", "政治"),
            ("8899bf2d-00a3-41f6-857d-609fc68562d2", "中央法规/行政/国家通讯传播委员会/人事业务目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04030008", "政治"),
            ("1440bacc-b27b-47e5-9fce-ac6dae2aa439", "中央法规/行政/国家通讯传播委员会/传播目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04030004", "政治"),
            ("54e3bef8-712f-4fd1-abed-97382e5f7833", "中央法规/行政/国家通讯传播委员会/信息业务目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04030010", "政治"),
            ("89420d91-7849-48dc-bb9e-23422e1924c8", "中央法规/行政/国家通讯传播委员会/其他目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04030011", "政治"),
            ("17c693d4-e455-4170-bcdc-c862287fd329", "中央法规/行政/国家通讯传播委员会/基本目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04030002", "政治"),
            ("7381f112-3fd1-47e8-9224-7f5b1b45ece0", "中央法规/行政/国家通讯传播委员会/收费标准目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04030005", "政治"),
            ("67a8799c-62f0-4dae-bd33-f8c179942577", "中央法规/行政/国家通讯传播委员会/法制业务目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04030006", "政治"),
            ("f93b5fb1-049c-4528-8e17-6fd5232b675a", "中央法规/行政/国家通讯传播委员会/秘书业务目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04030007", "政治"),
            ("ca7688f9-213e-447d-a26a-9176f1804e99", "中央法规/行政/国家通讯传播委员会/组织目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04030001", "政治"),
            ("e0119bf2-b512-46e6-80e6-702d7933d5ce", "中央法规/行政/国家通讯传播委员会/通讯目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04030003", "政治"),
            ("53a65930-ad01-4e7a-9c7d-46693dd0e530", "中央法规/行政/国立故宫博物院", "", "政治"),
            ("79c170ad-a111-49a0-8d6d-d68786887cb5", "中央法规/行政/国立故宫博物院/故宫博物目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04027002", "政治"),
            ("e380f5e7-66c1-4f30-972c-929ecc54a2bc", "中央法规/行政/国立故宫博物院/组织目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04027001", "政治"),
            ("792e4d55-6624-4d5f-a2c8-109a00e47e2c", "中央法规/行政/国防目", "", "政治"),
            ("1be0f0b4-3b76-4dd1-b1a5-4504d991bc26", "中央法规/行政/国防目/主计财务目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04004011", "政治"),
            ("d361b80c-c76e-4a45-b189-743f9369a6d1", "中央法规/行政/国防目/交通通信目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04004010", "政治"),
            ("7799dff5-6fed-447c-aa59-321501d3c9fd", "中央法规/行政/国防目/人事目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04004003", "政治"),
            ("14150fe4-ff96-4334-9f85-6a8dd512757b", "中央法规/行政/国防目/作战目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04004007", "政治"),
            ("54af1766-fc0d-4644-b398-fbfded2b16fd", "中央法规/行政/国防目/保险抚恤目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04004005", "政治"),
            ("533a3e29-72b4-4520-b92c-2b21e0475df2", "中央法规/行政/国防目/兵役目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04004004", "政治"),
            ("c8fa2d44-209e-4237-b689-6bbb67ef5d0c", "中央法规/行政/国防目/军备后勤目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04004009", "政治"),
            ("1280b605-f925-4827-b1a9-ba0029275c68", "中央法规/行政/国防目/军法目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04004012", "政治"),
            ("f4dd1527-f86c-4e67-848a-2c7aa31a73be", "中央法规/行政/国防目/医务目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04004013", "政治"),
            ("1c52c25c-b2cc-47d6-ba57-06b284096e1a", "中央法规/行政/国防目/政战目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04004002", "政治"),
            ("788f2faf-204c-45c0-bf9c-b5ae44d1d2d0", "中央法规/行政/国防目/教育训练目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04004008", "政治"),
            ("b6801346-d11b-4a10-8c33-73052a353b14", "中央法规/行政/国防目/服制旗章目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04004006", "政治"),
            ("100fc876-970c-4826-83bd-41a7d3d03472", "中央法规/行政/国防目/留守业务目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04004014", "政治"),
            ("c4b53c5e-28d9-4a21-ab6b-1c9114a758c3", "中央法规/行政/国防目/组织目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04004001", "政治"),
            ("e4228f68-2793-488f-8183-02b03522fe35", "中央法规/行政/外交部", "", "政治"),
            ("db61067c-e3cb-4710-9af0-74569e6740a8", "中央法规/行政/外交部/国际发展目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04003004", "政治"),
            ("482e5cc0-e0be-4e7b-878f-5ef1fbaafb68", "中央法规/行政/外交部/外交业务目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04003003", "政治"),
            ("82d28b74-e5e3-4b1c-aab2-31eebfe68c1c", "中央法规/行政/外交部/组织目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04003001", "政治"),
            ("a2e19411-3eb4-4d6f-89da-5d4b1529db35", "中央法规/行政/外交部/领事业务目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04003002", "政治"),
            ("4287ce38-17c4-45e7-a46d-2ce4336854e4", "中央法规/行政/大陆委员会", "", "政治"),
            ("3de21a2a-118f-4209-a179-98c9629cda33", "中央法规/行政/大陆委员会/两岸文教目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04017003", "政治"),
            ("486cd1b1-c36f-44ec-bfce-e4f26d063a70", "中央法规/行政/大陆委员会/两岸法政目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04017005", "政治"),
            ("cb2707ce-60d2-4e55-9b88-1454554e1d36", "中央法规/行政/大陆委员会/两岸经贸目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04017004", "政治"),
            ("dbc235fa-8aa2-4d39-b3eb-4e73f7c1bbb5", "中央法规/行政/大陆委员会/人事法规目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04017008", "政治"),
            ("b439dcf0-9ddd-42e4-86e9-fbf13651cf20", "中央法规/行政/大陆委员会/基本法规目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04017002", "政治"),
            ("a0011ac7-d26b-41c5-9336-878f29b3f954", "中央法规/行政/大陆委员会/港澳事务目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04017006", "政治"),
            ("58def00b-65da-4a33-b95d-985626606303", "中央法规/行政/大陆委员会/组织目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04017001", "政治"),
            ("0c5fa243-4e40-4827-a422-5c7bb4475bf6", "中央法规/行政/大陆委员会/通用法规目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04017009", "政治"),
            ("f24f6376-7f60-48af-8740-742fb5e61935", "中央法规/行政/客家委员会", "", "政治"),
            ("3b8a0bb2-5532-495a-87cc-856d0b6eb9b6", "中央法规/行政/客家委员会/客家事务目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04023002", "政治"),
            ("12b89bc9-49fc-4b28-b72b-834c40dd0ef3", "中央法规/行政/客家委员会/组织目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04023001", "政治"),
            ("19743fc3-8f50-44c1-ac4c-da14e528c4d0", "中央法规/行政/教育部", "", "政治"),
            ("d0f27208-d964-4203-a731-0375b66b0703", "中央法规/行政/教育部/人事目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04006015", "政治"),
            ("f375cc91-9e41-4ce1-86a7-598ddec4cf45", "中央法规/行政/教育部/会计目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04006017", "政治"),
            ("152fca6a-ec01-471c-902e-9cf9fff56cfb", "中央法规/行政/教育部/体育目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04006013", "政治"),
            ("4c49d620-61d5-4f2a-9abf-d26a7a702eeb", "中央法规/行政/教育部/国民及学前教育目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04006012", "政治"),
            ("e5a4b0ec-c93b-47f5-b7ce-ada75cfff820", "中央法规/行政/教育部/国际及两岸事务目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04006008", "政治"),
            ("49de9ce7-c028-4cb2-89b5-6ddeb5bd2a24", "中央法规/行政/教育部/学生事务及特殊教育", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04006020", "政治"),
            ("00e74ecc-8882-462f-8235-c99f002c3417", "中央法规/行政/教育部/师资培育及艺术教育目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04006009", "政治"),
            ("b5f6f1a7-0146-487a-b324-8ac61fb91b46", "中央法规/行政/教育部/技术及职业教育目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04006006", "政治"),
            ("1408d80b-2b17-4108-a3fd-487aeaed5e60", "中央法规/行政/教育部/政风目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04006016", "政治"),
            ("cc701ed6-506e-4331-821e-f9e62248a846", "中央法规/行政/教育部/教育通用目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04006002", "政治"),
            ("fc48451b-9f4c-4f4a-92e6-bc7630c80574", "中央法规/行政/教育部/法制目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04006019", "政治"),
            ("ae0b1e2f-b5b6-4ece-9cd9-56d66f337787", "中央法规/行政/教育部/私立学校目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04006004", "政治"),
            ("475a3db2-f3d7-47be-a8fe-206b08ab5cf3", "中央法规/行政/教育部/秘书目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04006014", "政治"),
            ("00689162-00ce-478a-bf2e-40eb36ea6675", "中央法规/行政/教育部/終身教育目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04006007", "政治"),
            ("dffd7ebf-5b81-4c10-bc12-237b94e3ca55", "中央法规/行政/教育部/组织目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04006001", "政治"),
            ("f456086a-3980-4a3d-ab4a-88c506d8e3b6", "中央法规/行政/教育部/统计目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04006018", "政治"),
            ("18dfe245-cfdf-44fb-9328-1c80b36f3464", "中央法规/行政/教育部/综合规划目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04006003", "政治"),
            ("31aadff2-a0f1-4098-bb79-ab40bb82496a", "中央法规/行政/教育部/资讯及科技教育目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04006010", "政治"),
            ("f0986ae3-29c7-407a-b30b-9adbd6bc4da3", "中央法规/行政/教育部/青年发展目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04006011", "政治"),
            ("00e8812f-72d5-4ec2-8aca-66ecccf1b948", "中央法规/行政/教育部/高等教育目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04006005", "政治"),
            ("6622659e-f558-4e96-9279-ee88adbb9cd1", "中央法规/行政/数字发展部", "", "政治"),
            ("8adb457e-8221-46fb-8545-4b2e33a80a82", "中央法规/行政/数字发展部/多元创新目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04081008", "政治"),
            ("63a15575-9228-41bc-bf9e-5a73689f070e", "中央法规/行政/数字发展部/数位政府目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04081006", "政治"),
            ("59394bdf-9145-41a3-a8d7-dd312613afa7", "中央法规/行政/数字发展部/数位策略目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04081003", "政治"),
            ("21355171-4163-4d82-b69a-2d7c5af8c5cb", "中央法规/行政/数字发展部/数字产业目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04081010", "政治"),
            ("6565c080-4623-47c2-8bf0-02d126f42603", "中央法规/行政/数字发展部/民主网络目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04081007", "政治"),
            ("de377e10-af1c-41bc-804a-4c2cb7f61991", "中央法规/行政/数字发展部/组织目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04081001", "政治"),
            ("dcd8c397-2789-437e-a28a-cfe4c58c44d0", "中央法规/行政/数字发展部/资源管理目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04081005", "政治"),
            ("1a0240be-e972-47d2-adda-306fc68f4be3", "中央法规/行政/数字发展部/资通安全目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04081009", "政治"),
            ("03d78fa1-4457-4b5e-9c3c-3a8695454e2b", "中央法规/行政/数字发展部/通用目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04081002", "政治"),
            ("8a34ffc4-a65e-42f6-9ed7-d742b819bc4e", "中央法规/行政/数字发展部/韧性建设目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04081004", "政治"),
            ("1752fcbd-993a-436e-83c5-6455eecb9f9e", "中央法规/行政/文化部", "", "政治"),
            ("87419f3c-4c42-4424-be0e-c780f498ac43", "中央法规/行政/文化部/建设目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04014006", "政治"),
            ("184a0bde-597d-4a0a-9cc2-32a6fc5941a1", "中央法规/行政/文化部/影视出版目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04014004", "政治"),
            ("9b66c707-32c0-4dc0-bea6-ae1bc689728f", "中央法规/行政/文化部/文创产业目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04014002", "政治"),
            ("76afb760-accb-433f-9eff-0be193ca4643", "中央法规/行政/文化部/文化艺术目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04014005", "政治"),
            ("ff03e089-ec20-4318-8b00-b8f50ab638a5", "中央法规/行政/文化部/文化资产目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04014003", "政治"),
            ("20ea8725-0dc3-4740-ab92-3fcc2ba1542a", "中央法规/行政/文化部/组织目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04014001", "政治"),
            ("8fd371d8-7d0d-4039-879f-64930fb67d18", "中央法规/行政/法务部", "", "政治"),
            ("788090cb-a8a4-41cc-99d3-f9b7c77dc214", "中央法规/行政/法务部/人事目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04007009", "政治"),
            ("a2f2cdef-24f7-438c-8128-3046f0da867f", "中央法规/行政/法务部/会计目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04007010", "政治"),
            ("03c599e0-8c3b-4148-86a2-b95d9ace1e7e", "中央法规/行政/法务部/保护目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04007006", "政治"),
            ("f8cd94ef-1a9a-416e-9037-21d0c1cefe12", "中央法规/行政/法务部/国际两岸目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04007007", "政治"),
            ("06fa4b76-9462-45d2-949e-c9c332b706c6", "中央法规/行政/法务部/廉政目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04007015", "政治"),
            ("067fbdba-d32d-465f-b5fe-5ccdf9506e9f", "中央法规/行政/法务部/检察目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04007005", "政治"),
            ("ab026893-03a6-4aae-a529-f7fc64e36452", "中央法规/行政/法务部/法制目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04007003", "政治"),
            ("5cde0fd8-66ed-41db-b8d6-737c5da5b9b2", "中央法规/行政/法务部/法医目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04007018", "政治"),
            ("4fad8ff6-614c-4265-b651-198341852f86", "中央法规/行政/法务部/法律事务目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04007004", "政治"),
            ("68616fb7-57c3-44fb-bfc8-de6395f80d2d", "中央法规/行政/法务部/法训目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04007017", "政治"),
            ("511cfd69-923c-434e-89ff-b01508e58b0c", "中央法规/行政/法务部/矫正目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04007016", "政治"),
            ("cf2cf71b-11b2-4227-8352-0d9cbec48ce9", "中央法规/行政/法务部/组织目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04007001", "政治"),
            ("37d6c3be-bb1e-4e6b-835f-a36a9093df14", "中央法规/行政/法务部/综合规划目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04007002", "政治"),
            ("1d20c086-0999-4092-b29b-5b542828d399", "中央法规/行政/法务部/行政执行目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04007014", "政治"),
            ("c3948331-f911-43f9-a64c-79fe82951f0f", "中央法规/行政/法务部/调查目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04007013", "政治"),
            ("307cee12-2665-4325-ac07-73d531e8979c", "中央法规/行政/海洋委员会", "", "政治"),
            ("8b1df505-cf3c-41c9-a766-12edf72b8a9d", "中央法规/行政/海洋委员会/人事目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04019005", "政治"),
            ("371598c5-1530-4bea-ab13-a0c91af5ba68", "中央法规/行政/海洋委员会/海岸巡防目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04019002", "政治"),
            ("69273294-2e52-4aff-90e5-dc34a08a919b", "中央法规/行政/海洋委员会/海洋资源目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04019003", "政治"),
            ("e8fa267e-c39a-4eed-9c99-86f1bac17ade", "中央法规/行政/海洋委员会/秘书目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04019004", "政治"),
            ("a92ba851-f4e2-4968-9bcd-ea8540513e0f", "中央法规/行政/海洋委员会/组织目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04019001", "政治"),
            ("09545f27-124a-4e9c-ad61-65814151561d", "中央法规/行政/经济部", "", "政治"),
            ("50c369f5-328d-4f4f-9e8a-11af6b23caf8", "中央法规/行政/经济部/中小企业目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04057014", "政治"),
            ("6e4d162e-d84d-4b19-a0fb-7a844e0e0b3c", "中央法规/行政/经济部/加工出口目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04057006", "政治"),
            ("adad0504-ac63-4c19-bf56-2d2492dd2697", "中央法规/行政/经济部/商业目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04057008", "政治"),
            ("cabeefd2-e295-46b7-a042-9ddafedcee04", "中央法规/行政/经济部/国营经济事业目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04057012", "政治"),
            ("04b20ec7-8935-4082-9cab-d80d79fa8de7", "中央法规/行政/经济部/国际贸易目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04057009", "政治"),
            ("454f7ace-4d75-467e-99f9-f85474ba0d2e", "中央法规/行政/经济部/处务目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04057002", "政治"),
            ("da320d43-dff9-47f2-a728-7b7d1d6520f0", "中央法规/行政/经济部/工业目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04057004", "政治"),
            ("213f9b88-b067-43c7-b8ac-9f0b2d2ef60b", "中央法规/行政/经济部/投资目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04057005", "政治"),
            ("af16bada-49dd-4656-8c1e-69047ed26736", "中央法规/行政/经济部/标准检验目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04057010", "政治"),
            ("d16a28e3-195a-4df1-ab93-84b2ccb5c863", "中央法规/行政/经济部/水利目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04057011", "政治"),
            ("56f7dca6-c30f-44b7-8964-e6ad5fb1a183", "中央法规/行政/经济部/知识产权目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04057007", "政治"),
            ("7ce951d9-65db-4914-87cb-96af6f417d6b", "中央法规/行政/经济部/矿业目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04057003", "政治"),
            ("7b68d96e-0ab8-4a55-870e-a07c2a3d2996", "中央法规/行政/经济部/组织目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04057001", "政治"),
            ("dad3b26c-fff5-4af7-bdf5-38e00f2a104e", "中央法规/行政/经济部/能源管理目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04057013", "政治"),
            ("9699e389-6006-45d9-af6b-aeeac9c38a50", "中央法规/行政/行政机构人事行政总处", "", "政治"),
            ("89fb1ceb-ab7e-48a3-a163-fc243c365da6", "中央法规/行政/行政机构人事行政总处/培训考用目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04025004", "政治"),
            ("8eb2c9d3-c47e-4b79-b8bf-81c51f86b3e8", "中央法规/行政/行政机构人事行政总处/组织目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04025001", "政治"),
            ("da81073f-8c51-4f6f-b3fa-9dd45cc78f76", "中央法规/行政/行政机构人事行政总处/组编人力目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04025003", "政治"),
            ("4cfe3841-39b8-4bc5-b84f-ddef1e19ab80", "中央法规/行政/行政机构人事行政总处/给与福利目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04025005", "政治"),
            ("00549f7a-5f9f-41fc-b486-7a02effa0e87", "中央法规/行政/行政机构人事行政总处/综合规划目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04025002", "政治"),
            ("3320082e-9f78-4d48-9fca-5bc831f4cf4c", "中央法规/行政/行政院主计总处", "", "政治"),
            ("1a455774-e84f-4e2e-8909-3e4beead02bf", "中央法规/行政/行政院主计总处/主计人事目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04024006", "政治"),
            ("72f34f8d-0fd5-4d48-87a2-090190b12239", "中央法规/行政/行政院主计总处/主计资讯目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04024005", "政治"),
            ("34316f24-fad4-4bf6-807c-f578b93ef9ba", "中央法规/行政/行政院主计总处/会计目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04024003", "政治"),
            ("591143dc-be48-4bde-97c3-f0274d436923", "中央法规/行政/行政院主计总处/其他目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04024007", "政治"),
            ("8bccdd8c-2eff-4758-8e6b-414abe0873e4", "中央法规/行政/行政院主计总处/岁计目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04024002", "政治"),
            ("84f24400-c0a9-4dfb-89a4-1099a1f2d4cc", "中央法规/行政/行政院主计总处/组织目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04024001", "政治"),
            ("1e3fefbd-a941-4a2e-b2af-dfced4d31516", "中央法规/行政/行政院主计总处/统计目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04024004", "政治"),
            ("c4e88eb4-1a7c-44e6-af7b-784b8c3b71ee", "中央法规/行政/行政院公共工程委员会", "", "政治"),
            ("e7cf631b-0b06-4eeb-a56b-80e910fdbbdb", "中央法规/行政/行政院公共工程委员会/处务目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04053002", "政治"),
            ("2e2a6dfc-1426-4243-9549-594b4400cbc3", "中央法规/行政/行政院公共工程委员会/组织目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04053001", "政治"),
            ("e8b7edf0-3c3f-49c0-86a2-f64f98d045fd", "中央法规/行政/行政院公共工程委员会/通用目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04053003", "政治"),
            ("85572881-7c4e-4a96-9dc6-81110ed00863", "中央法规/行政/行政院农业委员会", "", "政治"),
            ("44e847a8-6298-482c-b045-7e732b7c822a", "中央法规/行政/行政院农业委员会/农业发展目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04055003", "政治"),
            ("df6aa76f-89c4-435f-a198-1526ea977637", "中央法规/行政/行政院农业委员会/农业科技目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04055009", "政治"),
            ("c99d70b6-716c-4dd2-b092-68a459b56908", "中央法规/行政/行政院农业委员会/农业金融目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04055008", "政治"),
            ("1e029a07-48d5-4267-bf84-3e64a46838f6", "中央法规/行政/行政院农业委员会/农民辅导目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04055010", "政治"),
            ("a8244d5a-79a3-418c-8a8f-a6e01e77fac5", "中央法规/行政/行政院农业委员会/农田水利目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04055011", "政治"),
            ("67fd74f9-78ec-4b7e-87bd-52650ad9074a", "中央法规/行政/行政院农业委员会/农粮目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04055004", "政治"),
            ("159afe0b-e228-4ed5-8371-58e1be86aeb2", "中央法规/行政/行政院农业委员会/动物防检疫目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04055014", "政治"),
            ("827e4bb1-ec01-4076-86e9-a82888c55762", "中央法规/行政/行政院农业委员会/处务目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04055002", "政治"),
            ("6020bf58-968e-4079-ae09-ebb9d89cff77", "中央法规/行政/行政院农业委员会/林业目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04055005", "政治"),
            ("bbd21a6b-4713-44e2-a354-7096629b9a83", "中央法规/行政/行政院农业委员会/植物防检疫目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04055015", "政治"),
            ("4ca0cd0e-3170-46b2-9e1b-038e95cb6aed", "中央法规/行政/行政院农业委员会/水土保持目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04055012", "政治"),
            ("f4218f69-951c-40ee-9947-c81e5d62133e", "中央法规/行政/行政院农业委员会/渔业目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04055006", "政治"),
            ("712bfdf1-08d5-47a6-b4ab-0ad9c3800b26", "中央法规/行政/行政院农业委员会/畜牧目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04055007", "政治"),
            ("1f03d322-43ca-4b8d-8a93-fa28810e30b1", "中央法规/行政/行政院农业委员会/组织目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04055001", "政治"),
            ("19cec71b-788a-48ae-a741-da28c83812b9", "中央法规/行政/行政院农业委员会/野生动物保育目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04055013", "政治"),
            ("574eaa56-8205-4f43-aaed-ebe762ff39cf", "中央法规/行政/行政院原子能委员会", "", "政治"),
            ("7f65c233-4250-4719-aef6-1612c715ac41", "中央法规/行政/行政院原子能委员会/原子能目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04054003", "政治"),
            ("9d2e49f3-01af-4469-8765-5a40f719b1cb", "中央法规/行政/行政院原子能委员会/处务目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04054002", "政治"),
            ("03de420e-9d89-43d3-9e25-3c3685c1ccd6", "中央法规/行政/行政院原子能委员会/组织目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04054001", "政治"),
            ("b0367c6f-3528-466e-97ba-157860bef28d", "中央法规/行政/行政院环境保护署", "", "政治"),
            ("50f115a1-9f7f-48a3-8ad5-897ada49379a", "中央法规/行政/行政院环境保护署/公害纠纷目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04056009", "政治"),
            ("7709ba12-fa25-47d1-9265-60ef5e148758", "中央法规/行政/行政院环境保护署/卫生及毒物管理目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04056007", "政治"),
            ("7e8b152c-c581-493a-95ef-d15c364a5cf4", "中央法规/行政/行政院环境保护署/噪音管制目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04056004", "政治"),
            ("98b84785-12e3-47fb-8256-5f0f29baf45c", "中央法规/行政/行政院环境保护署/土壤及地下水目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04056012", "政治"),
            ("edcb8523-fac6-4ef8-bcd2-945ad81f5721", "中央法规/行政/行政院环境保护署/基本目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04056011", "政治"),
            ("b00ea409-5892-4dac-af3a-76990a2cf840", "中央法规/行政/行政院环境保护署/处务目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04056002", "政治"),
            ("3276339e-4fb6-4ab7-8125-dfc54b23c120", "中央法规/行政/行政院环境保护署/室内空气质量目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04056014", "政治"),
            ("ebfedfd4-3ba7-43f1-876f-0719c38b7fa8", "中央法规/行政/行政院环境保护署/废弃物管理目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04056006", "政治"),
            ("df04ca45-93cb-4f0f-a28b-8d26872d3c8d", "中央法规/行政/行政院环境保护署/检验目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04056008", "政治"),
            ("f524e70c-25bd-4da2-b204-2b266f9dbdd1", "中央法规/行政/行政院环境保护署/水质保护目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04056005", "政治"),
            ("e5968ca6-48db-47d9-aa30-c769535416ae", "中央法规/行政/行政院环境保护署/环境影响评估目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04056010", "政治"),
            ("ac316080-19d6-4cea-a234-ab5ede458ff7", "中央法规/行政/行政院环境保护署/环境教育目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04056013", "政治"),
            ("9ea6af77-e409-4705-a8cc-5a22205449d9", "中央法规/行政/行政院环境保护署/空气质量保护目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04056003", "政治"),
            ("0ccd42f8-617a-4ebf-be40-d99f755c6527", "中央法规/行政/行政院环境保护署/组织目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04056001", "政治"),
            ("14cd87ef-4602-4b5e-923f-8d1633633344", "中央法规/行政/财政目", "", "政治"),
            ("0a55e1eb-49fb-4c3e-b1cf-0b0737cc8924", "中央法规/行政/财政目/关务目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04005009", "政治"),
            ("c9a7b0d1-0950-42c4-b6ad-ea9332daf4fa", "中央法规/行政/财政目/国库目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04005007", "政治"),
            ("494b3b53-0591-4a35-bc41-0517779452ab", "中央法规/行政/财政目/国有财产目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04005010", "政治"),
            ("8a2dcd04-c96f-4ea6-93fe-fdfc3dba309f", "中央法规/行政/财政目/国际财政目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04005003", "政治"),
            ("8cf3667d-e5e4-4c7f-9207-10d34b24f8cc", "中央法规/行政/财政目/推动促参目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04005005", "政治"),
            ("14ee9274-bf7b-44aa-8458-b225e092aea4", "中央法规/行政/财政目/组织目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04005001", "政治"),
            ("0f13fedc-3da0-4d37-8cfc-827c92b2fd90", "中央法规/行政/财政目/综合规划目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04005002", "政治"),
            ("b33e633e-354b-4f9a-8675-1a0f0439c528", "中央法规/行政/财政目/财政信息目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04005006", "政治"),
            ("f1318a78-385d-469f-90bb-dfb42da87447", "中央法规/行政/财政目/赋税目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04005008", "政治"),
            ("8d7305ef-6517-480e-83a7-b5289f0974c7", "中央法规/行政/金融监督管理委员会", "", "政治"),
            ("4c6d2fa4-5f1c-4aa6-996c-5887dd1cb801", "中央法规/行政/金融监督管理委员会/保险目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04018009", "政治"),
            ("4d2d9cdf-7290-4f7b-af58-11547f20c781", "中央法规/行政/金融监督管理委员会/基金管理目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04018005", "政治"),
            ("074e62a3-06bf-4bdf-8b98-af2002dc4890", "中央法规/行政/金融监督管理委员会/收费目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04018002", "政治"),
            ("132e8d0c-f744-485a-9a0b-96a6e3a5a435", "中央法规/行政/金融监督管理委员会/检查目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04018007", "政治"),
            ("4d00d01e-6ffc-40dc-9c3e-dbf1f5a02436", "中央法规/行政/金融监督管理委员会/消费者保护目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04018010", "政治"),
            ("bac4e256-f332-48ad-a118-1453c38c27a9", "中央法规/行政/金融监督管理委员会/组织目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04018001", "政治"),
            ("9ba1adbb-83e7-48a3-b1eb-75577f5a81fd", "中央法规/行政/金融监督管理委员会/裁罚措施公布目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04018003", "政治"),
            ("712ce776-91e6-4913-ac8d-ac553107dfd3", "中央法规/行政/金融监督管理委员会/证券暨期货管理目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04018006", "政治"),
            ("f38a3bd1-18ff-4af5-a194-babf99c4360e", "中央法规/行政/金融监督管理委员会/金融交易监视目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04018004", "政治"),
            ("5b2b9a26-a2f1-4560-820b-9add59df941b", "中央法规/行政/金融监督管理委员会/金融科技目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04018011", "政治"),
            ("2d7e9ebc-69ae-4dab-89c8-820c243e64ff", "中央法规/行政/金融监督管理委员会/银行目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04018008", "政治"),
            ("5f5761fd-1060-4492-bf96-ecce6d91c481", "中央法规/行政/院本部", "", "政治"),
            ("9596972d-f1c0-4cb5-a6e0-1895bfb7766a", "中央法规/行政/院本部/基金管理目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04001003", "政治"),
            ("b581526f-e4a5-4a57-a82b-3fd7cd5eee16", "中央法规/行政/院本部/消费者保护目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04001004", "政治"),
            ("5fce7f8a-c171-4a22-a0d9-cf0965909483", "中央法规/行政/院本部/组织目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04001001", "政治"),
            ("99c10ef9-5d3c-48b3-ac50-d27dc5065285", "中央法规/行政/院本部/通用目", "https://law.moj.gov.tw/Law/LawSearchLaw.aspx?TY=04001002", "政治"),
            ("1b087526-4d06-419a-b9ae-f32f0a23ebf5", "最新讯息", "", "政治"),
            ("8a053ada-11d0-4b03-99ea-0b7bc44b5ab5", "最新讯息/地方法规", "https://law.moj.gov.tw/News/NewsList.aspx?type=q", "政治"),
            ("0d00c4a1-a60f-464b-abdf-e4b7818894c1", "最新讯息/法律", "https://law.moj.gov.tw/News/NewsList.aspx?type=l", "政治"),
            ("1538d26f-f65e-40d1-921e-f3678ae573ec", "最新讯息/法规命令", "https://law.moj.gov.tw/News/NewsList.aspx?type=m", "政治"),
            ("d04c0d73-bd1a-4355-bf9d-48a8d5640a9d", "最新讯息/法规草案", "https://law.moj.gov.tw/News/NewsList.aspx?type=s", "政治"),
            ("db54d5a2-6cb8-4edb-86d8-0b4de8ea8dfb", "最新讯息/行政规则", "https://law.moj.gov.tw/News/NewsList.aspx?type=o", "政治"),
        ]
    ]
    
    def __init__(self):
        BaseParser.__init__(self)

    # URL分类器: 用于对新闻页URL进行分类
    def url_classifier(self, url):
        # 分类表(基于URL地址进行分类)
        classifier_map = {
            # class(A) -> exp(https://law.moj.gov.tw/News/NewsDetail.aspx?msgid=173671)
            "https://law.moj.gov.tw/News/NewsDetail.aspx": "A",
            # class(B) -> exp(https://law.moj.gov.tw/LawClass/LawAll.aspx?pcode=A0010021)
            "https://law.moj.gov.tw/LawClass/LawAll.aspx": "B",
            # class(C) -> exp(https://lawsearch.taichung.gov.tw/GLRSout/LawContent.aspx?id=GL003323)
            "https://lawsearch.taichung.gov.tw/GLRSout/LawContent.aspx": "C",
            # class(C) -> exp(https://law.tycg.gov.tw/LawContent.aspx?id=GL002383)
            "https://law.tycg.gov.tw/LawContent.aspx": "C",
            # class(D) -> exp(https://gazette.nat.gov.tw/egFront/detail.do?metaid=138282&log=detailLog)
            "https://gazette.nat.gov.tw/egFront/detail.do": "D",
        }
        # 重定向链接(parse_list方法中过滤用)
        classifier_map["https://law.moj.gov.tw/Hot/AddHotLaw.ashx"] = "PASS"
        return classifier_map.get(url.strip().split('?')[0], '')

    def parse_list(self, response) -> list:
        news_urls = response.xpath('//a[@id="hlkNAME"]/@href|//a[@id="hlkLawName"]/@href').extract() or []
        # 根据分类表进行过滤(用于线上环境，开发阶段需要屏蔽该代码)
        news_urls = [url for url in news_urls if self.url_classifier(urljoin(response.url, url))]
        for news_url in list(set(news_urls)):
            yield urljoin(response.url, news_url)

    def get_title(self, response) -> str:
        title_xpath = {
            "A": '//head/title/text()',
            "B": '//head/title/text()',
            "C": '//table[@class="table table-bordered tab-edit"]/tr[1]/td/text()',
            "D": '//meta[@property="og:title"]/@content',
        }.get(self.url_classifier(response.url))
        return response.xpath(title_xpath).extract_first(default="").split("-", 1)[0].strip() if title_xpath else ""

    def get_author(self, response) -> list:
        return []

    def get_pub_time(self, response) -> str:
        time_xpath = {
            "A": '//div[@class="text-con"]/table/tbody/tr[1]/td/text()',
            "B": '//tr[@id="trLNNDate"]/td/text()|//tr[@id="trLNODate"]/td/text()',
            "C": '//table[@class="table table-bordered tab-edit"]/tr[2]/td/text()',
            "D": '//div[@class="Data_Info"]/div/section/p/span[2]',
        }.get(self.url_classifier(response.url))
        try:
            y, m, d = re.findall(r'\d+', response.xpath(time_xpath).extract_first(default="").strip())
            y = 1911 + int(y)
            m = f'0{m}' if len(m) < 2 else m
            d = f'0{d}' if len(d) < 2 else d
            return f'{y}-{m}-{d} 00:00:00'
        except:
            return "9999-01-01 00:00:00"

    def get_tags(self, response) -> list:
        return []

    def get_content_media(self, response) -> list:
        # URL类别
        url_category = self.url_classifier(response.url)
        # 解析正文数据
        content = []
        # class(A) -> https://law.moj.gov.tw/News/NewsDetail.aspx
        if url_category == "A":
            for tr_tag in response.xpath('//div[@class="container"]//table/tbody/tr'):
                # tag(th)
                th_text = tr_tag.xpath("./th/text()").extract_first(default="").strip()
                # tag(td)
                td_tag = tr_tag.xpath("./td")
                if td_tag.attrib.get("class") != "text-pre":
                    td_text = " ".join(td_tag.xpath(".//text()").extract() or []).strip()
                    content.append({"type": "text", "data": f'{th_text} {td_text}'})
                else:
                    content.append({"type": "text", "data": th_text})
                    for text in td_tag.xpath(".//text()").extract() or []:
                        text = text.strip()
                        text and content.append({"type": "text", "data": text})
        # class(B) -> https://law.moj.gov.tw/LawClass/LawAll.aspx
        elif url_category == "B":
            # 解析元信息
            for tr_tag in response.xpath('//table[@class="table"]/tr'):
                th_text = tr_tag.xpath("./th/text()").extract_first(default="").strip()
                td_text = "".join(tr_tag.xpath("./td//text()").extract() or []).strip()
                content.append({"type": "text", "data": f'{th_text} {td_text}'})
            # 解析正文
            for tag in response.xpath('//div[@class="law-reg-content"]/*'):
                tag_class = tag.attrib.get("class")
                if tag_class == "h3 char-2":
                    content.append({"type": "text", "data": tag.xpath('./text()').extract_first(default="").strip()})
                elif tag_class == "row":
                    for text in tag.xpath('.//text()').extract():
                        text = text.strip()
                        text and content.append({"type": "text", "data": text})
        # class(C) -> https://lawsearch.taichung.gov.tw/GLRSout/LawContent.aspx
        elif url_category == "C":
            # 解析元信息
            for tr_tag in response.xpath('//table[@class="table table-bordered tab-edit"]/tr'):
                th_text = tr_tag.xpath("./th/text()").extract_first(default="").strip()
                td_text = "\n".join(tr_tag.xpath("./td//text()").extract() or []).strip()
                content.append({"type": "text", "data": f'{th_text} {td_text}'})
            # 解析正文
            for tag in response.xpath('//table[@class="table tab-list tab-nobg tab-law law-content"]//tr'):
                text = ''.join([t.strip() for t in tag.xpath(".//text()").extract()]).strip()
                text and content.append({"type": "text", "data": text})
            # 解析下载资源
            for tag in response.xpath('//table[@class="table table-bordered tab-edit"]//a'):
                file_url = tag.attrib.get("href")
                if not file_url.startswith("Download.ashx"):
                    continue
                try:
                    file_url = urljoin(response.url, file_url)
                    file_name = tag.xpath("./text()").extract_first(default="").strip()
                    suffix = file_name.split(".")[-1].lower()
                    content.append({
                        "type": "file",
                        "src": file_url,
                        "name": file_name,
                        "description": None,
                        "md5src": self.get_md5_value(file_url) + f".{suffix}"
                    })
                except:
                    pass
        # class(D) -> https://gazette.nat.gov.tw/egFront/detail.do
        elif url_category == "D":
            # 解析正文数据
            for tag in response.xpath('//div[@class="Data_Info"]/div/section[2]/*'):
                if tag.root.tag in ["p", "h3"]:
                    text = ' '.join(tag.xpath('.//text()').extract()).strip()
                    text and content.append({"type": "text", "data": text})
            # 解析PDF资源
            for tag in response.xpath('//div[@class="Control_BTN visible-xs-block"]/a'):
                file_url = urljoin(response.url, tag.attrib.get("href"))
                suffix = file_url.split("?")[0].split(".")[-1].lower()
                if not suffix in ["pdf"]:
                    continue
                content.append({
                    "type": "file",
                    "src": file_url,
                    "name": tag.attrib.get("title", ""),
                    "description": None,
                    "md5src": self.get_md5_value(file_url) + f".{suffix}"
                })
        else:
            pass

        return content

    def get_detected_lang(self, response) -> str:
        return 'zh-CN'

    def get_like_count(self, response) -> int:
        return 0

    def get_comment_count(self, response) -> int:
        return 0

    def get_forward_count(self, response) -> int:
        return 0

    def get_read_count(self, response) -> int:
        return 0

    def get_if_repost(self, response) -> bool:
        return False

    def get_repost_source(self, response) -> str:
        return ""
