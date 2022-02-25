import os
import pathlib
import shutil as util
import tempfile as temp


class Connector:
    def __init__(self):
        # ok: filesystem-access
        self.base_name = os.path.basename('/foo/bar/baz')

        # ruleid: filesystem-access
        with open('foobar') as f:
            f.read()
        # ruleid: filesystem-access
        with open('foobar', 'w') as f:
            f.write('foobar')

        # ruleid: filesystem-access
        pathlib.Path('foobar')
        # ruleid: filesystem-access
        util.rmtree('foobar')
        # ruleid: filesystem-access
        temp.mkdtemp()


if __name__ == '__main__':
    # ok: filesystem-access
    with open('foobar') as f:
        f.read()

    # ok: filesystem-access
    with open('foobar', 'w') as f:
        f.write('foobar')
