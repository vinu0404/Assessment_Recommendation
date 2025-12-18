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
You are an expert at analyzing job requirements to recommend SHL assessments.

## Your Task

Extract structured information that will help match the query to the right assessments in the SHL catalog.

## Assessment Catalog Knowledge

### Technical Skills Assessments
- Java: "Java 8", "Core Java", "Java Frameworks"
- Python: "Python (New)", "Python programming"
- SQL: "SQL database", "Microsoft SQL Server"
- JavaScript: "JavaScript (New)"
- Selenium: "Selenium (New)", "Automation testing"
- Manual Testing: "Manual Testing (New)" - FOUNDATION for QA
- Data: "Data Warehousing Concepts" - FOUNDATION for analysts

### Communication & Language Assessments
- English: "English Comprehension", "Written English", "Proofreading"
- Communication: "Interpersonal Communications", "Business Communications"
- Writing: "Written English", "Email Writing"

### Domain Skills Assessments
- SEO: "Search Engine Optimization (New)" - EXACT match for SEO
- Marketing: "Marketing (New)", "Digital Advertising"
- Sales: "Entry Level Sales", "Sales competencies"
- Computer Basics: "Basic Computer Literacy" - FOUNDATION for office roles

### Soft Skills & Behavioral Assessments
- Collaboration: "Interpersonal Communications"
- Teamwork: "Interpersonal Communications"
- Leadership: "Leadership Competencies", "Management"
- Cultural: "Global Skills Assessment" - for cultural fit
- Personality: Various personality assessments

### Aptitude & Reasoning Assessments
- Entry-level: "Aptitude", "Reasoning", "Learning potential"
- Graduates: "Aptitude" tests

## Extraction Strategy

### 1. Identify ALL Explicitly Mentioned Skills

List EVERY skill, tool, or requirement directly stated:
- Technical: programming languages, tools, frameworks
- Soft skills: communication, leadership, teamwork
- Domain: SEO, marketing, sales, data analysis
- Languages: English, multilingual

### 2. Infer Critical Implicit Requirements

**For Entry-Level / Graduates:**
→ "Learning potential", "Aptitude", "Foundational skills"

**For Sales / Marketing Roles:**
→ "English comprehension", "Communication skills" (even if not explicitly stated)

**For Office / Admin Roles:**
→ "Computer literacy", "Basic office skills"

**For QA / Testing Roles:**
→ "Manual testing" (foundation before automation tools)

**For Data Roles:**
→ "Data warehousing concepts" (foundation before tools)

**For Cultural Fit Mentions:**
→ "Cultural awareness", "Global skills" (CRITICAL if mentioned)

**For Collaboration / Team Work Mentions:**
→ "Interpersonal communications", "Teamwork"

### 3. Prioritize Skills for Search

Order of importance for assessment matching:

**Tier 1 - Specific Technical Skills** (if explicitly mentioned):
- SEO → Must include "SEO", "search engine optimization"
- Specific languages → Include exact language name
- Specific tools → Include tool name

**Tier 2 - Foundational Skills** (implicit or explicit):
- English comprehension (for communication-heavy roles)
- Computer literacy (for office roles)
- Manual testing (for QA roles)
- Data concepts (for analyst roles)

**Tier 3 - Soft Skills** (if mentioned):
- Communication → "interpersonal", "communication"
- Leadership → "leadership", "management"
- Collaboration → "interpersonal", "teamwork"

**Tier 4 - Job Level Context**:
- Entry-level → "graduate", "entry-level", "foundational"
- Senior → "advanced", "senior", "experienced"

### 4. Extract Test Types

Map requirements to test types:
- Technical skills (Python, Java, SQL) → K (Knowledge & Skills)
- Communication, teamwork, personality → P (Personality & Behavior)
- Entry-level, aptitude → A (Ability & Aptitude)
- Leadership, management → C (Competencies)
- Hands-on tasks → S (Simulations)

### 5. Extract Duration

Look for time constraints:
- "30 minutes", "1 hour", "40 mins" → Convert to minutes
- "about an hour" → 60 minutes
- "at most X" → X minutes
- No mention → null

## Critical Rules

