"""HashForge / HashForge Package."""

from .config import AppConfig, load_config
from .profile import Profile, run_profile_wizard
from .generators import generate_base_candidates, extract_date_parts, make_leet
from .mutations import HashcatRule, load_rule_file, transform_candidates_stream
from .hashcat import (
    RuleMetadata,
    discover_rule_files,
    format_rules_table,
    prompt_select_rule,
    estimate_search_space,
    EstimationReport,
)
from .output import stream_candidates_to_file
from .pipeline import run_hashforge_pipeline
from .legacy import (
    CONFIG,
    read_config,
    concats,
    komb,
    print_to_file,
    print_cow,
    version,
    improve_dictionary,
    interactive,
    generate_wordlist_from_profile,
    download_http,
    alectodb_download,
    download_wordlist,
    download_wordlist_http,
    mkdir_if_not_exists,
    get_parser,
    main,
)

__all__ = [
    # Modern HashForge API
    "AppConfig",
    "load_config",
    "Profile",
    "run_profile_wizard",
    "generate_base_candidates",
    "extract_date_parts",
    "make_leet",
    "HashcatRule",
    "load_rule_file",
    "transform_candidates_stream",
    "RuleMetadata",
    "discover_rule_files",
    "format_rules_table",
    "prompt_select_rule",
    "estimate_search_space",
    "EstimationReport",
    "stream_candidates_to_file",
    "run_hashforge_pipeline",
    # Legacy HashForge API
    "CONFIG",
    "read_config",
    "concats",
    "komb",
    "print_to_file",
    "print_cow",
    "version",
    "improve_dictionary",
    "interactive",
    "generate_wordlist_from_profile",
    "download_http",
    "alectodb_download",
    "download_wordlist",
    "download_wordlist_http",
    "mkdir_if_not_exists",
    "get_parser",
    "main",
]
