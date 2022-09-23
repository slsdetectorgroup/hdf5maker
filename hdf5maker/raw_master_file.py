from pathlib import Path
import re
import numpy as np
import json

class RawMasterFile:
    def __init__(self, fname, lazy=False, fastquad=False):
        self.json = False
        self.dict = {}
        self.fname = Path(fname)
        self.fastquad = fastquad
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
            files = [self.data_fname(i) for i in range(self.dict["nmod"] * 2)]
            if self.fastquad:
                return files[0::2]
            else:
                 return files
        
        return [self.data_fname(i) for i in range(self.dict["nmod"])]

    def _find_number_of_modules(self):
        """Guess the number of modules from the files on disk"""

        #TODO! Refactor special case!
        if self.fastquad:
            self.dict["nmod"] = 2
        else:
            i = 0
            while self.data_fname(i).exists():
                i += 1
            if self.dict["Detector Type"] == "Eiger":
                assert i % 2 == 0, f"i={i}"
                self.dict["nmod"] = i // 2
            else:
                self.dict["nmod"] = i

    def _read(self):
        """
        Read master file and return contents as a dict
        """
        self.dict = {}
        if self.fname.suffix == ".json":
            with open(self.fname) as f:
                self.dict = json.load(f)
            self.json = True
            return

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
        ver = float(self.dict["Version"])
        if ver < 6.2:
            raise ValueError(f"File version {ver}, This converter only supports raw files of >v6.2")
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
                "Number of UDP Interfaces"
            )
        )
        time_fields = set((
            "Exptime", 
            "Exptime1", 
            "Exptime2",
            "Exptime3",
            "GateDelay1",
            "GateDelay2",
            "GateDelay3",
            "SubExptime",#Eiger
            "SubPeriod", #Eiger
            "Period"

        ))

        #some fields might not exist for all detectors 
        #hence using intersection
        for field in time_fields.intersection(self.dict.keys()):
            self.dict[field] = self.to_nanoseconds(self.dict[field])

        #Parse bothx .json and .raw master files
        if self.json:
            self.dict['Image Size'] = self.dict["Image Size in bytes"]
            self.dict['Pixels'] = (self.dict['Pixels']['x'], self.dict['Pixels']['y'])
            self.dict['nmod'] = self.dict['Geometry']['x']*self.dict['Geometry']['y']
        else:
            self.dict["Version"] = float(self.dict["Version"])
            for field in int_fields.intersection(self.dict.keys()):
                self.dict[field] = int(self.dict[field].split()[0])
            self.dict["Pixels"] = tuple(
                int(i) for i in self.dict["Pixels"].strip("[]").split(",")
            )

        if "Rate Corrections" in self.dict:
            self.dict["Rate Corrections"] = (
                self.dict["Rate Corrections"].strip("[]").split(",")
            )
            n = len(self.dict["Rate Corrections"])
            assert (
                self.dict["nmod"] == n
            ), f'nmod from Rate Corrections {n} differs from nmod {self.dict["nmod"]}'

        #Parse threshold for Mythen3 (if needed)
        if "Threshold Energies" in self.dict.keys():
            th = self.dict["Threshold Energies"]
            if isinstance(th, str):
                th = [int(i) for i in th.strip('[]').split(',')]
                self.dict["Threshold Energies"] = th

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