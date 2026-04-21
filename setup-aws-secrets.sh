#!/bin/bash

# GitHub Actions Setup Helper
# This script helps set up GitHub Secrets for AWS credentials

set -e

echo "🔐 GitHub Actions AWS Secrets Setup"
echo "=================================="
echo ""

# Check if GitHub CLI is installed
if ! command -v gh &> /dev/null; then
    echo "❌ GitHub CLI is not installed"
    echo "Install it from: https://cli.github.com/"
    exit 1
fi

# Get repository info
REPO=$(gh repo view --json nameWithOwner --jq '.nameWithOwner')
echo "📦 Repository: $REPO"
echo ""

echo "ℹ️  You need the following AWS credentials:"
echo "   - AWS_ACCESS_KEY_ID"
echo "   - AWS_SECRET_ACCESS_KEY"
echo "   - AWS_SESSION_TOKEN (only for temporary STS credentials)"
echo "   - AWS_REGION (e.g., us-east-1)"
echo ""

# Prompt for secrets
read -sp "Enter AWS_ACCESS_KEY_ID: " AWS_ACCESS_KEY_ID
echo ""
read -sp "Enter AWS_SECRET_ACCESS_KEY: " AWS_SECRET_ACCESS_KEY
echo ""
read -sp "Enter AWS_SESSION_TOKEN (optional): " AWS_SESSION_TOKEN
echo ""
read -p "Enter AWS_REGION [us-east-1]: " AWS_REGION
AWS_REGION=${AWS_REGION:-us-east-1}

# Temporary STS credentials (ASIA...) require a session token.
if [[ "$AWS_ACCESS_KEY_ID" == ASIA* ]] && [ -z "$AWS_SESSION_TOKEN" ]; then
    echo "❌ Detected temporary AWS credentials (ASIA...), but AWS_SESSION_TOKEN is missing"
    echo "Provide AWS_SESSION_TOKEN to use temporary credentials"
    exit 1
fi

# Optional validation before storing secrets.
if command -v aws &> /dev/null; then
    echo ""
    echo "🔍 Validating AWS credentials with STS..."

    export AWS_ACCESS_KEY_ID
    export AWS_SECRET_ACCESS_KEY
    export AWS_SESSION_TOKEN
    export AWS_REGION

    sts_error_file=$(mktemp)

    if aws sts get-caller-identity --output json > /dev/null 2>"$sts_error_file"; then
        echo "✅ AWS credentials are valid"
    else
        echo "❌ AWS credential validation failed"
        cat "$sts_error_file"
        if [[ "$AWS_ACCESS_KEY_ID" == ASIA* ]]; then
            echo "Temporary credentials may be missing/expired session token"
        fi
        rm -f "$sts_error_file"
        exit 1
    fi

    rm -f "$sts_error_file"
else
    echo "ℹ️  AWS CLI not found, skipping credential validation"
fi

# Set secrets
echo ""
echo "📝 Setting GitHub Secrets..."

gh secret set AWS_ACCESS_KEY_ID --body "$AWS_ACCESS_KEY_ID"
echo "✅ AWS_ACCESS_KEY_ID set"

gh secret set AWS_SECRET_ACCESS_KEY --body "$AWS_SECRET_ACCESS_KEY"
echo "✅ AWS_SECRET_ACCESS_KEY set"

if [ -n "$AWS_SESSION_TOKEN" ]; then
    gh secret set AWS_SESSION_TOKEN --body "$AWS_SESSION_TOKEN"
    echo "✅ AWS_SESSION_TOKEN set"
else
    echo "ℹ️  AWS_SESSION_TOKEN skipped (not provided)"
fi

gh secret set AWS_REGION --body "$AWS_REGION"
echo "✅ AWS_REGION set"

echo ""
echo "✨ GitHub Secrets configured successfully!"
echo ""
echo "📋 To view configured secrets:"
echo "   gh secret list"
echo ""
echo "⚠️  IMPORTANT:"
echo "   - These secrets are encrypted and only available in GitHub Actions"
echo "   - Never commit your credentials to git"
echo "   - Rotate your credentials regularly"
