"""
Test suite for Cyber Incident Response OpenEnv
"""
import pytest
from env.environment import CyberIncidentEnv
from env.models import HostStatus, Alert, Action
from env.tasks import TASKS, Task


class TestEnvironmentInitialization:
    """Test environment initialization for different tasks"""
    
    def test_environment_creates_with_easy_task(self):
        """Test that environment initializes with easy task"""
        env = CyberIncidentEnv(task_id="easy")
        assert env.task_id == "easy"
        assert env.max_steps == 10
        
    def test_environment_creates_with_medium_task(self):
        """Test that environment initializes with medium task"""
        env = CyberIncidentEnv(task_id="medium")
        assert env.task_id == "medium"
        assert env.max_steps == 20
        
    def test_environment_creates_with_hard_task(self):
        """Test that environment initializes with hard task"""
        env = CyberIncidentEnv(task_id="hard")
        assert env.task_id == "hard"
        assert env.max_steps == 30
        
    def test_default_task_is_easy(self):
        """Test that default task is easy"""
        env = CyberIncidentEnv()
        assert env.task_id == "easy"


class TestEnvironmentReset:
    """Test environment reset functionality"""
    
    def test_reset_initializes_hosts(self):
        """Test that reset initializes all hosts"""
        env = CyberIncidentEnv()
        env.reset()
        
        assert len(env.hosts) == 4
        assert "workstation_1" in env.hosts
        assert "workstation_2" in env.hosts
        assert "file_server" in env.hosts
        assert "db_server" in env.hosts
        
    def test_reset_sets_initial_infection(self):
        """Test that reset sets initial infection on workstation_1"""
        env = CyberIncidentEnv()
        env.reset()
        
        assert env.hosts["workstation_1"].status == HostStatus.INFECTED
        assert env.hosts["workstation_2"].status == HostStatus.CLEAN
        assert env.hosts["file_server"].status == HostStatus.CLEAN
        assert env.hosts["db_server"].status == HostStatus.CLEAN
        
    def test_reset_creates_initial_alert(self):
        """Test that reset creates initial alert"""
        env = CyberIncidentEnv()
        env.reset()
        
        assert len(env.alerts) > 0
        assert env.alerts[0].host == "workstation_1"
        assert "Suspicious activity" in env.alerts[0].message
        
    def test_reset_returns_observation(self):
        """Test that reset returns valid observation"""
        env = CyberIncidentEnv()
        obs = env.reset()
        
        assert obs.time_step == 0
        assert obs.infected_estimate >= 0
        assert len(obs.network_status) == 4


class TestEnvironmentStep:
    """Test environment step functionality"""
    
    def test_step_increments_time(self):
        """Test that step increments time_step"""
        env = CyberIncidentEnv()
        env.reset()
        
        obs, _, _, _ = env.step({"investigate_host": "workstation_1"})
        assert obs.time_step == 1
        
    def test_step_returns_valid_tuple(self):
        """Test that step returns (obs, reward, done, info)"""
        env = CyberIncidentEnv()
        env.reset()
        
        obs, reward, done, info = env.step({"investigate_host": "workstation_1"})
        
        assert obs is not None
        assert isinstance(reward, (int, float))
        assert isinstance(done, bool)
        assert isinstance(info, dict)
        
    def test_investigate_host_gives_reward(self):
        """Test that investigating a host gives positive reward"""
        env = CyberIncidentEnv()
        env.reset()
        
        _, reward, _, _ = env.step({"investigate_host": "workstation_1"})
        assert reward >= 0.0
        
    def test_step_ends_when_max_steps_reached(self):
        """Test that environment ends when max_steps is reached"""
        env = CyberIncidentEnv(task_id="easy")
        env.reset()
        
        done = False
        for i in range(10):
            obs, reward, done, info = env.step({"investigate_host": "workstation_1"})
            if i < 9:
                assert not done
            else:
                assert done
        
        assert obs.time_step == 10


class TestTaskDefinitions:
    """Test task definitions"""
    
    def test_all_tasks_have_valid_goals(self):
        """Test that all tasks have goals"""
        for task_id, task in TASKS.items():
            assert task.goal is not None
            assert len(task.goal) > 0
            
    def test_all_tasks_have_valid_max_steps(self):
        """Test that all tasks have reasonable max_steps"""
        for task_id, task in TASKS.items():
            assert task.max_steps > 0
            assert task.max_steps >= 5
            
    def test_task_difficulty_progression(self):
        """Test that tasks get progressively harder"""
        easy_steps = TASKS["easy"].max_steps
        medium_steps = TASKS["medium"].max_steps
        hard_steps = TASKS["hard"].max_steps
        
        assert easy_steps < medium_steps < hard_steps


class TestHostOperations:
    """Test host-related operations"""
    
    def test_isolate_infected_host_increases_reward(self):
        """Test that isolating infected host gives reward"""
        env = CyberIncidentEnv()
        env.reset()
        
        _, reward, _, _ = env.step({"isolate_host": "workstation_1"})
        assert reward >= 0.3
        
    def test_isolate_changes_host_status(self):
        """Test that isolate changes host status to ISOLATED"""
        env = CyberIncidentEnv()
        env.reset()
        
        env.step({"isolate_host": "workstation_1"})
        assert env.hosts["workstation_1"].status == HostStatus.ISOLATED
        
    def test_patch_clean_host_gives_reward(self):
        """Test that patching clean host gives reward"""
        env = CyberIncidentEnv()
        env.reset()
        
        _, reward, _, _ = env.step({"patch_host": "workstation_2"})
        assert reward > 0.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
