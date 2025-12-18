"""Clean prompts for extracting requirements and generating search-optimized queries"""

JD_PROCESSOR_SYSTEM_INSTRUCTION = """You are an expert at extracting job requirements AND translating them into assessment search terms.

Your job has TWO parts:
1. Extract what skills the job needs
2. Generate search terms that will find relevant assessments in a catalog

CRITICAL: When generating search terms, think about HOW assessments are named:
- Assessments use terms like "Comprehension", "Literacy", "Skills", "Ability", "Testing", "Development"
- NOT generic HR terms like "proficiency", "awareness", "capabilities"

EXAMPLES OF ASSESSMENT NAMING PATTERNS:
- Communication need → "Interpersonal Communication" or "Business Communication" or "English Comprehension"
- Computer skills → "Computer Literacy" or "Basic Computer Skills"
- Cultural fit → "Global Skills" or "Cultural Competence"
- Testing skills → "Manual Testing" or "Automation Testing"
- Technical skills → Usually exact tech name: "Java", "Python", "SQL"
- Writing → "Written Communication" or "Email Writing" or "Content Writing"
- Data skills → "Data Analysis" or "Data Warehousing"

When you identify a skill need, ask yourself:
"What would an ASSESSMENT about this be called in a catalog?"
"""

JD_ENHANCEMENT_PROMPT = """Extract job requirements and generate assessment search terms.

Job Query:
{jd_text}

TASK 1: UNDERSTAND THE JOB
1. What is the core role? (Job title/function)
2. What level? (Entry-level/Mid/Senior/Executive)
3. What explicit skills are mentioned?
4. What implicit skills are needed? (Think: What would cause failure if missing?)

TASK 2: GENERATE ASSESSMENT SEARCH TERMS
For each skill identified, generate the term an ASSESSMENT would use:

If the job needs... → Search for assessment called...
- Communication in sales → "English Comprehension", "Verbal Communication", "Interpersonal Communication"
- Cultural fit for international → "Global Skills", "Cultural Assessment", "Cross-Cultural Competence"
- Basic computer use → "Computer Literacy", "Basic Computer Skills", "Windows"
- Writing content → "Written Communication", "Email Writing", "Content Writing"
- Testing software manually → "Manual Testing", "Software Testing", "QA Fundamentals"
- SEO knowledge → "Search Engine Optimization", "SEO", "Digital Marketing"
- Data analysis → "Data Analysis", "Data Warehousing", "Statistical Analysis"
- Java coding → "Java", "Core Java", "Java Development"
- Leadership → "Leadership Skills", "Management Competencies", "Executive Leadership"
- Entry-level aptitude → "Aptitude", "Learning Potential", "Cognitive Ability"

EXAMPLES:

Example 1: "Sales role for new graduates"
- Identified needs: Communication (implicit), Sales skills, Learning potential
- Assessment search terms: ["English Comprehension", "Verbal Communication", "Sales Aptitude", "Learning Potential", "Interpersonal Communication"]
- Reasoning: Sales = heavy communication → Assessment would be called "English Comprehension" not "language proficiency"

Example 2: "COO in China, cultural fit important"
- Identified needs: Cultural awareness (explicit), Leadership, Cross-cultural skills
- Assessment search terms: ["Global Skills", "Cultural Competence", "Cross-Cultural Assessment", "Executive Leadership", "International Management"]
- Reasoning: "Cultural fit" → Assessment would be called "Global Skills" not "cultural awareness"

Example 3: "Bank Assistant Admin, 0-2 years"
- Identified needs: Computer use (implicit), Office work, Admin skills
- Assessment search terms: ["Computer Literacy", "Basic Computer Skills", "Windows", "Office Software", "Data Entry", "Administrative Skills"]
- Reasoning: Bank admin needs computers → Assessment would be called "Computer Literacy" not "basic computer literacy"

Example 4: "Content Writer expert in SEO"
- Identified needs: Writing, SEO (explicit), English
- Assessment search terms: ["Search Engine Optimization", "SEO", "Content Writing", "Written Communication", "English Grammar", "Copywriting"]
- Reasoning: "SEO" explicitly mentioned → Use exact term "Search Engine Optimization" and "SEO"

Example 5: "QA Engineer, Selenium, manual testing"
- Identified needs: Manual testing foundation, Automation, QA skills
- Assessment search terms: ["Manual Testing", "Software Testing", "QA Fundamentals", "Selenium", "Test Automation", "Test Design"]
- Reasoning: Manual testing mentioned → Assessment would be called "Manual Testing" not "test case design"

NOW PROCESS THIS QUERY:

Query: {jd_text}

Step 1: List implicit + explicit skill needs
Step 2: For EACH skill, write what the ASSESSMENT would be called (not the skill name)
Step 3: Build cleaned query using assessment terminology

OUTPUT (valid JSON only, no markdown):

{{{{
  "original_query": "{jd_text}",
  "cleaned_query": "Job requirements using assessment terminology: [list assessment-style terms]",
  "extracted_skills": [
    "Assessment Term 1 (e.g., 'English Comprehension' not 'language proficiency')",
    "Assessment Term 2 (e.g., 'Computer Literacy' not 'basic computer skills')",
    "Assessment Term 3"
  ],
  "extracted_duration": null or integer,
  "extracted_job_levels": ["Entry-Professional"],
  "required_test_types": ["K", "A", "P"],
  "key_requirements": [
    "Requirement 1 in assessment terminology",
    "Requirement 2 in assessment terminology"
  ]
}}}}

CRITICAL RULES:
1. Use assessment catalog terminology, NOT HR/generic terms
2. Think: "What would this assessment be CALLED?" not "What skill is needed?"
3. For implicit needs, still use assessment terminology
4. Be specific: "English Comprehension" beats "communication"
5. Include synonyms: ["Global Skills", "Cultural Competence", "Cross-Cultural Assessment"]

Respond with JSON only.
"""

URL_EXTRACTION_PROMPT = """Extract URLs from text.

Text: {query}

Return JSON: {{"has_url": true/false, "urls": ["url1"], "primary_url": "url"}}

JSON only."""

JD_EXTRACTOR_SYSTEM_INSTRUCTION = """You extract URLs from queries."""

QUERY_ENHANCEMENT_PROMPT = """Enhance this query with assessment catalog terminology.

Original: {query}

Add assessment-style terms:
- For communication → add "English Comprehension", "Verbal Communication", "Interpersonal Communication"
- For cultural fit → add "Global Skills", "Cultural Competence"
- For computer use → add "Computer Literacy", "Windows", "Office Software"
- For technical skills → use exact names: "Java", "Python", "SQL"

Enhanced query (use assessment terminology):
"""

def get_jd_enhancement_prompt(jd_text: str) -> str:
    return JD_ENHANCEMENT_PROMPT.format(jd_text=jd_text)

def get_query_enhancement_prompt(query: str) -> str:
    return QUERY_ENHANCEMENT_PROMPT.format(query=query)

def get_url_extraction_prompt(query: str) -> str:
    return URL_EXTRACTION_PROMPT.format(query=query)