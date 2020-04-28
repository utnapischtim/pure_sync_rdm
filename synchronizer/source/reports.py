from datetime                       import date, datetime
from setup                          import log_files_name

class Reports:

    def add_template(self, files, template, arguments):
        report = report_templates[template[0]][template[1]].format(*arguments)
        self.add(files, report)

    def add(self, files, report):
        for file in files:
            if file == 'records_full':
                print(report)
            file_name = log_files_name[file]
            open(file_name, "a").write(f'{report}\n')



report_templates = {

    # GENERAL
    'general': {
        # Intro                     Arguments -> title, current time
        'title': """

--   --   --

-- {} -- {}""",

        },

    # PAGES
    'pages': {
        'page_and_size': 'Page: {} - page size: {}',
    },

    # CHANGES
    'changes': {
        'summary': """
Metadata         ->  successful: {} - errors:   {}
File             ->  successful: {} - errors:   {}
Delete           ->  successful: {} - errors:   {}

Pure changes:
Update:     {} - Create:     {} - Delete:    {}
Incomplete: {} - Duplicated: {} - Irrelevant:{}
"""
    },

}