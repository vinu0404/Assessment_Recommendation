def get_assessment_map() -> dict:
    """
    Return comprehensive mapping of keywords to assessment names
    
    Each mapping includes:
    - Primary keyword variations
    - Assessment-specific terminology
    - Related concepts for better vector retrieval
    """
    
    assessment_mappings = {
        # ==================== PROGRAMMING LANGUAGES ====================
        'java': 'Java programming Java 8 Core Java Java development object-oriented',
        'python': 'Python programming Python development scripting automation pandas',
        'javascript': 'JavaScript JS ECMAScript Node.js frontend development',
        'sql': 'SQL database query writing data management relational database',
        'c++': 'C++ programming object-oriented systems programming',
        'c#': 'C# .NET programming Microsoft development',
        'php': 'PHP web development server-side scripting',
        'ruby': 'Ruby programming Ruby on Rails web development',
        'scala': 'Scala programming functional programming JVM',
        'kotlin': 'Kotlin Android development JVM programming',
        'swift': 'Swift iOS development Apple programming',
        'go': 'Go golang Google programming concurrent',
        'rust': 'Rust systems programming memory safety',
        'r programming': 'R statistical programming data analysis',
        
        # ==================== WEB & FRONTEND ====================
        'react': 'React.js JavaScript frontend component framework',
        'angular': 'Angular TypeScript frontend framework SPA',
        'vue': 'Vue.js JavaScript frontend reactive framework',
        'html': 'HTML markup web development frontend',
        'css': 'CSS styling web design frontend',
        'typescript': 'TypeScript JavaScript static typing',
        'jquery': 'jQuery JavaScript library DOM manipulation',
        'bootstrap': 'Bootstrap CSS framework responsive design',
        
        # ==================== BACKEND & FRAMEWORKS ====================
        'node': 'Node.js JavaScript backend server-side',
        'express': 'Express.js Node.js web framework backend',
        'django': 'Django Python web framework backend',
        'flask': 'Flask Python micro framework backend',
        'spring': 'Spring framework Java enterprise backend',
        'hibernate': 'Hibernate ORM Java persistence',
        '.net': '.NET Microsoft framework C# development',
        'asp.net': 'ASP.NET web framework Microsoft',
        
        # ==================== DATABASES ====================
        'mysql': 'MySQL database SQL relational RDBMS',
        'postgresql': 'PostgreSQL database SQL relational',
        'mongodb': 'MongoDB NoSQL database document store',
        'oracle': 'Oracle database SQL enterprise RDBMS',
        'sql server': 'SQL Server Microsoft database RDBMS',
        'redis': 'Redis cache in-memory database NoSQL',
        'cassandra': 'Cassandra NoSQL distributed database',
        'database': 'database management SQL NoSQL data storage',
        
        # ==================== DATA SCIENCE & ML ====================
        'machine learning': 'machine learning ML AI data science algorithms',
        'ml': 'machine learning ML artificial intelligence',
        'ai': 'artificial intelligence AI machine learning deep learning',
        'nlp': 'natural language processing NLP text analysis linguistics',
        'computer vision': 'computer vision image processing visual recognition',
        'deep learning': 'deep learning neural networks AI ML',
        'tensorflow': 'TensorFlow machine learning deep learning framework',
        'pytorch': 'PyTorch machine learning deep learning framework',
        'data science': 'data science machine learning analytics statistics',
        'data analysis': 'data analysis analytics statistics business intelligence',
        'data analyst': 'data analysis data warehousing SQL Excel analytics business intelligence',
        'data warehousing': 'data warehousing ETL data modeling analytics',
        'etl': 'ETL data integration data warehousing pipeline',
        'big data': 'big data Hadoop Spark distributed computing',
        'hadoop': 'Hadoop big data distributed processing',
        'spark': 'Apache Spark big data processing analytics',
        
        # ==================== TESTING & QA ====================
        'qa': 'quality assurance testing manual testing test cases',
        'quality assurance': 'QA testing quality control test automation',
        'testing': 'software testing QA quality assurance test cases',
        'manual testing': 'manual testing QA test cases quality assurance foundational',
        'automation testing': 'test automation Selenium automated testing',
        'selenium': 'Selenium automation testing WebDriver test automation',
        'junit': 'JUnit unit testing Java test framework',
        'testng': 'TestNG testing framework Java automation',
        'cucumber': 'Cucumber BDD testing Gherkin',
        'test automation': 'test automation Selenium automated testing QA',
        
        # ==================== DEVOPS & CLOUD ====================
        'devops': 'DevOps CI/CD automation deployment infrastructure',
        'aws': 'AWS Amazon cloud computing infrastructure',
        'azure': 'Microsoft Azure cloud computing platform',
        'gcp': 'Google Cloud Platform GCP cloud computing',
        'cloud': 'cloud computing AWS Azure infrastructure',
        'docker': 'Docker containerization DevOps deployment',
        'kubernetes': 'Kubernetes container orchestration K8s DevOps',
        'jenkins': 'Jenkins CI/CD automation DevOps pipeline',
        'git': 'Git version control source control GitHub',
        'ci/cd': 'CI/CD continuous integration deployment automation',
        
        # ==================== OFFICE & PRODUCTIVITY ====================
        'excel': 'Microsoft Excel spreadsheet data analysis formulas',
        'ms excel': 'Microsoft Excel spreadsheet analysis pivot tables',
        'word': 'Microsoft Word document processing writing',
        'powerpoint': 'PowerPoint presentation slides Microsoft Office',
        'ms office': 'Microsoft Office Excel Word PowerPoint productivity',
        'office': 'Microsoft Office productivity software business applications',
        'computer literacy': 'computer literacy basic computer Windows Office skills foundational',
        'computer skills': 'computer skills computer literacy Office software',
        'windows': 'Windows operating system Microsoft computer literacy',
        
        # ==================== PROJECT MANAGEMENT ====================
        'jira': 'Jira project management agile tracking',
        'confluence': 'Confluence documentation collaboration wiki',
        'agile': 'Agile Scrum methodology project management',
        'scrum': 'Scrum Agile sprint methodology',
        'project management': 'project management planning coordination delivery',
        'sdlc': 'SDLC software development lifecycle project management',
        'product manager': 'product management roadmap strategy prioritization',
        'product management': 'product strategy roadmap stakeholder management',
        
        # ==================== SOFT SKILLS ====================
        'communication': 'interpersonal communication business communication verbal written',
        'interpersonal': 'interpersonal communication collaboration relationship building',
        'collaboration': 'interpersonal communication teamwork collaboration cross-functional',
        'teamwork': 'teamwork interpersonal communication collaboration team player',
        'leadership': 'leadership competencies management people management',
        'management': 'management leadership people management supervision',
        'people management': 'people management leadership team management supervision',
        'mentoring': 'mentoring coaching leadership development',
        'coaching': 'coaching mentoring leadership development guidance',
        'problem solving': 'problem solving analytical thinking critical thinking',
        'analytical': 'analytical thinking problem solving reasoning critical thinking',
        'critical thinking': 'critical thinking analytical reasoning problem solving',
        'decision making': 'decision making judgment critical thinking problem solving',
        'time management': 'time management organization planning prioritization',
        'organization': 'organizational skills time management planning coordination',
        'attention to detail': 'attention to detail accuracy precision thoroughness',
        'adaptability': 'adaptability flexibility change management resilience',
        'flexibility': 'flexibility adaptability change management agile',
        
        # ==================== CUSTOMER & SERVICE ====================
        'customer service': 'customer service customer support service orientation communication',
        'customer support': 'customer support customer service communication problem solving',
        'customer': 'customer service customer focus service orientation',
        'client': 'client relationship client communication stakeholder management',
        'stakeholder': 'stakeholder management communication relationship building',
        'service': 'customer service service orientation support',
        
        # ==================== SALES & MARKETING ====================
        'sales': 'sales competencies sales assessment entry-level sales selling',
        'selling': 'sales selling persuasion negotiation',
        'business development': 'business development sales partnerships growth',
        'marketing': 'marketing assessment digital marketing brand management',
        'digital marketing': 'digital marketing online marketing social media',
        'content': 'content writing content creation copywriting',
        'content writer': 'content writing copywriting editorial writing',
        'content writing': 'content writing copywriting creative writing editorial',
        'copywriting': 'copywriting content writing marketing communications',
        'seo': 'search engine optimization SEO digital marketing online visibility',
        'social media': 'social media digital marketing online presence',
        'email marketing': 'email marketing digital marketing campaigns',
        'brand': 'brand management marketing brand positioning',
        'advertising': 'advertising marketing campaigns creative',
        
        # ==================== FINANCE & ACCOUNTING ====================
        'finance': 'financial analysis financial management accounting',
        'financial': 'financial analysis financial management finance accounting',
        'accounting': 'accounting financial accounting bookkeeping',
        'financial analyst': 'financial analysis financial modeling Excel accounting',
        'financial analysis': 'financial analysis accounting budgeting forecasting',
        'budgeting': 'budgeting financial planning forecasting',
        'forecasting': 'forecasting financial planning budgeting analytics',
        'financial modeling': 'financial modeling Excel financial analysis',
        'sap': 'SAP ERP financial systems accounting',
        'oracle financials': 'Oracle financial systems ERP accounting',
        
        # ==================== HR & RECRUITMENT ====================
        'hr': 'human resources HR management talent management',
        'human resources': 'human resources HR talent management people management',
        'recruitment': 'recruitment talent acquisition hiring',
        'talent acquisition': 'talent acquisition recruitment hiring',
        'talent management': 'talent management HR development performance',
        'employee relations': 'employee relations HR conflict resolution',
        
        # ==================== LANGUAGE & WRITING ====================
        'english': 'English comprehension English language written English verbal English',
        'written english': 'written English English comprehension writing grammar',
        'writing': 'writing skills written English composition proofreading',
        'writing skills': 'writing written English composition communication',
        'grammar': 'grammar English language writing proofreading',
        'proofreading': 'proofreading grammar editing written English',
        'editing': 'editing proofreading writing grammar',
        'verbal': 'verbal communication speaking interpersonal communication',
        'presentation': 'presentation skills public speaking communication',
        'public speaking': 'public speaking presentation verbal communication',
        
        # ==================== JOB LEVELS ====================
        'entry-level': 'entry-level graduate foundational aptitude learning potential',
        'entry level': 'entry-level graduate foundational aptitude learning potential',
        'graduate': 'graduate entry-level aptitude learning potential foundational',
        'new graduate': 'graduate entry-level aptitude learning potential fresh',
        'junior': 'junior entry-level foundational basic',
        'mid-level': 'intermediate professional experienced mid-career',
        'senior': 'senior advanced experienced expert',
        'manager': 'manager management leadership people management',
        'director': 'director leadership strategic management executive',
        'executive': 'executive leadership strategic senior management C-level',
        'coo': 'COO executive leadership strategic operations chief',
        'ceo': 'CEO executive leadership strategic chief',
        'vp': 'vice president VP executive leadership senior',
        
        # ==================== CULTURAL & INTERNATIONAL ====================
        'cultural fit': 'cultural awareness global skills international cultural assessment cross-cultural',
        'cultural': 'global skills cultural assessment cultural awareness international',
        'international': 'international global cross-cultural cultural awareness',
        'global': 'global skills international cultural awareness cross-cultural',
        'cross-cultural': 'cross-cultural global cultural awareness international',
        'diversity': 'diversity inclusion cultural awareness DEI',
        
        # ==================== COGNITIVE & APTITUDE ====================
        'aptitude': 'aptitude reasoning learning potential cognitive ability',
        'reasoning': 'reasoning aptitude analytical thinking cognitive',
        'cognitive': 'cognitive ability reasoning aptitude learning',
        'learning potential': 'learning potential aptitude cognitive reasoning',
        'numerical': 'numerical ability quantitative reasoning math',
        'verbal ability': 'verbal ability verbal reasoning comprehension',
        'logical': 'logical reasoning analytical thinking problem solving',
        
        # ==================== SPECIFIC BUSINESS FUNCTIONS ====================
        'operations': 'operations management process improvement efficiency',
        'supply chain': 'supply chain logistics operations management',
        'logistics': 'logistics supply chain operations coordination',
        'procurement': 'procurement purchasing supply chain vendor management',
        'business analyst': 'business analysis requirements analysis stakeholder management',
        'analyst': 'analysis analytical thinking problem solving data',
        'consultant': 'consulting advisory analysis problem solving stakeholder',
        'consulting': 'consulting advisory strategic problem solving',
        
        # ==================== DOMAIN-SPECIFIC ====================
        'healthcare': 'healthcare medical clinical patient care',
        'medical': 'medical healthcare clinical medical knowledge',
        'nursing': 'nursing healthcare patient care clinical',
        'legal': 'legal law compliance regulatory',
        'compliance': 'compliance regulatory legal risk management',
        'regulatory': 'regulatory compliance legal risk',
        'risk management': 'risk management compliance assessment mitigation',
        'audit': 'audit compliance financial audit internal control',
        
        # ==================== TECHNICAL DOMAINS ====================
        'networking': 'networking network infrastructure IT systems',
        'network': 'networking network administration IT infrastructure',
        'security': 'security cybersecurity information security IT',
        'cybersecurity': 'cybersecurity security information security IT',
        'information security': 'information security cybersecurity security IT',
        'system admin': 'system administration IT infrastructure operations',
        'it': 'IT information technology systems technical',
        
        # ==================== CREATIVE & DESIGN ====================
        'design': 'design creative visual UX UI',
        'graphic design': 'graphic design visual design creative Adobe',
        'ui': 'UI design user interface UX design',
        'ux': 'UX design user experience UI design',
        'creative': 'creative design innovation content',
        'adobe': 'Adobe design creative tools Photoshop',
        
        # ==================== ADMIN & SUPPORT ====================
        'admin': 'administrative admin assistant office management',
        'administrative': 'administrative admin office management coordination',
        'assistant': 'assistant administrative support coordination',
        'office management': 'office management administrative coordination',
        'coordination': 'coordination organization planning administrative',
        'scheduling': 'scheduling coordination time management planning',
        
        # ==================== SPECIALIZED SKILLS ====================
        'presales': 'presales sales support technical sales solutions',
        'pre-sales': 'presales sales support technical demonstration',
        'technical sales': 'technical sales presales solution selling',
        'rfp': 'RFP proposal writing presales business development',
        'proposal': 'proposal writing RFP business writing',
        'demo': 'demonstration presentation product demo presales',
        'presentation skills': 'presentation communication public speaking demonstration',
        
        # ==================== RESEARCH & INNOVATION ====================
        'research': 'research analysis investigation innovation',
        'innovation': 'innovation creativity problem solving strategic thinking',
        'strategic': 'strategic thinking strategy planning leadership',
        'strategic thinking': 'strategic thinking innovation leadership planning',
        
        # ==================== E-COMMERCE & DIGITAL ====================
        'ecommerce': 'ecommerce online retail digital commerce',
        'e-commerce': 'ecommerce online business digital retail',
        'digital': 'digital technology online digital transformation',
        'online': 'online digital ecommerce web-based',
    }
    
    return assessment_mappings


