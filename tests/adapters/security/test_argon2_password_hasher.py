from recomendacoes_api.adapters.security.argon2_password_hasher import Argon2PasswordHasher


def test_hash_does_not_expose_the_password():
    assert "secret123" not in Argon2PasswordHasher().hash("secret123")


def test_verify_accepts_the_original_password():
    hasher = Argon2PasswordHasher()

    assert hasher.verify("secret123", hasher.hash("secret123")) is True


def test_verify_rejects_a_different_password():
    hasher = Argon2PasswordHasher()

    assert hasher.verify("other-pass", hasher.hash("secret123")) is False
