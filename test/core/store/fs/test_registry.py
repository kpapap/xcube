import os.path
import unittest
from abc import ABC, abstractmethod
from typing import Type, Union

import fsspec
import xarray as xr

from test.s3test import MOTO_SERVER_ENDPOINT_URL
from test.s3test import S3Test
from xcube.core.mldataset import MultiLevelDataset
from xcube.core.new import new_cube
from xcube.core.store import DataDescriptor
from xcube.core.store import DataStoreError
from xcube.core.store import DatasetDescriptor
from xcube.core.store import MultiLevelDatasetDescriptor
from xcube.core.store import MutableDataStore
from xcube.core.store.fs.registry import new_fs_data_store
from xcube.core.store.fs.store import FsDataStore
from xcube.util.temp import new_temp_dir

ROOT_DIR = 'xcube'
DATA_PATH = 'testing/data'


# noinspection PyUnresolvedReferences,PyPep8Naming
class FsDataStoresTestMixin(ABC):
    @abstractmethod
    def create_data_store(self) -> FsDataStore:
        pass

    @classmethod
    def prepare_fs(cls, fs: fsspec.AbstractFileSystem, root: str):
        if fs.isdir(root):
            # print(f'{fs.protocol}: deleting {root}')
            fs.delete(root, recursive=True)

        # print(f'{fs.protocol}: making root {root}')
        fs.mkdirs(root)

        # Write a text file into each subdirectory so
        # we also test that store.get_data_ids() scans
        # recursively.
        dir_path = root
        for subdir_name in DATA_PATH.split('/'):
            dir_path += '/' + subdir_name
            # print(f'{fs.protocol}: making {dir_path}')
            fs.mkdir(dir_path)
            file_path = dir_path + '/README.md'
            # print(f'{fs.protocol}: writing {file_path}')
            with fs.open(file_path, 'w') as fp:
                fp.write('\n')

    def test_mldataset_levels(self):
        data_store = self.create_data_store()
        self.assertMultiLevelDatasetFormatSupported(data_store)

    def test_dataset_zarr(self):
        data_store = self.create_data_store()
        self.assertDatasetFormatSupported(data_store, '.zarr')

    def test_dataset_netcdf(self):
        data_store = self.create_data_store()
        self.assertDatasetFormatSupported(data_store, '.nc')

    # TODO: add assertGeoDataFrameSupport

    def assertMultiLevelDatasetFormatSupported(self,
                                               data_store: MutableDataStore):
        self.assertDatasetSupported(data_store,
                                    '.levels',
                                    'mldataset',
                                    MultiLevelDataset,
                                    MultiLevelDatasetDescriptor)

    def assertDatasetFormatSupported(self,
                                     data_store: MutableDataStore,
                                     filename_ext: str):
        self.assertDatasetSupported(data_store,
                                    filename_ext,
                                    'dataset',
                                    xr.Dataset,
                                    DatasetDescriptor)

    def assertDatasetSupported(
            self,
            data_store: MutableDataStore,
            filename_ext: str,
            expected_data_type_alias: str,
            expected_type: Union[Type[xr.Dataset],
                                 Type[MultiLevelDataset]],
            expected_descriptor_type: Union[Type[DatasetDescriptor],
                                            Type[MultiLevelDatasetDescriptor]]
    ):
        """
        Call all DataStore operations to ensure data of type
        xr.Dataset//MultiLevelDataset is supported by *data_store*.

        :param data_store: The filesystem data store instance.
        :param filename_ext: Filename extension that identifies
            a supported dataset format.
        :param expected_data_type_alias: The expected data type alias.
        :param expected_type: The expected data type.
        :param expected_descriptor_type: The expected data descriptor type.
        """

        data_id = f'{DATA_PATH}/ds{filename_ext}'

        self.assertIsInstance(data_store, MutableDataStore)

        self.assertEqual({'dataset', 'mldataset', 'geodataframe'},
                         set(data_store.get_data_types()))

        with self.assertRaises(DataStoreError):
            data_store.get_data_types_for_data(data_id)
        self.assertEqual(False, data_store.has_data(data_id))
        self.assertEqual([], list(data_store.get_data_ids()))

        data = new_cube(variables=dict(A=8, B=9))
        data_store.write_data(data, data_id)
        self.assertEqual({expected_data_type_alias},
                         set(data_store.get_data_types_for_data(data_id)))
        self.assertEqual(True, data_store.has_data(data_id))
        self.assertEqual([data_id], list(data_store.get_data_ids()))

        data_descriptors = list(data_store.search_data())
        self.assertEqual(1, len(data_descriptors))
        self.assertIsInstance(data_descriptors[0], DataDescriptor)
        self.assertIsInstance(data_descriptors[0], expected_descriptor_type)

        data = data_store.open_data(data_id)
        self.assertIsInstance(data, expected_type)

        try:
            data_store.delete_data(data_id)
        except PermissionError:  # Typically occurs on win32 due to fsspec
            return
        with self.assertRaises(DataStoreError):
            data_store.get_data_types_for_data(data_id)
        self.assertEqual(False, data_store.has_data(data_id))
        self.assertEqual([], list(data_store.get_data_ids()))


class FileFsDataStoresTest(FsDataStoresTestMixin, unittest.TestCase):

    def create_data_store(self) -> FsDataStore:
        root = os.path.join(new_temp_dir(prefix='xcube'), ROOT_DIR)
        self.prepare_fs(fsspec.filesystem('file'), root)
        return new_fs_data_store('file', root=root, max_depth=3)


class MemoryFsDataStoresTest(FsDataStoresTestMixin, unittest.TestCase):

    def create_data_store(self) -> FsDataStore:
        root = ROOT_DIR
        self.prepare_fs(fsspec.filesystem('memory'), root)
        return new_fs_data_store('memory', root=root, max_depth=3)


class S3FsDataStoresTest(FsDataStoresTestMixin, S3Test):

    def create_data_store(self) -> FsDataStore:
        root = ROOT_DIR
        fs_params = dict(
            anon=False,
            client_kwargs=dict(
                endpoint_url=MOTO_SERVER_ENDPOINT_URL,
            )
        )
        self.prepare_fs(fsspec.filesystem('s3', **fs_params), root)
        return new_fs_data_store('s3',
                                 root=root,
                                 max_depth=3,
                                 fs_params=fs_params)