import re
from typing import List, Dict
from langchain.tools import tool
from app import logger


def detect_parentheses_notation(text: str) -> List[Dict[str, str]]:
    issues                  = []
    lines                   = text.split('\n')
    pattern1                = r'\(\\[a-zA-Z]+(?:\{[^}]*\})*\)'
    pattern2                = r'\(([a-zA-Z](?:_\{?[a-zA-Z0-9]+\}?)?)\)(?=\s|[,;.!?]|$)'

    for line_num, line in enumerate(lines, 1):
        matches1 = re.finditer(pattern1, line)
        for match in matches1:
            matched_text    = match.group(0)
            latex_cmd       = matched_text[1:-1]
            suggestion      = f"${latex_cmd}$"

            issues.append({
                "line"      : line_num,
                "type"      : "parentheses_notation",
                "found"     : matched_text,
                "fix"       : suggestion,
                "context"   : line.strip()[:100]
            })

        matches2 = re.finditer(pattern2, line)
        for match in matches2:
            matched_text    = match.group(0)
            var             = match.group(1)
            skip_words      = ['a', 'A', 'I', 'or', 'of', 'in', 'is', 'as', 'at', 'by', 'to']

            if var in skip_words:
                continue

            context = line[max(0, match.start()-20):min(len(line), match.end()+20)]
            if any(c in context for c in ['=', '+', '-', '*', '/', '^', '\\', 'where', 'with', 'for']):
                suggestion = f"${var}$"
                issues.append({
                    "line"      : line_num,
                    "type"      : "parentheses_single_var",
                    "found"     : matched_text,
                    "fix"       : suggestion,
                    "context"   : line.strip()[:100]
                })

    return issues


def detect_bare_brackets(text: str) -> List[Dict[str, str]]:
    issues                  = []
    lines                   = text.split('\n')
    pattern                 = r'\[\s*(\\[a-zA-Z]+[^\]]{0,200})\s*\]'

    for line_num, line in enumerate(lines, 1):
        matches = re.finditer(pattern, line)
        for match in matches:
            matched_text    = match.group(0)
            equation        = match.group(1)
            suggestion      = f"$$\n{equation}\n$$"

            issues.append({
                "line"      : line_num,
                "type"      : "bare_brackets",
                "found"     : matched_text[:80] + "..." if len(matched_text) > 80 else matched_text,
                "fix"       : suggestion[:80] + "..." if len(suggestion) > 80 else suggestion,
                "context"   : line.strip()[:100]
            })

    return issues


@tool
def validate_latex_formatting(response_text: str) -> dict:
    """
    Validate LaTeX formatting in a response to ensure frontend compatibility.

    This tool checks for:
    1. Forbidden parentheses notation: (\lambda), (\mu), (n), etc.
    2. Bare square brackets: [ equation ] instead of $$ equation $$

    Args:
        response_text: The text response to validate

    Returns:
        dict with:
        - valid: bool - True if no issues found
        - issues_count: int - Total number of issues
        - issues: list - Detailed list of issues with fixes
        - summary: str - Human-readable summary

    Example:
        If response contains "where (\lambda) is the eigenvalue and [ f(x) = x^2 ]":
        Returns: {
            "valid": False,
            "issues_count": 2,
            "issues": [
                {"type": "parentheses_notation", "found": "(\lambda)", "fix": "$\lambda$", ...},
                {"type": "bare_brackets", "found": "[ f(x) = x^2 ]", "fix": "$$ f(x) = x^2 $$", ...}
            ],
            "summary": "Found 2 LaTeX formatting issues that will break frontend rendering..."
        }
    """
    try:
        logger.info("Validating LaTeX formatting in response")

        if not response_text or not isinstance(response_text, str):
            return {
                "valid"         : True,
                "issues_count"  : 0,
                "issues"        : [],
                "summary"       : "No content to validate"
            }

        all_issues = []

        paren_issues    = detect_parentheses_notation(response_text)
        bracket_issues  = detect_bare_brackets(response_text)

        all_issues.extend(paren_issues)
        all_issues.extend(bracket_issues)

        is_valid = len(all_issues) == 0

        if is_valid:
            summary = "✅ All LaTeX formatting is correct! Response is ready to send."
        else:
            summary = f"❌ Found {len(all_issues)} LaTeX formatting issue(s) that will break frontend rendering:\n\n"

            by_type = {}
            for issue in all_issues:
                issue_type = issue["type"]
                if issue_type not in by_type:
                    by_type[issue_type] = []
                by_type[issue_type].append(issue)

            for issue_type, issues in by_type.items():
                type_name = {
                    "parentheses_notation"      : "Parentheses around LaTeX",
                    "parentheses_single_var"    : "Parentheses around variables",
                    "bare_brackets"             : "Bare square brackets"
                }.get(issue_type, issue_type)

                summary += f"\n{len(issues)}x {type_name}:\n"
                for issue in issues[:3]:
                    summary += f"  Line {issue['line']}: '{issue['found']}' → '{issue['fix']}'\n"
                if len(issues) > 3:
                    summary += f"  ... and {len(issues) - 3} more\n"

            summary += "\n🔧 Fix these issues by replacing the 'found' patterns with the 'fix' suggestions."
            summary += "\nThen call this validator again to verify the corrections."

        result = {
            "valid"         : is_valid,
            "issues_count"  : len(all_issues),
            "issues"        : all_issues,
            "summary"       : summary
        }

        logger.info(f"LaTeX validation result: {'PASS' if is_valid else 'FAIL'} ({len(all_issues)} issues)")

        return result

    except Exception as e:
        logger.error(f"Error in validate_latex_formatting: {str(e)}")
        return {
            "valid"         : False,
            "issues_count"  : 0,
            "issues"        : [],
            "summary"       : f"Validator error: {str(e)}"
        }


class LaTeXValidatorTools:
    validate_latex_formatting = validate_latex_formatting
