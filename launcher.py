# -*- encoding:utf-8 -*-

import logging
import host

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(filename)s[line:%(lineno)d] '
                               '- %(levelname)s: %(message)s')
    service = host.MainService()
