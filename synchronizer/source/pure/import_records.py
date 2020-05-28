import json
from xml.etree                  import ElementTree as ET
from xml.dom                    import minidom
from source.rdm.requests        import Requests

class ImportRecords:
    def __init__(self):
        self.rdm_requests = Requests()
        self.file_name = "/home/bootcamp/src/pure_sync_rdm/synchronizer/data/temporary_files/test.xml"

    def run_import(self):

        item = self._get_rdm_record_metadata('9zs2w-cj227')
        self._create_xml(item)

        item = self._get_rdm_record_metadata('05qm8-ats84')
        self._create_xml(item)


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
        attributes = [['id', ['contributors', 0, 'uuid']], ['contactPerson', 'true']]
        self._add_attribute(item, persons, attributes)

        person = self._sub_element(persons, ns_dataset, 'person')
        attributes = [['lookupId', ['contributors', 0, 'externalId']]]
        self._add_attribute(item, person, attributes)

        role = self._sub_element(persons, ns_dataset, 'role')
        self._add_text(item, role, ['contributors', 0, 'personRole'])

        start_date = self._sub_element(persons, ns_dataset, 'associationStartDate')    # REVIEW!!!!
        self._add_text(item, start_date, 'not in rdm - ???')

        # Available date
        date = self._sub_element(body, ns_dataset, 'availableDate')

        sub_date = self._sub_element(date, ns_commons, 'year')
        self._add_text(item, sub_date, ['publication_date'])

        # Publisher
        publisher = self._sub_element(body, ns_dataset, 'publisher')    # REVIEW!!!!
        self._sub_element(publisher, ns_dataset, 'name')
        self._sub_element(publisher, ns_dataset, 'type')

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
            return self._get_value(item, path)


    def _get_value(self, item, path: list):
        """ Gets field value from a given path """
        child = item
        count = 0
        # Iterates over the given path
        for i in path:
            # If the child (step in path) exists or is equal to zero
            if i in child or i == 0:
                # Counts if the iteration took place over every path element
                count += 1
                child = child[i]
            else:
                return False

        # If the full path is not available (missing field)
        if len(path) != count:
            return False

        value = str(child)

        # REPLACEMENTS
        value = value.replace('\t', ' ')        # replace \t with ' '
        value = value.replace('\\', '\\\\')     # adds \ before \
        value = value.replace('"', '\\"')       # adds \ before "
        value = value.replace('\n', '')         # removes new lines
        return value


    def _get_rdm_record_metadata(self, recid):
        response = self.rdm_requests.get_metadata('', recid)

        if response.status_code >= 300:
            return False

        # Load response
        return json.loads(response.content)['metadata']