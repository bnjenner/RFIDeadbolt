import os
import hashlib
import hmac
from pathlib import Path

# Save Hashed Password
def save_password(hash_file: str, password: str):
	hashed = hashlib.sha256(password.encode()).hexdigest()
	hash_file = Path(hash_file)
	hash_file.parent.mkdir(parents=True, exist_ok=True)
	hash_file.write_text(hashed)
	hash_file.chmod(0o600)  # Restrict permissions immediately after writing

# Check Password
def check_password(hash_file: str, user_input: str) -> bool:
	hash_file = Path(hash_file)
	if not hash_file.exists():
	    raise FileNotFoundError(f"No password hash found at {hash_file}.")
	stored_hash = hash_file.read_text().strip()
	input_hash = hashlib.sha256(user_input.encode()).hexdigest()
	return hmac.compare_digest(input_hash, stored_hash)