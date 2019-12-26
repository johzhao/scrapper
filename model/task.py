import json


class Task:

    @classmethod
    def from_string(cls, content: str) -> 'Task':
        data = json.loads(content)
        return Task(data.get('url'), data.get('type'), data.get('reference'))

    def __init__(self, url: str, type_: str, reference: str):
        self.url = url
        self.type_ = type_
        self.reference = reference

    def __str__(self):
        data = {
            'url': self.url,
            'type': self.type_,
            'reference': self.reference,
        }
        return json.dumps(data, ensure_ascii=False, sort_keys=True)
