"""
Skill Registry - Central registration and management of Agent Skills.

This module provides a centralized registry for all Agent Skills in the system.
It enables dynamic skill loading, discovery, and execution following the
hackathon architecture requirements.

Architecture:
- Skills are registered with metadata (name, tier, description, functions)
- Skills can be loaded dynamically by name
- Registry enforces tier boundaries (Bronze/Silver/Gold)
- All skill executions are logged for audit purposes
"""

import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field


@dataclass
class SkillRegistration:
    """Represents a registered skill with its metadata."""
    name: str
    tier: str  # "Core", "Bronze", "Silver", "Gold"
    description: str
    module_path: str
    class_name: str
    hitl_required: bool
    functions: List[str] = field(default_factory=list)
    instance: Any = None
    enabled: bool = True
    registered_at: str = field(default_factory=lambda: datetime.now().isoformat())


class SkillRegistry:
    """
    Central registry for all Agent Skills.
    
    Provides:
    - Skill registration and discovery
    - Dynamic skill loading
    - Tier-based filtering
    - Execution logging and audit
    """

    def __init__(self):
        """Initialize the skill registry."""
        self._skills: Dict[str, SkillRegistration] = {}
        self._logger = logging.getLogger(__name__)
        self._execution_log: List[Dict[str, Any]] = []

    def register(self, name: str, tier: str, description: str,
                 module_path: str, class_name: str,
                 hitl_required: bool = False,
                 functions: Optional[List[str]] = None,
                 enabled: bool = True) -> bool:
        """
        Register a skill with the registry.
        
        Args:
            name: Unique skill name
            tier: Skill tier ("Core", "Bronze", "Silver", "Gold")
            description: Human-readable description
            module_path: Python module path (e.g., "src.skills.linkedin_skill")
            class_name: Class name within the module
            hitl_required: Whether human-in-the-loop approval is required
            functions: List of public function names
            enabled: Whether the skill is enabled
            
        Returns:
            True if registration successful, False otherwise
        """
        if name in self._skills:
            self._logger.warning(f"Skill '{name}' is already registered. Overwriting.")
        
        registration = SkillRegistration(
            name=name,
            tier=tier,
            description=description,
            module_path=module_path,
            class_name=class_name,
            hitl_required=hitl_required,
            functions=functions or [],
            enabled=enabled
        )
        
        self._skills[name] = registration
        self._logger.info(f"Registered skill: {name} (Tier: {tier})")
        return True

    def get(self, name: str) -> Optional[SkillRegistration]:
        """Get a skill registration by name."""
        return self._skills.get(name)

    def get_skill_instance(self, name: str) -> Optional[Any]:
        """
        Get or create a skill instance by name.
        
        Args:
            name: Skill name
            
        Returns:
            Skill instance or None if not found
        """
        registration = self._skills.get(name)
        if not registration:
            self._logger.error(f"Skill '{name}' not found in registry")
            return None
        
        if not registration.enabled:
            self._logger.warning(f"Skill '{name}' is disabled")
            return None
        
        # Return cached instance if available
        if registration.instance is not None:
            return registration.instance
        
        # Dynamically load the skill
        try:
            module = __import__(registration.module_path, fromlist=[registration.class_name])
            skill_class = getattr(module, registration.class_name)
            registration.instance = skill_class()
            self._logger.info(f"Loaded skill instance: {name}")
            return registration.instance
        except Exception as e:
            self._logger.error(f"Failed to load skill '{name}': {e}")
            return None

    def execute(self, name: str, function: str, **kwargs) -> Dict[str, Any]:
        """
        Execute a skill function.
        
        Args:
            name: Skill name
            function: Function name to execute
            **kwargs: Function arguments
            
        Returns:
            Function result dictionary
        """
        start_time = datetime.now()
        
        # Get skill instance
        skill = self.get_skill_instance(name)
        if not skill:
            return {
                "success": False,
                "error": f"Skill '{name}' not found or not loaded"
            }
        
        # Check if function exists
        if not hasattr(skill, function):
            return {
                "success": False,
                "error": f"Function '{function}' not found in skill '{name}'"
            }
        
        # Check HITL requirement
        registration = self._skills.get(name)
        if registration and registration.hitl_required:
            self._logger.warning(f"HITL required for skill '{name}' - ensure approval workflow")
        
        # Execute the function
        try:
            func = getattr(skill, function)
            result = func(**kwargs)
            
            # Log execution
            self._log_execution(name, function, kwargs, result, start_time)
            
            return result
            
        except Exception as e:
            error_result = {
                "success": False,
                "error": str(e)
            }
            self._log_execution(name, function, kwargs, error_result, start_time)
            return error_result

    def _log_execution(self, skill_name: str, function: str, 
                       inputs: Dict, result: Dict, start_time: datetime):
        """Log skill execution for audit purposes."""
        execution_record = {
            "timestamp": start_time.isoformat(),
            "skill_name": skill_name,
            "function": function,
            "inputs": {k: str(v)[:100] for k, v in inputs.items()},  # Truncate for safety
            "success": result.get("success", False),
            "duration_ms": (datetime.now() - start_time).total_seconds() * 1000
        }
        self._execution_log.append(execution_record)
        
        # Keep log size manageable
        if len(self._execution_log) > 1000:
            self._execution_log = self._execution_log[-500:]

    def get_execution_log(self, limit: int = 100) -> List[Dict[str, Any]]:
        """Get recent execution log entries."""
        return self._execution_log[-limit:]

    def list_skills(self, tier: Optional[str] = None, 
                    enabled_only: bool = True) -> List[Dict[str, Any]]:
        """
        List registered skills with optional filtering.
        
        Args:
            tier: Filter by tier (optional)
            enabled_only: Only return enabled skills
            
        Returns:
            List of skill metadata dictionaries
        """
        skills = []
        for name, reg in self._skills.items():
            if enabled_only and not reg.enabled:
                continue
            if tier and reg.tier != tier:
                continue
            
            skills.append({
                "name": reg.name,
                "tier": reg.tier,
                "description": reg.description,
                "hitl_required": reg.hitl_required,
                "functions": reg.functions,
                "enabled": reg.enabled
            })
        
        return skills

    def get_skills_by_tier(self, tier: str) -> List[str]:
        """Get list of skill names for a specific tier."""
        return [
            name for name, reg in self._skills.items()
            if reg.tier == tier and reg.enabled
        ]


