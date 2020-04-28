from datetime                       import date, datetime
from setup                          import log_files_name
from source.general_functions       import add_spaces

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


    def summary_global_counters(self, report_files, global_counters):
        arguments = []
        arguments.append(add_spaces(global_counters['successful_push_metadata']))
        arguments.append(add_spaces(global_counters['successful_push_file']))
        arguments.append(add_spaces(global_counters['successful_record_delete']))
        arguments.append(add_spaces(global_counters['errors_push_metadata']))
        arguments.append(add_spaces(global_counters['errors_put_file']))
        arguments.append(add_spaces(global_counters['errors_record_delete']))

        self.add_template(report_files, ['general', 'summary'], arguments)

        http_response_str = self.metadata_http_responses(global_counters)
        self.add(report_files, http_response_str)


    def pages_single_line(self, global_counters, pag, pag_size):
        current_time = datetime.now().strftime("%H:%M:%S")
        arguments = []
        arguments.append(add_spaces(current_time))
        arguments.append(add_spaces(pag))
        arguments.append(add_spaces(pag_size))
        arguments.append(add_spaces(global_counters['successful_push_metadata']))
        arguments.append(add_spaces(global_counters['errors_push_metadata']))
        arguments.append(add_spaces(global_counters['successful_push_file']))
        arguments.append(add_spaces(global_counters['errors_put_file']))
        arguments.append(add_spaces(global_counters['abstracts']))
        arguments.append(add_spaces(global_counters['orcids']))
        arguments.append(self.metadata_http_responses(global_counters))

        self.add_template(['pages'], ['pages', 'summary_single_line'], arguments)
        return


    def metadata_http_responses(self, global_counters):
        http_response_str = 'Metadata HTTP responses -> '
        for key in global_counters['http_responses']:
            http_response_str += f"{key}: {global_counters['http_responses'][key]}, "
        return http_response_str[:-2] + '\n'



report_templates = {

    # GENERAL
    'general': {
        # Intro                     Arguments -> title, current time
        'title': """

--   --   --

-- {} -- {}""",

        # Summary global counters
        'summary': """
Successful      -> metadata: {} - files: {} - delete: {}
Errors          -> metadata: {} - files: {} - delete: {}
"""

        },



    # PAGES
    'pages': {
        'page_and_size': '\nPage: {} - page size: {}',

        'summary_single_line': """
{} - Page{} - Size{} - \
Metadata (ok{},error {}) - \
File (ok{}, error{}) - \
Abstracts:{} - Orcids:{} - \
{}\
"""
    },



    # CHANGES
    'changes': {
        'summary': """Pure changes:
Update:     {} - Create:     {} - Delete:    {}
Incomplete: {} - Duplicated: {} - Irrelevant:{}
"""
    }
}