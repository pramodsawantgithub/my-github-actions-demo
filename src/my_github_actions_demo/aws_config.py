"""
AWS Configuration Module
Safely loads AWS credentials from environment variables
"""

import os
from typing import Optional


class AWSConfig:
    """AWS Configuration handler"""

    def __init__(self):
        self.access_key_id = os.getenv("AWS_ACCESS_KEY_ID")
        self.secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY")
        self.session_token = os.getenv("AWS_SESSION_TOKEN")
        self.region = os.getenv("AWS_REGION", "us-east-1")
        self.account_id = os.getenv("AWS_ACCOUNT_ID")

    def is_configured(self) -> bool:
        """Check if AWS credentials are properly configured"""
        return bool(self.access_key_id and self.secret_access_key)

    def get_credentials(self) -> Optional[dict]:
        """Get AWS credentials as a dictionary"""
        if not self.is_configured():
            return None

        return {
            "aws_access_key_id": self.access_key_id,
            "aws_secret_access_key": self.secret_access_key,
            "aws_session_token": self.session_token,
            "region_name": self.region,
        }

    def validate(self) -> tuple[bool, str]:
        """Validate AWS configuration"""
        if not self.access_key_id:
            return False, "AWS_ACCESS_KEY_ID not set"
        if not self.secret_access_key:
            return False, "AWS_SECRET_ACCESS_KEY not set"
        # Temporary STS credentials (ASIA...) require a session token.
        if self.access_key_id and self.access_key_id.startswith("ASIA") and not self.session_token:
            return False, "AWS_SESSION_TOKEN required for temporary credentials"
        if not self.region:
            return False, "AWS_REGION not set"
        return True, "AWS configuration is valid"


# Singleton instance
aws_config = AWSConfig()


def get_aws_config() -> AWSConfig:
    """Get the AWS configuration instance"""
    return aws_config
