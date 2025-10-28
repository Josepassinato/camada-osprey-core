"""
Visa Information Auto-Updater System
Automatically monitors USCIS, State Department, and Federal Register for changes
"""

import asyncio
import aiohttp
import json
import re
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from bs4 import BeautifulSoup
import logging
from motor.motor_asyncio import AsyncIOMotorDatabase
from uuid import uuid4

# AI Integration for change detection
from emergentintegrations.llm.chat import LlmChat

logger = logging.getLogger(__name__)

@dataclass
class ScrapedData:
    source: str
    form_code: str
    data_type: str
    content: str
    url: str
    scraped_at: datetime
    raw_html: Optional[str] = None

class VisaAutoUpdater:
    def __init__(self, db: AsyncIOMotorDatabase, llm_key: str):
        self.db = db
        self.llm_client = LlmChat(api_key=llm_key)
        self.sources = {
            'uscis': 'https://egov.uscis.gov/processing-times/',
            'uscis_fees': 'https://www.uscis.gov/forms/filing-fees',
            'state_bulletin': 'https://travel.state.gov/content/travel/en/legal/visa-law0/visa-bulletin.html',
            'federal_register': 'https://www.federalregister.gov/agencies/homeland-security-department'
        }
    
    async def run_weekly_update(self):
        """Main function to run weekly visa updates"""
        logger.info("🤖 Starting weekly visa information update...")
        
        try:
            # 1. Scrape all sources
            scraped_data = await self._scrape_all_sources()
            
            # 2. Detect changes using AI
            changes = await self._detect_changes_with_ai(scraped_data)
            
            # 3. Store pending updates for admin approval
            await self._store_pending_updates(changes)
            
            # 4. Send admin notifications
            await self._notify_admin_of_pending_updates()
            
            logger.info(f"✅ Weekly update completed. Found {len(changes)} potential changes")
            return {"success": True, "changes_detected": len(changes)}
            
        except Exception as e:
            logger.error(f"❌ Weekly update failed: {e}")
            return {"success": False, "error": str(e)}
    
    async def _scrape_all_sources(self) -> List[ScrapedData]:
        """Scrape data from all visa information sources"""
        scraped_data = []
        
        async with aiohttp.ClientSession() as session:
            # Scrape USCIS Processing Times
            scraped_data.extend(await self._scrape_uscis_processing_times(session))
            
            # Scrape USCIS Filing Fees
            scraped_data.extend(await self._scrape_uscis_fees(session))
            
            # Scrape State Department Visa Bulletin
            scraped_data.extend(await self._scrape_visa_bulletin(session))
            
            # Scrape Federal Register for regulation changes
            scraped_data.extend(await self._scrape_federal_register(session))
        
        return scraped_data
    
    async def _scrape_uscis_processing_times(self, session: aiohttp.ClientSession) -> List[ScrapedData]:
        """Scrape USCIS processing times"""
        scraped_data = []
        
        try:
            # USCIS processing times by form
            forms_to_check = ['I-130', 'I-485', 'I-765', 'N-400', 'I-539', 'I-129']
            
            for form in forms_to_check:
                url = f"https://egov.uscis.gov/processing-times/more-info/{form.replace('-', '')}"
                
                try:
                    async with session.get(url, timeout=30) as response:
                        if response.status == 200:
                            html = await response.text()
                            soup = BeautifulSoup(html, 'html.parser')
                            
                            # Extract processing time information
                            processing_info = self._extract_processing_time(soup, form)
                            
                            scraped_data.append(ScrapedData(
                                source='uscis',
                                form_code=form,
                                data_type='processing_time',
                                content=json.dumps(processing_info),
                                url=url,
                                scraped_at=datetime.utcnow(),
                                raw_html=html[:1000]  # Store first 1000 chars for debugging
                            ))
                            
                except Exception as e:
                    logger.warning(f"Failed to scrape {form}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"USCIS processing times scraping failed: {e}")
        
        return scraped_data
    
    def _extract_processing_time(self, soup: BeautifulSoup, form_code: str) -> Dict[str, Any]:
        """Extract processing time from USCIS page"""
        processing_info = {
            'form_code': form_code,
            'processing_ranges': [],
            'last_updated': datetime.utcnow().isoformat()
        }
        
        # Look for processing time tables or divs
        time_elements = soup.find_all(['div', 'td'], class_=re.compile(r'processing|time'))
        
        for element in time_elements:
            text = element.get_text(strip=True)
            # Extract time ranges like "8 to 12 months"
            time_match = re.search(r'(\d+\.?\d*)\s*(?:to|-)?\s*(\d+\.?\d*)\s*(month|day|week)', text, re.IGNORECASE)
            if time_match:
                processing_info['processing_ranges'].append({
                    'office': element.get('data-office', 'Unknown'),
                    'min_time': float(time_match.group(1)),
                    'max_time': float(time_match.group(2)) if time_match.group(2) else float(time_match.group(1)),
                    'unit': time_match.group(3).lower()
                })
        
        return processing_info
    
    async def _scrape_uscis_fees(self, session: aiohttp.ClientSession) -> List[ScrapedData]:
        """Scrape USCIS filing fees"""
        scraped_data = []
        
        try:
            url = "https://www.uscis.gov/forms/filing-fees"
            
            async with session.get(url, timeout=30) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Extract fee information
                    fee_info = self._extract_fee_information(soup)
                    
                    scraped_data.append(ScrapedData(
                        source='uscis',
                        form_code='ALL',
                        data_type='filing_fee',
                        content=json.dumps(fee_info),
                        url=url,
                        scraped_at=datetime.utcnow()
                    ))
                    
        except Exception as e:
            logger.error(f"USCIS fees scraping failed: {e}")
        
        return scraped_data
    
    def _extract_fee_information(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract filing fee information from USCIS page"""
        fees = {}
        
        # Look for fee tables or lists
        fee_elements = soup.find_all(['table', 'tr', 'li'], string=re.compile(r'I-\d+|\$'))
        
        for element in fee_elements:
            text = element.get_text(strip=True)
            
            # Extract form and fee like "I-130 $535"
            fee_match = re.search(r'(I-\d+|N-\d+|AR-\d+).*?\$(\d+(?:,\d+)?)', text)
            if fee_match:
                form_code = fee_match.group(1)
                fee_amount = fee_match.group(2).replace(',', '')
                fees[form_code] = {
                    'amount': int(fee_amount),
                    'effective_date': datetime.utcnow().isoformat()
                }
        
        return fees
    
    async def _scrape_visa_bulletin(self, session: aiohttp.ClientSession) -> List[ScrapedData]:
        """Scrape State Department Visa Bulletin"""
        scraped_data = []
        
        try:
            url = "https://travel.state.gov/content/travel/en/legal/visa-law0/visa-bulletin.html"
            
            async with session.get(url, timeout=30) as response:
                if response.status == 200:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Extract visa bulletin data
                    bulletin_data = self._extract_visa_bulletin_data(soup)
                    
                    scraped_data.append(ScrapedData(
                        source='state_department',
                        form_code='BULLETIN',
                        data_type='visa_bulletin',
                        content=json.dumps(bulletin_data),
                        url=url,
                        scraped_at=datetime.utcnow()
                    ))
                    
        except Exception as e:
            logger.error(f"Visa bulletin scraping failed: {e}")
        
        return scraped_data
    
    def _extract_visa_bulletin_data(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract visa bulletin priority dates"""
        bulletin_data = {
            'current_month': datetime.utcnow().strftime('%B %Y'),
            'priority_dates': {},
            'retrogression_info': []
        }
        
        # Look for tables with priority dates
        tables = soup.find_all('table')
        
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    category = cells[0].get_text(strip=True)
                    date_text = cells[1].get_text(strip=True)
                    
                    # Extract date or "C" (current) or "U" (unavailable)
                    if any(cat in category.upper() for cat in ['EB-1', 'EB-2', 'EB-3', 'F1', 'F2', 'F3', 'F4']):
                        bulletin_data['priority_dates'][category] = date_text
        
        return bulletin_data
    
    async def _scrape_federal_register(self, session: aiohttp.ClientSession) -> List[ScrapedData]:
        """Scrape Federal Register for regulation changes"""
        scraped_data = []
        
        try:
            # Search for recent DHS/USCIS regulations
            base_url = "https://www.federalregister.gov/api/v1/articles"
            params = {
                'conditions[agencies][]': 'homeland-security-department',
                'conditions[term]': 'USCIS immigration',
                'conditions[publication_date][gte]': (datetime.utcnow() - timedelta(days=7)).strftime('%Y-%m-%d'),
                'per_page': 20,
                'format': 'json'
            }
            
            async with session.get(base_url, params=params, timeout=30) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    for article in data.get('results', []):
                        scraped_data.append(ScrapedData(
                            source='federal_register',
                            form_code='REGULATION',
                            data_type='regulation_change',
                            content=json.dumps({
                                'title': article.get('title'),
                                'abstract': article.get('abstract'),
                                'publication_date': article.get('publication_date'),
                                'document_number': article.get('document_number'),
                                'url': article.get('html_url')
                            }),
                            url=article.get('html_url', ''),
                            scraped_at=datetime.utcnow()
                        ))
                        
        except Exception as e:
            logger.error(f"Federal Register scraping failed: {e}")
        
        return scraped_data
    
    async def _detect_changes_with_ai(self, scraped_data: List[ScrapedData]) -> List[Dict[str, Any]]:
        """Use AI to detect significant changes in visa information"""
        changes = []
        
        for data in scraped_data:
            try:
                # Get current data from database
                current_data = await self._get_current_visa_data(data.form_code, data.data_type)
                
                if not current_data:
                    # New data - create initial record
                    changes.append({
                        'form_code': data.form_code,
                        'update_type': data.data_type,
                        'source': data.source,
                        'title': f'Initial {data.data_type} data for {data.form_code}',
                        'description': 'Initial data collection',
                        'old_value': None,
                        'new_value': json.loads(data.content),
                        'confidence_score': 1.0,
                        'detected_date': data.scraped_at
                    })
                    continue
                
                # Compare with AI
                change_analysis = await self._analyze_changes_with_ai(
                    current_data, 
                    json.loads(data.content),
                    data.form_code,
                    data.data_type
                )
                
                if change_analysis['has_changes']:
                    changes.append({
                        'form_code': data.form_code,
                        'update_type': data.data_type,
                        'source': data.source,
                        'title': change_analysis['title'],
                        'description': change_analysis['description'],
                        'old_value': current_data,
                        'new_value': json.loads(data.content),
                        'confidence_score': change_analysis['confidence'],
                        'detected_date': data.scraped_at
                    })
                    
            except Exception as e:
                logger.error(f"AI change detection failed for {data.form_code}: {e}")
                continue
        
        return changes
    
    async def _analyze_changes_with_ai(self, old_data: Dict, new_data: Dict, form_code: str, data_type: str) -> Dict[str, Any]:
        """Use AI to analyze if there are significant changes"""
        
        prompt = f"""
        Analyze the following visa information changes for {form_code} ({data_type}):
        
        OLD DATA:
        {json.dumps(old_data, indent=2)}
        
        NEW DATA:
        {json.dumps(new_data, indent=2)}
        
        Determine if there are significant changes that would affect visa applicants. 
        Respond with JSON format:
        {{
            "has_changes": true/false,
            "confidence": 0.0-1.0,
            "title": "Brief title of change",
            "description": "Detailed description of what changed",
            "significance": "high/medium/low",
            "affects_users": true/false
        }}
        
        Focus on:
        - Processing time changes (more than 1 month difference)
        - Fee changes (any amount)
        - New requirements or document changes
        - Priority date movements
        - Regulation changes affecting applications
        """
        
        try:
            response = await self.llm_client.chat_async(
                messages=[{"role": "user", "content": prompt}],
                model="gpt-4o",
                max_tokens=500,
                temperature=0.1
            )
            
            # Parse JSON response
            analysis = json.loads(response.strip())
            return analysis
            
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            return {
                "has_changes": False,
                "confidence": 0.0,
                "title": "Analysis failed",
                "description": f"Could not analyze changes: {e}",
                "significance": "unknown",
                "affects_users": False
            }
    
    async def _get_current_visa_data(self, form_code: str, data_type: str) -> Optional[Dict[str, Any]]:
        """Get current visa information from database"""
        try:
            doc = await self.db.visa_information.find_one({
                'form_code': form_code,
                'data_type': data_type,
                'is_active': True
            })
            return doc.get('data') if doc else None
        except Exception:
            return None
    
    async def _store_pending_updates(self, changes: List[Dict[str, Any]]):
        """Store detected changes as pending updates for admin review"""
        for change in changes:
            update_doc = {
                **change,
                'id': str(uuid4()),
                'status': 'pending',
                'created_at': datetime.utcnow()
            }
            
            await self.db.visa_updates.insert_one(update_doc)
    
    async def _notify_admin_of_pending_updates(self):
        """Send notification to admin about pending updates"""
        pending_count = await self.db.visa_updates.count_documents({'status': 'pending'})
        
        if pending_count > 0:
            logger.info(f"📧 {pending_count} pending visa updates require admin review")
            # Here you could integrate with email/SMS/Slack notifications
            
            # Store notification in database
            await self.db.admin_notifications.insert_one({
                'id': str(uuid4()),
                'type': 'visa_updates',
                'title': f'{pending_count} Visa Updates Pending Review',
                'message': f'There are {pending_count} automatically detected visa information updates waiting for your review and approval.',
                'created_at': datetime.utcnow(),
                'read': False,
                'priority': 'high' if pending_count > 5 else 'medium'
            })

async def schedule_weekly_updates():
    """Schedule function to be called weekly"""
    # This would be called by a scheduler like APScheduler or Celery
    pass