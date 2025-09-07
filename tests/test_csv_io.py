import pytest
import os
from fishki.csv_io import read_csv, write_csv
from fishki.models import Card

@pytest.fixture
def sample_csv_file(tmp_path):
    csv_content = """de,en,example,tags,notes
der Apfel,apple,"Ich esse einen Apfel.","food,A1",
trinken,to drink,"Ich trinke Wasser.","verb,A1"
"""
    file_path = tmp_path / "sample.csv"
    file_path.write_text(csv_content, encoding="utf-8-sig")
    return str(file_path)

@pytest.fixture
def sample_cards():
    return [
        Card(de="groß", en="big", example="Das Haus ist groß.", tags="adj"),
        Card(de="klein", en="small", example="Die Maus ist klein.", tags="adj,A1"),
    ]

def test_read_csv_success(sample_csv_file):
    data = read_csv(sample_csv_file)
    assert len(data) == 2
    assert data[0]['de'] == 'der Apfel'
    assert data[0]['en'] == 'apple'
    assert data[1]['tags'] == 'verb,A1'

def test_read_csv_missing_columns(tmp_path):
    csv_content = "de,example\nword,example"
    file_path = tmp_path / "missing.csv"
    file_path.write_text(csv_content)
    with pytest.raises(ValueError, match="Missing required columns"):
        read_csv(str(file_path))

def test_write_csv(sample_cards, tmp_path):
    file_path = tmp_path / "output.csv"
    write_csv(sample_cards, path=str(file_path))

    assert os.path.exists(file_path)
    
    with open(file_path, 'r', encoding='utf-8-sig') as f:
        content = f.read()
        assert "de,en,example,tags,notes" in content
        assert "groß,big" in content
        assert "klein,small" in content

def test_write_csv_returns_string(sample_cards):
    csv_string = write_csv(sample_cards)
    assert isinstance(csv_string, str)
    assert "de,en,example,tags,notes" in csv_string
    assert "adj,A1" in csv_string