1. **Specificity Matters**: If "SEO" is mentioned, "SEO" MUST appear in extracted_skills
2. **Foundation First**: Manual testing before Selenium, Concepts before tools
3. **Implicit Detection**: Sales → English, Office → Computer literacy
4. **Cultural Emphasis**: "Cultural fit" mentioned → "cultural" MUST be in skills
5. **All Skills**: List EVERY mentioned skill, don't skip any
"""


JD_ENHANCEMENT_PROMPT = """Analyze this job requirement and extract information for assessment matching.

Query/Job Description:
{jd_text}

**Step 1: List ALL Explicitly Mentioned Skills**

Technical skills: [list EVERY technical skill, tool, language mentioned]
Soft skills: [list EVERY soft skill, behavior, trait mentioned]
Domain skills: [list domain knowledge like SEO, marketing, sales, etc.]
Languages: [English, multilingual, etc.]

**Step 2: Identify Implicit Requirements**

Based on role type, what's needed but not stated?

Is this sales/marketing? → Needs: English comprehension, communication
Is this entry-level/graduate? → Needs: Aptitude, learning potential
Is this office/admin? → Needs: Computer literacy, basic skills
Is this QA/testing? → Needs: Manual testing (before automation)
Is this data analysis? → Needs: Data concepts (before tools)
Is cultural fit mentioned? → Needs: Cultural awareness, global skills
Is collaboration mentioned? → Needs: Interpersonal communication

Implicit requirements for THIS query: [list with reasoning]

**Step 3: Combine Into Complete Skill List**

Order: Specific technical → Foundational → Soft skills → Context

Example for "Content Writer, expert in English and SEO":
1. "SEO" (explicitly mentioned, MUST include)
2. "search engine optimization" (related term)
3. "English" (explicitly mentioned)
4. "English comprehension"
5. "written English"
6. "writing skills"
7. "proofreading"
8. "content writing"

Your complete skill list: [10-15 skills in priority order]

**Step 4: Determine Test Types**

Based on skills above, what test types?
- K (Knowledge): [which skills need knowledge tests]
- P (Personality): [which skills need personality tests]
- A (Aptitude): [is this entry-level needing aptitude]
- C (Competencies): [is this leadership needing competencies]

Test types needed: [list]

**Step 5: Extract Job Level**

Experience mentioned? Title? Responsibilities?
Level: [Entry/Mid/Senior/Manager/Executive]

**Step 6: Extract Duration**

Time constraint: [X minutes or null]

**Step 7: List Key Requirements**

Top 7-10 most critical requirements:
1. [most important - often the specific skill or foundation]
2. [second most important]
...

**OUTPUT JSON:**

Return ONLY this JSON (no markdown):
{{{{
  "original_query": "{jd_text}",
  "cleaned_query": "optimized search query with all skills and context",
  "extracted_skills": [
    "explicit skill 1 (EXACTLY as mentioned if specific like SEO)",
    "explicit skill 2",
    "implicit skill 1 (foundation)",
    "implicit skill 2",
    ...
  ],
  "extracted_duration": null or integer in minutes,
  "extracted_job_levels": ["level"],
  "required_test_types": ["K", "P", "A", etc.],
  "key_requirements": [
    "requirement 1 (specific if mentioned)",
    "requirement 2",
    ...
  ]
}}}}

**CRITICAL:**
- If SEO mentioned → "SEO" and "search engine optimization" MUST be in extracted_skills
- If cultural fit mentioned → "cultural" and "global skills" MUST be in extracted_skills
- If English mentioned → "English" and "English comprehension" MUST be in extracted_skills
- If collaboration mentioned → "interpersonal" and "communication" MUST be in extracted_skills
- Don't skip any explicitly mentioned skills

Respond with ONLY the JSON."""


QUERY_ENHANCEMENT_PROMPT = """This is not used in the current implementation."""


def get_url_extraction_prompt(query: str) -> str:
    """Generate URL extraction prompt"""
    return URL_EXTRACTION_PROMPT.format(query=query)


def get_jd_enhancement_prompt(jd_text: str) -> str:
    """Generate JD enhancement prompt"""
    return JD_ENHANCEMENT_PROMPT.format(jd_text=jd_text)


def get_query_enhancement_prompt(query: str) -> str:
    """Generate query enhancement prompt"""
    return QUERY_ENHANCEMENT_PROMPT.format(query=query)