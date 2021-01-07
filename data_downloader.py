import requests
import json
import gzip
import os


class GDCDownloader(object):
    def __init__(self, config):

        self.__config = config

    def seve_b_file(self, file_name, content):
        print("saving file ...")
        file = open(file_name, 'wb')
        file.write(content)
        file.close()

    def check_dir_exsits(self, dir):
        if not os.path.exists(dir):
            os.makedirs(dir)

    def download_file(self, file_id, stage):
        try:
            print("Downloading file: {}  ...".format(file_id))

            data_endpt = self.__config["data_endpt"] + file_id
            response = requests.get(data_endpt)

            unzipped_file = gzip.decompress(response.content)

            file_dir = self.__config["dir"] + "/" + stage + "/"
            self.check_dir_exsits(file_dir)

            self.seve_b_file(file_dir + file_id + ".tsv", unzipped_file)

            print("File has been downloaded successfully")
        except Exception as err:
            print("Error occurred while downloading and saving file: {} ".format(err))


def main():
    """Main Function"""
    config = json.load(open("config.json"))
    gdc_downloader = GDCDownloader(config)
    print('Enter file id:')
    file_id = input()
    gdc_downloader.download_file(file_id=file_id)


if __name__ == '__main__':
    main()
