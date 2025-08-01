#!/usr/bin/env python3
"""
Clean Law Agent Startup - No Warnings
Starts Law Agent with all warnings suppressed for clean output.
"""

# Apply warning suppressions before importing anything
import os
import warnings

# Set TensorFlow environment variables
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'

# Suppress warnings
warnings.filterwarnings("ignore", category=FutureWarning)
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", message=".*sparse_softmax_cross_entropy.*")
warnings.filterwarnings("ignore", message=".*oneDNN custom operations.*")
warnings.filterwarnings("ignore", message=".*encoder_attention_mask.*")

# Now import and start Law Agent
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import and run
from run_law_agent_robust import LawAgentServer

def main():
    """Main function with clean output."""
    print("🏛️  LAW AGENT - CLEAN STARTUP")
    print("=" * 50)
    print("🔇 Warnings suppressed for clean output")
    print("🚀 Starting Law Agent...")
    print("=" * 50)
    
    # Create and start server
    server = LawAgentServer(port=8000, host="0.0.0.0")
    server.start(auto_port=True, enable_monitoring=True)

if __name__ == "__main__":
    main()
