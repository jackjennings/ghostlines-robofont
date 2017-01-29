from ghostlines.storage.lib_storage import LibStorage


class TestLibStorage(object):

    def test_retrieval(arg):
        lib = {"foo": "baz"}
        storage = LibStorage(lib, "foo")

        assert storage.retrieve() == "baz"

    def test_retrieval_when_key_does_not_exist(arg):
        lib = {}
        storage = LibStorage(lib, "foo")

        assert storage.retrieve() == ""

    def test_storage(arg):
        lib = {"foo": "baz"}
        storage = LibStorage(lib, "foo")

        storage.store("bin")

        assert lib["foo"] == "bin"

    def test_storage_when_key_does_not_exist(arg):
        lib = {}
        storage = LibStorage(lib, "foo")

        storage.store("cat")

        assert lib["foo"] == "cat"
