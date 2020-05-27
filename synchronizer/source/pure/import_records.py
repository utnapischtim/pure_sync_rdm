import json
from xml.etree                  import ElementTree as ET
from xml.dom                    import minidom
from source.rdm.requests        import Requests

class ImportRecords:
    def __init__(self):
        self.rdm_requests = Requests()
        self.file_name = "/home/bootcamp/src/pure_sync_rdm/synchronizer/data/temporary_files/test.xml"

    def run_import(self):
        
        rdm_data = self._get_rdm_record_metadata()
        
        self._create_xml(rdm_data)
        # self._create_xml_test()




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

        ET.SubElement(body, "{%s}title" % ns_dataset).text = item['title']

        # ET.SubElement(body, "{%s}managingOrganisation" % ns_dataset, lookupId=item['managingOrganisationalUnit_externalId'])

        # persons = ET.SubElement(body, "{%s}persons" % ns_dataset, 
        #                                 id=item['contributors'][0]['uuid'],    # REVIEW!!!!
        #                                 contactPerson='true')
        # ET.SubElement(persons, "{%s}person" % ns_dataset, lookupId=item['contributors'][0]['externalId'])
        # ET.SubElement(persons, "{%s}role" % ns_dataset).text = item['contributors'][0]['personRole']
        # ET.SubElement(persons, "{%s}associationStartDate" % ns_dataset).text = '2002-02-02'    # REVIEW!!!!

        # date = ET.SubElement(body, "{%s}availableDate" % ns_dataset)
        # ET.SubElement(date, "{%s}year" % ns_commons).text = item['publication_date']

        # publisher = ET.SubElement(body, "{%s}publisher" % ns_dataset, 
        #                                 lookupId="none")    # REVIEW!!!!
        # ET.SubElement(publisher, "{%s}name" % ns_dataset).text = 'none'
        # ET.SubElement(publisher, "{%s}type" % ns_dataset).text = 'none'

        # Wrap it in an ElementTree instance and save as XML
        xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="   ")
        open(self.file_name, "w").write(xml_str)


    def _add_sub_element(self, element: object, namespace: str, sub_element_name: str, attributes = {}, value = ''):

        ET.SubElement(element, "{%s}%s" % (namespace, sub_element_name))


    def _create_xml_test(self):
        
        ns_dataset = 'v1.dataset.pure.atira.dk'
        ns_commons = 'v3.commons.pure.atira.dk'

        ET.register_namespace('v1',ns_dataset)
        ET.register_namespace('v3',ns_commons)

        # Build a tree structure
        root = ET.Element("{%s}datasets" % ns_dataset)

        body = ET.SubElement(root, "{%s}dataset" % ns_dataset, 
                                id="50cc689b-95d9-4d2d-b848-25f52eb01a84",
                                type='dataset')

        ET.SubElement(body, "{%s}title" % ns_dataset).text = 'testtitle'
        ET.SubElement(body, "{%s}managingOrganisation" % ns_dataset, lookupId='20753')

        persons = ET.SubElement(body, "{%s}persons" % ns_dataset, 
                                        id='c0a3f804-fb58-4bbb-9ee4-0a3f7276c0c8',
                                        contactPerson='true')
        ET.SubElement(persons, "{%s}person" % ns_dataset, lookupId='24990')
        ET.SubElement(persons, "{%s}role" % ns_dataset).text = 'datacollector'
        ET.SubElement(persons, "{%s}associationStartDate" % ns_dataset).text = '2002-02-02'

        date = ET.SubElement(body, "{%s}availableDate" % ns_dataset)
        ET.SubElement(date, "{%s}year" % ns_commons).text = '2013'

        publisher = ET.SubElement(body, "{%s}publisher" % ns_dataset, 
                                        lookupId="45d22915-6545-4428-896a-8b8046191d5d")
        ET.SubElement(publisher, "{%s}name" % ns_dataset).text = 'New publisher'
        ET.SubElement(publisher, "{%s}type" % ns_dataset).text = 'publisher'

        # Wrap it in an ElementTree instance and save as XML
        xml_str = minidom.parseString(ET.tostring(root)).toprettyxml(indent="   ")
        open(self.file_name, "w").write(xml_str)



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