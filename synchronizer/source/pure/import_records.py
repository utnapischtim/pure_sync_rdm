import json
from xml.etree                  import ElementTree as ET
from xml.dom                    import minidom
from source.rdm.requests        import Requests

class ImportRecords:
    def __init__(self):
        self.rdm_requests = Requests()

    def run_import(self):
        
        self._create_xml()

        # rdm_data = self._get_rdm_record_metadata()

        # for item in rdm_data:
        #     print(f'{item}: {rdm_data[item]}')



    def _create_xml(self):
    
        file_name = "/home/bootcamp/src/pure_sync_rdm/synchronizer/source/pure/test.xml"
        
        ns_dataset = 'v1.dataset.pure.atira.dk'
        ns_commons = 'v3.commons.pure.atira.dk'

        ET.register_namespace('v1',ns_dataset)
        ET.register_namespace('v3',ns_commons)

        # Build a tree structure
        root = ET.Element("{v1.dataset.pure.atira.dk}datasets")

        body = ET.SubElement(root, "{v1.dataset.pure.atira.dk}dataset", 
                                id="50cc689b-95d9-4d2d-b848-25f52eb01a84",
                                type='dataset')

        ET.SubElement(body, "{v1.dataset.pure.atira.dk}title").text = 'testtitle'
        ET.SubElement(body, "{v1.dataset.pure.atira.dk}managingOrganisation", lookupId='20753')

        persons = ET.SubElement(body, "{v1.dataset.pure.atira.dk}persons", 
                                        id='c0a3f804-fb58-4bbb-9ee4-0a3f7276c0c8',
                                        contactPerson='true')
        ET.SubElement(persons, "{v1.dataset.pure.atira.dk}person", lookupId='24990')
        ET.SubElement(persons, "{v1.dataset.pure.atira.dk}role").text = 'datacollector'
        ET.SubElement(persons, "{v1.dataset.pure.atira.dk}associationStartDate").text = '2002-02-02'

        date = ET.SubElement(body, "{v1.dataset.pure.atira.dk}availableDate")
        ET.SubElement(date, "{v3.commons.pure.atira.dk}year").text = '2013'

        publisher = ET.SubElement(body, "{v1.dataset.pure.atira.dk}publisher", 
                                        lookupId="45d22915-6545-4428-896a-8b8046191d5d")
        ET.SubElement(publisher, "{v1.dataset.pure.atira.dk}name").text = 'New publisher'
        ET.SubElement(publisher, "{v1.dataset.pure.atira.dk}type").text = 'publisher'

        # Wrap it in an ElementTree instance and save as XML
        xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="   ")
        open(file_name, "w").write(xml_str)



    def _get_rdm_record_metadata(self):
        response = self.rdm_requests.get_metadata('', '05qm8-ats84')
        print(response)

        if response.status_code >= 300:
            return False

        # Load response
        return json.loads(response.content)['metadata']




# root = ET.Element("root")
# doc = ET.SubElement(root, "doc")

# ET.SubElement(doc, "field1", name="blah").text = "some value1"
# ET.SubElement(doc, "field2", name="asdfasd").text = "some vlaue2"

# tree = ET.ElementTree(root)
# tree.write("/home/bootcamp/src/pure_sync_rdm/synchronizer/tests/test.xml")