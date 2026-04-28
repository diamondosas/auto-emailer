import os
import json
import pytest
from core import AutoMailerCore
from datetime import datetime

@pytest.fixture
def test_csv(tmp_path):
    csv_file = tmp_path / "test_data.csv"
    csv_file.write_text("NAME,EMAIL,AMOUNT\nJohn,john@example.com,100\nDoe,doe@example.com,200")
    return str(csv_file)

@pytest.fixture
def limits_file(tmp_path):
    return str(tmp_path / "test_limits.json")

def test_daily_counter(limits_file):
    core = AutoMailerCore(limits_file=limits_file)
    assert core.sent_today == 0
    assert core.can_send() == True

    core.sent_today = 500
    core._save_limits()
    assert core.can_send() == False

    # Reload
    core2 = AutoMailerCore(limits_file=limits_file)
    assert core2.sent_today == 500
    assert core2.can_send() == False

def test_template_parsing(test_csv):
    core = AutoMailerCore()
    template = "Hello $NAME, your amount is $AMOUNT."
    subject = "Invoice for $NAME"

    gen = core.get_msg_generator(test_csv, template, subject)

    # First row
    email, body, subj = next(gen)
    assert email == "john@example.com"
    assert body == "Hello John, your amount is 100."
    assert subj == "Invoice for John"

    # Second row
    email, body, subj = next(gen)
    assert email == "doe@example.com"
    assert body == "Hello Doe, your amount is 200."
    assert subj == "Invoice for Doe"

def test_get_attachments_no_dir():
    core = AutoMailerCore()
    assert core.get_attachments(attach_dir="NON_EXISTENT_DIR") is None

def test_get_attachments_with_list(tmp_path):
    core = AutoMailerCore()
    file1 = tmp_path / "test1.txt"
    file1.write_text("content 1")
    file2 = tmp_path / "test2.txt"
    file2.write_text("content 2")

    result = core.get_attachments(attach_dir=str(tmp_path), confirmed_files=["test1.txt", "test2.txt"])
    assert result is not None
    assert len(result["names"]) == 2
    assert "test1.txt" in result["names"]
    assert b"content 1" in result["contents"]
