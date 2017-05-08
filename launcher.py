# -*- encoding:utf-8 -*-

import logging
import src.base.host

if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s - %(filename)s[line:%(lineno)d] '
                               '- %(levelname)s: %(message)s')
    service = src.base.host.MainService()
