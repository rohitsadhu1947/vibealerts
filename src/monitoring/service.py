"""
Vibe_Alerts - Monitoring Service
Continuously monitors NSE/BSE for new quarterly result announcements
"""

import asyncio
import aiohttp
import json
from typing import List, Optional
from datetime import datetime
from loguru import logger
from redis import Redis

from src.database.models import Announcement


class SourceMonitor:
    """Base class for all source monitors"""
    
    def __init__(self, config: dict):
        self.name = config['name']
        self.url = config['url']
        self.timeout = config['timeout']
        self.enabled = config['enabled']
        self.priority = config.get('priority', 99)
        self.session: Optional[aiohttp.ClientSession] = None
        
    async def fetch(self) -> List[Announcement]:
        """Fetch announcements from source"""
        raise NotImplementedError
        
    async def parse(self, data: any) -> List[Announcement]:
        """Parse response into announcements"""
        raise NotImplementedError
        
    def is_quarterly_result(self, text: str) -> bool:
        """Check if announcement is quarterly result"""
        text_lower = text.lower()
        
        # FIRST: Filter out administrative/non-actionable announcements
        exclude_keywords = [
            'newspaper publication',
            'newspaper advertisement',
            'published in newspaper',
            'publication of financial results',  # Notice ABOUT publication, not the results
            'newspaper notice',
            'press release publication',
            'advertisement in newspaper',
            'notice published in',
            'copy of newspaper',
            'intimation of newspaper publication',
            'submission of newspaper',
            'compliance certificate',
            'record date',
            'book closure',
            'agm notice',
            'egm notice',
            'intimation of loss of share certificate',
            'duplicate share certificate',
            'postal ballot',
            'e-voting',
        ]
        
        # If it's an administrative notice, reject immediately
        if any(kw in text_lower for kw in exclude_keywords):
            return False
        
        # SECOND: Check if it's an actual result announcement
        keywords = [
            # Financial results keywords
            'financial result',
            'financial results',
            'quarterly result',
            'quarterly results',
            'quarterly and',  # "quarterly and half year"
            'unaudited financial',
            'unaudited results',
            'audited results',
            'standalone results',
            'consolidated results',
            'quarterly and year to date',
            
            # Quarter identifiers
            'q1', 'q2', 'q3', 'q4',
            'quarter ended',
            'half year ended',
            'year ended',
            
            # Financial year patterns
            'fy20', 'fy21', 'fy22', 'fy23', 'fy24', 'fy25', 'fy26',
            
            # Result announcements
            'outcome of board meeting',
            'submission of financial results',
            'intimation of financial results',
            'approved financial results',
            
            # Specific metrics (strong signals)
            'revenue', 'profit', 'loss', 'ebitda', 'eps',
            'net profit', 'gross profit', 'pat', 'pbt',
        ]
        return any(kw in text_lower for kw in keywords)


