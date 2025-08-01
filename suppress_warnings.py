#!/usr/bin/env python3
"""
Warning Suppression Utility for Law Agent
Suppress TensorFlow, PyTorch, and other ML library warnings for cleaner output.
"""

import os
import warnings
import logging

def suppress_tensorflow_warnings():
    """Suppress TensorFlow warnings and info messages."""
    
    # Set environment variables before importing TensorFlow
    os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'  # Disable oneDNN optimizations
    os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'   # Suppress INFO and WARNING messages
    os.environ['CUDA_VISIBLE_DEVICES'] = '-1'  # Disable GPU (use CPU only)
    
    try:
        import tensorflow as tf
        
        # Suppress TensorFlow logging
        tf.get_logger().setLevel('ERROR')
        
        # Disable specific warnings
        tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)
        
        print("✅ TensorFlow warnings suppressed")
        
    except ImportError:
        print("⚠️ TensorFlow not installed")

def suppress_pytorch_warnings():
    """Suppress PyTorch warnings."""
    
    try:
        import torch
        
        # Suppress specific PyTorch warnings
        warnings.filterwarnings("ignore", category=FutureWarning, module="torch")
        warnings.filterwarnings("ignore", message=".*encoder_attention_mask.*")
        
        # Set number of threads
        torch.set_num_threads(int(os.environ.get('TORCH_NUM_THREADS', '4')))
        
        print("✅ PyTorch warnings suppressed")
        
    except ImportError:
        print("⚠️ PyTorch not installed")

def suppress_transformers_warnings():
    """Suppress Transformers library warnings."""
    
    try:
        import transformers
        
        # Suppress transformers warnings
        transformers.logging.set_verbosity_error()
        
        # Suppress specific warnings
        warnings.filterwarnings("ignore", category=FutureWarning, module="transformers")
        warnings.filterwarnings("ignore", message=".*BertSdpaSelfAttention.*")
        
        print("✅ Transformers warnings suppressed")
        
    except ImportError:
        print("⚠️ Transformers not installed")

def suppress_general_warnings():
    """Suppress general Python warnings."""
    
    # Suppress specific warning categories
    warnings.filterwarnings("ignore", category=DeprecationWarning)
    warnings.filterwarnings("ignore", category=PendingDeprecationWarning)
    warnings.filterwarnings("ignore", category=FutureWarning)
    warnings.filterwarnings("ignore", category=UserWarning, module="sklearn")
    warnings.filterwarnings("ignore", category=UserWarning, module="numpy")
    
    # Suppress specific messages
    warnings.filterwarnings("ignore", message=".*sparse_softmax_cross_entropy.*")
    warnings.filterwarnings("ignore", message=".*oneDNN custom operations.*")
    
    print("✅ General warnings suppressed")

def suppress_logging_warnings():
    """Suppress excessive logging from various libraries."""
    
    # Set logging levels for noisy libraries
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('requests').setLevel(logging.WARNING)
    logging.getLogger('matplotlib').setLevel(logging.WARNING)
    logging.getLogger('PIL').setLevel(logging.WARNING)
    
    print("✅ Logging warnings suppressed")

def apply_all_suppressions():
    """Apply all warning suppressions."""
    
    print("🔇 SUPPRESSING ML LIBRARY WARNINGS")
    print("=" * 50)
    
    suppress_general_warnings()
    suppress_tensorflow_warnings()
    suppress_pytorch_warnings()
    suppress_transformers_warnings()
    suppress_logging_warnings()
    
    print("=" * 50)
    print("✅ All warnings suppressed for cleaner output!")
    print("💡 This improves readability without affecting functionality")

def create_clean_startup_script():
    """Create a clean startup script with warning suppression."""
    
    script_content = '''#!/usr/bin/env python3
"""
Clean Law Agent Startup - No Warnings
Starts Law Agent with all warnings suppressed for clean output.
"""

# Apply warning suppressions before importing anything
import suppress_warnings
suppress_warnings.apply_all_suppressions()

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
'''
    
    with open('start_law_agent_clean.py', 'w') as f:
        f.write(script_content)
    
    print("✅ Created clean startup script: start_law_agent_clean.py")

if __name__ == "__main__":
    apply_all_suppressions()
    create_clean_startup_script()
