import logging

import requests

logger = logging.getLogger(__name__)
logger.addHandler(logging.NullHandler())


class Downloader:

    def __init__(self, headers: dict):
        self.session = requests.session()
        self.session.headers.update(headers)

    def download_url(self, url: str, referer: str) -> str:
        logger.info(f'Prepare to download the url {url} with the reference {referer}')
        if referer:
            self.session.headers['Referer'] = referer
        else:
            self.session.headers.pop('Referer', None)

        response = self.session.get(url)
        if response.status_code != 200:
            raise Exception(f'The status code for url {url} was {response.status_code}')

        self.session.cookies = response.cookies
        logger.info(f'Succeed download the url {url}')
        return response.text
