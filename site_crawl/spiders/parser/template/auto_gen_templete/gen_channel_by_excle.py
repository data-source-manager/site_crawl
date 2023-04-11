import csv
import uuid

site_name = "台湾行政院全球资讯网"


def get_board_info():
    with open("../../../util/site.csv") as f:
        reader = csv.reader(f)
        uuid_list = []
        board_info = {}
        for row in reader:
            row = row[0].split("\t")
            if row[1]:
                board_name = f'{site_name}_{row[1]}/{row[0]}'
                uid = str(uuid.uuid4())
                uuid_list.append(uid)
                board_info[board_name] = uid
            else:
                board_name = f'{site_name}_{row[0]}'
                uid = str(uuid.uuid4())
                uuid_list.append(uid)
                board_info[board_name] = uid
        print(board_info)
        for x in uuid_list:
            print(x)


if __name__ == '__main__':
    get_board_info()
