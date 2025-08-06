"""Configuration management for the Law Agent system."""

import os
from typing import Optional
from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    """Application settings with environment variable support."""
    
    # Database Configuration
    database_url: str = Field(default="sqlite:///./law_agent.db", env="DATABASE_URL")
    redis_url: str = Field(default="redis://localhost:6379/0", env="REDIS_URL")
    
    # API Configuration
    api_host: str = Field(default="0.0.0.0", env="API_HOST")
    api_port: int = Field(default=8000, env="API_PORT")
    api_reload: bool = Field(default=True, env="API_RELOAD")
    
    # Security
    secret_key: str = Field(default="dev-secret-key", env="SECRET_KEY")
    algorithm: str = Field(default="HS256", env="ALGORITHM")
    access_token_expire_minutes: int = Field(default=30, env="ACCESS_TOKEN_EXPIRE_MINUTES")
    
    # AI/ML Configuration
    huggingface_token: Optional[str] = Field(default=None, env="HUGGINGFACE_TOKEN")
    openai_api_key: Optional[str] = Field(default="sk-proj-dummy-key-for-development", env="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4", env="OPENAI_MODEL")
    openai_temperature: float = Field(default=0.3, env="OPENAI_TEMPERATURE")
    openai_max_tokens: int = Field(default=2000, env="OPENAI_MAX_TOKENS")

    # Grok AI Configuration
    grok_api_key: Optional[str] = Field(default=None, env="GROK_API_KEY")
    grok_model: str = Field(default="grok-beta", env="GROK_MODEL")
    grok_temperature: float = Field(default=0.3, env="GROK_TEMPERATURE")
    grok_max_tokens: int = Field(default=2000, env="GROK_MAX_TOKENS")
    use_grok_ai: bool = Field(default=True, env="USE_GROK_AI")

    # Free Hugging Face AI Configuration
    huggingface_api_key: Optional[str] = Field(default=None, env="HUGGINGFACE_API_KEY")
    huggingface_model: str = Field(default="microsoft/DialoGPT-large", env="HUGGINGFACE_MODEL")

    # Advanced AI Configuration
    use_advanced_ai: bool = Field(default=True, env="USE_ADVANCED_AI")
    legal_reasoning_model: str = Field(default="gpt-4", env="LEGAL_REASONING_MODEL")
    case_law_analysis: bool = Field(default=True, env="CASE_LAW_ANALYSIS")
    document_analysis: bool = Field(default=True, env="DOCUMENT_ANALYSIS")
    
    # Legal Data Sources
    legal_api_key: Optional[str] = Field(default=None, env="LEGAL_API_KEY")
    court_data_api: Optional[str] = Field(default=None, env="COURT_DATA_API")
    
    # Logging
    log_level: str = Field(default="INFO", env="LOG_LEVEL")
    log_file: str = Field(default="logs/law_agent.log", env="LOG_FILE")
    
    # Reinforcement Learning
    rl_model_path: str = Field(default="models/rl_policy", env="RL_MODEL_PATH")
    rl_learning_rate: float = Field(default=0.001, env="RL_LEARNING_RATE")
    rl_exploration_rate: float = Field(default=0.1, env="RL_EXPLORATION_RATE")
    
    # Vector Database
    chroma_persist_directory: str = Field(default="./chroma_db", env="CHROMA_PERSIST_DIRECTORY")
    vector_dimension: int = Field(default=384, env="VECTOR_DIMENSION")
    
    # Monitoring
    prometheus_port: int = Field(default=9090, env="PROMETHEUS_PORT")
    enable_metrics: bool = Field(default=True, env="ENABLE_METRICS")

    # Performance Optimization
    torch_num_threads: int = Field(default=4, env="TORCH_NUM_THREADS")
    omp_num_threads: int = Field(default=4, env="OMP_NUM_THREADS")
    tokenizers_parallelism: bool = Field(default=False, env="TOKENIZERS_PARALLELISM")

    # System Monitoring
    enable_health_monitoring: bool = Field(default=True, env="ENABLE_HEALTH_MONITORING")
    health_check_interval: int = Field(default=30, env="HEALTH_CHECK_INTERVAL")

    # Advanced Features
    enable_auto_port_resolution: bool = Field(default=True, env="ENABLE_AUTO_PORT_RESOLUTION")
    enable_graceful_shutdown: bool = Field(default=True, env="ENABLE_GRACEFUL_SHUTDOWN")
    enable_resource_monitoring: bool = Field(default=True, env="ENABLE_RESOURCE_MONITORING")

    # TensorFlow Configuration
    tf_enable_onednn_opts: str = Field(default="0", env="TF_ENABLE_ONEDNN_OPTS")
    tf_cpp_min_log_level: str = Field(default="2", env="TF_CPP_MIN_LOG_LEVEL")
    cuda_visible_devices: str = Field(default="-1", env="CUDA_VISIBLE_DEVICES")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Global settings instance
settings = Settings()