# Global registry instance
_registry: Optional[SkillRegistry] = None


def get_registry() -> SkillRegistry:
    """Get the global skill registry instance."""
    global _registry
    if _registry is None:
        _registry = SkillRegistry()
        _register_default_skills(_registry)
    return _registry


def _register_default_skills(registry: SkillRegistry):
    """Register all default skills with the registry."""
    
    # Core Skills (Required for all tiers)
    registry.register(
        name="FileManagerSkill",
        tier="Core",
        description="Secure file operations for Obsidian vault (read/write/list/move/delete)",
        module_path="src.skills.file_manager_skill",
        class_name="FileManagerSkill",
        hitl_required=False,
        functions=["execute", "read_file", "write_file", "list_directory", "move_file", "delete_file"]
    )
    
    registry.register(
        name="VaultReadSkill",
        tier="Core",
        description="Read content from vault files",
        module_path="src.skills.vault_read_skill",
        class_name="read_from_vault",
        hitl_required=False,
        functions=["read_from_vault"]
    )
    
    registry.register(
        name="VaultWriteSkill",
        tier="Core",
        description="Write content to vault files",
        module_path="src.skills.vault_write_skill",
        class_name="write_to_vault",
        hitl_required=False,
        functions=["write_to_vault"]
    )
    
    registry.register(
        name="TaskCompletionSkill",
        tier="Core",
        description="Move processed files from Needs_Action to Done",
        module_path="src.skills.task_completion_skill",
        class_name="move_to_done",
        hitl_required=False,
        functions=["move_to_done"]
    )
    
    # Bronze Tier Skills (Basic automation)
    registry.register(
        name="PlanGenerationSkill",
        tier="Bronze",
        description="Generate structured plans for tasks from Needs_Action",
        module_path="src.skills.plan_generation_skill",
        class_name="PlanGenerationSkill",
        hitl_required=False,
        functions=["execute", "create_plan_from_task", "run_once"]
    )
    
    # Silver Tier Skills (Advanced automation)
    registry.register(
        name="LinkedInSkill",
        tier="Silver",
        description="Automates LinkedIn posting using Selenium with HITL oversight",
        module_path="src.skills.linkedin_skill",
        class_name="LinkedInSkill",
        hitl_required=True,
        functions=["execute", "post_linkedin_update"]
    )
    
    # Gold Tier Skills (Business operations)
    registry.register(
        name="AccountingOdooSkill",
        tier="Gold",
        description="Manage business finances via Odoo (invoices, payments, revenue reports)",
        module_path="src.skills.accounting_odoo_skill",
        class_name="AccountingOdooSkill",
        hitl_required=True,
        functions=["create_invoice", "register_payment", "get_daily_revenue"]
    )
    
    registry.register(
        name="SocialMediaSkill",
        tier="Gold",
        description="Cross-platform social media posting (Facebook, Instagram, X/Twitter) with social summary generation",
        module_path="src.skills.social_media_skill",
        class_name="SocialMediaSkill",
        hitl_required=True,
        functions=[
            "post_to_facebook",
            "post_to_twitter",
            "post_to_instagram",
            "post_to_social_platforms",
            "generate_social_summary",
            "execute_approved_post"
        ]
    )
    
    registry.register(
        name="CEOBriefingSkill",
        tier="Gold",
        description="Generate executive CEO briefings with revenue and bottleneck analysis",
        module_path="src.skills.ceo_briefing_skill",
        class_name="CEOBriefingSkill",
        hitl_required=False,
        functions=["generate_briefing", "get_business_goals", "get_financial_summary"]
    )


def register_all_skills():
    """Initialize and register all skills. Call this at application startup."""
    return get_registry()


def list_all_skills(tier: Optional[str] = None) -> List[Dict[str, Any]]:
    """List all registered skills with optional tier filtering."""
    return get_registry().list_skills(tier)


def execute_skill(skill_name: str, function: str, **kwargs) -> Dict[str, Any]:
    """Execute a skill function by name."""
    return get_registry().execute(skill_name, function, **kwargs)


# Initialize registry on module import
if __name__ != "__main__":
    # Lazy initialization - registry created on first get_registry() call
    pass


if __name__ == "__main__":
    # Test the registry
    print("Testing Skill Registry...")
    print("-" * 50)
    
    registry = get_registry()
    
    # List all skills
    print("\nAll Registered Skills:")
    for skill in registry.list_skills():
        print(f"  - {skill['name']} (Tier: {skill['tier']}, HITL: {skill['hitl_required']})")
    
    # List by tier
    print("\nSilver Tier Skills:")
    for name in registry.get_skills_by_tier("Silver"):
        print(f"  - {name}")
    
    print("\nGold Tier Skills:")
    for name in registry.get_skills_by_tier("Gold"):
        print(f"  - {name}")
    
    # Test skill execution
    print("\nTesting FileManagerSkill execution...")
    result = registry.execute("FileManagerSkill", "list_directory", path=".", pattern="*.py")
    print(f"  Result: {result['success']}, Found {result.get('total_items', 0)} items")
    
    print("\n" + "-" * 50)
    print("Skill Registry test completed!")