def get_fallback_skills() -> list:
    """
    Return list of fallback skill keywords for basic extraction
    
    Used when LLM extraction fails - searches for these keywords
    """
    return [
        # Programming & Technical
        'java', 'python', 'sql', 'javascript', 'c++', 'c#', 'php',
        'react', 'angular', 'node', 'django', 'spring',
        
        # Testing & QA
        'testing', 'qa', 'selenium', 'manual testing', 'automation',
        
        # Data & Analytics
        'data', 'analyst', 'machine learning', 'ml', 'ai', 'analytics',
        
        # Office & Tools
        'excel', 'word', 'powerpoint', 'office', 'jira', 'confluence',
        
        # Soft Skills
        'communication', 'leadership', 'teamwork', 'collaboration',
        'management', 'problem solving', 'analytical',
        
        # Sales & Marketing
        'sales', 'marketing', 'seo', 'content', 'digital marketing',
        
        # Finance & Business
        'finance', 'accounting', 'financial', 'business analyst',
        
        # Customer & Service
        'customer service', 'customer support', 'service',
        
        # Language & Writing
        'english', 'writing', 'proofreading', 'grammar',
        
        # Job Levels
        'entry-level', 'graduate', 'senior', 'manager', 'executive',
        
        # Cultural & International
        'cultural', 'global', 'international',
        
        # General
        'computer literacy', 'aptitude', 'cognitive', 'project management'
    ]

