from functools import lru_cache

from app.pipeline import process
from app.sources import load_sample


@lru_cache(maxsize=2)
def preview(sample):
    return process(load_sample(sample))
