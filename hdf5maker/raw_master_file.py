from pathlib import Path
import re
import numpy as np

class RawMasterFile:
    def __init__(self, fname, lazy=False):
        self.dict = {}
        self.fname = Path(fname)
        if not lazy:
            self._parse_fname()
            self._read()
            self._parse_values()

    def __getitem__(self, key):
        return self.dict[key]

    def _parse_fname(self):
        try:
            base, _, run_id = self.fname.stem.rsplit("_", 2)
            self.base = self.fname.parent / base
            self.run_id = int(run_id)
        except:
            raise ValueError(f"Could not parse master file name: {self.fname}")

    def data_fname(self, i, findex=0):
        return Path(f"{self.base}_d{i}_f{findex}_{self.run_id}.raw")

    @property
    def data_file_names(self):
        if self.dict["Detector Type"] == "Eiger":
            return [self.data_fname(i) for i in range(self.dict["nmod"] * 2)]
        return [self.data_fname(i) for i in range(self.dict["nmod"])]

    def _find_number_of_modules(self):
        i = 0
        while self.data_fname(i).exists():
            i += 1
        if self.dict["Detector Type"] == "Eiger":
            assert i % 2 == 0
            self.dict["nmod"] = i // 2
        else:
            self.dict["nmod"] = i

    def _read(self):
        """
        Read master file and return contents as a dict
        """
        self.dict = {}

        with open(self.fname) as f:
            lines = f.readlines()

        it = iter(lines)

        for line in it:
            if line.startswith("#Frame"):
                break
            if line == "\n":
                continue
            if line.startswith("Scan Parameters"):
                while not line.endswith("]\n"):
                    line += next(it)

            field, value = line.split(":", 1)
            self.dict[field.strip(" ")] = value.strip(" \n")

        frame_header = {}
        for line in it:
            field, value = line.split(":", 1)
            frame_header[field.strip()] = value.strip(" \n")

        self.dict["Frame Header"] = frame_header
        self._find_number_of_modules()
        if self.dict["Version"] != "6.2":
            raise ValueError("This converter only supports raw files of v6.2")
        # return self._parse_values()

    def _parse_values(self):
        int_fields = set(
            (
                "Max Frames Per File",
                "Image Size",
                "Frame Padding",
                "Total Frames",
                "Dynamic Range",
                "Ten Giga",
                "Quad",
                "Number of Lines read out",
            )
        )

        for field in int_fields.intersection(self.dict.keys()):
            self.dict[field] = int(self.dict[field].split()[0])

        self.dict["Pixels"] = tuple(
            int(i) for i in self.dict["Pixels"].strip("[]").split(",")
        )

        if self.dict['Detector Type'] == 'Mythen3':
            self.dict["Exptime1"] = self.to_nanoseconds(self.dict["Exptime1"])
            self.dict["Exptime2"] = self.to_nanoseconds(self.dict["Exptime2"])
            self.dict["Exptime3"] = self.to_nanoseconds(self.dict["Exptime3"])
        else:
            self.dict["Exptime"] = self.to_nanoseconds(self.dict["Exptime"])
        
        if self.dict['Detector Type'] == 'Eiger':
            self.dict["SubExptime"] = self.to_nanoseconds(self.dict["SubExptime"])
            self.dict["SubPeriod"] = self.to_nanoseconds(self.dict["SubPeriod"])

        self.dict["Period"] = self.to_nanoseconds(self.dict["Period"])

        if "Rate Corrections" in self.dict:
            self.dict["Rate Corrections"] = (
                self.dict["Rate Corrections"].strip("[]").split(",")
            )
            n = len(self.dict["Rate Corrections"])
            assert (
                self.dict["nmod"] == n
            ), f'nmod from Rate Corrections {n} differs from nmod {self.dict["nmod"]}'

    @staticmethod
    def to_nanoseconds(t):
        nanoseconds = {"s": 1000 * 1000 * 1000, "ms": 1000 * 1000, "us": 1000, "ns": 1}
        try:
            value = re.match(r"(\d+(?:\.\d+)?)", t).group()
            unit = t[len(value) :]
            value = int(float(value) * nanoseconds[unit])
            value = np.timedelta64(value, 'ns')
        except:
            raise ValueError(f"Could not convert: {t} to nanoseconds")
        return value