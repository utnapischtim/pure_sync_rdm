from datetime                       import date, datetime
from setup                          import log_files_name
from source.general_functions       import add_spaces, check_if_directory_exists, current_time

class Reports:

    def add_template(self, files, template, arguments):
        if template == ['general', 'title']:
            arguments.append(current_time())
        report = report_templates[template[0]][template[1]].format(*arguments)
        self.add(files, report)


    def add(self, files, report):
        
        check_if_directory_exists('reports')
        
        if files == []:
            files = ['console']

        # For each log file
        for file in files:
            # Prints in console only when saving in console file
            if file == 'console':
                print(report)
            # Get file name
            file_name = log_files_name[file]
            # Adds report to file
            open(file_name, "a").write(f'{report}\n')


    def summary_global_counters(self, report_files, global_counters):
        arguments = []
        arguments.append(add_spaces(global_counters['metadata']['success']))
        arguments.append(add_spaces(global_counters['file']['success']))
        arguments.append(add_spaces(global_counters['delete']['success']))
        arguments.append(add_spaces(global_counters['metadata']['error']))
        arguments.append(add_spaces(global_counters['file']['error']))
        arguments.append(add_spaces(global_counters['delete']['error']))
        self.add_template(report_files, ['general', 'summary'], arguments)

        if global_counters['http_responses']:
            http_response_str = self.metadata_http_responses(global_counters)
            self.add(report_files, http_response_str)


    def pages_single_line(self, global_counters, pag, pag_size):
        current_time = datetime.now().strftime("%H:%M:%S")
        arguments = []
        arguments.append(add_spaces(current_time))
        arguments.append(add_spaces(pag))
        arguments.append(add_spaces(pag_size))
        arguments.append(add_spaces(global_counters['metadata']['success']))
        arguments.append(add_spaces(global_counters['metadata']['error']))
        arguments.append(add_spaces(global_counters['file']['success']))
        arguments.append(add_spaces(global_counters['file']['error']))
        if global_counters['http_responses']:
            arguments.append(self.metadata_http_responses(global_counters))

        self.add_template(['pages'], ['pages', 'summary_single_line'], arguments)
        return


    def metadata_http_responses(self, global_counters):
        if not global_counters['http_responses']:
            return

        http_response_str = 'Metadata HTTP responses -> '
        for key in global_counters['http_responses']:
            http_response_str += f"{key}: {global_counters['http_responses'][key]}, "
        return http_response_str[:-2]



report_templates = {

    # GENERAL       ***
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

    # PAGES       ***
    'pages': {
        'page_and_size': '\nPage: {} - page size: {}',

        'summary_single_line': """\
{} - Page{} - Size{} - \
Metadata (ok{}, error {}) - \
File (ok{}, error{}) - \
{}"""},



    # CHANGES       ***
    'changes': {
        'summary': """Pure changes:
Update:     {} - Create:     {} - Delete:    {}
Incomplete: {} - Duplicated: {} - Irrelevant:{}
"""
    }
}