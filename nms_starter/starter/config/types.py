class ServerType:
    _physical_types = set()
    _logical_types = set()

    def add_physical_type(self, server_type):
        self._physical_types.add(server_type)

    def add_logical_type(self, server_type):
        self._logical_types.add(server_type)

    def add_types(self, physical_types, logical_types):
        self._physical_types.update(physical_types)
        self._logical_types.update(logical_types)

    def is_physical_type(self, server_type):
        return server_type in self._physical_types or server_type == 'x86_server' or server_type == 'physical'

    def is_logical_type(self, server_type):
        return server_type in self._logical_types

    def __repr__(self):
        return 'physical_type:{}, \nlogical_type: {}'.format(self._physical_types, self._logical_types)


def init_types():
    from dao.nms_redis import get_types
    r = get_types()
    server_type_judgment.add_types(*r)


server_type_judgment = ServerType()
