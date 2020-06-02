import json
from xml.etree                      import ElementTree as ET
from xml.dom                        import minidom
from source.rdm.requests            import Requests
from source.general_functions       import get_value, current_date, add_spaces
from source.pure.general_functions  import get_pure_record_metadata_by_uuid
from source.reports                 import Reports


class ImportRecords:

    def __init__(self):
        self.rdm_requests = Requests()
        self.report = Reports()
        self.file_name = "/home/bootcamp/src/pure_sync_rdm/synchronizer/data/temporary_files/test.xml"

    def run_import(self):

        # Report title
        self.report.add_template(['console'], ['general', 'title'], ['PURE IMPORT'])

        page = 1
        page_size = 20
        next_page = True

        # Get RDM records by page
        while next_page:

            data = self._get_rdm_records_metadata(page, page_size)
            if not data:
                self.report.add("\n\tEnd task\n")
                return

            self.report.add_template(['console'], ['pages', 'page_and_size'], [page, page_size])
            self.report.add('')  # adds empty line

            count = 0

            for item in data:

                count += 1
                self.full_item = item
                self.report_base = f"{add_spaces(count)} - {item['id']} -"
                item_metadata = item['metadata']

                # # Checks if the record was created today
                # if not self._check_date(item):
                #     self.report.add("\n\tEnd task\n")
                #     next_page = False
                #     break

                # Checks if the record has a uuid
                if not self._check_uuid(item_metadata):
                    continue

                self.report.add(f"{self.report_base} Adding")

                self._create_xml(item_metadata)

            page += 1

    def _check_uuid(self, item):
        """ If a uuid is specified in the RDM record means that it was imported
            from Pure. In this case, the record will be ignored """
        if 'uuid' in item:
            self.report.add(f"{self.report_base} Already in Pure")
            return False
        return True

    def _check_date(self, item):
        """ Checks if the record was created today """
        if item['created'] > current_date():
            return True
        else:
            date = item['created'].split('T')[0]
            self.report.add(f"{self.report_base} Too old: {date}")
            return False

    def _create_xml(self, item):
        """ Creates the xml file that will be imported in pure """
        ns_dataset = 'v1.dataset.pure.atira.dk'     # Name Space dataset
        ns_commons = 'v3.commons.pure.atira.dk'     # Name Space commons

        ET.register_namespace('v1', ns_dataset)
        ET.register_namespace('v3', ns_commons)

        # Build a tree structure
        root = ET.Element("{%s}datasets" % ns_dataset)

        self._populate_xml(item, root, ns_dataset, ns_commons)

    def _populate_xml(self, item, root, ns_dataset, ns_commons):

        # Dataset element
        body = ET.SubElement(root, "{%s}dataset" % ns_dataset)
        body.set('type', 'dataset')

        # Title
        title = self._sub_element(body, ns_dataset, 'title')
        title.text = get_value(item, ['title'])

        # Managing organisation
        organisational_unit = self._sub_element(body, ns_dataset, 'managingOrganisation')
        self._add_attribute(item, organisational_unit, 'lookupId', ['managingOrganisationalUnit_externalId'])

        # Persons
        persons = self._sub_element(body, ns_dataset, 'persons')
        persons.set('contactPerson', 'true')

        for person_data in item['contributors']:
            # External id
            person_id = self._sub_element(persons, ns_dataset, 'person')
            self._add_attribute(person_data, person_id, 'lookupId', ['externalId'])
            # Role
            role = self._sub_element(persons, ns_dataset, 'role')
            role.text = get_value(person_data, ['personRole'])
            # Name
            name = self._sub_element(persons, ns_dataset, 'name')
            name.text = get_value(person_data, ['name'])

        # Available date
        date = self._sub_element(body, ns_dataset, 'availableDate')
        sub_date = self._sub_element(date, ns_commons, 'year')
        sub_date.text = get_value(item, ['publication_date'])

        # Publisher
        publisher = self._sub_element(body, ns_dataset, 'publisher')    # REVIEW!!!!
        self._sub_element(publisher, ns_dataset, 'name')                # Data not in rdm
        self._sub_element(publisher, ns_dataset, 'type')                # Data not in rdm

        # Description
        descriptions = self._sub_element(body, ns_dataset, 'descriptions')
        description = self._sub_element(descriptions, ns_dataset, 'description')
        description.text = get_value(item, ['abstract'])

        # Links
        links = self._sub_element(body, ns_dataset, 'links')    # Review
        # Files
        link = self._sub_element(links, ns_dataset, 'link')
        link.set('type', 'files')
        link.text = get_value(self.full_item, ['links', 'files'])
        # Self
        link = self._sub_element(links, ns_commons, 'link')
        link.set('type', 'self')
        link.text = get_value(self.full_item, ['links', 'self'])

        self._end_xml(root)

    def _end_xml(self, root):
        # Wrap it in an ElementTree instance and save as XML
        xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="   ")
        open(self.file_name, "w").write(xml_str)

    def _sub_element(self, element, namespace: str, sub_element_name: str):
        """ Adds the the xml a sub element """
        return ET.SubElement(element, "{%s}%s" % (namespace, sub_element_name))

    def _add_attribute(self, item: object, sub_element, attribute: str, value_path: list):
        """ Gets from the rdm response a value and adds it as attribute to a given xml element """
        value = get_value(item, value_path)
        if value:
            sub_element.set(attribute, value)

    def _add_text(self, item: object, sub_element: object, path):
        """ Gets from the rdm response a value and adds it as text to a given xml element """
        sub_element.text = get_value(item, path)

    def _get_rdm_records_metadata(self, page: int, page_size: int):
        """ Requests to rdm records metadata by page """
        params = {'sort': 'mostrecent', 'size': page_size, 'page': page}
        response = self.rdm_requests.get_metadata(params)
        if response.status_code >= 300:
            return False
        # Load response
        json_data = json.loads(response.content)['hits']['hits']

        # Checks if any record is listed
        if not json_data:
            return False

        return json_data
