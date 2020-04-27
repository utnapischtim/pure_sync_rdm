from datetime                       import date, datetime
from setup                          import log_files_name

class Reports:

    def add_to_report(self, file, report):
        if file == 'records_full':
            print(report)
        file_name = log_files_name[file]
        open(file_name, "a").write(f'{report}\n')


    def get_report_template(self, report_files, template, arguments):
    
        report = report_templates[template].format(*arguments)

        for report_file in report_files:
            self.add_to_report(report_file, report)



report_templates = {

    'intro_title': """

--   --   --

{} -- {} --""",

    'page_and_size': 'Page: {} - page size: {}'
}