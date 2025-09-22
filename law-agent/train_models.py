#!/usr/bin/env python3
"""
Train RL models and optimize system
"""

import sys
import os
sys.path.append('.')

from law_agent.ai.rl_model_trainer import train_rl_models

def main():
    print("🚀 TRAINING RL MODELS...")
    print("=" * 50)
    
    try:
        result = train_rl_models()
        
        print("🎉 RL MODELS TRAINED SUCCESSFULLY!")
        print(f"Training examples: {result['training_examples']}")
        print(f"Model directory: {result['model_dir']}")
        print("✅ RandomForestRegressor is now trained and ready!")
        
        return True
        
    except Exception as e:
        print(f"❌ Training failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    if success:
        print("\n🎯 NEXT STEPS:")
        print("1. Restart the server to load trained models")
        print("2. Test the system with queries")
        print("3. Provide feedback to improve RL performance")
    else:
        print("\n❌ Please check the error and try again")
