from fraggler.utils.fsa_file import FsaFile
import numpy as np


def test_fsa_file():
    fsa = FsaFile(file="demo/multiplex.fsa", ladder="LIZ")

    assert fsa.file.name == "multiplex.fsa"
    assert fsa.ladder == "LIZ"
    assert fsa.trace_channel == "DATA1"
    assert not fsa.normalize
    assert fsa.min_interpeak_distance is not None
    assert fsa.min_height is not None
    assert fsa.max_ladder_trace_distance is not None


def test_normalization():
    fsa_norm = FsaFile(file="demo/multiplex.fsa", ladder="LIZ", normalize=True)
    fsa_non_norm = FsaFile(
        file="demo/multiplex.fsa", ladder="LIZ", normalize=False
    )

    assert np.any(fsa_norm.trace != fsa_non_norm.trace)
