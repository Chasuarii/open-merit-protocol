import json
import base64
from typing import Dict, Any
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey, Ed25519PublicKey
from cryptography.hazmat.primitives import serialization

def generate_builder_keypair() -> Dict[str, str]:
    """Generates a self-sovereign Ed25519 keypair for a builder or sandbox node."""
    priv = Ed25519PrivateKey.generate()
    pub = priv.public_key()
    return {
        "private_key": base64.b64encode(
            priv.private_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PrivateFormat.Raw,
                encryption_algorithm=serialization.NoEncryption()
            )
        ).decode("utf-8"),
        "public_key": base64.b64encode(
            pub.public_bytes(
                encoding=serialization.Encoding.Raw,
                format=serialization.PublicFormat.Raw
            )
        ).decode("utf-8")
    }

def sign_skill_payload(payload: Dict[str, Any], private_key_b64: str) -> Dict[str, Any]:
    """Signs a canonical Skill Vector or Cartridge Evaluation result."""
    clean_payload = {k: v for k, v in payload.items() if k != "signature"}
    canonical_bytes = json.dumps(clean_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    
    priv_bytes = base64.b64decode(private_key_b64)
    priv_key = Ed25519PrivateKey.from_private_bytes(priv_bytes)
    sig_b64 = base64.b64encode(priv_key.sign(canonical_bytes)).decode("utf-8")
    
    signed = dict(clean_payload)
    signed["signature"] = sig_b64
    return signed

def verify_skill_payload(signed_payload: Dict[str, Any], signer_pubkey_b64: str) -> bool:
    """Verifies authenticity without contacting any central server or credential issuer."""
    if "signature" not in signed_payload:
        return False
    sig_bytes = base64.b64decode(signed_payload["signature"])
    clean_payload = {k: v for k, v in signed_payload.items() if k != "signature"}
    canonical_bytes = json.dumps(clean_payload, sort_keys=True, separators=(",", ":")).encode("utf-8")
    
    pub_bytes = base64.b64decode(signer_pubkey_b64)
    pub_key = Ed25519PublicKey.from_public_bytes(pub_bytes)
    try:
        pub_key.verify(sig_bytes, canonical_bytes)
        return True
    except Exception:
        return False

if __name__ == "__main__":
    keys = generate_builder_keypair()
    sample = {"builder_pubkey": keys["public_key"], "cartridge_id": "robotics.control_loops.v1", "elo_rating": 1865}
    signed = sign_skill_payload(sample, keys["private_key"])
    print("Verified:", verify_skill_payload(signed, keys["public_key"]))
    print(json.dumps(signed, indent=2))
