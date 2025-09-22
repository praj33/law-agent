#!/usr/bin/env python3
"""System Dashboard - Real-time monitoring of RL system."""

import requests
import json
import time
import os
from datetime import datetime
from typing import Dict, Any

BASE_URL = "http://localhost:8000"

class SystemDashboard:
    """Real-time system monitoring dashboard."""
    
    def __init__(self):
        self.last_stats = {}
    
    def clear_screen(self):
        """Clear terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
    
    def get_rl_stats(self) -> Dict[str, Any]:
        """Get current RL system statistics."""
        try:
            response = requests.get(f"{BASE_URL}/api/v1/rl/status", timeout=3)
            if response.status_code == 200:
                return response.json()
            return {"error": f"HTTP {response.status_code}"}
        except Exception as e:
            return {"error": str(e)}
    
    def format_memory_stats(self, memory_system: Dict[str, Any]) -> str:
        """Format memory system statistics."""
        episodic = memory_system.get("episodic_memory_size", 0)
        semantic = memory_system.get("semantic_memory_domains", 0)
        procedural = memory_system.get("procedural_memory_size", 0)
        
        return f"Episodic: {episodic} | Semantic: {semantic} | Procedural: {procedural}"
    
    def format_learning_metrics(self, learning_metrics: Dict[str, Any]) -> str:
        """Format learning metrics."""
        exploration = learning_metrics.get("exploration_rate", 0)
        total_states = learning_metrics.get("total_states", 0)
        ml_trained = learning_metrics.get("ml_models_trained", False)
        
        return f"Exploration: {exploration:.6f} | States: {total_states} | ML: {'✅' if ml_trained else '❌'}"
    
    def display_dashboard(self):
        """Display real-time dashboard."""
        while True:
            try:
                self.clear_screen()
                
                # Header
                print("🚀 ADVANCED RL LAW AGENT - SYSTEM DASHBOARD")
                print("=" * 60)
                print(f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | Press Ctrl+C to exit")
                print("=" * 60)
                
                # Get RL statistics
                rl_stats = self.get_rl_stats()
                
                if "error" in rl_stats:
                    print(f"❌ ERROR: {rl_stats['error']}")
                    print("\n💡 Make sure the server is running:")
                    print("   python -m law_agent.api.main")
                else:
                    # System Status
                    print("🔍 SYSTEM STATUS")
                    print("-" * 30)
                    is_advanced = rl_stats.get("is_advanced", False)
                    policy_type = rl_stats.get("rl_policy_type", "Unknown")
                    qtable_size = rl_stats.get("q_table_size", 0)
                    
                    print(f"🧠 RL Policy: {policy_type}")
                    print(f"⚡ Advanced Mode: {'✅ ACTIVE' if is_advanced else '❌ BASIC'}")
                    print(f"📊 Q-table Size: {qtable_size} states")
                    
                    # Memory System
                    memory_system = rl_stats.get("memory_system", {})
                    if memory_system:
                        print(f"\n🧠 MEMORY SYSTEM")
                        print("-" * 30)
                        print(f"📚 {self.format_memory_stats(memory_system)}")
                    
                    # Learning Metrics
                    learning_metrics = rl_stats.get("learning_metrics", {})
                    if learning_metrics:
                        print(f"\n📈 LEARNING METRICS")
                        print("-" * 30)
                        print(f"🎯 {self.format_learning_metrics(learning_metrics)}")
                    
                    # Domain Performance
                    domain_performance = rl_stats.get("domain_performance", {})
                    if domain_performance:
                        print(f"\n⚖️  DOMAIN PERFORMANCE")
                        print("-" * 30)
                        for domain, perf in domain_performance.items():
                            if isinstance(perf, dict):
                                accuracy = perf.get("accuracy", 0)
                                count = perf.get("count", 0)
                                print(f"   {domain}: {accuracy:.1%} accuracy ({count} cases)")
                    
                    # Performance Analytics
                    analytics = rl_stats.get("performance_analytics", {})
                    if analytics:
                        print(f"\n📊 PERFORMANCE ANALYTICS")
                        print("-" * 30)
                        learning_metrics_analytics = analytics.get("learning_metrics", {})
                        if learning_metrics_analytics:
                            total_exp = learning_metrics_analytics.get("total_experiences", 0)
                            domains_learned = learning_metrics_analytics.get("domains_learned", 0)
                            avg_expertise = learning_metrics_analytics.get("avg_domain_expertise", 0)
                            print(f"📚 Total Experiences: {total_exp}")
                            print(f"⚖️  Domains Learned: {domains_learned}")
                            print(f"🎯 Avg Domain Expertise: {avg_expertise:.3f}")
                    
                    # Changes from last check
                    if self.last_stats:
                        print(f"\n🔄 CHANGES SINCE LAST CHECK")
                        print("-" * 30)
                        
                        # Q-table growth
                        last_qtable = self.last_stats.get("q_table_size", 0)
                        qtable_growth = qtable_size - last_qtable
                        if qtable_growth > 0:
                            print(f"📈 Q-table grew by {qtable_growth} states")
                        
                        # Exploration decay
                        last_exploration = self.last_stats.get("learning_metrics", {}).get("exploration_rate", 0)
                        current_exploration = learning_metrics.get("exploration_rate", 0)
                        if last_exploration > 0 and current_exploration < last_exploration:
                            decay = last_exploration - current_exploration
                            print(f"📉 Exploration decayed by {decay:.6f}")
                        
                        # Memory growth
                        last_memory = self.last_stats.get("memory_system", {})
                        current_memory = memory_system
                        
                        for memory_type in ["episodic_memory_size", "semantic_memory_domains", "procedural_memory_size"]:
                            last_val = last_memory.get(memory_type, 0)
                            current_val = current_memory.get(memory_type, 0)
                            if current_val > last_val:
                                growth = current_val - last_val
                                print(f"🧠 {memory_type.replace('_', ' ').title()} grew by {growth}")
                    
                    # Store current stats for next comparison
                    self.last_stats = rl_stats.copy()
                
                # Footer
                print("\n" + "=" * 60)
                print("🔄 Refreshing in 5 seconds... (Ctrl+C to exit)")
                
                time.sleep(5)
                
            except KeyboardInterrupt:
                print("\n\n👋 Dashboard stopped by user")
                break
            except Exception as e:
                print(f"\n❌ Dashboard error: {e}")
                time.sleep(5)

def show_system_info():
    """Show current system information."""
    print("📋 SYSTEM INFORMATION")
    print("=" * 40)
    
    try:
        # Server health
        health = requests.get(f"{BASE_URL}/health", timeout=3)
        print(f"🔍 Server Status: {'✅ ONLINE' if health.status_code == 200 else '❌ OFFLINE'}")
        
        # RL system info
        rl_stats = requests.get(f"{BASE_URL}/api/v1/rl/status", timeout=3)
        if rl_stats.status_code == 200:
            data = rl_stats.json()
            print(f"🧠 RL Policy: {data.get('rl_policy_type', 'Unknown')}")
            print(f"⚡ Advanced Mode: {'✅' if data.get('is_advanced') else '❌'}")
            print(f"📊 Q-table Size: {data.get('q_table_size', 0)}")
            
            memory = data.get('memory_system', {})
            print(f"🧠 Memory - Episodic: {memory.get('episodic_memory_size', 0)}, Semantic: {memory.get('semantic_memory_domains', 0)}")
            
            learning = data.get('learning_metrics', {})
            print(f"📈 Learning - Exploration: {learning.get('exploration_rate', 0):.6f}, States: {learning.get('total_states', 0)}")
        else:
            print(f"🧠 RL System: ❌ ERROR (HTTP {rl_stats.status_code})")
        
    except Exception as e:
        print(f"❌ Error getting system info: {e}")

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "info":
        show_system_info()
    else:
        dashboard = SystemDashboard()
        dashboard.display_dashboard()
