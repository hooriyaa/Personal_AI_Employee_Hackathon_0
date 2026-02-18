"""
Skills Package for AI Employee System.

This package provides all the skills available to the AI Employee,
organized by tier following the hackathon architecture:

Core Tier (Required for all):
- File Manager (read/write/list/move/delete)
- Vault Read/Write
- Task Completion

Bronze Tier (Basic automation):
- Plan Generation

Silver Tier (Advanced automation):
- LinkedIn Automation

Gold Tier (Business operations):
- Accounting (Odoo integration)
- Social Media Management
- CEO Briefing Generation

Architecture: Local-First AI Employee with Agent Skills
Security: No credentials/secrets written to vault, HITL for sensitive actions
"""

# =============================================================================
# Core Tier Skills - Required Foundation
# =============================================================================

from src.skills.file_manager_skill import (
    FileManagerSkill,
    read_file,
    write_file,
    list_directory
)

from src.skills.vault_read_skill import read_from_vault
from src.skills.vault_write_skill import write_to_vault
from src.skills.task_completion_skill import move_to_done

# =============================================================================
# Bronze Tier Skills - Basic Automation
# =============================================================================

from src.skills.plan_generation_skill import PlanGenerationSkill

# =============================================================================
# Silver Tier Skills - Advanced Automation
# =============================================================================

from src.skills.linkedin_skill import (
    LinkedInSkill,
    post_linkedin_update
)

# =============================================================================
# Gold Tier Skills - Business Operations
# =============================================================================

from src.skills.accounting_odoo_skill import (
    AccountingOdooSkill,
    create_invoice
)

from src.skills.social_media_skill import (
    SocialMediaSkill,
    post_to_facebook,
    post_to_twitter
)

from src.skills.ceo_briefing_skill import (
    CEOBriefingSkill,
    generate_ceo_briefing,
    get_business_goals,
    get_financial_summary
)

# =============================================================================
# Skill Registry (Dynamic Loading)
# =============================================================================

from src.skills.registry import (
    SkillRegistry,
    get_registry,
    register_all_skills,
    execute_skill,
    list_all_skills
)

# =============================================================================
# Legacy Skill Registry (Backward Compatibility)
# =============================================================================

SKILL_REGISTRY = {
    # Core Tier
    "file_manager": FileManagerSkill,
    "read_file": read_file,
    "write_file": write_file,
    "list_directory": list_directory,
    "vault_read": read_from_vault,
    "vault_write": write_to_vault,
    "move_to_done": move_to_done,

    # Bronze Tier
    "plan_generation": PlanGenerationSkill,

    # Silver Tier
    "linkedin": LinkedInSkill,
    "post_linkedin_update": post_linkedin_update,

    # Gold Tier
    "accounting_odoo": AccountingOdooSkill,
    "create_invoice": create_invoice,
    "social_media": SocialMediaSkill,
    "post_to_facebook": post_to_facebook,
    "post_to_twitter": post_to_twitter,
    "ceo_briefing": CEOBriefingSkill,
    "generate_ceo_briefing": generate_ceo_briefing,
    "get_business_goals": get_business_goals,
    "get_financial_summary": get_financial_summary,
}


def get_all_skills():
    """
    Get all available skills.

    Returns:
        dict: Dictionary of skill names to skill classes/functions
    """
    return SKILL_REGISTRY.copy()


def get_skill(skill_name: str):
    """
    Get a specific skill by name.

    Args:
        skill_name: Name of the skill to retrieve

    Returns:
        Skill class or function, or None if not found
    """
    return SKILL_REGISTRY.get(skill_name)


def get_skills_by_tier(tier: str):
    """
    Get skills filtered by tier.

    Args:
        tier: Tier name ('core', 'bronze', 'silver', 'gold')

    Returns:
        dict: Dictionary of skills for the specified tier
    """
    tier_skills = {
        "core": [
            "file_manager", "read_file", "write_file", "list_directory",
            "vault_read", "vault_write", "move_to_done"
        ],
        "bronze": ["plan_generation"],
        "silver": ["linkedin", "post_linkedin_update"],
        "gold": [
            "accounting_odoo", "create_invoice", "social_media", "post_to_facebook",
            "post_to_twitter", "ceo_briefing",
            "generate_ceo_briefing", "get_business_goals", "get_financial_summary"
        ]
    }

    skill_names = tier_skills.get(tier.lower(), [])
    return {name: SKILL_REGISTRY[name] for name in skill_names if name in SKILL_REGISTRY}


# =============================================================================
# Skill Initialization Helper
# =============================================================================

def initialize_skills():
    """
    Initialize all skill instances.

    Returns:
        dict: Dictionary of initialized skill instances
    """
    initialized = {}

    # Initialize class-based skills
    for name, skill_class in SKILL_REGISTRY.items():
        if isinstance(skill_class, type):  # It's a class
            try:
                initialized[name] = skill_class()
            except Exception as e:
                print(f"Warning: Failed to initialize skill '{name}': {e}")
        else:
            # It's a function, store as-is
            initialized[name] = skill_class

    return initialized


# =============================================================================
# Tier Validation Helper
# =============================================================================

def validate_tier_requirements(tier: str) -> dict:
    """
    Validate that all required skills for a tier are available.

    Args:
        tier: Tier to validate ('bronze', 'silver', 'gold')

    Returns:
        dict: Validation result with status and missing skills
    """
    requirements = {
        "bronze": ["plan_generation"],
        "silver": ["plan_generation", "linkedin"],
        "gold": [
            "plan_generation", "linkedin", "accounting_odoo",
            "social_media", "ceo_briefing"
        ]
    }

    required = requirements.get(tier.lower(), [])
    missing = [name for name in required if name not in SKILL_REGISTRY]

    return {
        "tier": tier,
        "valid": len(missing) == 0,
        "required_skills": required,
        "missing_skills": missing,
        "available_skills": [name for name in required if name in SKILL_REGISTRY]
    }


# =============================================================================
# Public API
# =============================================================================

__all__ = [
    # Core Tier
    'FileManagerSkill',
    'read_file',
    'write_file',
    'list_directory',
    'read_from_vault',
    'write_to_vault',
    'move_to_done',

    # Bronze Tier
    'PlanGenerationSkill',

    # Silver Tier
    'LinkedInSkill',
    'post_linkedin_update',

    # Gold Tier
    'AccountingOdooSkill',
    'create_invoice',
    'SocialMediaSkill',
    'post_to_facebook',
    'post_to_twitter',
    'CEOBriefingSkill',
    'generate_ceo_briefing',
    'get_business_goals',
    'get_financial_summary',

    # Registry
    'SkillRegistry',
    'get_registry',
    'register_all_skills',
    'execute_skill',
    'list_all_skills',

    # Legacy Registry
    'SKILL_REGISTRY',
    'get_all_skills',
    'get_skill',
    'get_skills_by_tier',
    'initialize_skills',
    'validate_tier_requirements',
]
