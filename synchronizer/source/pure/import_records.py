import json
from xml.etree                  import ElementTree as ET
from xml.dom                    import minidom
from source.rdm.requests        import Requests

class ImportRecords:
    def __init__(self):
        self.rdm_requests = Requests()
        self.file_name = "/home/bootcamp/src/pure_sync_rdm/synchronizer/data/temporary_files/test.xml"

    def run_import(self):
        
        item = self._get_rdm_record_metadata()
        
        self._create_xml(item)


    def _create_xml(self, item):

        ns_dataset = 'v1.dataset.pure.atira.dk'
        ns_commons = 'v3.commons.pure.atira.dk'

        ET.register_namespace('v1',ns_dataset)
        ET.register_namespace('v3',ns_commons)
        # Build a tree structure
        root = ET.Element("{%s}datasets" % ns_dataset)

        body = ET.SubElement(root, "{%s}dataset" % ns_dataset, 
                                id=item['uuid'],
                                type='dataset')

        self._add_sub_element(body, ns_dataset, 'title', [], item['title'])

        self._add_sub_element(body, ns_dataset, 'managingOrganisation', [['lookupId', item['managingOrganisationalUnit_externalId']]])

        persons = self._add_sub_element(body, ns_dataset, 'persons', [['id', item['contributors'][0]['uuid']], ['contactPerson', 'true']])

        self._add_sub_element(persons, ns_dataset, 'person', [['lookupId', item['contributors'][0]['externalId']]])
        self._add_sub_element(persons, ns_dataset, 'role', [], item['contributors'][0]['personRole'])
        self._add_sub_element(persons, ns_dataset, 'associationStartDate', [], '2002-02-02')    # REVIEW!!!!

        date = self._add_sub_element(body, ns_dataset, 'availableDate')
        self._add_sub_element(date, ns_commons, 'year', [], item['publication_date'])

        publisher = self._add_sub_element(body, ns_dataset, 'publisher', [['lookupId', "none"]])    # REVIEW!!!!
        self._add_sub_element(publisher, ns_dataset, 'name', [], 'none')
        self._add_sub_element(publisher, ns_dataset, 'type', [], 'none')

        # Wrap it in an ElementTree instance and save as XML
        xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="   ")
        open(self.file_name, "w").write(xml_str)


    def _add_sub_element(self, element: object, namespace: str, sub_element_name: str, attributes = [], value = ''):

        # value = self._get_value(self.item, path)

        sub_element = ET.SubElement(element, "{%s}%s" % (namespace, sub_element_name))

        for attribute in attributes:
            if attribute[1]:
                sub_element.set(attribute[0], attribute[1])

        if value:
            sub_element.text = value

        return sub_element


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


    def _get_rdm_record_metadata(self):
        # response = self.rdm_requests.get_metadata('', '9zs2w-cj227')
        response = self.rdm_requests.get_metadata('', '05qm8-ats84')

        if response.status_code >= 300:
            return False

        # Load response
        return json.loads(response.content)['metadata']

