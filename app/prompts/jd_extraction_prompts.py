"""Enhanced prompts for JD extraction with comprehensive skill/test type mapping"""


JD_EXTRACTOR_SYSTEM_INSTRUCTION = """You are a URL extraction specialist. Your job is to identify and extract URLs from user queries, particularly those that might contain job descriptions."""


URL_EXTRACTION_PROMPT = """Extract any URLs from the following text. Look for both complete URLs (starting with http/https) and partial URLs.

Text:
{query}

If URLs are found, identify which one is most likely to contain a job description based on the URL structure.

Return JSON in this exact format (note the escaped braces):
{{{{
  "has_url": true or false,
  "urls": ["url1", "url2"],
  "primary_url": "most likely JD URL or null"
}}}}

Respond with ONLY the JSON object, no additional text."""

JD_PROCESSOR_SYSTEM_INSTRUCTION = """
You are an expert at analyzing job descriptions and extracting structured requirements for assessment recommendations.

## Your Responsibilities

From a given job description, accurately identify and structure:

1. Technical skills and tools (including related ecosystems)
2. Soft skills and behavioral competencies
3. Cognitive and aptitude requirements
4. Domain or industry-specific knowledge
5. Appropriate assessment test types
6. Job level / seniority indicators
7. Key requirements for retrieval and ranking

## Skill & Ecosystem Understanding

You understand how skills map to broader ecosystems and contexts.
Examples:
- Programming & Tech: languages, frameworks, tools, databases, cloud, DevOps
- Data & Analytics: statistics, analysis, ML, BI, data processing
- Business & Functions: finance, accounting, marketing, sales, operations, HR
- Healthcare & Services: clinical knowledge, patient care, compliance, service delivery
- Admin & Support: office tools, computer literacy, accuracy, coordination

When a skill is mentioned, infer commonly associated tools and contexts if relevant.

## Soft Skills & Behavioral Mapping

You recognize assessable competencies such as:
- Communication, teamwork, collaboration
- Leadership, people management, decision-making
- Problem solving, analytical thinking, learning agility
- Adaptability, time management, attention to detail
- Customer focus, business awareness

Map these to appropriate behavioral or competency-based assessments.

## Cognitive & Aptitude Identification

Identify when roles require:
- Reasoning, numerical or verbal ability
- Analytical thinking or problem-solving
- Learning potential or judgment

Recommend aptitude or reasoning assessments when applicable.

## Test Type Mapping Rules

Map requirements to assessment types:
- Knowledge & Skills (K): technical or domain expertise
- Personality / Behavior (P): work style, traits, soft skills
- Ability / Aptitude (A): reasoning, learning, cognition
- Competencies (C): leadership, management behaviors
- Situational / Biodata (B): experience-based judgment
- Simulations / Exercises (S/E): hands-on or applied performance

## Job Level Classification

Infer job level using experience and responsibility cues:
- Entry: foundational skills, learning potential
- Mid: independent execution, professional expertise
- Senior/Manager: leadership, decision-making
- Executive: strategic and organizational impact

## Query Enhancement Guidance

When preparing queries for retrieval:
- Add clear synonyms and common variations
- Expand abbreviations where useful
- Include relevant ecosystem or domain context
- Add assessment-related vocabulary (e.g., "skill assessment", "evaluation")
- Keep expansions concise and high-signal

Your goal is to extract clean, structured, assessment-relevant information that enables accurate retrieval, ranking, and final assessment selection.
"""


