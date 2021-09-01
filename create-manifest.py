import base64
import json
import ssl
import yaml
import requests


class GitSecurityContent:
    # Added below line to resolve SSL exceptions
    ssl._create_default_https_context = ssl._create_unverified_context

    def __init__(self, git_branch, repo_username, repo_name, test_detection_main_dir):
        self.GIT_BRANCH = git_branch
        self.REPO_USERNAME = repo_username
        self.REPO_NAME = repo_name
        # In sub dict we want traverse
        self.DETECTION_SUB_DIR = ["cloud", "endpoint"]

        # dir from where we start traversing
        self.TEST_DETECTION_MAIN_DIR_NAME = test_detection_main_dir

        # API end point
        self.GIT_API_END_POINT = f"https://api.github.com/repos/{self.REPO_USERNAME}/{self.REPO_NAME}/git/trees/{self.GIT_BRANCH}"

        # Sample JSON tpo store the all the response
        self.SAMPLE_JSON = {"cloud": {}, "endpoint": {}}

        # Create JSON for this detection only
        self.TEST_DETECTION_NAME = (
            "abnormally_high_number_of_cloud_infrastructure_api_calls.test.yml"
        )
        # This contains all files and their respective paths
        self.ALL_RECURSIVE_PATH = []

    def fetch_file_info(self, endpoint, is_recursive=False):
        headers = {
            "accept": "application/vnd.github.v3+json"
        }
        params = {"recursive": 1} if is_recursive else {}
        response = requests.get(f"{endpoint}", headers=headers, params=params)
        if response.status_code == 200:
            return json.loads(response.content)
        raise Exception(f"Something went wrong, {json.loads(response.content)}")

    def decode_git_response(self, data):
        decoded_content = base64.b64decode(data["content"])
        return yaml.safe_load(decoded_content)

    def write_json_file(self):
        with open("temp_manifest_init.json", "w+") as file1:
            print(self.SAMPLE_JSON)
            json.dump(self.SAMPLE_JSON, file1, indent=4)

    def find_dict_from_list(self, list_data, path):
        return next(item for item in list_data if item["path"] == path)

    def generate_manifest(self):
        # Store all the recursive path
        recursive_response = self.fetch_file_info(
            self.GIT_API_END_POINT, is_recursive=True
        )
        self.ALL_RECURSIVE_PATH = recursive_response.get("tree")

        # Fetch first set of folder structure
        fetch_first_set_from_repo = self.fetch_file_info(self.GIT_API_END_POINT)

        # Traverse through all files and dir in main tree from first set
        for path in fetch_first_set_from_repo.get("tree"):
            # Fetch the tests dir
            if path.get("path") == self.TEST_DETECTION_MAIN_DIR_NAME:
                tests_dir_response = self.fetch_file_info(path.get("url"))

                # Traverse through all files and dir in tests dir
                for sub_dir in tests_dir_response.get("tree"):

                    # Check sub dir name in our detection sub dir list
                    if sub_dir.get("path") in self.DETECTION_SUB_DIR:

                        # Fetch all the test detections in sub dir
                        fetch_detection_in_sub_dir = self.fetch_file_info(
                            sub_dir.get("url")
                        )

                        # Fetch only abnormally_high_number_of_cloud_infrastructure_api_calls.test.yml
                        final_detection = self.find_dict_from_list(
                            fetch_detection_in_sub_dir.get("tree"),
                            self.TEST_DETECTION_NAME,
                        )

                        # Fetch detection content
                        detection_content = self.fetch_file_info(
                            final_detection.get("url")
                        )
                        decoded_detection_response = self.decode_git_response(
                            detection_content
                        )

                        temp_detection_dict = dict(TEST=decoded_detection_response)

                        # APPEND MAIN YML FILE DATA
                        main_yml_file_content = self.find_dict_from_list(
                            self.ALL_RECURSIVE_PATH,
                            f'detections/{decoded_detection_response["tests"][0]["file"]}',
                        )
                        main_yml_file_content_data = self.fetch_file_info(
                            main_yml_file_content.get("url")
                        )
                        main_detection_decoded_response = self.decode_git_response(
                            main_yml_file_content_data
                        )
                        temp_detection_dict["YAML"] = main_detection_decoded_response

                        # APPEND BASELINE DATA IF ANY, Appending const baseline
                        # if decoded_response.get("tests")("baselines"):
                        temp_detection_dict["BASELINE"] = {}

                        # APPEND TEST YAML file details
                        self.SAMPLE_JSON[sub_dir["path"]][
                            decoded_detection_response["tests"][0]["name"]
                        ] = temp_detection_dict
                        break

    def main(self):
        self.generate_manifest()
        self.write_json_file()


if __name__ == "__main__":
    git_security_content = GitSecurityContent(
        "develop", "splunk", "security_content", "tests"
    )
    git_security_content.main()
