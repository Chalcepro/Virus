import unittest

import torch

from utils import get_device


class DeviceSelectionTests(unittest.TestCase):
    def test_get_device_returns_supported_device(self):
        device = get_device()
        self.assertIsInstance(device, torch.device)
        self.assertIn(device.type, {"cpu", "cuda", "mps"})


if __name__ == "__main__":
    unittest.main()
