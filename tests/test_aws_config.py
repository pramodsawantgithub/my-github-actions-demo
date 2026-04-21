"""
AWS Configuration Tests
"""

import os
import pytest

from my_github_actions_demo.aws_config import AWSConfig, get_aws_config


def test_aws_config_not_configured(monkeypatch):
    """Test AWS config when credentials are not set"""
    monkeypatch.delenv("AWS_ACCESS_KEY_ID", raising=False)
    monkeypatch.delenv("AWS_SECRET_ACCESS_KEY", raising=False)

    config = AWSConfig()
    assert not config.is_configured()
    assert config.get_credentials() is None


def test_aws_config_with_credentials(monkeypatch):
    """Test AWS config with credentials set"""
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "AKIA1234567890ABCDEF")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "test_secret_key_123")
    monkeypatch.setenv("AWS_REGION", "us-west-2")

    config = AWSConfig()
    assert config.is_configured()
    assert config.access_key_id == "AKIA1234567890ABCDEF"
    assert config.region == "us-west-2"


def test_aws_config_default_region(monkeypatch):
    """Test AWS config uses default region"""
    monkeypatch.delenv("AWS_REGION", raising=False)

    config = AWSConfig()
    assert config.region == "us-east-1"


def test_aws_config_validation_missing_access_key(monkeypatch):
    """Test validation fails when access key is missing"""
    monkeypatch.delenv("AWS_ACCESS_KEY_ID", raising=False)
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "test_secret")

    config = AWSConfig()
    is_valid, message = config.validate()
    assert not is_valid
    assert "AWS_ACCESS_KEY_ID" in message


def test_aws_config_validation_missing_secret_key(monkeypatch):
    """Test validation fails when secret key is missing"""
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "AKIA1234567890ABCDEF")
    monkeypatch.delenv("AWS_SECRET_ACCESS_KEY", raising=False)

    config = AWSConfig()
    is_valid, message = config.validate()
    assert not is_valid
    assert "AWS_SECRET_ACCESS_KEY" in message


def test_aws_config_validation_success(monkeypatch):
    """Test validation succeeds with all credentials"""
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "AKIA1234567890ABCDEF")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "test_secret_key_123")
    monkeypatch.setenv("AWS_REGION", "us-east-1")

    config = AWSConfig()
    is_valid, message = config.validate()
    assert is_valid
    assert "valid" in message.lower()


def test_temp_credentials_require_session_token(monkeypatch):
    """Temporary ASIA credentials must include AWS_SESSION_TOKEN"""
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "ASIA1234567890ABCDE")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "test_secret_key_123")
    monkeypatch.delenv("AWS_SESSION_TOKEN", raising=False)

    config = AWSConfig()
    is_valid, message = config.validate()
    assert not is_valid
    assert "AWS_SESSION_TOKEN" in message


def test_temp_credentials_with_session_token(monkeypatch):
    """Temporary ASIA credentials validate when session token is present"""
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "ASIA1234567890ABCDE")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "test_secret_key_123")
    monkeypatch.setenv("AWS_SESSION_TOKEN", "test_session_token")

    config = AWSConfig()
    is_valid, message = config.validate()
    assert is_valid
    assert "valid" in message.lower()


def test_get_aws_config():
    """Test singleton pattern"""
    config1 = get_aws_config()
    config2 = get_aws_config()
    assert config1 is config2
