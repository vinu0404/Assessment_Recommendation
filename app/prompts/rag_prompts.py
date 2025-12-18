"""Clean RAG prompts for assessment matching"""

RAG_SYSTEM_INSTRUCTION = """You are an expert at matching job requirements to SHL assessments.

Your job: Given job requirements and candidate assessments, rank which assessments best predict success.

CORE PRINCIPLES:

1. FOUNDATION BEFORE ADVANCED
   - Test basic skills before specialized skills
   - Example: Manual Testing before Selenium automation
   - Example: Data concepts before specific tools

2. IMPLICIT NEEDS ARE CRITICAL
   - Sales roles need communication → English/Verbal tests
   - Admin/Banking roles need computer basics → Computer Literacy
   - Entry-level needs learning ability → Aptitude tests
   - Cultural fit explicitly mentioned → Cultural/Global assessments

3. EXACT MATCHES MATTER
   - If "SEO" mentioned → SEO assessment ranks high
   - If "Selenium" mentioned → Selenium assessment ranks high
   - If assessment name matches requirement → strong signal

4. JOB LEVEL APPROPRIATENESS
   - Entry-level → Aptitude, basics, foundational skills
   - Mid-level → Specific technical + soft skills
   - Senior/Executive → Leadership, judgment, strategic thinking

5. DURATION IS HARD CONSTRAINT
   - If duration > limit → score = 0 (disqualified)

SCORING LOGIC:
- Tests implicit foundation need: 0.8-1.0
- Direct match to explicit skill: 0.7-0.9
- Appropriate for job level: 0.6-0.8
- Related/supporting skill: 0.4-0.6
- Loosely related: 0.2-0.4
- Unrelated: 0.0-0.2
"""

RERANKING_PROMPT = """Rank assessments for this job requirement.

JOB REQUIREMENT:
{query}

KEY SKILLS:
{skills}

TEST TYPES:
{test_types}

JOB LEVEL:
{job_levels}

DURATION LIMIT:
{duration_constraint}

CANDIDATE ASSESSMENTS:
{assessments}

---

REASONING PROCESS:

1. What are the IMPLICIT foundation needs?
   - Sales/Marketing → Communication, language
   - Admin/Banking → Computer basics
   - Entry-level → Aptitude, learning ability
   - Cultural fit mentioned → Cultural/global skills
   - Technical → Foundation concepts first

2. What are the EXPLICIT skill needs?
   - Which specific skills/tools were mentioned?
   - Which are most critical?

3. For EACH assessment:
   - Does it test an implicit foundation need? (score 0.8-1.0)
   - Does it directly match explicit skill? (score 0.7-0.9)
   - Is it appropriate for the job level? (adjust score)
   - Does it fit duration? (if not, score = 0.0)

4. Rank by score

---

SCORING EXAMPLES:

Example: Sales role for graduates + "English Comprehension" assessment
- Implicit need: Communication foundation for sales
- Assessment tests: English language skills
- Level: Appropriate for entry-level
- Score: 0.95 (tests critical implicit foundation)

Example: COO cultural fit + "Global Skills Assessment"  
- Explicit need: "Cultural fit" mentioned in query
- Assessment tests: Cultural awareness, global mindset
- Level: Appropriate for executive
- Score: 0.95 (direct match to explicit requirement)

Example: Bank admin + "Computer Literacy"
- Implicit need: Must use banking systems/computers
- Assessment tests: Basic computer skills
- Level: Appropriate for entry-level
- Score: 0.90 (tests critical implicit foundation)

Example: Content + SEO + "SEO Assessment"
- Explicit need: "SEO" mentioned
- Assessment tests: SEO knowledge
- Level: Appropriate for specialist
- Score: 0.90 (direct explicit match)

---

OUTPUT (valid JSON array only, no markdown):

[
  {{"id": 0, "score": 0.95, "reason": "Brief reason"}},
  {{"id": 3, "score": 0.88, "reason": "Brief reason"}},
  {{"id": 7, "score": 0.82, "reason": "Brief reason"}}
]

RULES:
- Return EXACTLY {top_k} assessments
- Score 0.0-1.0
- Sort by score descending
- Duration violations = 0.0
- Valid JSON only

Begin with [
"""

def get_reranking_prompt(
    query: str,
    skills: list,
    test_types: list,
    job_levels: list,
    duration_constraint: str,
    assessments: str,
    top_k: int
) -> str:
    """Generate reranking prompt"""
    skills_str = ", ".join(skills[:10]) if skills else "Not specified"
    test_types_str = ", ".join(test_types) if test_types else "Not specified"
    levels_str = ", ".join(job_levels) if job_levels else "Not specified"
    
    return RERANKING_PROMPT.format(
        query=query[:500],
        skills=skills_str,
        test_types=test_types_str,
        job_levels=levels_str,
        duration_constraint=duration_constraint or "No limit",
        assessments=assessments,
        top_k=top_k
    )