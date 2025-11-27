"""
Configuration module for Azure OpenAI
Handles model initialization for all agents
"""
import os
from agno.models.azure import AzureOpenAI

def get_azure_openai_model(deployment_name: str = None, max_tokens: int = None):
    """
    Get configured Azure OpenAI model instance
    
    Args:
        deployment_name: Azure deployment name (defaults to env var AZURE_OPENAI_DEPLOYMENT)
        max_tokens: Maximum tokens for completion (optional)
    
    Returns:
        AzureOpenAI instance configured with Azure credentials
    """
    api_key = os.getenv("AZURE_OPENAI_API_KEY")
    endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
    api_version = os.getenv("AZURE_OPENAI_API_VERSION", "2024-08-01-preview")
    deployment = deployment_name or os.getenv("AZURE_OPENAI_DEPLOYMENT")
    
    model_kwargs = {
        "id": deployment,
        "azure_deployment": deployment,
        "azure_endpoint": endpoint,
        "api_key": api_key,
        "api_version": api_version
    }
    
    if max_tokens is not None:
        model_kwargs["max_tokens"] = max_tokens
    
    return AzureOpenAI(**model_kwargs)
