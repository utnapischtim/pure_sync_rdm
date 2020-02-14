# TEST TITLE2
self.data += '"title": [{'
self.add_field(item, 'value',                                ['title'])
self.data += '"version": "1", '
self.add_field(item, 'modifiedBy',                           ['info', 'modifiedBy'])
self.add_field(item, 'modifiedDate',                         ['info', 'modifiedDate'])
self.data = self.data[:-2]
self.data += '}], '



    "title": {
      "description": "Record title.",
      "type": "array",
      "items": {
        "type": "object",
        "properties": {
          "value": {
            "description": "",
            "type": "string"
          },
          "version": {
            "description": "",
            "type": "string"
          },
          "modifiedBy": {
            "description": "",
            "type": "string"
          },
          "modifiedDate": {
            "description": "",
            "type": "string"
          }
        }
      }
    },