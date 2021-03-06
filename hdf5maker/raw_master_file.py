from pathlib import Path

class RawMasterFile:
    def __init__(self, fname, lazy = False):
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

    def data_fname(self, i):
        return Path(f"{self.base}_d{i}_f0_{self.run_id}.raw")

    @property
    def data_file_names(self):
        if self.dict['Detector Type'] == 'Eiger':
            return [self.data_fname(i) for i in range(self.dict['nmod']*2)] 
        return [self.data_fname(i) for i in range(self.dict['nmod'])]

    def _find_number_of_modules(self):
        i = 0
        while self.data_fname(i).exists():
            i += 1
        if self.dict["Detector Type"] == "Eiger":
            assert i % 2 == 0
            self.dict["nmod"] = i//2

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
                "Frame Padding",
                "Total Frames",
                "Dynamic Range",
                "Ten Giga",
                "Quad",
                "Number of Lines read out",
            )
        )

        for field in int_fields.intersection(self.dict.keys()):
            self.dict[field] = int(self.dict[field])

        self.dict["Pixels"] = tuple(int(i) for i in self.dict["Pixels"].strip("[]").split(","))
        if "Rate Corrections" in self.dict:
            self.dict["Rate Corrections"] = self.dict["Rate Corrections"].strip("[]").split(",")
            n = len(self.dict["Rate Corrections"])
            assert self.dict["nmod"] == n, f'nmod from Rate Corrections {n} differs from nmod {self.dict["nmod"]}'

