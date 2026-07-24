### converting fasta to join format

import json
from Bio import SeqIO
import os


def fasta_to_json(fasta_file, output_dir, input_name="AF3Input_",chain_id="A"):
    """
    Converts each sequence in a FASTA file into a separate AlphaFold 3 JSON input file.

    Args:
        fasta_file (str): Path to the input FASTA file.
        output_dir (str): Directory where the JSON files will be saved.
        input_name (str): Prefix for the 'name' field in JSON.
    """
    os.makedirs(output_dir, exist_ok=True)

    for record in SeqIO.parse(fasta_file, "fasta"):
        # Build the JSON structure
        af3_json = {
            "name": f"{input_name}{record.id}",
            "modelSeeds": [1],
            "sequences": [
                {
                    "protein": {
                        "id": chain_id,
                        "sequence": str(record.seq)
                    }
                }
            ],
            "dialect": "alphafold3",
            "version": 1
        }

        # File name: <record.id>.json
        output_filename = f"{record.id}.json"
        output_path = os.path.join(output_dir, output_filename)

        # Write JSON to file
        with open(output_path, "w") as f:
            json.dump(af3_json, f, indent=4)

        print(f"✅ Saved {output_filename}")
# Example Usage
fasta_to_json("/home/dreano/Predicted_GPCRs/Human/Sequence/Ensembl/human_gpcr_cleaned.fasta",
              "/home/dreano/Predicted_GPCRs/Human/Sequence/Ensembl/cleaned_json/",
              "Human GPCRs ")