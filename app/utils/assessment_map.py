def get_assessment_map() -> dict:
    """Return mapping of keywords to assessment names"""
    assessment_mappings = {
                    # Technical Skills
                    'java': 'Java programming assessment',
                    'python': 'Python programming assessment',
                    'sql': 'SQL database assessment',
                    'javascript': 'JavaScript assessment',
                    'selenium': 'Selenium automation testing',
                    'manual testing': 'manual testing assessment QA',
                    
                    # Soft Skills
                    'communication': 'interpersonal communication business communication',
                    'collaboration': 'interpersonal communication teamwork',
                    'interpersonal': 'interpersonal communication',
                    'teamwork': 'interpersonal communication collaboration',
                    
                    # Language Skills
                    'english': 'English comprehension English language written English',
                    'writing': 'written English writing skills proofreading',
                    
                    # Domain Skills
                    'seo': 'search engine optimization SEO',
                    'marketing': 'marketing assessment',
                    'sales': 'sales assessment entry-level sales',
                    'entry-level': 'aptitude learning potential entry-level',
                    'graduate': 'graduate assessment aptitude learning potential',
                    'computer literacy': 'computer literacy basic computer Windows',
                    'cultural fit': 'cultural awareness global skills international',
                    'cultural': 'global skills cultural assessment',
                    'leadership': 'leadership competencies management',
                    'coo': 'executive leadership strategic',
                    'executive': 'executive leadership senior management',
                    'data analyst': 'data warehousing data analysis SQL Excel',
                    'data': 'data warehousing data analysis',
                }
    return assessment_mappings
                    


def get_fallback_skill()->list:
    """Return list of fallback skill keywords"""
    return [
            'java', 'python', 'sql', 'javascript', 'communication',
            'leadership', 'sales', 'marketing', 'data', 'analyst',
            'seo', 'english', 'writing', 'cultural', 'testing'
        ]