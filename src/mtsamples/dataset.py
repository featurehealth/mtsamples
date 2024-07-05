import json
import pkg_resources

__all__ = ["load_dataset"]

def load_dataset(dataset_path=None):
    if dataset_path is None:
        dataset_path = pkg_resources.resource_filename(__name__, 'data/mtsamples.json')
    with open(dataset_path, 'r') as f:
        dataset = json.load(f)
    return dataset
