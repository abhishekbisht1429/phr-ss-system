import os.path

import requests
import config


def add(file_path):
    with open(file_path, 'rb') as file:
        file_name = os.path.basename(file_path)

        res = requests.post(config.ipfs_add_url, files={file_name: file})

        if res.status_code == requests.codes.ok:
            print("uploaded successfully")
            print(res.json())
            return res.status_code, res.json()
        else:
            print(res.status_code)
            return res.status_code, None


if __name__ == '__main__':
    add('temp/user1')