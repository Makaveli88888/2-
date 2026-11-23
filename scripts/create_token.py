"""Mint a short-lived user JWT for local development/admin provisioning.

Usage: python -m scripts.create_token <user_id>
Requires JWT_SECRET in the environment or .env.
"""
import sys

from app.security import create_access_token


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: python -m scripts.create_token <user_id>")
        return 2
    print(create_access_token(sys.argv[1]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
