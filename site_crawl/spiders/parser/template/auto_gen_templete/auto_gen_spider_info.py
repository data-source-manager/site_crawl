import os
import uuid
from string import Template

from site_crawl.spiders.util.tools import genUUID

from apps.entry_id import source_dict
from site_crawl.spiders.parser.template.auto_gen_templete.parse_template_str import template_str

domain = "dnn.mn"
country = "mn"
main_domain_name = "dnn"

app_id = 320
source_name = "日报"
get_channel_by_csv = False

board_info = {
    "政治": "https://dnn.mn/%D0%BC%D1%8D%D0%B4%D1%8D%D1%8D/%D1%83%D0%BB%D1%81-%D1%82%D3%A9%D1%80/",
    "外国": "https://dnn.mn/%D0%BC%D1%8D%D0%B4%D1%8D%D1%8D/%D0%B3%D0%B0%D0%B4%D0%B0%D0%B0%D0%B4/",
    "视频": "https://dnn.mn/%D0%B2%D0%B8%D0%B4%D0%B5%D0%BE-%D0%BC%D1%8D%D0%B4%D1%8D%D1%8D/",
    "角落/科学与技术":"https://dnn.mn/%D0%BC%D1%8D%D0%B4%D1%8D%D1%8D/%D0%B1%D1%83%D0%BB%D0%B0%D0%BD%D0%B3%D1%83%D1%83%D0%B4/%D1%88%D0%B8%D0%BD%D0%B6%D0%BB%D1%8D%D1%85-%D1%83%D1%85%D0%B0%D0%B0%D0%BD-%D1%82%D0%B5%D1%85%D0%BD%D0%BE%D0%BB%D0%BE%D0%B3%D0%B8/"
}

file_path = os.path.realpath(__file__)
parser_path = os.path.dirname(os.path.dirname(os.path.dirname(file_path)))
if __name__ == '__main__':
    channel_info = []
    temp_str = Template(template_str)
    country_name = country.replace(country[0], country[0].upper())
    domain_name = main_domain_name.replace(main_domain_name[0], main_domain_name[0].upper())
    for chan in board_info.items():
        channel_info.append({
            'url': chan[1],
            'direction': country.lower(),
            'source_name': source_name,
            'site_board_name': chan[0],
            'board_theme': '政治',
            'if_front_position': False,
            "board_id": genUUID(f"{source_name}_{chan[0]}")
        })
    site_id = source_dict.get(source_name) if source_dict.get(source_name) else str(uuid.uuid4())
    print(f"站点id: self.site_id='{site_id}'")

    res_template = temp_str.substitute(country=f'{country_name}', domain=domain_name,
                                       spider_name=main_domain_name, channel=channel_info)
    parse_file_name = f"{country}_{main_domain_name}"
    parse_init = f'from .{parse_file_name} import {country_name}{domain_name}Parser'
    print(parse_init)
    app_info = f"""
        {app_id}:AppConfig(
        appid={app_id},
        appname='{app_id}_{main_domain_name}',
        appclass=parser.{country_name}{domain_name}Parser,
        appdomain='{domain}'
    ),
    """
    print(app_info)
    parser_path = os.path.join(parser_path, f'{parse_file_name}.py')
    if not os.path.exists(parser_path):
        with open(f'{parser_path}', "w", encoding="utf-8") as f:
            f.write(res_template)
