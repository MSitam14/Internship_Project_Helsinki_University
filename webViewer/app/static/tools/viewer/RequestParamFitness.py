from enum import Enum
import json
from typing import Optional

class AtomType(Enum):
    sybyl = "Sybyl"
    custom = "Custom"

class RequestParamFitness:

    pdb_name: str
    pdb_content: str

    densities_fold: str = "Fitness_score/data/densities/"
    frequencies_fold: str = "Fitness_score/data/frequencies/"

    run_frequencies: bool
    water_env: bool
    atom_type: AtomType
    environment_size: int
    pocket_num: Optional[str]
    model_num: int
    l_ori: Optional[int]


    def __init__(self, pdb_name: str, pdb_content: str, run_frequencies: bool, water_env: bool, atom_type: AtomType, environment_size: int, pocket_num: Optional[str], model_num: int, l_ori: Optional[int] = None):
        self.pdb_name = pdb_name
        self.pdb_content = pdb_content
        self.run_frequencies = run_frequencies
        self.water_env = water_env
        self.atom_type = atom_type
        self.environment_size = environment_size
        self.pocket_num = pocket_num
        self.model_num = model_num
        self.l_ori = l_ori

        self.frequencies_fold += atom_type.name + "/"
        self.densities_fold += atom_type.name + "/"

    def toJson(self):
        data = {
            "pdb":{
                "name": self.pdb_name,
                "content": self.pdb_content
            },
            "params": {
                "densities_fold": self.densities_fold,
                "frequencies_fold": self.frequencies_fold,
                "run_frequencies": self.run_frequencies,
                "water_env": self.water_env,
                "atom_type": self.atom_type.name,
                "environment_size": self.environment_size,
                "pocket_num": self.pocket_num,
                "model_num": self.model_num,
                "l_ori": self.l_ori
            }

        }

        if data["params"]["pocket_num"] is None or data["params"]["pocket_num"] == 0:
            data["params"]["pocket_num"] = None

        return json.dumps(data)
