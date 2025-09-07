import time
import statistics
import json
import asyncio
import aiohttp
from yarl import URL
from typing import List, Dict, Optional
from datetime import datetime
import psutil
import traceback
import logging
from pathlib import Path

from evaluation.test_datasets import MedicalReferralTestDataset, PerformanceBenchmarks

logger = logging.getLogger(__name__)

class FastAPISystemEvaluator:
    """Quantitative evaluation for your FastAPI medical referral system"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session_cookies = {}
        self.cookie_jar = aiohttp.CookieJar()  # Persistent cookie jar
        self.test_data = MedicalReferralTestDataset()
        self.benchmarks = PerformanceBenchmarks()
        self.results_dir = Path("evaluation_results")
        self.results_dir.mkdir(exist_ok=True)
        
    async def check_server_connectivity(self) -> bool:
        """Check if FastAPI server is accessible"""
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    self.base_url,
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    logger.info(f" Server accessible: HTTP {response.status}")
                    return True
                    
        except aiohttp.ClientConnectorError:
            logger.error(f" Cannot connect to {self.base_url}")
            logger.error(" Make sure FastAPI server is running: python app.py")
            return False
        except Exception as e:
            logger.error(f" Server check failed: {e}")
            return False

    async def authenticate_system(self, username: str = "admin", password: str = "hospital123") -> bool:
        """Authenticate with your FastAPI system"""
        
        try:
            # Use the persistent cookie jar
            async with aiohttp.ClientSession(
                cookie_jar=self.cookie_jar
            ) as session:
                
                login_url = f"{self.base_url}/login"  # Initialize default login URL
                
                # Check if login page exists
                async with session.get(
                    f"{self.base_url}/login",
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    
                    if response.status == 404:
                        logger.error(" Login endpoint not found - checking alternative paths")
                        
                        # Try alternative login paths
                        alternative_paths = ["/auth/login", "/api/login", "/user/login"]
                        
                        for path in alternative_paths:
                            try:
                                async with session.get(f"{self.base_url}{path}") as alt_response:
                                    if alt_response.status != 404:
                                        logger.info(f" Found login at: {path}")
                                        login_url = f"{self.base_url}{path}"
                                        break
                            except:
                                continue
                        else:
                            logger.warning("No login endpoint found - trying direct access")
                            return True  # Assume no authentication required
                
                # Attempt login
                login_data = {
                    "username": username,
                    "password": password
                }
                
                async with session.post(
                    login_url,
                    data=login_data,
                    allow_redirects=False,
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    
                    # Check for successful login (redirect or success response)
                    if response.status in [200, 302, 303]:
                        # Extract all cookies from the session
                        self.session_cookies = {}
                        
                        for cookie in self.cookie_jar:
                            self.session_cookies[cookie.key] = cookie.value
                        
                        logger.info(f" Authentication successful - stored {len(self.session_cookies)} cookies")
                        logger.info(f" Cookie names: {list(self.session_cookies.keys())}")
                        return True
                    else:
                        logger.error(f" Authentication failed: HTTP {response.status}")
                        response_text = await response.text()
                        logger.error(f"Response: {response_text[:200]}")
                        return False
                        
        except aiohttp.ClientConnectorError:
            logger.error(" Cannot connect to FastAPI server - is it running on localhost:8000?")
            return False
        except Exception as e:
            logger.error(f" Authentication error: {e}")
            return False

    async def measure_api_performance(self, num_requests: int = 30) -> Dict:
        """Measure performance of your FastAPI endpoints"""
        
        test_endpoints = [
            {
                "name": "Dashboard",
                "method": "GET",
                "url": f"{self.base_url}/dashboard",
                "requires_auth": True
            },
            {
                "name": "Referrals Management",
                "method": "GET",
                "url": f"{self.base_url}/referrals/manage",
                "requires_auth": True
            },
            {
                "name": "Health Check",
                "method": "GET",
                "url": f"{self.base_url}/health",
                "requires_auth": False
            },
            {
                "name": "Root Endpoint",
                "method": "GET",
                "url": f"{self.base_url}/",
                "requires_auth": False
            }
        ]
        
        results = {}
        
        for endpoint in test_endpoints:
            logger.info(f" Testing {endpoint['name']} endpoint...")
            
            response_times = []
            success_count = 0
            error_count = 0
            
            # Use the persistent cookie jar for authenticated requests
            cookie_jar = self.cookie_jar if endpoint['requires_auth'] else aiohttp.CookieJar()
            
            async with aiohttp.ClientSession(cookie_jar=cookie_jar) as session:
                for i in range(num_requests):
                    start_time = time.time()
                    
                    try:
                        # The cookie jar automatically handles cookies
                        
                        if endpoint['method'] == 'POST':
                            async with session.post(
                                endpoint['url'],
                                data=endpoint.get('data', {}),
                                timeout=aiohttp.ClientTimeout(total=30)
                            ) as response:
                                await response.read()
                        else:
                            async with session.get(
                                endpoint['url'],
                                timeout=aiohttp.ClientTimeout(total=30)
                            ) as response:
                                await response.read()
                        
                        end_time = time.time()
                        response_time = (end_time - start_time) * 1000
                        response_times.append(response_time)
                        
                        if response.status < 400:
                            success_count += 1
                        else:
                            error_count += 1
                            
                    except Exception as e:
                        error_count += 1
                        logger.warning(f"Request {i+1} failed for {endpoint['name']}: {e}")
            
            if response_times:
                results[endpoint['name']] = {
                    'mean_response_time_ms': round(statistics.mean(response_times), 2),
                    'median_response_time_ms': round(statistics.median(response_times), 2),
                    'p95_response_time_ms': round(sorted(response_times)[int(0.95 * len(response_times))], 2),
                    'success_rate': round(success_count / num_requests * 100, 2),
                    'error_rate': round(error_count / num_requests * 100, 2)
                }
                
                logger.info(f" {endpoint['name']}: {results[endpoint['name']]['mean_response_time_ms']}ms avg")
        
        return results

    async def evaluate_ai_accuracy(self) -> Dict:
        """Test AI accuracy using your upload_and_query endpoint"""
        
        test_cases = self.test_data.get_priority_classification_dataset()
        
        results = {
            "total_cases": len(test_cases),
            "successful_analyses": 0,
            "failed_analyses": 0,
            "priority_correct": 0,
            "processing_times": [],
            "detailed_results": []
        }
        
        logger.info(" Testing AI accuracy...")
        
        # Debug current session state
        logger.info(f" Available session cookies: {len(self.session_cookies)}")
        if self.session_cookies:
            logger.info(f" Cookie names: {list(self.session_cookies.keys())}")
        
        # Use the persistent cookie jar that already has authentication cookies
        async with aiohttp.ClientSession(
            cookie_jar=self.cookie_jar,
            timeout=aiohttp.ClientTimeout(total=60)
        ) as session:
            
            for test_case in test_cases:
                try:
                    # Prepare form data
                    form_data = aiohttp.FormData()
                    form_data.add_field('query', test_case["referral_text"])
                    form_data.add_field('request_type', 'referral')
                    form_data.add_field('context_data', '')
                    
                    start_time = time.time()
                    
                    # Headers that match browser behavior
                    headers = {
                        'Accept': 'application/json, text/html, application/xhtml+xml, */*',
                        'Accept-Language': 'en-US,en;q=0.9',
                        'Accept-Encoding': 'gzip, deflate',
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                        'Origin': self.base_url,
                        'Referer': f"{self.base_url}/dashboard"
                    }
                    
                    logger.info(f" Testing {test_case['case_id']}...")
                    
                    async with session.post(
                        f"{self.base_url}/upload_and_query",
                        data=form_data,
                        headers=headers,
                        allow_redirects=False
                    ) as response:
                        
                        end_time = time.time()
                        processing_time = (end_time - start_time) * 1000
                        results["processing_times"].append(processing_time)
                        
                        logger.info(f" {test_case['case_id']} response: HTTP {response.status}")
                        
                        if response.status == 200:
                            # Success case
                            try:
                                ai_result = await response.json()
                                results["successful_analyses"] += 1
                                
                                # Extract priority from response
                                referral_priority = ai_result.get("referral_priority", "")
                                ai_priority = self._extract_priority(referral_priority)
                                
                                # Check accuracy
                                ground_truth = test_case["ground_truth"]["priority"].lower()
                                priority_correct = self._normalize_priority(ai_priority) == self._normalize_priority(ground_truth)
                                
                                if priority_correct:
                                    results["priority_correct"] += 1
                                
                                results["detailed_results"].append({
                                    "case_id": test_case["case_id"],
                                    "ai_priority": ai_priority,
                                    "ground_truth": ground_truth,
                                    "correct": priority_correct,
                                    "processing_time_ms": processing_time
                                })
                                
                                logger.info(f" {test_case['case_id']}: {ai_priority} (correct: {priority_correct}, {processing_time:.0f}ms)")
                                
                            except json.JSONDecodeError:
                                response_text = await response.text()
                                logger.error(f" {test_case['case_id']}: Invalid JSON response")
                                logger.error(f"Response preview: {response_text[:200]}")
                                results["failed_analyses"] += 1
                                
                        elif response.status in [302, 401]:
                            # Authentication issue
                            logger.error(f" {test_case['case_id']}: HTTP {response.status} - Re-authenticating...")
                            results["failed_analyses"] += 1
                            
                            # Try to re-authenticate for next request
                            if await self.authenticate_system():
                                # Update jar with new cookies
                                for name, value in self.session_cookies.items():
                                    session.cookie_jar.update_cookies({name: value}, response_url=URL(self.base_url))
                        
                        else:
                            # Other error
                            response_text = await response.text()
                            logger.error(f" {test_case['case_id']}: HTTP {response.status}")
                            logger.error(f"Response preview: {response_text[:200]}")
                            results["failed_analyses"] += 1
                            
                except Exception as e:
                    results["failed_analyses"] += 1
                    logger.error(f" {test_case['case_id']} exception: {e}")
    
        # Calculate metrics
        if results["successful_analyses"] > 0:
            results["priority_accuracy"] = round(results["priority_correct"] / results["successful_analyses"] * 100, 2)
            results["avg_processing_time_ms"] = round(statistics.mean(results["processing_times"]), 2)
        else:
            results["priority_accuracy"] = 0
            results["avg_processing_time_ms"] = 0
        
        return results

    def _extract_priority(self, response_text: str) -> str:
        """Extract priority from AI response with improved precision"""
        if not response_text:
            return "Unknown"
        
        text_lower = response_text.lower()
        
        # To look for explicit priority classifications first
        patterns = [
            "priority classification: routine",
            "priority: routine", 
            "classification: routine",
            "nhs priority: routine",
            "priority classification: emergent",
            "priority: emergent",
            "classification: emergent", 
            "nhs priority: emergent",
            "priority classification: urgent",
            "priority: urgent",
            "classification: urgent",
            "nhs priority: urgent"
        ]
        
        for pattern in patterns:
            if pattern in text_lower:
                if "routine" in pattern:
                    return "Routine"
                elif "emergent" in pattern:
                    return "Emergent"
                elif "urgent" in pattern:
                    return "Urgent"
        
        # To look for standalone priority words in context
        lines = response_text.split('\n')
        for line in lines:
            line_lower = line.lower().strip()
            
            # Check for lines that explicitly state the priority
            if (line_lower.startswith('routine') or 
                line_lower.startswith('**routine') or
                'this case should be classified as routine' in line_lower or
                'classification: routine' in line_lower):
                return "Routine"
            elif (line_lower.startswith('emergent') or 
                  line_lower.startswith('**emergent') or
                  'this case should be classified as emergent' in line_lower or
                  'classification: emergent' in line_lower):
                return "Emergent"
            elif (line_lower.startswith('urgent') or 
                  line_lower.startswith('**urgent') or
                  'this case should be classified as urgent' in line_lower or
                  'classification: urgent' in line_lower):
                return "Urgent"
        
        # Fallback to simple keyword matching (last resort)
        if "emergent" in text_lower and "routine" not in text_lower and "urgent" not in text_lower:
            return "Emergent"
        elif "routine" in text_lower and "emergent" not in text_lower:
            return "Routine"
        elif "urgent" in text_lower and "routine" not in text_lower and "emergent" not in text_lower:
            return "Urgent"
        
        return "Unknown"

    def _normalize_priority(self, priority: str) -> str:
        """Normalize priority for comparison"""
        if not priority:
            return "routine"
        
        priority_lower = priority.lower()
        
        if priority_lower in ["emergent", "emergency", "critical"]:
            return "emergent"
        elif priority_lower in ["urgent", "high"]:
            return "urgent"
        else:
            return "routine"

    def measure_system_resources(self, duration_seconds: int = 30) -> Dict:
        """Monitor system resource usage"""
        
        logger.info(f" Monitoring resources for {duration_seconds}s...")
        
        cpu_readings = []
        memory_readings = []
        
        start_time = time.time()
        
        while time.time() - start_time < duration_seconds:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory_percent = psutil.virtual_memory().percent
            
            cpu_readings.append(cpu_percent)
            memory_readings.append(memory_percent)
        
        return {
            "cpu_usage": {
                "average_percent": round(statistics.mean(cpu_readings), 2),
                "max_percent": round(max(cpu_readings), 2)
            },
            "memory_usage": {
                "average_percent": round(statistics.mean(memory_readings), 2),
                "max_percent": round(max(memory_readings), 2)
            }
        }

    async def run_comprehensive_evaluation(self) -> Dict:
        """Run complete quantitative evaluation"""
        
        logger.info(" Starting Comprehensive Evaluation")
        start_time = datetime.now()
        
        evaluation_results = {
            "metadata": {
                "timestamp": start_time.isoformat(),
                "base_url": self.base_url,
                "evaluation_type": "FastAPI System Performance"
            }
        }
        
        try:
            # 0. Check server connectivity first
            logger.info("\n Checking Server Connectivity...")
            server_accessible = await self.check_server_connectivity()
            evaluation_results["server_connectivity"] = "SUCCESS" if server_accessible else "FAILED"
            
            if not server_accessible:
                logger.error(" Cannot proceed - server not accessible")
                return evaluation_results
            
            # 1. Authentication
            logger.info("\n Testing Authentication...")
            auth_success = await self.authenticate_system()
            evaluation_results["authentication_status"] = "SUCCESS" if auth_success else "FAILED"
            
            if not auth_success:
                logger.error(" Cannot proceed without authentication")
                return evaluation_results
            
            # 2. API Performance
            logger.info("\n Testing API Performance...")
            api_performance = await self.measure_api_performance()
            evaluation_results["api_performance"] = api_performance
            
            # 3. AI Accuracy
            logger.info("\n Testing AI Analysis...")
            ai_evaluation = await self.evaluate_ai_accuracy()
            evaluation_results["ai_analysis"] = ai_evaluation
            
            # 4. System Resources
            logger.info("\n Monitoring System Resources...")
            resource_usage = self.measure_system_resources()
            evaluation_results["system_resources"] = resource_usage
            
            # 5. Benchmark Comparison
            evaluation_results["benchmark_comparison"] = self._compare_benchmarks(evaluation_results)
            
            # Save results
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            results_file = self.results_dir / f"evaluation_results_{timestamp}.json"
            
            with open(results_file, 'w') as f:
                json.dump(evaluation_results, f, indent=2)
            
            logger.info(f"\n Evaluation Complete! Results: {results_file}")
            
        except Exception as e:
            logger.error(f" Evaluation failed: {e}")
            evaluation_results["error"] = str(e)
        
        finally:
            total_duration = (datetime.now() - start_time).total_seconds()
            evaluation_results["total_duration_seconds"] = round(total_duration, 2)
        
        return evaluation_results

    def _compare_benchmarks(self, results: Dict) -> Dict:
        """Compare against healthcare benchmarks"""
        
        comparison = {"overall_grade": ""}
        
        # AI Performance Assessment
        if "ai_analysis" in results:
            ai_results = results["ai_analysis"]
            accuracy = ai_results.get("priority_accuracy", 0)
            
            if accuracy >= 90:
                ai_grade = "Excellent"
            elif accuracy >= 85:
                ai_grade = "Good"
            elif accuracy >= 70:
                ai_grade = "Acceptable"
            else:
                ai_grade = "Needs Improvement"
            
            comparison["ai_performance"] = {
                "accuracy": accuracy,
                "grade": ai_grade,
                "avg_response_time": ai_results.get("avg_processing_time_ms", 0)
            }
        
        # Overall Grade
        grades = []
        if "ai_performance" in comparison:
            if comparison["ai_performance"]["grade"] == "Excellent":
                grades.append(4)
            elif comparison["ai_performance"]["grade"] == "Good":
                grades.append(3)
            elif comparison["ai_performance"]["grade"] == "Acceptable":
                grades.append(2)
            else:
                grades.append(1)
        
        if grades:
            avg_grade = sum(grades) / len(grades)
            if avg_grade >= 3.5:
                comparison["overall_grade"] = "A - Excellent Performance"
            elif avg_grade >= 3.0:
                comparison["overall_grade"] = "B - Good Performance"
            elif avg_grade >= 2.5:
                comparison["overall_grade"] = "C - Satisfactory Performance"
            else:
                comparison["overall_grade"] = "D - Needs Improvement"
        
        return comparison

    def print_summary(self, results: Dict):
        """Print evaluation summary"""
        
        print("\n" + "="*60)
        print(" FASTAPI SYSTEM EVALUATION SUMMARY")
        print("="*60)
        
        if 'authentication_status' in results:
            status = results['authentication_status']
            emoji = "✅" if status == "SUCCESS" else "❌"
            print(f"\n Authentication: {emoji} {status}")
        
        if 'api_performance' in results:
            print("\n API Performance:")
            for endpoint, metrics in results['api_performance'].items():
                print(f"   {endpoint}: {metrics['mean_response_time_ms']}ms avg")
        
        if 'ai_analysis' in results:
            ai = results['ai_analysis']
            print(f"\n AI Analysis:")
            print(f"   • Priority Accuracy: {ai['priority_accuracy']}%")
            print(f"   • Avg Processing Time: {ai['avg_processing_time_ms']}ms")
            print(f"   • Successful Analyses: {ai['successful_analyses']}/{ai['total_cases']}")
        
        if 'system_resources' in results:
            res = results['system_resources']
            print(f"\n System Resources:")
            print(f"   • CPU Usage: {res['cpu_usage']['average_percent']}%")
            print(f"   • Memory Usage: {res['memory_usage']['average_percent']}%")
        
        if 'benchmark_comparison' in results:
            grade = results['benchmark_comparison'].get('overall_grade', 'Not Available')
            print(f"\n Overall Grade: {grade}")
        
        print("\n" + "="*60)