import os

import jinja2

from .utils import today_Ymd


class Reporter(object):
    def __init__(self, repo_name: str, typos: list) -> None:
        self.repo_name = repo_name
        self.typos = typos

    def generate_report(self) -> None:

        data = self._generate_data()
        self._generate_html(data)

    def _generate_data(self):
        if len(self.typos) < 1:
            return
        data = []
        for typo in self.typos:
            data.append({"name": typo, "files": []})
        # TODO need to find filename and linenumber -> add to data
        # Sample data
        # data = [
        #     {
        #         "name": self.typos[0],
        #         "files": [
        #             {
        #                 "name": "/Users/minhokim/code/python/typofinder/typofinder/typofinder.py",
        #                 "lines": [
        #                     {
        #                         "number": "9",
        #                         "content": "    def generate_report(self[str]=None) -> None:",
        #                         "includes_typo": False,
        #                     },
        #                     {
        #                         "number": "10",
        #                         "content": "        def _generate_data[str]=None):",
        #                         "includes_typo": True,
        #                     },
        #                     {
        #                         "number": "11",
        #                         "content": "            data = [",
        #                         "includes_typo": False,
        #                     },
        #                 ],
        #             }
        #         ],
        #     }
        # ]
        return data

    def _generate_html(self, data=None):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        template_dir = os.path.join(base_dir, "templates")
        loader = jinja2.FileSystemLoader(template_dir)
        env = jinja2.Environment(loader=loader)
        template = env.get_template("template.html")
        if data:
            output = template.render(data)
        output_dir = os.path.join(base_dir, "reports")
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        output_file = os.path.join(
            output_dir, f"report-{self.repo_name}-{today_Ymd()}.html"
        )
        with open(output_file, "w") as file:
            file.write(template.render(repo_name=self.repo_name, typos=data))
        print(output_file)
