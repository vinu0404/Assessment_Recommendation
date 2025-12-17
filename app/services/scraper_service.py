import asyncio
import json
from pathlib import Path
from typing import Dict, Any, Optional, List
import requests
from bs4 import BeautifulSoup
import re
from app.config import settings
from app.utils.logger import get_logger

logger = get_logger("scraper_service")


class ScraperService:
    """Service for scraping SHL assessment catalog"""
    
    def __init__(self):
        self.base_url = "https://www.shl.com"
        self.catalog_url = f"{self.base_url}/products/product-catalog/"
        self.delay = settings.SCRAPER_DELAY
        self.timeout = settings.SCRAPER_TIMEOUT
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        }
        self.test_type_mapping = {
            'A': 'Ability & Aptitude',
            'B': 'Biodata & Situational Judgement',
            'C': 'Competencies',
            'D': 'Development & 360',
            'E': 'Assessment Exercises',
            'K': 'Knowledge & Skills',
            'P': 'Personality & Behavior',
            'S': 'Simulations'
        }
    
    def get_catalog_page(self, start: int = 0) -> Optional[BeautifulSoup]:
        """Fetch a single catalog page for Individual Test Solutions"""
        try:
            url = f"{self.catalog_url}?start={start}&type=1"
            logger.info(f"Fetching URL: {url}")
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            return BeautifulSoup(response.content, 'html.parser')
        except Exception as e:
            logger.error(f"Error fetching catalog page (start={start}): {e}")
            return None
    
    def find_all_individual_test_tables(self, soup: BeautifulSoup) -> List:
        """Find all tables that might contain Individual Test Solutions"""
        tables = []
        section_headers = soup.find_all(['h3', 'h2', 'h4'])
        for header in section_headers:
            if 'Individual Test Solutions' in header.get_text():
                logger.info(f"Found 'Individual Test Solutions' header: {header.get_text()}")
                table_wrapper = header.find_next('div', class_='custom__table-wrapper')
                if table_wrapper:
                    tables.append(table_wrapper)
                    break
        if not tables:
            logger.warning("Could not find by header, searching all table wrappers...")
            all_wrappers = soup.find_all('div', class_='custom__table-wrapper')
            logger.info(f"Found {len(all_wrappers)} table wrappers")
            tables = all_wrappers
        
        return tables
    
    def get_max_page_dynamically(self, soup: BeautifulSoup) -> int:
        """Dynamically find the maximum page number for Individual Test Solutions"""
        try:
            paginations = soup.find_all('ul', class_='pagination')
            logger.info(f"Found {len(paginations)} pagination elements")
            
            max_page = 1
            
            for idx, pagination in enumerate(paginations):
                logger.info(f"Analyzing pagination element {idx + 1}...")
                page_numbers = []
                items = pagination.find_all('li', class_='pagination__item')
                
                for item in items:
                    link = item.find('a', class_='pagination__link')
                    if link:
                        text = link.get_text(strip=True)
                        if text.isdigit():
                            page_numbers.append(int(text))
                        href = link.get('href', '')
                        match = re.search(r'start=(\d+)', href)
                        if match:
                            start_val = int(match.group(1))
                            page_from_start = (start_val // 12) + 1
                            page_numbers.append(page_from_start)
                    span = item.find('span', class_='pagination__link')
                    if span and span.get_text(strip=True).isdigit():
                        page_numbers.append(int(span.get_text(strip=True)))
                
                if page_numbers:
                    pagination_max = max(page_numbers)
                    logger.info(f"Pagination {idx + 1} max page: {pagination_max} (pages found: {sorted(set(page_numbers))})")
                    max_page = max(max_page, pagination_max)
            for pagination in paginations:
                last_links = pagination.find_all('a', class_='pagination__link')
                for link in last_links:
                    href = link.get('href', '')
                    match = re.search(r'start=(\d+)', href)
                    if match:
                        start_val = int(match.group(1))
                        calculated_page = (start_val // 12) + 1
                        max_page = max(max_page, calculated_page)
            
            logger.info(f"Final determined max page: {max_page}")
            return max_page
            
        except Exception as e:
            logger.error(f"Error determining max page: {e}")
            return 1
    
    def extract_tests_from_page(self, soup: BeautifulSoup) -> List[Dict[str, Any]]:
        """Extract test information from a catalog page"""
        tests = []
        
        try:

            table_wrappers = self.find_all_individual_test_tables(soup)
            
            if not table_wrappers:
                logger.warning("No table wrappers found!")
                return tests
            
            for wrapper_idx, table_wrapper in enumerate(table_wrappers):
                logger.info(f"Processing table wrapper {wrapper_idx + 1}/{len(table_wrappers)}")
                
                table = table_wrapper.find('table')
                if not table:
                    logger.warning(f"No table found in wrapper {wrapper_idx + 1}")
                    continue
                
                header_row = table.find('tr')
                if header_row:
                    header_text = header_row.get_text()
                    logger.info(f"Table header: {header_text[:100]}")
                    if 'Pre-packaged' in header_text or 'Job Solutions' in header_text:
                        logger.info("Skipping Pre-packaged Job Solutions table")
                        continue

                rows = table.find_all('tr', attrs={'data-entity-id': True})
                logger.info(f"Found {len(rows)} test rows in table {wrapper_idx + 1}")
                
                for row in rows:
                    try:
                        test_data = self.extract_test_from_row(row)
                        if test_data:
                            tests.append(test_data)
                            logger.debug(f"Extracted: {test_data['name']}")
                    except Exception as e:
                        logger.warning(f"Error parsing row: {e}")
                        continue
        
        except Exception as e:
            logger.error(f"Error extracting tests from page: {e}")
        
        return tests
    
    def extract_test_from_row(self, row) -> Optional[Dict[str, Any]]:
        """Extract test data from a single table row"""
        try:
            title_cell = row.find('td', class_='custom__table-heading__title')
            if not title_cell:
                return None
            
            link = title_cell.find('a')
            if not link:
                return None
            
            test_name = link.get_text(strip=True)
            test_url = link.get('href', '')
            if test_url.startswith('/'):
                test_url = self.base_url + test_url
            elif not test_url.startswith('http'):
                test_url = self.base_url + '/' + test_url
            general_cells = row.find_all('td', class_='custom__table-heading__general')
            remote_support = "No"
            adaptive_support = "No"
            
            if len(general_cells) >= 2:
                remote_circle = general_cells[0].find('span', class_='catalogue__circle')
                if remote_circle and '-yes' in ' '.join(remote_circle.get('class', [])):
                    remote_support = "Yes"
                
                adaptive_circle = general_cells[1].find('span', class_='catalogue__circle')
                if adaptive_circle and '-yes' in ' '.join(adaptive_circle.get('class', [])):
                    adaptive_support = "Yes"
            test_types = []
            keys_cell = row.find('td', class_='product-catalogue__keys')
            if keys_cell:
                key_spans = keys_cell.find_all('span', class_='product-catalogue__key')
                for span in key_spans:
                    letter = span.get_text(strip=True)
                    if letter in self.test_type_mapping:
                        test_types.append(self.test_type_mapping[letter])
            
            return {
                'name': test_name,
                'url': test_url,
                'remote_support': remote_support,
                'adaptive_support': adaptive_support,
                'test_type': test_types
            }
        
        except Exception as e:
            logger.warning(f"Error extracting test from row: {e}")
            return None
    
    def get_test_details(self, test_url: str) -> Dict[str, Any]:
        """Fetch detailed information from individual test page"""
        try:
            response = requests.get(test_url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            details = {
                'description': '',
                'job_levels': '',
                'languages': '',
                'duration': None,
                'test_type': []
            }
            

            desc_section = soup.find('h4', string='Description')
            if desc_section:
                desc_p = desc_section.find_next('p')
                if desc_p:
                    details['description'] = desc_p.get_text(strip=True)
            

            job_section = soup.find('h4', string='Job levels')
            if job_section:
                job_p = job_section.find_next('p')
                if job_p:
                    details['job_levels'] = job_p.get_text(strip=True)

            lang_section = soup.find('h4', string='Languages')
            if lang_section:
                lang_p = lang_section.find_next('p')
                if lang_p:
                    details['languages'] = lang_p.get_text(strip=True)
            
            length_section = soup.find('h4', string='Assessment length')
            if length_section:
                parent = length_section.find_parent('div', class_='product-catalogue-training-calendar__row')
                length_p = parent.find('p') if parent else length_section.find_next('p')
                
                if length_p:
                    duration_text = length_p.get_text(strip=True)
                    patterns = [
                        r'=\s*(\d+)',  # "= 10"
                        r'(\d+)\s*(?:minutes?|mins?)',  # "10 minutes"
                        r'(\d+)\s*min',  # "10min"
                        r'(\d+)'  # Any number
                    ]
                    for pattern in patterns:
                        match = re.search(pattern, duration_text, re.IGNORECASE)
                        if match:
                            details['duration'] = int(match.group(1))
                            break
            
            test_type_text = soup.find('p', class_='product-catalogue__small-text')
            if test_type_text and 'Test Type:' in test_type_text.get_text():
                type_spans = test_type_text.find_all('span', class_='product-catalogue__key')
                test_types = []
                for span in type_spans:
                    letter = span.get_text(strip=True)
                    if letter in self.test_type_mapping:
                        test_types.append(self.test_type_mapping[letter])
                if test_types:
                    details['test_type'] = test_types
            
            return details
            
        except Exception as e:
            logger.error(f"Error fetching test details from {test_url}: {e}")
            return {}
    
    async def scrape_all_tests(self) -> Dict[str, Dict[str, Any]]:
        """Scrape all Individual Test Solutions dynamically"""
        all_tests = {}
        
        logger.info("="*80)
        logger.info("Starting Dynamic Scrape of Individual Test Solutions")
        logger.info("="*80)
        logger.info("Step 1: Fetching first page...")
        first_page = self.get_catalog_page(0)
        
        if not first_page:
            logger.error("Failed to fetch first page!")
            return all_tests
        logger.info("Step 2: Determining total pages...")
        max_page = self.get_max_page_dynamically(first_page)
        logger.info(f"✓ Found maximum page: {max_page}")
        
        logger.info("Step 3: Extracting tests from first page...")
        first_page_tests = self.extract_tests_from_page(first_page)
        logger.info(f"✓ Found {len(first_page_tests)} tests on page 1")
        
        for test in first_page_tests:
            all_tests[test['url']] = test
        
        await asyncio.sleep(self.delay)

        logger.info(f"Step 4: Processing pages 2-{max_page}...")
        items_per_page = 12
        
        for page_num in range(2, max_page + 1):
            start_index = (page_num - 1) * items_per_page
            logger.info(f"→ Page {page_num}/{max_page} (start={start_index})")
            
            page_soup = self.get_catalog_page(start_index)
            if not page_soup:
                logger.warning(f"  ✗ Failed to fetch page {page_num}")
                continue
            
            tests = self.extract_tests_from_page(page_soup)
            logger.info(f"  ✓ Found {len(tests)} tests")
            
            new_tests = 0
            for test in tests:
                if test['url'] not in all_tests:
                    all_tests[test['url']] = test
                    new_tests += 1
            
            if new_tests < len(tests):
                logger.debug(f"  Note: {len(tests) - new_tests} duplicates skipped")
            
            await asyncio.sleep(self.delay)
        
        logger.info("="*80)
        logger.info(f"Catalog scraping complete! Total unique tests: {len(all_tests)}")
        logger.info("="*80)
        
        logger.info("Step 5: Fetching detailed information for each test...")
        for idx, (url, test_data) in enumerate(all_tests.items(), 1):
            logger.info(f"[{idx}/{len(all_tests)}] {test_data['name']}")
            details = self.get_test_details(url)
            
            if details:
                test_data.update(details)

            if idx % 10 == 0:
                logger.info(f"  Progress: {idx}/{len(all_tests)} ({idx*100//len(all_tests)}%)")
            
            await asyncio.sleep(self.delay)
        
        logger.info("="*80)
        logger.info(f"Total tests scraped: {len(all_tests)}")
        logger.info("="*80)
        
        return all_tests
    
    def save_to_json(self, data: Dict[str, Any], filename: str = None):
        """Save scraped data to JSON file"""
        filename = filename or settings.ASSESSMENTS_JSON_PATH
        
        try:
            output_path = Path(filename)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Data saved to {filename}")
            logger.info(f"Total tests saved: {len(data)}")
        except Exception as e:
            logger.error(f"Error saving to JSON: {e}")
            raise
    
    def load_from_json(self, filename: str = None) -> Dict[str, Any]:
        """Load assessments from JSON file"""
        filename = filename or settings.ASSESSMENTS_JSON_PATH
        
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logger.info(f"✓ Loaded {len(data)} assessments from {filename}")
            return data
        except FileNotFoundError:
            logger.warning(f"⚠ Assessment file not found: {filename}")
            return {}
        except Exception as e:
            logger.error(f"✗ Error loading from JSON: {e}")
            return {}


scraper_service = ScraperService()


def get_scraper_service() -> ScraperService:
    """Get scraper service instance"""
    return scraper_service