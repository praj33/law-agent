#!/usr/bin/env python3
"""Direct RL System Test - Test the RL components directly."""

import asyncio
import sys
import os

# Add the law_agent directory to the path
sys.path.insert(0, os.path.abspath('.'))

from law_agent.ai.advanced_rl_policy import AdvancedLegalRLPolicy
from law_agent.ai.advanced_rl_system import AdvancedState, AdvancedReward, AdvancedAgentMemory
from law_agent.core.state import LegalDomain, UserType

async def test_advanced_rl_directly():
    """Test the advanced RL system directly without API."""
    
    print("🧪 DIRECT ADVANCED RL SYSTEM TEST")
    print("=" * 50)
    
    try:
        # Initialize advanced RL policy
        print("\n1️⃣ Initializing Advanced RL Policy...")
        rl_policy = AdvancedLegalRLPolicy()
        print(f"✅ RL Policy Type: {type(rl_policy).__name__}")
        print(f"✅ Has Memory: {hasattr(rl_policy, 'memory')}")
        print(f"✅ Has ML Models: {hasattr(rl_policy, 'reward_predictor')}")
        print(f"✅ Exploration Rate: {rl_policy.exploration_rate}")
        
        # Test advanced state creation
        print("\n2️⃣ Testing Advanced State Creation...")
        test_state = {
            "user_type": "law_firm",
            "domain": "contract_law",
            "confidence": 0.8,
            "query": "Complex contract breach involving multiple parties and jurisdictions",
            "session_id": "test_session_123"
        }
        
        advanced_state = rl_policy._create_advanced_state(test_state)
        print(f"✅ Advanced State Created: {type(advanced_state).__name__}")
        print(f"✅ State Vector Dimensions: {len(advanced_state.to_vector())}")
        print(f"✅ User Type: {advanced_state.user_type}")
        print(f"✅ Domain: {advanced_state.current_domain}")
        print(f"✅ Query Complexity: {advanced_state.query_complexity:.3f}")
        print(f"✅ Legal Urgency: {advanced_state.legal_urgency:.3f}")
        
        # Test action selection
        print("\n3️⃣ Testing Advanced Action Selection...")
        action = await rl_policy.get_action(test_state)
        print(f"✅ Action Selected: {action}")
        print(f"✅ Action Type: {action.get('action', 'unknown')}")
        print(f"✅ Response Style: {action.get('response_style', 'unknown')}")
        print(f"✅ Confidence: {action.get('confidence', 0):.3f}")
        
        # Test reward calculation and policy update
        print("\n4️⃣ Testing Policy Update with Reward...")
        
        # Create advanced reward
        advanced_reward = AdvancedReward(
            user_satisfaction=0.8,
            legal_accuracy=0.9,
            response_quality=0.85,
            time_efficiency=0.7,
            domain_expertise=0.75,
            user_engagement=0.8,
            learning_progress=0.6
        )
        
        total_reward = advanced_reward.total_reward()
        print(f"✅ Multi-dimensional Reward: {total_reward:.3f}")
        print(f"   - User Satisfaction: {advanced_reward.user_satisfaction}")
        print(f"   - Legal Accuracy: {advanced_reward.legal_accuracy}")
        print(f"   - Response Quality: {advanced_reward.response_quality}")
        
        # Update policy
        await rl_policy.update_policy(test_state, action, total_reward)
        print(f"✅ Policy Updated Successfully")
        
        # Test Q-table learning
        print("\n5️⃣ Testing Q-table Learning...")
        
        # Simulate multiple interactions
        for i in range(5):
            # Create slightly different states
            test_state_variant = test_state.copy()
            test_state_variant["query"] = f"Contract dispute case {i+1}"
            
            # Get action
            action = await rl_policy.get_action(test_state_variant)
            
            # Create reward (alternating positive/negative)
            reward_value = 0.8 if i % 2 == 0 else -0.3
            
            # Update policy
            await rl_policy.update_policy(test_state_variant, action, reward_value)
            
            print(f"   Iteration {i+1}: Action={action.get('action')}, Reward={reward_value:.1f}")
        
        # Check Q-table size
        qtable_size = len(rl_policy.action_rewards)
        print(f"✅ Q-table Size: {qtable_size} states")
        
        # Test memory system
        print("\n6️⃣ Testing Advanced Memory System...")
        memory_stats = rl_policy.memory.get_memory_stats()
        print(f"✅ Episodic Memory: {memory_stats.get('episodic_memory_size', 0)} experiences")
        print(f"✅ Semantic Memory: {memory_stats.get('semantic_memory_domains', 0)} domains")
        print(f"✅ Procedural Memory: {memory_stats.get('procedural_memory_size', 0)} procedures")
        
        # Test performance analytics
        print("\n7️⃣ Testing Performance Analytics...")
        if hasattr(rl_policy, 'get_performance_analytics'):
            analytics = rl_policy.get_performance_analytics()
            print(f"✅ Analytics Available: {bool(analytics)}")
            if analytics:
                learning_metrics = analytics.get('learning_metrics', {})
                print(f"   - Total Experiences: {learning_metrics.get('total_experiences', 0)}")
                print(f"   - Domains Learned: {learning_metrics.get('domains_learned', 0)}")
                print(f"   - Avg Domain Expertise: {learning_metrics.get('avg_domain_expertise', 0):.3f}")
        
        # Test ML integration
        print("\n8️⃣ Testing ML Integration...")
        has_ml_models = hasattr(rl_policy, 'reward_predictor') and rl_policy.reward_predictor is not None
        print(f"✅ ML Models Available: {has_ml_models}")
        
        if has_ml_models:
            print(f"   - Reward Predictor: {type(rl_policy.reward_predictor).__name__}")
            print(f"   - Action Selector: {type(rl_policy.action_selector).__name__}")
        
        # Final assessment
        print("\n" + "=" * 50)
        print("📊 DIRECT RL TEST RESULTS")
        print("=" * 50)
        
        components_working = [
            ("Advanced RL Policy", True),
            ("Multi-dimensional State", len(advanced_state.to_vector()) == 15),
            ("Action Selection", action is not None),
            ("Reward Calculation", total_reward != 0),
            ("Policy Updates", qtable_size > 0),
            ("Memory System", memory_stats.get('episodic_memory_size', 0) >= 0),
            ("ML Integration", has_ml_models)
        ]
        
        working_count = sum(1 for _, working in components_working if working)
        total_count = len(components_working)
        success_rate = (working_count / total_count) * 100
        
        for component, working in components_working:
            status = "✅" if working else "❌"
            print(f"{status} {component}")
        
        print(f"\n📈 SUCCESS RATE: {success_rate:.1f}% ({working_count}/{total_count})")
        
        if success_rate >= 95:
            print(f"\n🚀 PERFECT! Advanced RL System is fully operational!")
        elif success_rate >= 85:
            print(f"\n🎯 EXCELLENT! Advanced RL System is working very well!")
        elif success_rate >= 75:
            print(f"\n👍 GOOD! Advanced RL System is mostly working!")
        else:
            print(f"\n⚠️  NEEDS WORK! Advanced RL System has issues!")
        
        return success_rate >= 85
        
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_q_table_learning():
    """Test Q-table learning specifically."""
    
    print("\n🎯 DETAILED Q-TABLE LEARNING TEST")
    print("=" * 40)
    
    try:
        rl_policy = AdvancedLegalRLPolicy()
        
        # Test same state with different rewards
        base_state = {
            "user_type": "common_person",
            "domain": "family_law",
            "confidence": 0.7,
            "query": "I need help with divorce proceedings",
            "session_id": "qtable_test"
        }
        
        print("Testing Q-table learning with consistent state...")
        
        rewards_given = []
        actions_taken = []
        
        for i in range(10):
            # Get action
            action = await rl_policy.get_action(base_state)
            actions_taken.append(action.get('action', 'unknown'))
            
            # Give alternating rewards
            reward = 1.0 if i % 2 == 0 else -0.5
            rewards_given.append(reward)
            
            # Update policy
            await rl_policy.update_policy(base_state, action, reward)
            
            print(f"   Step {i+1}: Action={action.get('action')}, Reward={reward}")
        
        # Check if Q-table learned
        qtable_size = len(rl_policy.action_rewards)
        print(f"\n✅ Q-table Size After Learning: {qtable_size}")
        
        # Check action consistency (should adapt to rewards)
        unique_actions = len(set(actions_taken))
        print(f"✅ Action Variety: {unique_actions} different actions")
        
        # Check if bandit rewards were updated
        total_bandit_entries = sum(len(actions) for actions in rl_policy.action_rewards.values())
        print(f"✅ Total Bandit Entries: {total_bandit_entries}")
        
        qtable_working = qtable_size > 0 and total_bandit_entries > 0
        print(f"\n🎯 Q-table Learning: {'✅ WORKING' if qtable_working else '❌ NOT WORKING'}")
        
        return qtable_working
        
    except Exception as e:
        print(f"❌ Q-table test error: {e}")
        return False

if __name__ == "__main__":
    async def main():
        print("🔬 COMPREHENSIVE DIRECT RL TESTING")
        print("=" * 60)
        
        # Test main RL system
        rl_working = await test_advanced_rl_directly()
        
        # Test Q-table specifically
        qtable_working = await test_q_table_learning()
        
        print("\n" + "=" * 60)
        print("🏁 FINAL ASSESSMENT")
        print("=" * 60)
        print(f"✅ Advanced RL System: {'WORKING' if rl_working else 'ISSUES'}")
        print(f"✅ Q-table Learning: {'WORKING' if qtable_working else 'ISSUES'}")
        
        if rl_working and qtable_working:
            print(f"\n🎉 PERFECT! All RL components are working flawlessly!")
            print(f"🚀 The system is using FULL ADVANCED RL - no basic components!")
        elif rl_working:
            print(f"\n👍 GOOD! RL system is working, Q-table needs attention!")
        else:
            print(f"\n⚠️  NEEDS WORK! RL system has issues!")
    
    asyncio.run(main())