class NSEMonitor(SourceMonitor):
    """NSE corporate announcements monitor"""
    
    async def fetch(self) -> List[Announcement]:
        """Fetch from NSE API with enhanced bot protection handling"""
        if not self.session:
            return []
            
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://www.nseindia.com/',
            'X-Requested-With': 'XMLHttpRequest',
            'Connection': 'keep-alive',
            'sec-ch-ua': '"Not_A Brand";v="8", "Chromium";v="120"',
            'sec-ch-ua-mobile': '?0',
            'sec-ch-ua-platform': '"Windows"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
        }
        
        try:
            # First, visit homepage to get cookies (NSE requirement)
            try:
                async with self.session.get(
                    'https://www.nseindia.com',
                    headers={'User-Agent': headers['User-Agent']},
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as resp:
                    # Just get cookies, ignore response
                    pass
            except:
                pass  # Continue even if homepage fails
            
            # Add small delay to appear more human-like
            await asyncio.sleep(0.5)
            
            # Now fetch the API
            async with self.session.get(
                self.url,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as resp:
                if resp.status == 200:
                    content_type = resp.headers.get('Content-Type', '')
                    
                    # Check if we got JSON or HTML
                    if 'application/json' in content_type:
                        data = await resp.json()
                        return await self.parse(data)
                    else:
                        # Got HTML instead of JSON - NSE is blocking us
                        logger.warning("NSE returned HTML instead of JSON (bot protection active)")
                        return []
                else:
                    logger.warning(f"NSE fetch failed: HTTP {resp.status}")
                    return []
        except asyncio.TimeoutError:
            logger.warning(f"NSE fetch timeout after {self.timeout}s")
            return []
        except aiohttp.ClientError as e:
            logger.warning(f"NSE fetch error: {e}")
            return []
        except Exception as e:
            logger.error(f"NSE fetch unexpected error: {e}")
            return []
    
    async def parse(self, data: any) -> List[Announcement]:
        """Parse NSE API response"""
        announcements = []
        
        # NSE returns list of announcements
        items = data if isinstance(data, list) else []
        
        for item in items:
            try:
                desc = item.get('desc', '') or item.get('description', '')
                
                if not self.is_quarterly_result(desc):
                    continue
                
                ann = Announcement(
                    source='nse',
                    symbol=item.get('symbol', '').strip(),
                    date=item.get('an_dt', '') or item.get('date', ''),
                    description=desc,
                    attachment_url=item.get('attchmntFile', '') or item.get('attachment', ''),
                    attachment_text=item.get('attchmntText', ''),
                    timestamp=datetime.now()
                )
                
                if ann.symbol and ann.attachment_url:
                    announcements.append(ann)
                    
            except Exception as e:
                logger.error(f"NSE parse error for item: {e}")
                continue
        
        return announcements


class BSEMonitor(SourceMonitor):
    """BSE announcements monitor"""
    
    async def fetch(self) -> List[Announcement]:
        """Fetch from BSE API"""
        if not self.session:
            return []
            
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }
        
        try:
            async with self.session.get(
                self.url,
                headers=headers,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as resp:
                if resp.status == 200:
                    # BSE might return HTML or XML
                    text = await resp.text()
                    return await self.parse(text)
                else:
                    logger.warning(f"BSE fetch failed: HTTP {resp.status}")
                    return []
        except asyncio.TimeoutError:
            logger.warning(f"BSE fetch timeout after {self.timeout}s")
            return []
        except Exception as e:
            logger.error(f"BSE fetch error: {e}")
            return []
    
    async def parse(self, data: str) -> List[Announcement]:
        """Parse BSE response (HTML/XML)"""
        # TODO: Implement BSE parsing based on actual response format
        # For MVP, return empty list
        return []


class MoneyControlRSSMonitor(SourceMonitor):
    """MoneyControl RSS feed monitor (working alternative to NSE/BSE)"""
    
    async def fetch(self) -> List[Announcement]:
        """Fetch from MoneyControl RSS"""
        if not self.session:
            return []
        
        try:
            async with self.session.get(
                self.url,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as resp:
                if resp.status == 200:
                    text = await resp.text()
                    return await self.parse(text)
                else:
                    logger.warning(f"MoneyControl RSS fetch failed: HTTP {resp.status}")
                    return []
        except asyncio.TimeoutError:
            logger.warning(f"MoneyControl RSS timeout after {self.timeout}s")
            return []
        except Exception as e:
            logger.error(f"MoneyControl RSS error: {e}")
            return []
    
    async def parse(self, xml_text: str) -> List[Announcement]:
        """Parse RSS feed XML"""
        import re
        from xml.etree import ElementTree as ET
        
        announcements = []
        
        try:
            root = ET.fromstring(xml_text)
            
            # Find all items in the RSS feed
            for item in root.findall('.//item'):
                try:
                    title = item.find('title').text if item.find('title') is not None else ''
                    description = item.find('description').text if item.find('description') is not None else ''
                    link = item.find('link').text if item.find('link') is not None else ''
                    pub_date = item.find('pubDate').text if item.find('pubDate') is not None else ''
                    
                    # Check if this is a quarterly result
                    combined_text = f"{title} {description}".lower()
                    if not self.is_quarterly_result(combined_text):
                        continue
                    
                    # Extract symbol from title (usually in format: "SYMBOL: Q3 Results...")
                    symbol_match = re.search(r'^([A-Z]+):', title)
                    symbol = symbol_match.group(1) if symbol_match else 'UNKNOWN'
                    
                    # Extract date from pubDate (format: "Mon, 13 Nov 2024 10:00:00")
                    date_match = re.search(r'(\d{1,2} \w{3} \d{4})', pub_date)
                    date = date_match.group(1) if date_match else ''
                    
                    ann = Announcement(
                        source='moneycontrol',
                        symbol=symbol,
                        date=date,
                        description=title,
                        attachment_url=link,  # Link to MoneyControl article
                        attachment_text=description,
                        timestamp=datetime.now()
                    )
                    
                    if ann.symbol != 'UNKNOWN':
                        announcements.append(ann)
                        
                except Exception as e:
                    logger.debug(f"Error parsing RSS item: {e}")
                    continue
            
            if announcements:
                logger.info(f"MoneyControl RSS: Found {len(announcements)} result announcements")
            
        except ET.ParseError as e:
            logger.error(f"Failed to parse RSS XML: {e}")
        except Exception as e:
            logger.error(f"RSS parsing error: {e}")
        
        return announcements


class EconomicTimesRSSMonitor(SourceMonitor):
    """Economic Times RSS feed monitor - WORKING alternative"""
    
    async def fetch(self) -> List[Announcement]:
        """Fetch from Economic Times RSS"""
        if not self.session:
            return []
        
        try:
            async with self.session.get(
                self.url,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as resp:
                if resp.status == 200:
                    text = await resp.text()
                    return await self.parse(text)
                else:
                    logger.warning(f"Economic Times RSS fetch failed: HTTP {resp.status}")
                    return []
        except asyncio.TimeoutError:
            logger.warning(f"Economic Times RSS timeout after {self.timeout}s")
            return []
        except Exception as e:
            logger.error(f"Economic Times RSS error: {e}")
            return []
    
    async def parse(self, xml_text: str) -> List[Announcement]:
        """Parse RSS feed XML"""
        import re
        from xml.etree import ElementTree as ET
        
        announcements = []
        
        try:
            root = ET.fromstring(xml_text)
            
            for item in root.findall('.//item'):
                try:
                    title = item.find('title').text if item.find('title') is not None else ''
                    description = item.find('description').text if item.find('description') is not None else ''
                    link = item.find('link').text if item.find('link') is not None else ''
                    pub_date = item.find('pubDate').text if item.find('pubDate') is not None else ''
                    
                    # Check if this is a quarterly result
                    combined_text = f"{title} {description}".lower()
                    if not self.is_quarterly_result(combined_text):
                        continue
                    
                    # Try to extract symbol from title
                    symbol_match = re.search(r'\b([A-Z][A-Z]+)\b', title)
                    symbol = symbol_match.group(1) if symbol_match else 'UNKNOWN'
                    
                    # Extract date from pubDate
                    date_match = re.search(r'(\d{1,2} \w{3} \d{4})', pub_date)
                    date = date_match.group(1) if date_match else ''
                    
                    ann = Announcement(
                        source='economic_times',
                        symbol=symbol,
                        date=date,
                        description=title,
                        attachment_url=link,
                        attachment_text=description,
                        timestamp=datetime.now()
                    )
                    
                    if ann.symbol != 'UNKNOWN':
                        announcements.append(ann)
                        
                except Exception as e:
                    logger.debug(f"Error parsing ET RSS item: {e}")
                    continue
            
            if announcements:
                logger.info(f"Economic Times RSS: Found {len(announcements)} result announcements")
                
                # Debug: Log details
                for ann in announcements:
                    logger.debug(f"  ET Result: {ann.symbol} | Date: {ann.date} | Desc: {ann.description[:80]}")
            
        except ET.ParseError as e:
            logger.error(f"Failed to parse ET RSS XML: {e}")
        except Exception as e:
            logger.error(f"ET RSS parsing error: {e}")
        
        return announcements


class LivemintRSSMonitor(SourceMonitor):
    """Livemint RSS feed monitor - WORKING alternative"""
    
    async def fetch(self) -> List[Announcement]:
        """Fetch from Livemint RSS"""
        if not self.session:
            return []
        
        try:
            async with self.session.get(
                self.url,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as resp:
                if resp.status == 200:
                    text = await resp.text()
                    return await self.parse(text)
                else:
                    logger.warning(f"Livemint RSS fetch failed: HTTP {resp.status}")
                    return []
        except asyncio.TimeoutError:
            logger.warning(f"Livemint RSS timeout after {self.timeout}s")
            return []
        except Exception as e:
            logger.error(f"Livemint RSS error: {e}")
            return []
    
    async def parse(self, xml_text: str) -> List[Announcement]:
        """Parse RSS feed XML"""
        import re
        from xml.etree import ElementTree as ET
        
        announcements = []
        
        try:
            root = ET.fromstring(xml_text)
            
            for item in root.findall('.//item'):
                try:
                    title = item.find('title').text if item.find('title') is not None else ''
                    description = item.find('description').text if item.find('description') is not None else ''
                    link = item.find('link').text if item.find('link') is not None else ''
                    pub_date = item.find('pubDate').text if item.find('pubDate') is not None else ''
                    
                    # Check if this is a quarterly result
                    combined_text = f"{title} {description}".lower()
                    if not self.is_quarterly_result(combined_text):
                        continue
                    
                    # Try to extract symbol from title
                    symbol_match = re.search(r'\b([A-Z][A-Z]+)\b', title)
                    symbol = symbol_match.group(1) if symbol_match else 'UNKNOWN'
                    
                    # Extract date from pubDate
                    date_match = re.search(r'(\d{1,2} \w{3} \d{4})', pub_date)
                    date = date_match.group(1) if date_match else ''
                    
                    ann = Announcement(
                        source='livemint',
                        symbol=symbol,
                        date=date,
                        description=title,
                        attachment_url=link,
                        attachment_text=description,
                        timestamp=datetime.now()
                    )
                    
                    if ann.symbol != 'UNKNOWN':
                        announcements.append(ann)
                        
                except Exception as e:
                    logger.debug(f"Error parsing Livemint RSS item: {e}")
                    continue
            
            if announcements:
                logger.info(f"Livemint RSS: Found {len(announcements)} result announcements")
                
                # Debug: Log details
                for ann in announcements:
                    logger.debug(f"  Livemint Result: {ann.symbol} | Date: {ann.date} | Desc: {ann.description[:80]}")
            
        except ET.ParseError as e:
            logger.error(f"Failed to parse Livemint RSS XML: {e}")
        except Exception as e:
            logger.error(f"Livemint RSS parsing error: {e}")
        
        return announcements


class MonitoringService:
    """Main monitoring orchestrator"""
    
    def __init__(self, config: dict, redis_client: Redis):
        self.config = config
        self.redis = redis_client
        self.monitors = self._initialize_monitors()
        self.dedup_ttl = config['redis'].get('dedup_ttl', 3600)
        self.poll_interval = config['monitoring']['poll_interval']
        self.session: Optional[aiohttp.ClientSession] = None
        
    def _initialize_monitors(self) -> List[SourceMonitor]:
        """Initialize all enabled monitors"""
        monitors = []
        
        for source_config in self.config['monitoring']['sources']:
            if not source_config['enabled']:
                continue
                
            if source_config['name'] == 'nse_api':
                monitors.append(NSEMonitor(source_config))
            elif source_config['name'] == 'bse_api':
                monitors.append(BSEMonitor(source_config))
            elif source_config['name'] == 'bse_library':
                monitors.append(BSELibraryMonitor(source_config))
            elif source_config['name'] == 'moneycontrol_rss':
                monitors.append(MoneyControlRSSMonitor(source_config))
            elif source_config['name'] == 'economic_times_rss':
                monitors.append(EconomicTimesRSSMonitor(source_config))
            elif source_config['name'] == 'livemint_rss':
                monitors.append(LivemintRSSMonitor(source_config))
        
        # Sort by priority
        monitors.sort(key=lambda m: m.priority)
        
        logger.info(f"Initialized {len(monitors)} monitors: {[m.name for m in monitors]}")
        return monitors
    
    async def start(self):
        """Start monitoring loop"""
        logger.info(f"Starting monitoring service (poll interval: {self.poll_interval}s)")
        
        # Create shared aiohttp session
        self.session = aiohttp.ClientSession()
        
        # Assign session to all monitors
        for monitor in self.monitors:
            monitor.session = self.session
        
        try:
            while True:
                try:
                    await self._monitor_cycle()
                    await asyncio.sleep(self.poll_interval)
                except Exception as e:
                    logger.error(f"Monitor cycle error: {e}")
                    await asyncio.sleep(5)
        finally:
            await self.session.close()
    
    async def _monitor_cycle(self):
        """Single monitoring cycle - fetch from all sources in parallel"""
        
        # Fetch from all sources concurrently
        tasks = [monitor.fetch() for monitor in self.monitors]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Process results
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                logger.error(f"Monitor {self.monitors[i].name} error: {result}")
                continue
            
            # result is a list of announcements
            for announcement in result:
                await self._process_announcement(announcement)
    
    async def _process_announcement(self, ann: Announcement):
        """Process a single announcement with deduplication"""
        
        # Check deduplication
        dedup_key = f"processed:{ann.symbol}:{ann.date}"
        
        if self.redis.exists(dedup_key):
            logger.debug(f"Already processed: {ann.symbol} on {ann.date}")
            return
        
        # Mark as processed
        self.redis.setex(dedup_key, self.dedup_ttl, "1")
        
        # Queue for extraction
        self.redis.lpush('extraction_queue', json.dumps(ann.to_json()))
        
        logger.info(f"📋 New result detected: {ann.symbol} from {ann.source}")
    
    async def monitor(self):
        """Generator that yields new announcements"""
        logger.info(f"Starting monitoring generator (poll interval: {self.poll_interval}s)")
        
        # Create shared aiohttp session
        async with aiohttp.ClientSession() as session:
            # Assign session to all monitors
            for monitor in self.monitors:
                monitor.session = session
            
            while True:
                try:
                    # Fetch from all sources concurrently
                    tasks = [monitor.fetch() for monitor in self.monitors]
                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    
                    # Process results
                    for i, result in enumerate(results):
                        if isinstance(result, Exception):
                            logger.error(f"Monitor {self.monitors[i].name} error: {result}")
                            continue
                        
                        # result is a list of announcements
                        for announcement in result:
                            # Check deduplication
                            dedup_key = f"processed:{announcement.symbol}:{announcement.date}"
                            
                            if self.redis.exists(dedup_key):
                                logger.debug(f"⏭️  Skipping already processed: {announcement.symbol} ({announcement.date})")
                                continue
                            
                            # Mark as processed
                            self.redis.setex(dedup_key, self.dedup_ttl, "1")
                            
                            logger.info(f"📋 New result: {announcement.symbol} from {announcement.source}")
                            logger.info(f"   Description: {announcement.description[:100]}...")
                            yield announcement
                    
                    await asyncio.sleep(self.poll_interval)
                    
                except Exception as e:
                    logger.error(f"Monitor cycle error: {e}")
                    await asyncio.sleep(5)


class BSELibraryMonitor(SourceMonitor):
    """BSE announcements monitor using bse Python library"""
    
    async def fetch(self) -> List[Announcement]:
        """Fetch from BSE using bse library"""
        try:
            logger.info("Fetching BSE announcements via bse library...")
            
            # Import here to catch import errors
            try:
                from bse import BSE
                import tempfile
                logger.debug("BSE library imported successfully")
            except ImportError as e:
                logger.error(f"Failed to import BSE library: {e}")
                return []
            
            # Use BSE library (synchronous, but fast)
            # Use temp directory for any downloads
            download_folder = tempfile.gettempdir()
            logger.debug(f"Using download folder: {download_folder}")
            
            try:
                logger.debug("Initializing BSE library...")
                bse = BSE(download_folder=download_folder)
                logger.debug("BSE library initialized successfully")
                
                logger.debug("Calling bse.announcements()...")
                response = bse.announcements()
                logger.debug(f"Got response from BSE: {type(response)}")
                
                bse.exit()
                
            except TypeError as e:
                logger.error(f"BSE initialization error: {e}")
                logger.error(f"This might be a version issue. Trying alternate initialization...")
                # Try alternate approach
                import os
                os.makedirs('/tmp/bse_downloads', exist_ok=True)
                bse = BSE('/tmp/bse_downloads')
                response = bse.announcements()
                bse.exit()
            
            # Process response (whether from try or except block)
            if response and 'Table' in response:
                announcements = response['Table']
                logger.info(f"BSE library returned {len(announcements)} announcements")
                return await self.parse(announcements)
            else:
                logger.warning("BSE library returned empty or invalid response")
                return []
                    
        except Exception as e:
            logger.error(f"BSE library error: {e}")
            return []
    
    async def parse(self, data: List[dict]) -> List[Announcement]:
        """Parse BSE library response"""
        announcements = []
        
        for item in data:
            try:
                # Get the announcement details
                headline = item.get('HEADLINE', '') or item.get('MORE', '')
                subcategory = item.get('SUBCATNAME', '')
                
                # Check if this is a quarterly result
                combined_text = f"{headline} {subcategory}".lower()
                if not self.is_quarterly_result(combined_text):
                    continue
                
                # Extract symbol from company name (scrip code)
                scrip_code = item.get('SCRIP_CD', '')
                company_name = item.get('SLONGNAME', '')
                
                # Get PDF attachment if available
                attachment_name = item.get('ATTACHMENTNAME', '')
                attachment_url = ''
                if attachment_name:
                    # BSE PDF URL format
                    attachment_url = f"https://www.bseindia.com/xml-data/corpfiling/AttachLive/{attachment_name}"
                
                # Parse date
                date_str = item.get('NEWS_DT', '') or item.get('DT_TM', '')
                
                ann = Announcement(
                    source='bse_library',
                    symbol=f"{scrip_code}",
                    date=date_str,
                    description=headline,
                    attachment_url=attachment_url,
                    attachment_text=company_name,
                    timestamp=datetime.now()
                )
                
                if ann.symbol and (ann.attachment_url or ann.description):
                    announcements.append(ann)
                    logger.debug(f"BSE: Found result for {company_name} ({scrip_code})")
                    
            except Exception as e:
                logger.error(f"BSE parse error for item: {e}")
                continue
        
        logger.info(f"BSE Library: Found {len(announcements)} result announcements")
        
        # Debug: Log details of found announcements
        for ann in announcements:
            logger.debug(f"  BSE Result: {ann.symbol} | Date: {ann.date} | Desc: {ann.description[:80]}")
        
        return announcements

