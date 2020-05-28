import json
from xml.etree                  import ElementTree as ET
from xml.dom                    import minidom
from source.rdm.requests        import Requests
from source.general_functions   import get_value

class ImportRecords:
    def __init__(self):
        self.rdm_requests = Requests()
        self.file_name = "/home/bootcamp/src/pure_sync_rdm/synchronizer/data/temporary_files/test.xml"

    def run_import(self):

        item = self._get_rdm_record_metadata('t0s1d-2x040')
        if not item:
            print('\nNo metadata..\n')
            return
        self._create_xml(item)

        # item = self._get_rdm_record_metadata('05qm8-ats84')
        # self._create_xml(item)


    def _create_xml(self, item):

        ns_dataset = 'v1.dataset.pure.atira.dk'     # Name Space dataset
        ns_commons = 'v3.commons.pure.atira.dk'     # Name Space commons

        ET.register_namespace('v1',ns_dataset)
        ET.register_namespace('v3',ns_commons)
        # Build a tree structure
        root = ET.Element("{%s}datasets" % ns_dataset)

        body = ET.SubElement(root, "{%s}dataset" % ns_dataset, 
                                id=item['uuid'],
                                type='dataset')
        # Title
        title = self._sub_element(body, ns_dataset, 'title')
        self._add_text(item, title, ['title'])

        # Managing organisation
        organisational_unit = self._sub_element(body, ns_dataset, 'managingOrganisation')
        attributes = [['lookupId', ['managingOrganisationalUnit_externalId']]]
        self._add_attribute(item, organisational_unit, attributes)

        # Persons
        persons = self._sub_element(body, ns_dataset, 'persons')
        attributes = [['contactPerson', 'true']]
        self._add_attribute(item, persons, attributes)

        for person_data in item['contributors']:
            person_id = self._sub_element(persons, ns_dataset, 'person')
            attributes = [['lookupId', ['externalId']]]
            self._add_attribute(person_data, person_id, attributes)

            role = self._sub_element(persons, ns_dataset, 'role')
            self._add_text(person_data, role, ['personRole'])

            role = self._sub_element(persons, ns_dataset, 'name')
            self._add_text(person_data, role, ['name'])

            start_date = self._sub_element(persons, ns_dataset, 'associationStartDate')    # REVIEW!!!!
            self._add_text(person_data, start_date, 'not in rdm - ???')

        # Available date
        date = self._sub_element(body, ns_dataset, 'availableDate')

        sub_date = self._sub_element(date, ns_commons, 'year')
        self._add_text(item, sub_date, ['publication_date'])

        # Publisher
        publisher = self._sub_element(body, ns_dataset, 'publisher')    # REVIEW!!!!
        self._sub_element(publisher, ns_dataset, 'name')
        self._sub_element(publisher, ns_dataset, 'type')

        #       ---         ---         ---
        # pure                          -   rdm
        # descriptions, description     -   abstract
        # physicalDatas, physicalData ??
        # links, link
        #       ---         ---         ---

        # Wrap it in an ElementTree instance and save as XML
        xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="   ")
        open(self.file_name, "w").write(xml_str)


    def _sub_element(self, element: object, namespace: str, sub_element_name: str):
        return ET.SubElement(element, "{%s}%s" % (namespace, sub_element_name))


    def _add_attribute(self, item, sub_element, attributes):
        for attribute in attributes:
            value = self._check_and_get_value(item, attribute[1])
            if value:
                sub_element.set(attribute[0], value)


    def _add_text(self, item, sub_element, path):
        sub_element.text = self._check_and_get_value(item, path)


    def _check_and_get_value(self, item, path):
        
        if type(path) == str:
            return path
        else:
            return get_value(item, path)


    def _get_rdm_record_metadata(self, recid):
        response = self.rdm_requests.get_metadata('', recid)

        if response.status_code >= 300:
            return False

        # Load response
        return json.loads(response.content)['metadata']