from src.utils import generate_password
import string

def test_generate_password_length():
    password = generate_password(length=20)
    assert len(password) == 20

def test_generate_password_complexity():
    password = generate_password()
    assert any(c.isupper() for c in password)
    assert any(c.islower() for c in password)
    assert any(c.isdigit() for c in password)
    assert any(c in string.punctuation for c in password)

def test_generate_password_no_special():
    password = generate_password(length=12, use_special=False)
    assert len(password) == 12
    assert all(c in (string.ascii_letters + string.digits) for c in password)