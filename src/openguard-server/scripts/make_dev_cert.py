"""Tạo chứng chỉ TLS tự ký cho dev và in dấu vân tay SHA-256 để ghim (cert pinning) ở agent.

    python scripts/make_dev_cert.py --host 192.168.1.10
    python -m uvicorn app.main:app --host 0.0.0.0 --port 8443 --ssl-keyfile data/dev.key --ssl-certfile data/dev.crt
    set OPENGUARD_PIN_SHA256=<giá trị in ra>     (agent)
    set OPENGUARD_CA_FILE=<đường dẫn dev.crt>    (agent: tin chứng chỉ tự ký này)
"""
import argparse
import datetime
import hashlib
import ipaddress
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.x509.oid import NameOID


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="localhost")
    ap.add_argument("--out", default="data")
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    key = ec.generate_private_key(ec.SECP256R1())
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, a.host)])
    san = [x509.DNSName("localhost")]
    try:
        san.append(x509.IPAddress(ipaddress.ip_address(a.host)))
    except ValueError:
        san.append(x509.DNSName(a.host))
    now = datetime.datetime.now(datetime.timezone.utc)
    cert = (x509.CertificateBuilder().subject_name(name).issuer_name(name).public_key(key.public_key())
            .serial_number(x509.random_serial_number()).not_valid_before(now - datetime.timedelta(minutes=1))
            .not_valid_after(now + datetime.timedelta(days=365)).add_extension(x509.SubjectAlternativeName(san), False)
            .sign(key, hashes.SHA256()))
    (out / "dev.key").write_bytes(key.private_bytes(serialization.Encoding.PEM, serialization.PrivateFormat.PKCS8, serialization.NoEncryption()))
    (out / "dev.crt").write_bytes(cert.public_bytes(serialization.Encoding.PEM))
    fp = hashlib.sha256(cert.public_bytes(serialization.Encoding.DER)).hexdigest()
    print(f"Đã tạo {out/'dev.crt'} và {out/'dev.key'} (TLS 1.2+ theo OpenSSL mặc định).")
    print(f"OPENGUARD_PIN_SHA256={fp}")


if __name__ == "__main__":
    main()
