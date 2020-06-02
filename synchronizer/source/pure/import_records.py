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

            self._create_xml(data)

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

    def _create_xml(self, data):
        """ Creates the xml file that will be imported in pure """

        name_space = {
            'dataset': 'v1.dataset.pure.atira.dk',
            'commons': 'v3.commons.pure.atira.dk',
        }

        ET.register_namespace('v1', name_space['dataset'])
        ET.register_namespace('v3', name_space['commons'])

        # Build a tree structure
        self.root = ET.Element("{%s}datasets" % name_space['dataset'])
    
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

            # If the rdm record has a uuid means that it was imported from pure
            if not self._check_uuid(item_metadata):
                continue

            self.report.add(f"{self.report_base} Adding")

            # Adds fields to the created xml element
            self._populate_xml(item_metadata, name_space)

        self._parse_xml()



    def _populate_xml(self, item, name_space):

        # Dataset element
        body = ET.SubElement(self.root, "{%s}dataset" % name_space['dataset'])
        body.set('type', 'dataset')

        # Title
        title = self._sub_element(body, name_space['dataset'], 'title')
        title.text = get_value(item, ['title'])

        # Managing organisation
        organisational_unit = self._sub_element(body, name_space['dataset'], 'managingOrganisation')
        self._add_attribute(item, organisational_unit, 'lookupId', ['managingOrganisationalUnit_externalId'])

        # Persons
        persons = self._sub_element(body, name_space['dataset'], 'persons')
        persons.set('contactPerson', 'true')

        for person_data in item['contributors']:
            # External id
            person_id = self._sub_element(persons, name_space['dataset'], 'person')
            self._add_attribute(person_data, person_id, 'lookupId', ['externalId'])
            # Role
            role = self._sub_element(persons, name_space['dataset'], 'role')
            role.text = get_value(person_data, ['personRole'])
            # Name
            name = self._sub_element(persons, name_space['dataset'], 'name')
            name.text = get_value(person_data, ['name'])

        # Available date
        date = self._sub_element(body, name_space['dataset'], 'availableDate')
        sub_date = self._sub_element(date, name_space['commons'], 'year')
        sub_date.text = get_value(item, ['publication_date'])

        # Publisher
        publisher = self._sub_element(body, name_space['dataset'], 'publisher')    # REVIEW!!!!
        self._sub_element(publisher, name_space['dataset'], 'name')                # Data not in rdm
        self._sub_element(publisher, name_space['dataset'], 'type')                # Data not in rdm

        # Description
        descriptions = self._sub_element(body, name_space['dataset'], 'descriptions')
        description = self._sub_element(descriptions, name_space['dataset'], 'description')
        description.text = get_value(item, ['abstract'])

        # Links
        links = self._sub_element(body, name_space['dataset'], 'links')    # Review
        # Files
        link = self._sub_element(links, name_space['dataset'], 'link')
        link.set('type', 'files')
        link.text = get_value(self.full_item, ['links', 'files'])
        # Self
        link = self._sub_element(links, name_space['dataset'], 'link')
        link.set('type', 'self')
        link.text = get_value(self.full_item, ['links', 'self'])

        # FIELDS THAT ARE NOT IN DATASET XSD - NEEDS REVIEW:
        # language                  ['languages', 0, 'value']
        # organisationalUnits       ['personAssociations' ...]
        # peerReview                ['peerReview']
        # createdDate               ['info', 'createdDate']
        # publicationDate           ['publicationStatuses', 0, 'publicationDate', 'year']
        # publicationStatus         ['publicationStatuses', 0, 'publicationStatuses', 0, 'value']
        # recordType                ['types', 0, 'value']
        # workflow                  ['workflows', 0, 'value']
        # pages                     ['info','pages']
        # volume                    ['info','volume']
        # journalTitle              ['info', 'journalAssociation', 'title', 'value']
        # journalNumber             ['info', 'journalNumber']


    def _parse_xml(self):
        # Wrap it in an ElementTree instance and save as XML
        xml_str = minidom.parseString(ET.tostring(self.root)).toprettyxml(indent="   ")
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

        self.report.add_template(['console'], ['pages', 'page_and_size'], [page, page_size])
        self.report.add('')  # adds empty line

        return json_data
