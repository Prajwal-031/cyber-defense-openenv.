import os
import json
import time
import random
from typing import List, Dict, Any
from openai import OpenAI, OpenAIError, RateLimitError
from dotenv import load_dotenv
from env.environment import CyberIncidentEnv
from env.models import Observation, Action

# Load environment variables from .env file
load_dotenv()

# Environment Variables
API_BASE_URL = os.getenv("API_BASE_URL", "https://api.openai.com/v1")
MODEL_NAME = os.getenv("MODEL_NAME", "gpt-4-mini")
HF_TOKEN = os.getenv("HF_TOKEN")
USE_LLM = os.getenv("USE_LLM", "false").lower() == "true"  # Disable LLM by default due to quota issues

# OpenAI Client Configuration
client = None
if USE_LLM and HF_TOKEN and HF_TOKEN != "missing_key":
    try:
        client = OpenAI(base_url=API_BASE_URL, api_key=HF_TOKEN)
        print("[INFO] OpenAI client initialized. LLM-based actions enabled.")
    except Exception as e:
        print(f"[WARNING] Failed to initialize OpenAI client: {e}. Using rule-based actions only.")
        client = None
else:
    print("[INFO] USE_LLM disabled or API key not found. Using rule-based actions exclusively.")

def get_defender_action(obs: Observation, task_goal: str) -> Dict[str, Any]:
    """
    Calls the LLM to decide on a defender action based on the observation.
    Includes robust error handling for rate limits and quota issues.
    Falls back to rule-based logic when LLM is unavailable.
    """
    # Rule-based fallback logic
    def fallback_action():
        if obs.suspected_hosts:
            # Prioritize isolating known infected hosts
            return {"isolate_host": obs.suspected_hosts[0]}
        # Otherwise, investigate a random workstation
        return {"investigate_host": random.choice(["workstation_1", "workstation_2"])}

    # If LLM is disabled or not available, use rule-based fallback
    if not client or not USE_LLM:
        return fallback_action()

    prompt = f"""
    You are a Blue Team defender in a Security Operations Center (SOC).
    Your goal is: {task_goal}
    
    Current Observation:
    - Alerts: {obs.alerts}
    - Suspected Hosts: {obs.suspected_hosts}
    - Infected Estimate: {obs.infected_estimate}
    - Time Step: {obs.time_step}
    - Network Status: {obs.network_status}
    
    Available Actions:
    - investigate_host: Provide host name to confirm infection.
    - isolate_host: Provide host name to contain infection.
    - patch_host: Provide host name to secure it.
    - block_ip: Provide IP address to block.
    
    Respond with a JSON object representing the action, e.g., {{"investigate_host": "workstation_1"}}.
    Only provide the JSON object.
    """
    
    max_retries = 2
    retry_delay = 1  # seconds
    
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=MODEL_NAME,
                messages=[
                    {"role": "system", "content": "You are a cybersecurity expert."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                timeout=10
            )
            action_json = json.loads(response.choices[0].message.content)
            return action_json
        except RateLimitError as e:
            if attempt < max_retries - 1:
                print(f"[RETRY] Rate limit hit (attempt {attempt + 1}/{max_retries}). Waiting {retry_delay}s before retry...")
                time.sleep(retry_delay)
                retry_delay *= 2  # Exponential backoff
            else:
                print(f"[FALLBACK] Max retries exceeded for rate limit. Using rule-based action.")
                return fallback_action()
        except Exception as e:
            error_msg = str(e)
            if "insufficient_quota" in error_msg or "quota" in error_msg.lower():
                print(f"[FALLBACK] OpenAI quota exceeded or billing issue. Using rule-based action.")
                print(f"  Error: {error_msg[:100]}...")
                return fallback_action()
            elif attempt < max_retries - 1:
                print(f"[RETRY] LLM call failed (attempt {attempt + 1}/{max_retries}): {str(e)[:80]}. Retrying...")
                time.sleep(retry_delay)
            else:
                print(f"[FALLBACK] LLM call failed after {max_retries} attempts. Using rule-based action.")
                return fallback_action()
    
    return fallback_action()

def run_episode(task_id: str) -> float:
    """
    Runs a single episode for a given task.
    """
    env = CyberIncidentEnv(task_id=task_id)
    obs = env.reset()
    done = False
    total_reward = 0.0
    step_count = 0
    
    while not done:
        try:
            action = get_defender_action(obs, env.task.goal)
            obs, reward, done, info = env.step(action)
            total_reward += reward
            print(f"[STEP] step={step_count} reward={reward:.2f}")
            step_count += 1
        except KeyboardInterrupt:
            print("\nEpisode interrupted by user.")
            raise
        except Exception as e:
            print(f"Error during step execution: {e}")
            break
        
    final_score = info.get("final_score", 0.0)
    return final_score

def benchmark_task(task_id: str, episodes: int = 5):
    """
    Benchmarks a task over multiple episodes.
    """
    print(f"\n[START] task={task_id} | episodes={episodes}")
    scores = []
    
    for i in range(episodes):
        try:
            print(f"  Episode {i+1}/{episodes}...", end=" ", flush=True)
            score = run_episode(task_id)
            scores.append(score)
            print(f"Score: {score:.2f}")
        except KeyboardInterrupt:
            print(f"\nBenchmark for {task_id} interrupted.")
            break
        except Exception as e:
            print(f"Error: {e}")
            break
        
    if scores:
        mean_score = sum(scores) / len(scores)
        print(f"[END] task={task_id} mean_score={mean_score:.2f} (episodes completed: {len(scores)}/{episodes})")
        return mean_score
    return 0.0

def main():
    print("="*70)
    print("CYBER INCIDENT ENVIRONMENT - BENCHMARK")
    print("="*70)
    print(f"LLM Mode: {'ENABLED' if (client and USE_LLM) else 'DISABLED (using rule-based actions)'}")
    print(f"Model: {MODEL_NAME if (client and USE_LLM) else 'Rule-Based Fallback'}")
    print("="*70)
    
    tasks = ["easy", "medium", "hard"]
    try:
        for task in tasks:
            benchmark_task(task, episodes=5)
    except KeyboardInterrupt:
        print("\nBenchmark process stopped by user.")
    
    print("\n" + "="*70)
    print("BENCHMARK COMPLETE")
    print("="*70)

if __name__ == "__main__":
    main()
