from models import User

def test_users_password():
    user = User(username="maria")
    user.set_password("hello123")
    assert user.check_password("hello123")
    assert not user.check_password("hello124")
    assert user.password_hash != "hello123"