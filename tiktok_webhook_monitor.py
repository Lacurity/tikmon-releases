#!/usr/bin/env python3
"""
TikTok Live & Upload Monitor with Webhook Support
Monitors @kloudy_gaming for live streams, offline events, and new uploads
Sends webhook messages instead of Discord bot messages
"""

import asyncio
import json
import logging
import os
import re
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
import aiohttp
import requests

class TikTokWebhookMonitor:
    """Monitor TikTok user for live status and uploads, send webhook notifications."""
    
    def __init__(self):
        # Hardcoded configuration - no config file needed
        self.username = "kloudy_gaming"
        self.webhook_url = "https://discord.com/api/webhooks/1428908394441474088/YjTzO5bEyLpEvLA7WRfLowDgramjZBG6fI9aW1tMSWM1GJO9gew0kjYyrWk2dPOigFiL"
        self.check_interval = 45
        self.monitor_uploads = True
        self.upload_check_interval = 300
        self.enable_logging = True
        self.webhook_username = "Lacs Monitor"
        self.webhook_avatar_url = "https://cdn-icons-png.flaticon.com/512/3046/3046121.png"
        
        # State tracking
        self.is_live = False
        self.last_live_check = None
        self.live_data = None
        self.last_video_count = 0
        self.last_upload_check = None
        
        # Statistics tracking
        self.stats = {
            "total_checks": 0,
            "failed_checks": 0,
            "live_detections": 0,
            "upload_detections": 0,
            "webhooks_sent": 0,
            "start_time": datetime.utcnow()
        }
        
        # Setup logging with UTF-8 encoding for Windows - only file logging, no console
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('tiktok_monitor.log', encoding='utf-8')
                # No StreamHandler = no console output
            ],
            force=True
        )
        self.logger = logging.getLogger(__name__)
        
        # Show banner
        self.show_banner()
    
    def show_banner(self) -> None:
        """Display ASCII banner and initial status - stays at top."""
        # Clear screen and move cursor to top
        os.system('cls' if os.name == 'nt' else 'clear')
        
        banner = """
 _  __                           __  __             _ _             
| |/ /__ _ _ __ _ __ ___   __ _  |  \/  | ___  _ __ (_) |_ ___  _ __ 
| ' // _` | '__| '_ ` _ \ / _` | | |\/| |/ _ \| '_ \| | __/ _ \| '__|
| . \ (_| | |  | | | | | | (_| | | |  | | (_) | | | | | || (_) | |   
|_|\_\__,_|_|  |_| |_| |_|\__,_| |_|  |_|\___/|_| |_|_|\__\___/|_|   
                                                                     
                                by Lac                                
================================================================"""
        print(banner)
        print(f"Target: @{self.username} | Interval: {self.check_interval}s | Webhook: {'✅' if self.webhook_url != 'YOUR_WEBHOOK_URL_HERE' else '❌'}")
        print("================================================================")
        
    def print_status_update(self, message: str, status_type: str = "info") -> None:
        """Print live/offline events and errors."""
        # Show live, offline, and errors
        if status_type in ["live", "offline", "error"]:
            status_icons = {
                "live": "🔴 [LIVE]",
                "offline": "⚫ [END ]",
                "error": "❌ [ERR ]"
            }
            icon = status_icons.get(status_type, "❌")
            # Print new line first to ensure events appear on new lines
            print(f"\n{icon} {message}")
        
    def update_status_line(self) -> None:
        """Update the status line with current statistics - overwrites same line."""
        uptime = datetime.utcnow() - self.stats["start_time"]
        # Format uptime as hours and minutes counting from 0
        hours = int(uptime.total_seconds() // 3600)
        minutes = int((uptime.total_seconds() % 3600) // 60)
        uptime_str = f"{hours:02d}h{minutes:02d}m"
        
        status = (f"🔵 [Data] {self.stats['total_checks']} | "
                 f"Failed: {self.stats['failed_checks']} | "
                 f"Live: {self.stats['live_detections']} | "
                 f"Uploads: {self.stats['upload_detections']} | "
                 f"Webhooks: {self.stats['webhooks_sent']} | "
                 f"Uptime: {uptime_str}")
        
        # Use \r to overwrite the same line
        print(f"\r{status}", end="", flush=True)
        
    def clear_and_refresh_banner(self) -> None:
        """Refresh the entire display with banner at top."""
        self.show_banner()
        print("Monitor active - watching for live streams...")
    
    async def check_tiktok_live_status(self) -> Dict[str, Any]:
        """Check if the TikTok user is currently live using multiple methods."""
        
        # Method 1: Try API endpoint (most reliable)
        try:
            result = await self._check_tiktok_api()
            if result.get("is_live") is not None:
                return result
        except Exception as e:
            self.logger.debug(f"API method failed: {e}")
        
        # Method 2: Try direct web scraping
        try:
            result = await self._check_tiktok_web()
            if result.get("is_live") is not None:
                return result
        except Exception as e:
            self.logger.debug(f"Web method failed: {e}")
        
        # Method 3: Try mobile endpoint
        try:
            result = await self._check_tiktok_mobile()
            if result.get("is_live") is not None:
                return result
        except Exception as e:
            self.logger.debug(f"Mobile method failed: {e}")
        
        # Default: not live
        self.logger.warning(f"All TikTok check methods failed for @{self.username}")
        return {"is_live": False}
    
    async def _check_tiktok_api(self) -> Dict[str, Any]:
        """Check TikTok API endpoint for live status - most reliable method."""
        
        # Use the API endpoint that returns JSON data
        api_url = f"https://www.tiktok.com/api-live/user/room/?aid=1988&app_language=en&app_name=tiktok_web&browser_language=en-US&browser_name=Mozilla&browser_online=true&browser_platform=Win32&browser_version=5.0%20%28Windows%20NT%2010.0%3B%20Win64%3B%20x64%29%20AppleWebKit%2F537.36%20%28KHTML%2C%20like%20Gecko%29%20Chrome%2F120.0.0.0%20Safari%2F537.36&cookie_enabled=true&device_platform=web_pc&focus_state=true&from_page=&history_len=2&is_fullscreen=false&is_page_visible=true&screen_height=1080&screen_width=1920&tz_name=America/New_York&channel=tiktok_web&data_collection_enabled=true&os=windows&priority_region=US&region=US&user_is_login=false&webcast_language=en&msToken=&referer=https://www.tiktok.com/@{self.username}/live&root_referer=https://www.tiktok.com/@{self.username}/live&uniqueId={self.username}&sourceType=54"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'Referer': f'https://www.tiktok.com/@{self.username}/live',
            'Origin': 'https://www.tiktok.com',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin'
        }
        
        timeout = aiohttp.ClientTimeout(total=10)
        connector = aiohttp.TCPConnector(limit=10)
        
        async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
            self.logger.info(f"Checking TikTok API endpoint for @{self.username}")
            
            try:
                async with session.get(api_url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        # The API structure is: data.liveRoom.status and data.user.status
                        if 'data' in data and 'liveRoom' in data['data']:
                            live_room = data['data']['liveRoom']
                            room_status = live_room.get('status', 0)
                            user_data = data['data'].get('user', {})
                            user_status = user_data.get('status', 0)
                            
                            # TikTok live status codes:
                            # 2 = Currently live and broadcasting
                            # 4 = Live room exists but stream ended/offline  
                            # 0 = No live room/never went live
                            
                            if room_status == 2:
                                # User is actually live!
                                stats = live_room.get('liveRoomStats', {})
                                viewer_count = stats.get('userCount', 0)
                                enter_count = stats.get('enterCount', 0)
                                title = live_room.get('title', 'TikTok Live Stream')
                                
                                self.logger.info(f"@{self.username} is LIVE! (API room status = 2)")
                                return {
                                    "is_live": True,
                                    "title": title,
                                    "viewers": viewer_count,
                                    "total_viewers": enter_count,
                                    "url": f"https://www.tiktok.com/@{self.username}/live",
                                    "username": self.username,
                                    "method": "api_endpoint",
                                    "detection_reason": f"Live room status = {room_status}"
                                }
                            else:
                                # User is not live (status 4 = ended, status 0 = no room)
                                status_msg = "ended" if room_status == 4 else "no active room"
                                self.logger.info(f"@{self.username} is NOT live (room status = {room_status}, {status_msg})")
                                return {
                                    "is_live": False,
                                    "method": "api_endpoint",
                                    "detection_reason": f"Live room status = {room_status} ({status_msg})"
                                }
                        else:
                            # No live room data in response
                            self.logger.info(f"@{self.username} is NOT live (no liveRoom data in API response)")
                            return {
                                "is_live": False,
                                "method": "api_endpoint", 
                                "detection_reason": "No liveRoom data in API response"
                            }
                    else:
                        self.logger.debug(f"API endpoint returned status {response.status}")
                        raise Exception(f"API returned {response.status}")
                        
            except Exception as e:
                self.logger.debug(f"API endpoint check failed: {str(e)}")
                raise Exception(f"API endpoint failed: {str(e)}")
    
    async def _check_tiktok_web(self) -> Dict[str, Any]:
        """Check TikTok live endpoint for live status - same logic as Karma bot."""
        
        # Use the direct live endpoint - much more reliable
        live_url = f"https://www.tiktok.com/@{self.username}/live"
        
        # Use requests instead of aiohttp for compatibility with Karma bot logic
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
            'Upgrade-Insecure-Requests': '1',
            'DNT': '1',
            'Sec-CH-UA': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-CH-UA-Mobile': '?0',
            'Sec-CH-UA-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1'
        }
        
        self.logger.info(f"Checking TikTok live endpoint for @{self.username}")
        
        try:
            # Use requests library (synchronous) like in the working test
            import requests
            response = requests.get(live_url, headers=headers, timeout=15, allow_redirects=False)
            status_code = response.status_code
            self.logger.info(f"Live endpoint returned status: {status_code}")
            
            if status_code == 200:
                # Status 200 doesn't always mean live - need to check content
                content = response.text
                self.logger.info(f"Got HTTP 200 on /live endpoint for @{self.username}, checking content...")
                
                # Check for actual live stream indicators
                live_indicators = [
                    '"isLive":true',
                    '"liveStatus":1', 
                    '"roomStatus":2',
                    '"status":2',  # Live room status ONLY when room is active
                    'data-e2e="live-avatar"',
                    'live-room-player',
                    'live-stream-container',
                    '"liveRoom":{"status":2',  # Only status 2 means actually live
                    'class="live-indicator"'  # More specific live indicator
                ]
                
                # Check for "not live" indicators that override live detection
                not_live_indicators = [
                    '"isLive":false',
                    '"liveStatus":0',
                    '"roomStatus":0',
                    '"roomStatus":4',  # Room ended
                    '"status":0',
                    '"status":4',  # User/room offline or ended
                    'user-not-live',
                    'live-room-ended',
                    'No live videos',
                    '"liveRoom":{"status":4',  # Live room ended
                    '"user":{"status":4'  # User offline
                ]
                
                # First check for explicit "not live" indicators
                has_not_live_indicator = any(indicator in content for indicator in not_live_indicators)
                if has_not_live_indicator:
                    self.logger.info(f"@{self.username} is NOT live (found not-live indicators)")
                    return {
                        "is_live": False,
                        "method": "live_endpoint",
                        "detection_reason": "Not-live indicators found in page content"
                    }
                
                # Check for live indicators
                has_live_indicator = any(indicator in content for indicator in live_indicators)
                
                if not has_live_indicator:
                    # No live indicators found - probably showing profile page
                    self.logger.info(f"@{self.username} is NOT live (no live indicators in content)")
                    return {
                        "is_live": False,
                        "method": "live_endpoint",
                        "detection_reason": "No live indicators found in page content"
                    }
                
                # Found live indicators - user is actually live!
                self.logger.info(f"@{self.username} is LIVE! (found live indicators in content)")
                
                # Try to extract viewer count and likes from live page
                viewer_count = 0
                like_count = 0
                total_viewers = 0
                
                # Enhanced patterns for viewer count
                viewer_patterns = [
                    r'"viewerCount":(\d+)',
                    r'"user_count":(\d+)',
                    r'"userCount":(\d+)',
                    r'"audience_count":(\d+)',
                    r'"total_user":(\d+)',
                    r'"liveRoomStats":\s*\{[^}]*"userCount":(\d+)',
                    r'"stats":\s*\{[^}]*"viewerCount":(\d+)'
                ]
                
                # Patterns for like count
                like_patterns = [
                    r'"diggCount":(\d+)',
                    r'"likeCount":(\d+)',
                    r'"like_count":(\d+)',
                    r'"totalLikes":(\d+)',
                    r'"liveRoomStats":\s*\{[^}]*"likeCount":(\d+)',
                    r'"stats":\s*\{[^}]*"diggCount":(\d+)'
                ]
                
                # Patterns for total/peak viewers
                total_viewer_patterns = [
                    r'"totalUser":(\d+)',
                    r'"total_user":(\d+)',
                    r'"peakViewerCount":(\d+)',
                    r'"maxUserCount":(\d+)',
                    r'"liveRoomStats":\s*\{[^}]*"totalUser":(\d+)'
                ]
                
                # Extract viewer count
                for pattern in viewer_patterns:
                    match = re.search(pattern, content)
                    if match:
                        viewer_count = int(match.group(1))
                        self.logger.info(f"Found {viewer_count} current viewers")
                        break
                
                # Extract like count
                for pattern in like_patterns:
                    match = re.search(pattern, content)
                    if match:
                        like_count = int(match.group(1))
                        self.logger.info(f"Found {like_count} likes")
                        break
                
                # Extract total/peak viewers
                for pattern in total_viewer_patterns:
                    match = re.search(pattern, content)
                    if match:
                        total_viewers = int(match.group(1))
                        self.logger.info(f"Found {total_viewers} total viewers")
                        break
                
                return {
                    "is_live": True,
                    "title": "TikTok Live Stream",
                    "viewers": viewer_count,
                    "likes": like_count,
                    "total_viewers": total_viewers,
                    "url": live_url,
                    "username": self.username,
                    "method": "live_endpoint",
                    "detection_reason": "Live indicators found in page content"
                }
                
            elif status_code == 302 or status_code == 301:
                # Redirect usually means not live - check where it redirects
                redirect_location = response.headers.get('Location', '')
                self.logger.info(f"Live endpoint redirected to: {redirect_location}")
                
                if '/live' not in redirect_location:
                    # Redirected away from live page = not live
                    self.logger.info(f"@{self.username} is not live (redirected away from /live)")
                    return {
                        "is_live": False,
                        "method": "live_endpoint", 
                        "detection_reason": f"Redirected to: {redirect_location}"
                    }
                else:
                    # Still on live page, might be live - follow redirect
                    redirect_response = requests.get(redirect_location, headers=headers, timeout=15)
                    if redirect_response.status_code == 200:
                        content = redirect_response.text
                        
                        # Check for live indicators in redirected page
                        live_indicators = [
                            '"isLive":true',
                            '"liveStatus":1',
                            '"roomStatus":2',
                            'live-indicator',
                            '"LiveRoom"'
                        ]
                        
                        is_live = any(indicator in content for indicator in live_indicators)
                        
                        if is_live:
                            self.logger.info(f"@{self.username} is LIVE! (found indicators after redirect)")
                            return {
                                "is_live": True,
                                "title": "TikTok Live Stream", 
                                "viewers": 0,
                                "url": live_url,
                                "username": self.username,
                                "method": "live_endpoint",
                                "detection_reason": "Live indicators in redirected page"
                            }
                        else:
                            self.logger.info(f"@{self.username} is not live (no indicators after redirect)")
                            return {
                                "is_live": False,
                                "method": "live_endpoint",
                                "detection_reason": "No live indicators after redirect"
                            }
                    else:
                        self.logger.warning(f"Redirect failed with status: {redirect_response.status_code}")
                        return {
                            "is_live": False,
                            "method": "live_endpoint",
                            "detection_reason": f"Redirect failed: {redirect_response.status_code}"
                        }
            
            elif status_code == 404:
                # User doesn't exist or page not found
                self.logger.warning(f"User @{self.username} not found (404)")
                return {
                    "is_live": False,
                    "method": "live_endpoint",
                    "detection_reason": "User not found (404)"
                }
            
            else:
                # Other status codes (403, 503, etc.)
                self.logger.warning(f"Unexpected status {status_code} on live endpoint")
                return {
                    "is_live": False,
                    "method": "live_endpoint", 
                    "detection_reason": f"HTTP {status_code}"
                }
                
        except requests.RequestException as e:
            self.logger.error(f"Request error checking live endpoint: {e}")
            return {
                "is_live": False,
                "method": "live_endpoint",
                "detection_reason": f"Request error: {str(e)}"
            }
    
    async def _check_tiktok_mobile(self) -> Dict[str, Any]:
        """Try TikTok mobile live endpoint - backup method."""
        mobile_live_url = f"https://m.tiktok.com/@{self.username}/live"
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 16_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.0 Mobile/15E148 Safari/604.1',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
        
        timeout = aiohttp.ClientTimeout(total=10)
        connector = aiohttp.TCPConnector(limit=10)
        
        async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
            self.logger.info(f"Checking mobile live endpoint for @{self.username}")
            
            try:
                async with session.get(mobile_live_url, headers=headers, allow_redirects=False) as response:
                    status_code = response.status
                    self.logger.info(f"Mobile live endpoint returned status: {status_code}")
                    
                    if status_code == 200:
                        # Status 200 on mobile doesn't always mean live - check content
                        content = await response.text()
                        self.logger.info(f"Got HTTP 200 on mobile /live endpoint for @{self.username}, checking content...")
                        
                        # Check for live indicators in mobile version
                        mobile_live_indicators = [
                            '"isLive":true',
                            '"liveStatus":1',
                            '"roomStatus":2',
                            'live-indicator',
                            'data-live="true"',
                            'live-room',
                            '"status":2'
                        ]
                        
                        # Check for not-live indicators
                        mobile_not_live_indicators = [
                            '"isLive":false',
                            '"liveStatus":0',
                            '"roomStatus":0',
                            '"status":0',
                            'user-not-live'
                        ]
                        
                        # Check for not-live indicators first
                        has_not_live = any(indicator in content for indicator in mobile_not_live_indicators)
                        if has_not_live:
                            self.logger.info(f"@{self.username} is NOT live (mobile not-live indicators)")
                            return {
                                "is_live": False,
                                "method": "mobile_live_endpoint",
                                "detection_reason": "Not-live indicators found in mobile page"
                            }
                        
                        # Check for live indicators
                        has_live = any(indicator in content for indicator in mobile_live_indicators)
                        if has_live:
                            self.logger.info(f"@{self.username} is LIVE! (Mobile live indicators found)")
                            return {
                                "is_live": True,
                                "title": "TikTok Live Stream",
                                "viewers": 0,
                                "url": mobile_live_url,
                                "username": self.username,
                                "method": "mobile_live_endpoint",
                                "detection_reason": "Live indicators found in mobile page"
                            }
                        else:
                            self.logger.info(f"@{self.username} is NOT live (no mobile live indicators)")
                            return {
                                "is_live": False,
                                "method": "mobile_live_endpoint",
                                "detection_reason": "No live indicators in mobile page"
                            }
                    else:
                        # Any other status = not live
                        self.logger.info(f"@{self.username} is not live (mobile endpoint status {status_code})")
                        return {
                            "is_live": False,
                            "method": "mobile_live_endpoint",
                            "detection_reason": f"HTTP {status_code} on mobile /live endpoint"
                        }
                        
            except Exception as e:
                self.logger.warning(f"Mobile live endpoint check failed: {str(e)}")
                raise Exception(f"Mobile endpoint failed: {str(e)}")
    
    async def check_new_uploads(self) -> List[Dict[str, Any]]:
        """Check for new video uploads."""
        if not self.monitor_uploads:
            return []
        
        try:
            url = f"https://www.tiktok.com/@{self.username}"
            
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-US,en;q=0.9',
            }
            
            timeout = aiohttp.ClientTimeout(total=15)
            connector = aiohttp.TCPConnector(limit=100, limit_per_host=30)
            
            async with aiohttp.ClientSession(timeout=timeout, connector=connector) as session:
                async with session.get(url, headers=headers, allow_redirects=True) as response:
                    if response.status == 200:
                        content = await response.text()
                        
                        # Extract video data - look for video patterns
                        video_pattern = r'"id":"(\d+)".*?"desc":"([^"]*)".*?"createTime":(\d+)'
                        videos = re.findall(video_pattern, content)
                        
                        new_videos = []
                        current_time = int(time.time())
                        
                        for video_id, description, create_time in videos:
                            create_time = int(create_time)
                            # Consider videos uploaded in the last hour as "new"
                            if current_time - create_time < 3600:  # 1 hour
                                new_videos.append({
                                    "id": video_id,
                                    "description": description,
                                    "create_time": create_time,
                                    "url": f"https://www.tiktok.com/@{self.username}/video/{video_id}"
                                })
                        
                        return new_videos
                    
        except Exception as e:
            self.logger.error(f"Error checking uploads: {e}")
        
        return []
    
    def send_webhook(self, title: str, description: str, color: int = 0xFF0000, fields: List[Dict] = None, ping_everyone: bool = False) -> bool:
        """Send a webhook message."""
        try:
            webhook_data = {
                "embeds": [{
                    "title": title,
                    "description": description,
                    "color": color,
                    "timestamp": datetime.utcnow().isoformat(),
                    "footer": {
                        "text": "Lacs Monitor"
                    }
                }]
            }
            
            # Add @everyone ping if requested
            if ping_everyone:
                webhook_data["content"] = "@everyone"
                webhook_data["allowed_mentions"] = {
                    "parse": ["everyone"]
                }
            
            # Add hardcoded webhook settings
            webhook_data["username"] = self.webhook_username
            webhook_data["avatar_url"] = self.webhook_avatar_url
            
            # Add fields if provided
            if fields:
                webhook_data["embeds"][0]["fields"] = fields
            
            response = requests.post(self.webhook_url, json=webhook_data, timeout=10)
            response.raise_for_status()
            
            # Track successful webhook
            self.stats["webhooks_sent"] += 1
            return True
            
        except Exception as e:
            self.print_status_update(f"Webhook failed: {e}", "error")
            return False
    
    async def send_live_notification(self, live_data: Dict[str, Any]) -> None:
        """Send live stream notification via webhook."""
        title = "🔴 TikTok Live Stream Started!"
        description = f"**@{live_data['username']}** is now live on TikTok!"
        
        fields = [
            {"name": "👤 Streamer", "value": f"@{live_data['username']}", "inline": True},
            {"name": "👀 Current Viewers", "value": f"{live_data.get('viewers', 0):,}", "inline": True}
        ]
        
        # Add likes if available
        if live_data.get('likes', 0) > 0:
            fields.append({"name": "❤️ Likes", "value": f"{live_data['likes']:,}", "inline": True})
        
        # Add total viewers if available and different from current
        if live_data.get('total_viewers', 0) > 0 and live_data.get('total_viewers', 0) != live_data.get('viewers', 0):
            fields.append({"name": "📊 Total Views", "value": f"{live_data['total_viewers']:,}", "inline": True})
        
        fields.append({"name": "🔗 Watch Now", "value": f"[Click here to watch!]({live_data['url']})", "inline": False})
        
        if live_data.get('detection_reason'):
            fields.append({"name": "🔍 Detection", "value": live_data['detection_reason'], "inline": False})
        
        success = self.send_webhook(title, description, color=0xFF0000, fields=fields, ping_everyone=True)
        if success:
            # Use simple text for console logging to avoid Unicode issues
            self.logger.info(f"Sent live notification for @{live_data['username']}")
    
    async def send_offline_notification(self, final_stats: Dict[str, Any] = None) -> None:
        """Send offline notification via webhook with final stream stats."""
        title = "📱 TikTok Stream Ended"
        description = f"**@{self.username}** has ended their live stream."
        
        fields = [
            {"name": "👤 Streamer", "value": f"@{self.username}", "inline": True},
            {"name": "📺 Status", "value": "Stream ended", "inline": True}
        ]
        
        # Add final stats if available
        if final_stats:
            if final_stats.get("viewers", 0) > 0:
                fields.append({"name": "👥 Final Viewers", "value": f"{final_stats['viewers']:,}", "inline": True})
            
            if final_stats.get("likes", 0) > 0:
                fields.append({"name": "❤️ Total Likes", "value": f"{final_stats['likes']:,}", "inline": True})
            
            if final_stats.get("total_viewers", 0) > 0:
                fields.append({"name": "📊 Peak/Total Views", "value": f"{final_stats['total_viewers']:,}", "inline": True})
        
        fields.append({"name": "💙 Thanks", "value": "Thanks for watching!", "inline": False})
        
        success = self.send_webhook(title, description, color=0x0099FF, fields=fields)
        if success:
            self.logger.info(f"Sent offline notification for @{self.username}")
            if final_stats:
                self.logger.info(f"Final stats - Viewers: {final_stats.get('viewers', 0)}, Likes: {final_stats.get('likes', 0)}, Total: {final_stats.get('total_viewers', 0)}")
    
    async def send_upload_notification(self, videos: List[Dict[str, Any]]) -> None:
        """Send new upload notification via webhook."""
        if not videos:
            return
        
        if len(videos) == 1:
            video = videos[0]
            title = "📹 New TikTok Upload!"
            description = f"**@{self.username}** just uploaded a new video!"
            
            fields = [
                {"name": "👤 Creator", "value": f"@{self.username}", "inline": True},
                {"name": "📝 Description", "value": video.get('description', 'No description')[:100], "inline": False},
                {"name": "🔗 Watch", "value": f"[View Video]({video['url']})", "inline": True}
            ]
        else:
            title = f"📹 {len(videos)} New TikTok Uploads!"
            description = f"**@{self.username}** just uploaded {len(videos)} new videos!"
            
            fields = [{"name": "👤 Creator", "value": f"@{self.username}", "inline": True}]
            
            for i, video in enumerate(videos[:3], 1):  # Show max 3 videos
                fields.append({
                    "name": f"Video {i}",
                    "value": f"[{video.get('description', 'No description')[:50]}...]({video['url']})",
                    "inline": False
                })
        
        success = self.send_webhook(title, description, color=0x00D4FF, fields=fields)
        if success:
            self.logger.info(f"Sent upload notification for {len(videos)} video(s)")
    
    async def monitor_loop(self) -> None:
        """Main monitoring loop."""
        
        while True:
            try:
                # Update stats
                self.stats["total_checks"] += 1
                
                # Check live status
                live_data = await self.check_tiktok_live_status()
                current_live_status = live_data.get("is_live", False)
                
                # Check for status changes
                if current_live_status and not self.is_live:
                    # Just went live
                    self.stats["live_detections"] += 1
                    self.is_live = True
                    self.live_data = live_data
                    await self.send_live_notification(live_data)
                    
                    # Show live notification
                    viewers = live_data.get("viewers", 0)
                    likes = live_data.get("likes", 0)
                    msg = f"{self.username} went LIVE!"
                    if viewers > 0:
                        msg += f" ({viewers:,} viewers"
                        if likes > 0:
                            msg += f", {likes:,} likes"
                        msg += ")"
                    self.print_status_update(msg, "live")
                    
                elif not current_live_status and self.is_live:
                    # Just went offline
                    final_stats = self.live_data if self.live_data else {}
                    self.is_live = False
                    self.live_data = None
                    await self.send_offline_notification(final_stats)
                    
                    # Show offline notification
                    final_viewers = final_stats.get("viewers", 0)
                    final_likes = final_stats.get("likes", 0)
                    msg = f"{self.username} live ended!"
                    if final_viewers > 0 or final_likes > 0:
                        stats_parts = []
                        if final_viewers > 0:
                            stats_parts.append(f"{final_viewers:,} viewers")
                        if final_likes > 0:
                            stats_parts.append(f"{final_likes:,} likes")
                        if stats_parts:
                            msg += f" ({', '.join(stats_parts)})"
                    self.print_status_update(msg, "offline")
                
                elif current_live_status and self.is_live:
                    # Still live, update data
                    self.live_data = live_data
                
                self.last_live_check = datetime.utcnow()
                
                # Check for uploads periodically (every 5 minutes)
                upload_check_interval = self.upload_check_interval
                if (self.last_upload_check is None or 
                    (datetime.utcnow() - self.last_upload_check).seconds >= upload_check_interval):
                    
                    new_videos = await self.check_new_uploads()
                    if new_videos:
                        self.stats["upload_detections"] += len(new_videos)
                        await self.send_upload_notification(new_videos)
                    
                    self.last_upload_check = datetime.utcnow()
                
                # Show data line
                self.update_status_line()
                
            except Exception as e:
                self.stats["failed_checks"] += 1
                self.print_status_update(f"Check failed: {str(e)}", "error")
                self.update_status_line()
            
            # Wait before next check
            await asyncio.sleep(self.check_interval)
    
    async def run(self) -> None:
        """Run the monitor."""
        try:
            await self.monitor_loop()
        except KeyboardInterrupt:
            self.logger.info("Monitor stopped by user")
        except Exception as e:
            self.logger.error(f"Monitor crashed: {e}")
            raise


async def main():
    """Main entry point."""
    try:
        monitor = TikTokWebhookMonitor()
        await monitor.run()
    except Exception as e:
        print(f"❌ [ERR ] Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())