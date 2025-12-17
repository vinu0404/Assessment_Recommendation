"""
Table and card rendering components for displaying assessments in Chainlit
"""

from typing import List, Dict, Any


def _safe_get(assessment: Dict[str, Any], key: str, default: str = 'N/A') -> str:
    """
    Safely get a value from assessment, handling None and 'None' string
    
    Args:
        assessment: Assessment dictionary
        key: Key to retrieve
        default: Default value if None or 'None'
        
    Returns:
        Value or default
    """
    value = assessment.get(key)
    if value is None or value == 'None' or value == '':
        return default
    return value


def render_assessment_list(assessments: List[Dict[str, Any]]) -> str:
    """
    Render multiple assessments as a compact list
    
    Args:
        assessments: List of assessment dictionaries
        
    Returns:
        Formatted markdown string
    """
    if not assessments:
        return "No assessments to display."
    
    lines = []
    
    for idx, assessment in enumerate(assessments, 1):
        name = assessment.get('name', 'Unknown')
        test_types = ', '.join(assessment.get('test_type', []))
        duration = assessment.get('duration')
        url = assessment.get('url', '')
        remote_support = assessment.get('remote_support', 'No')
        adaptive_support = assessment.get('adaptive_support', 'No')
        
        if duration and duration != 'None' and duration != '':
            duration_str = f"{duration} min"
        else:
            duration_str = "N/A"
        
        line = f"{idx}. **{name}** | {test_types or 'N/A'} | {duration_str} | {remote_support} | {adaptive_support} | [Link]({url})"
        lines.append(line)
    
    return "\n".join(lines)


def render_assessment_table(assessments: List[Dict[str, Any]]) -> str:
    """
    Render assessments as a markdown table
    
    Args:
        assessments: List of assessment dictionaries
        
    Returns:
        Formatted markdown table string
    """
    if not assessments:
        return "No assessments to display."
    
    table_lines = [
        "| # | Assessment | Test Type | Duration | Job Levels | Remote | Adaptive | Link |",
        "|---|------------|-----------|----------|------------|--------|----------|------|"
    ]
    
    for idx, assessment in enumerate(assessments, 1):
        name = assessment.get('name', 'Unknown')
        test_types = ', '.join(assessment.get('test_type', [])[:2]) 
        duration = assessment.get('duration')
        job_levels = _safe_get(assessment, 'job_levels')
        remote = _safe_get(assessment, 'remote_support')
        url = assessment.get('url', '')
        adaptive = _safe_get(assessment, 'adaptive_support')

        
        if duration and duration != 'None' and duration != '':
            duration_str = f"{duration} min"
        else:
            duration_str = "Not specified"
        if len(name) > 40:
            name = name[:37] + "..."
        
        if len(test_types) > 30:
            test_types = test_types[:27] + "..."
        elif not test_types:
            test_types = "N/A"
        
        if len(str(job_levels)) > 40:
            job_levels = str(job_levels)[:37] + "..."
        
        link = f"[View]({url})"
        
        row = f"| {idx} | {name} | {test_types} | {duration_str} | {job_levels} | {remote} | {adaptive} | {link} |"
        table_lines.append(row)
    
    return "\n".join(table_lines)


def render_summary_stats(assessments: List[Dict[str, Any]]) -> str:
    """
    Render summary statistics for assessments
    
    Args:
        assessments: List of assessment dictionaries
        
    Returns:
        Formatted summary string
    """
    if not assessments:
        return "No assessments to summarize."
    
    total = len(assessments)
    
    test_type_counts = {}
    for assessment in assessments:
        for test_type in assessment.get('test_type', []):
            test_type_counts[test_type] = test_type_counts.get(test_type, 0) + 1
    
    remote_count = sum(1 for a in assessments if a.get('remote_support') == 'Yes')
    adaptive_count = sum(1 for a in assessments if a.get('adaptive_support') == 'Yes')
    
    durations = []
    for a in assessments:
        dur = a.get('duration')
        if dur and dur != 'None' and dur != '':
            try:
                durations.append(float(dur))
            except (ValueError, TypeError):
                pass
    
    avg_duration = sum(durations) / len(durations) if durations else 0
    summary = f"""**Summary Statistics:**

- Total Assessments: {total}
- Remote Support: {remote_count} ({remote_count/total*100:.0f}%)
- Adaptive Support: {adaptive_count} ({adaptive_count/total*100:.0f}%)
"""
    
    if avg_duration > 0:
        summary += f"- Average Duration: {avg_duration:.0f} minutes\n"
    
    if test_type_counts:
        summary += "\n**Test Type Distribution:**\n"
        for test_type, count in sorted(test_type_counts.items(), key=lambda x: x[1], reverse=True):
            summary += f"- {test_type}: {count}\n"
    
    return summary
