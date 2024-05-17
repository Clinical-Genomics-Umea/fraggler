import subprocess
import pytest
import pandas as pd


def run_command(command):
    return subprocess.run(
        command, check=True, capture_output=True, text=True, shell=True
    )


def test_cli_help():
    result = run_command("fraggler --help")
    assert result.returncode == 0


def test_import_error():
    with pytest.raises(subprocess.CalledProcessError) as e:
        result = run_command("python3 error.py")
        assert result.returncode != 0


def test_not_working():
    with pytest.raises(subprocess.CalledProcessError) as e:
        result = run_command("fraggler area asdad")
        assert result.returncode != 0


def test_wrong_ladder():
    with pytest.raises(subprocess.CalledProcessError) as e:
        result = run_command("fraggler area demo/multiplex.fsa TEST_MULTI WRONG")
        assert result.returncode != 0


def test_cli_working():
    result = run_command("fraggler area demo/multiplex.fsa TEST_MULTI LIZ")
    assert result.returncode == 0
    text = "Running fraggler with following parameters:\n        In path: demo/multiplex.fsa\n        Out folder: TEST_MULTI\n        Ladder: LIZ\n        Peak model: gauss\n        Min ratio: 0.2\n        Min height: 30\n        Cutoff: 175\n        Trace channel: DATA1\n        Peak Height: 500\n        Custom Peaks: None\n        Out format: excel\n        Size standard channel: None\n        Distance between assays: 15\n"
    assert text in result.stderr

    peaks = "Number of assays found: 4\n        Number of peaks found: 10\n"
    assert peaks in result.stderr

    wrong_peaks = "Number of assays found: 5\n        Number of peaks found: 10\n"
    assert wrong_peaks not in result.stderr


def test_area_table():
    df = pd.read_excel("TEST_MULTI/areatable_multiplex.fsa.xlsx")
    quotiens = [0.57, 0.57, 2.15, 2.15, 0.6, 0.6, 2.3, 2.3, 2.3, 2.3]

    assert df.quotient.round(2).to_list() == quotiens