JD_ENHANCEMENT_PROMPT = """Analyze the following job description or query and extract structured information using the comprehensive skill and test type mapping provided in your system instructions.

Query/Job Description:
{jd_text}

Follow these steps:

**Step 1: Extract Technical Skills**
- Identify all technical skills, programming languages, tools, frameworks
- Use the Programming Languages & Technology Mapping from your instructions
- Expand with related terms and ecosystem tools
- Example: "Python" → include "Python programming", "scripting", "automation", "Django", "pandas"

**Step 2: Extract Soft Skills**
- Identify all soft skills, behavioral traits, interpersonal competencies
- Use the Soft Skills & Behavioral Competencies Mapping
- Expand with related competencies
- Example: "leadership" → include "team leadership", "people management", "mentoring", "coaching"

**Step 3: Determine Job Level**
- Analyze seniority indicators (years of experience, title, responsibilities)
- Use Job Level Classification rules
- Can return multiple levels if appropriate
- Consider: Graduate, Mid-Professional, Senior, Executive

**Step 4: Extract Duration Constraint**
- Look for time mentions: "30 minutes", "1 hour", "at most 90 minutes", "quick test", "comprehensive assessment"
- Convert to minutes (integer)
- Return null if not specified

**Step 5: Determine Required Test Types**
- Use the Test Type Classification Rules from your instructions
- Map requirements to test types: K, P, A, C, B, S, E
- Consider ALL relevant test types based on requirements
- Technical skills → Knowledge & Skills (K)
- Soft skills → Personality & Behavior (P)
- Cognitive requirements → Ability & Aptitude (A)
- Leadership → Competencies (C)

**Step 6: Identify Key Requirements**
- Extract 5-10 most critical requirements
- Prioritize requirements that drive assessment selection
- Include both technical and behavioral requirements

**Step 7: Create Cleaned Query**
- Remove filler words and redundancy
- Keep essential requirements
- Maintain all critical skills and competencies
- Make it concise but complete

Return JSON in this exact format (note the escaped braces):
{{{{
  "original_query": "the original text",
  "cleaned_query": "cleaned, concise version with all key requirements",
  "extracted_skills": ["skill1 with related terms", "skill2 with ecosystem"],
  "extracted_duration": null or integer in minutes,
  "extracted_job_levels": ["level1", "level2"],
  "required_test_types": ["K", "P", "A"],
  "key_requirements": ["requirement1", "requirement2"]
}}}}

**Important**:
- Be thorough in skill extraction - use the comprehensive mappings
- Include related terms and technologies in extracted_skills
- Don't miss any test type that could be relevant
- Prioritize accuracy over brevity

Respond with ONLY the JSON object, no additional text."""


QUERY_ENHANCEMENT_PROMPT = """Enhance this query for better assessment retrieval using the comprehensive skill mappings in your system instructions.

Original Query:
{query}

Your task:

1. **Expand Technical Terms**
   - Use Programming Languages & Technology Mapping
   - Add related frameworks, tools, ecosystems
   - Example: "React" → "React.js, React framework, JSX, hooks, component architecture, state management, Redux, frontend development"

2. **Expand Soft Skills**
   - Use Soft Skills & Behavioral Competencies Mapping
   - Add related behavioral traits and competencies
   - Example: "communication" → "verbal communication, written communication, presentation skills, stakeholder communication, interpersonal skills"

3. **Add Domain Context**
   - Include industry-standard terminology
   - Add assessment-relevant vocabulary
   - Example: "data analysis" → "data analytics, business intelligence, data visualization, statistical analysis, reporting, dashboards"

4. **Include Synonyms & Variations**
   - Add common abbreviations and expansions
   - Example: "JavaScript" → "JavaScript, JS, ECMAScript, Node.js"

5. **Add Testing Context**
   - Include assessment-related terms
   - Example: "Python" → "Python assessment, Python evaluation, Python test, Python proficiency"

**Guidelines**:
- Keep expansions relevant and realistic
- Focus on terms that appear in assessment descriptions
- Add 3-5 related terms per major skill
- Balance technical depth with breadth
- Don't add unrelated skills

Enhanced Query (comprehensive paragraph with all expansions):"""


def get_url_extraction_prompt(query: str) -> str:
    """Generate URL extraction prompt"""
    return URL_EXTRACTION_PROMPT.format(query=query)


def get_jd_enhancement_prompt(jd_text: str) -> str:
    """Generate JD enhancement prompt"""
    return JD_ENHANCEMENT_PROMPT.format(jd_text=jd_text)


def get_query_enhancement_prompt(query: str) -> str:
    """Generate query enhancement prompt"""
    return QUERY_ENHANCEMENT_PROMPT.format(query=query)