import pathlib
import unittest

paths = {"dummy_fpga.xml": pathlib.Path(__file__).parent.parent.joinpath("fpga_models", "dummy_fpga.xml"),
         "mmcme2_base_attributes.xml": pathlib.Path(__file__).parent.parent.joinpath("primitives", "mmcme2_base_attributes.xml")}


# This test case checks if all necessary files are available
class PathTest(unittest.TestCase):
    def setUp(self) -> None:
        self.file_dict = {key: open(value) for key,value in paths.items()}

    def tearDown(self) -> None:
        for key in self.file_dict:
            self.file_dict[key].close()

    def test_paths(self):
        for key in self.file_dict:
            self.assertTrue(self.file_dict[key].readable())