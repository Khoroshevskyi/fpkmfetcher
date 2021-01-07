import requests
import json
from data_downloader import GDCDownloader
from data_formatter import DataFormatter
from datetime import datetime
import time
import os


class GDCServer(object):
    def __init__(self, config):

        self.__config = config
        self.file_downloader = GDCDownloader(self.__config)

    def create_params(self, tumor_stage):

        cancer_type = {"op": "in",
                       "content":
                           {"field": "cases.primary_site",
                            "value": self.__config["primary_site"]}
                       }

        stage_value = {"op": "in",
                       "content":
                           {"field": "cases.diagnoses.tumor_stage",
                            "value": tumor_stage}
                       }

        filters = {"op": "and",
                   "content": [cancer_type,
                               stage_value
                               ]
                   }

        # With a GET request, the filters parameter needs to be converted
        # from a dictionary to JSON-formatted string
        parameters = {
            "filters": json.dumps(filters),
            "expand": ["files"],
            "format": self.__config["format"],
            "size": self.__config["size"]
        }

        return parameters

    # getting information with expanded diagnoses of one case
    def get_case_diagnoses(self, case_id):
        filters = {"op": "and",
                   "content": [{"op": "in",
                                "content":
                                    {"field": "cases.case_id",
                                     "value": case_id}
                                }
                               ]
                   }
        parameters = {
            "filters": json.dumps(filters),
            "expand": ["diagnoses"],
            "format": self.__config["format"]
        }
        case_diagnose = requests.get(self.__config["cases_endpt"], params=parameters)
        return case_diagnose.json()

    # getting specific cases information with files information and adding diagnoses for it
    def get_case_information(self, tumor_stage):
        try:
            data = requests.get(self.__config["cases_endpt"], params=self.create_params(tumor_stage)).json()

            for case_number in range(len(data["data"]["hits"])):
                diagnose = self.get_case_diagnoses(data["data"]["hits"][case_number]["case_id"])
                data["data"]["hits"][case_number]["diagnoses"] = diagnose["data"]["hits"][0]["diagnoses"]

            print("Information was found successfully!")
            print("Data infomration:  {}".format(data["data"]["pagination"]))

            return data

        except Exception as err:
            print("Error occurred while getting cases information: {}".format(err))

    def check_dir_exsits(self, dir):
        if not os.path.exists(dir):
            os.makedirs(dir)

    def save_file(self, data, path_name):
        print("Saving file: {}".format(path_name))
        file_object = open(path_name, "w+")
        file_object.write(data)
        file_object.close()
        print("File was saved successfully")

    def save_case_info(self, data, file_name):
        try:
            data_json = json.dumps(data, indent=4)
            file_time = datetime.now().strftime("_%Y_%m_%d")
            directory = self.__config["dir"] + "/info/"

            self.check_dir_exsits(directory)

            file_dir_name = directory + "_information_" + file_name + file_time + ".json"

            self.save_file(data_json, file_dir_name)

        except Exception as err:
            print("Error occurred while saving file: {}".format(err))

    def files_downloader(self, data, stage):
        len_all = len(data["hits"])
        nb_file = 0
        for case in data["hits"]:
            nb_file += 1
            self.file_downloader.download_file(case["fpkm_files"][0]["file_id"], stage)
            print("File:: {} out of {} have been downloaded".format(nb_file, len_all))

    def get(self):
        start = time.time()
        for stage in self.__config["tumor_stages"]:
            print("##################")
            print("Searching files of {} in https://api.gdc.cancer.gov ...".format(stage))
            data = self.get_case_information(self.__config["tumor_stages"][stage])

            self.file_formatter = DataFormatter(self.__config)
            data = self.file_formatter.choose_fpkm_data(data)

            self.save_case_info(data, stage)
            self.files_downloader(data, stage)
            # print(json.dumps(data, indent=4, sort_keys=True))
        end = time.time()
        print("time spent: {}".format(str(end - start)))


def main():
    """Main Function"""
    config = json.load(open("config.json"))
    gdc_server = GDCServer(config)
    gdc_server.get()


if __name__ == '__main__':
    main()
