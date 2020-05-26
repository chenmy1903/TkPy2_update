# -*- coding: UTF-8 -*-
# -*- coding: UTF-8 -*-
from pickleshare import PickleShareDB
from typing import Union

config_path = '~/.tkpy2/update'


class tkpy_file(object):
    def __init__(self, file_name: str, config: Union[list, dict], path: str = config_path):
        object.__init__(self)
        self.file_name: str = file_name
        self.config: Union[list, dict] = config
        self.path: str = path
        self.db = PickleShareDB(self.path)
        if file_name not in self.db:
            self.db[file_name] = config

    def read(self, config=None):
        """读文件"""
        if config:
            return self.db[self.file_name][config]
        return self.db[self.file_name]

    def write(self, config):
        """写文件"""
        self.db[self.file_name] = config

    def add(self, key, value):
        """添加新值"""
        new = self.db[self.file_name]
        if value:
            new[key] = value
            self.db[self.file_name] = new

    def delete(self, key):
        del self.db[self.file_name][key]

    def __delitem__(self, key):
        """删除项"""
        self.delete(key)

    def clear(self):
        """删除文件"""
        del self.db[self.file_name]

    def reset(self):
        self.clear()
        self.__init__(self.file_name, self.config, self.path)


def read_tkpy_file(file_name: str, path: str = config_path):
    db = PickleShareDB(path)
    return db[file_name]


if __name__ == "__main__":
    f = tkpy_file('config', {})
    f.add('test', 'This a test text.1')
    f.add('test3', '123')
    print(f.read())
    f.reset()
    print(f.read())
    f.clear()
