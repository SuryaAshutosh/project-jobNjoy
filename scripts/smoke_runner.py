#!/usr/bin/env python3

"""
JobBuddy Smoke Test Runner
Runs comprehensive smoke tests for the JobBuddy platform
"""

import argparse
import json
import os
import requests
import sys
import time
from datetime import datetime
from typing import Dict, Any, Optional

# Colors for terminal output
class Colors:
    OK = '\033[92m'      # GREEN
    FAIL = '\033[91m'    # RED
    WARN = '\033[93m'    # YELLOW
    RESET = '\033[0m'    # RESET

class SmokeTestRunner:
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.access_token = None
        self.test_results = []
        self.session = requests.Session()
        self.user_id = None
        self.resume_id = None
        self.application_id = None
        
    def log_result(self, test_name: str, status: str, details: str = ""):
        """Log test result"""
        timestamp = datetime.now().isoformat()
        result = {
            "timestamp": timestamp,
            "test_name": test_name,
            "status": status,
            "details": details
        }
        self.test_results.append(result)
        
        # Print to console
        status_symbol = "✓" if status == "PASS" else "✗"
        status_color = Colors.OK if status == "PASS" else Colors.FAIL
        print(f"{status_color}{status_symbol} {test_name}{Colors.RESET}")
        if details:
            print(f"  {details}")
    
    def make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make HTTP request with error handling"""
        url = f"{self.base_url}{endpoint}"
        try:
            response = self.session.request(method, url, **kwargs)
            return response
        except requests.exceptions.RequestException as e:
            raise Exception(f"Request failed: {str(e)}")
    
    def test_health_check(self) -> bool:
        """Test GET /health endpoint"""
        try:
            response = self.make_request("GET", "/health")
            if response.status_code == 200:
                self.log_result("Health Check", "PASS")
                return True
            else:
                self.log_result("Health Check", "FAIL", f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Health Check", "FAIL", str(e))
            return False
    
    def test_register_user(self) -> bool:
        """Test POST /auth/register endpoint"""
        try:
            payload = {
                "email": "smoketest_py@example.com",
                "password": "SmokeTestPass123!",
                "full_name": "Smoke Test User Python"
            }
            response = self.make_request("POST", "/api/auth/register", 
                                       json=payload,
                                       headers={"Content-Type": "application/json"})
            
            if response.status_code == 201:
                data = response.json()
                self.user_id = data.get("id")
                self.log_result("User Registration", "PASS")
                return True
            else:
                self.log_result("User Registration", "FAIL", f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("User Registration", "FAIL", str(e))
            return False
    
    def test_login_user(self) -> bool:
        """Test POST /auth/login endpoint"""
        try:
            payload = {
                "username": "smoketest_py@example.com",
                "password": "SmokeTestPass123!"
            }
            response = self.make_request("POST", "/api/auth/login",
                                       data=payload,
                                       headers={"Content-Type": "application/x-www-form-urlencoded"})
            
            if response.status_code == 200:
                data = response.json()
                self.access_token = data.get("access_token")
                self.session.headers.update({"Authorization": f"Bearer {self.access_token}"})
                self.log_result("User Login", "PASS")
                return True
            else:
                self.log_result("User Login", "FAIL", f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("User Login", "FAIL", str(e))
            return False
    
    def test_get_user_profile(self) -> bool:
        """Test GET /auth/me endpoint"""
        try:
            response = self.make_request("GET", "/api/auth/me")
            
            if response.status_code == 200:
                self.log_result("Get User Profile", "PASS")
                return True
            else:
                self.log_result("Get User Profile", "FAIL", f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Get User Profile", "FAIL", str(e))
            return False
    
    def test_upload_resume(self) -> bool:
        """Test resume upload endpoint"""
        try:
            # Create a simple text file as sample resume
            sample_resume_path = "/tmp/sample_resume_py.txt"
            with open(sample_resume_path, "w") as f:
                f.write("John Doe\nSoftware Engineer\nExperience: 5 years in Python, JavaScript\nEducation: BS Computer Science")
            
            with open(sample_resume_path, "rb") as f:
                files = {"file": f}
                response = self.make_request("POST", "/api/resume/upload", files=files)
            
            # Clean up
            os.remove(sample_resume_path)
            
            if response.status_code == 200:
                data = response.json()
                self.resume_id = data.get("id")
                self.log_result("Resume Upload", "PASS")
                return True
            else:
                self.log_result("Resume Upload", "FAIL", f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Resume Upload", "FAIL", str(e))
            return False
    
    def test_parse_resume(self) -> bool:
        """Test resume parsing endpoint"""
        if not self.resume_id:
            self.log_result("Resume Parsing", "FAIL", "No resume ID available")
            return False
            
        try:
            payload = {"background": False}
            response = self.make_request("POST", f"/api/resume/{self.resume_id}/parse",
                                       json=payload,
                                       headers={"Content-Type": "application/json"})
            
            if response.status_code == 200:
                self.log_result("Resume Parsing", "PASS")
                return True
            else:
                self.log_result("Resume Parsing", "FAIL", f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Resume Parsing", "FAIL", str(e))
            return False
    
    def test_import_jobs(self) -> bool:
        """Test job import endpoint"""
        try:
            payload = [
                {
                    "title": "Senior Software Engineer",
                    "company": "Tech Corp",
                    "location": "San Francisco, CA",
                    "description": "We are looking for a senior software engineer...",
                    "url": "https://techcorp.com/jobs/123",
                    "salary": "$120,000 - $150,000",
                    "source_id": "smoke_test_source_py"
                }
            ]
            response = self.make_request("POST", "/api/jobs/import",
                                       json=payload,
                                       headers={"Content-Type": "application/json"})
            
            if response.status_code == 201:
                self.log_result("Job Import", "PASS")
                return True
            else:
                self.log_result("Job Import", "FAIL", f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Job Import", "FAIL", str(e))
            return False
    
    def test_list_jobs(self) -> bool:
        """Test GET /jobs endpoint"""
        try:
            response = self.make_request("GET", "/api/jobs/")
            
            if response.status_code == 200:
                self.log_result("List Jobs", "PASS")
                return True
            else:
                self.log_result("List Jobs", "FAIL", f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("List Jobs", "FAIL", str(e))
            return False
    
    def test_create_application(self) -> bool:
        """Test application creation endpoint"""
        if not self.resume_id:
            self.log_result("Create Application", "FAIL", "No resume ID available")
            return False
            
        try:
            payload = {
                "job_id": "1",
                "resume_id": self.resume_id,
                "cover_letter": "I am excited to apply for this position..."
            }
            response = self.make_request("POST", "/api/applications/",
                                       json=payload,
                                       headers={"Content-Type": "application/json"})
            
            if response.status_code == 201:
                data = response.json()
                self.application_id = data.get("id")
                self.log_result("Create Application", "PASS")
                return True
            else:
                self.log_result("Create Application", "FAIL", f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Create Application", "FAIL", str(e))
            return False
    
    def test_agent_callback(self) -> bool:
        """Test agent callback endpoint"""
        if not self.application_id:
            self.log_result("Agent Callback", "FAIL", "No application ID available")
            return False
            
        try:
            params = {
                "application_id": self.application_id,
                "status": "SUBMITTED",
                "notes": "Application submitted by agent"
            }
            headers = {
                "Content-Type": "application/json",
                "X-Signature": "test_signature"
            }
            response = self.make_request("POST", "/api/applications/agent-result",
                                       params=params,
                                       headers=headers)
            
            if response.status_code == 200:
                self.log_result("Agent Callback", "PASS")
                return True
            else:
                self.log_result("Agent Callback", "FAIL", f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Agent Callback", "FAIL", str(e))
            return False
    
    def test_stripe_webhook(self) -> bool:
        """Test Stripe webhook endpoint"""
        if not self.user_id:
            self.log_result("Stripe Webhook", "FAIL", "No user ID available")
            return False
            
        try:
            payload = {
                "id": "evt_123456789",
                "object": "event",
                "type": "checkout.session.completed",
                "data": {
                    "object": {
                        "id": "cs_test_123456789",
                        "object": "checkout.session",
                        "customer": "cus_123456789",
                        "client_reference_id": self.user_id,
                        "mode": "subscription",
                        "payment_status": "paid",
                        "subscription": "sub_123456789"
                    }
                }
            }
            headers = {
                "Content-Type": "application/json",
                "Stripe-Signature": "test_signature"
            }
            response = self.make_request("POST", "/api/payments/webhook",
                                       json=payload,
                                       headers=headers)
            
            if response.status_code == 200:
                self.log_result("Stripe Webhook", "PASS")
                return True
            else:
                self.log_result("Stripe Webhook", "FAIL", f"Status code: {response.status_code}")
                return False
        except Exception as e:
            self.log_result("Stripe Webhook", "FAIL", str(e))
            return False
    
    def run_tests(self, skip_resume: bool = False, skip_stripe: bool = False, skip_agents: bool = False) -> Dict[str, Any]:
        """Run all smoke tests"""
        print(f"{Colors.WARN}Starting JobBuddy Smoke Tests{Colors.RESET}")
        print(f"Base URL: {self.base_url}")
        print("-" * 50)
        
        start_time = time.time()
        
        # Run tests in order
        tests = [
            ("Health Check", self.test_health_check),
            ("User Registration", self.test_register_user),
            ("User Login", self.test_login_user),
            ("Get User Profile", self.test_get_user_profile),
        ]
        
        # Add resume tests if not skipped
        if not skip_resume:
            tests.extend([
                ("Resume Upload", self.test_upload_resume),
                ("Resume Parsing", self.test_parse_resume),
            ])
        
        # Add job and application tests
        tests.extend([
            ("Job Import", self.test_import_jobs),
            ("List Jobs", self.test_list_jobs),
            ("Create Application", self.test_create_application),
        ])
        
        # Add agent tests if not skipped
        if not skip_agents:
            tests.append(("Agent Callback", self.test_agent_callback))
        
        # Add Stripe test if not skipped
        if not skip_stripe:
            tests.append(("Stripe Webhook", self.test_stripe_webhook))
        
        # Execute all tests
        for test_name, test_func in tests:
            try:
                test_func()
            except Exception as e:
                self.log_result(test_name, "FAIL", f"Unexpected error: {str(e)}")
        
        # Calculate duration
        end_time = time.time()
        duration = end_time - start_time
        
        # Generate summary
        passed = sum(1 for result in self.test_results if result["status"] == "PASS")
        failed = len(self.test_results) - passed
        
        summary = {
            "timestamp": datetime.now().isoformat(),
            "total_tests": len(self.test_results),
            "passed": passed,
            "failed": failed,
            "duration_seconds": duration,
            "results": self.test_results
        }
        
        return summary
    
    def print_summary(self, summary: Dict[str, Any]):
        """Print test summary table"""
        print("\n" + "=" * 50)
        print(f"{Colors.WARN}Smoke Test Summary{Colors.RESET}")
        print("=" * 50)
        
        for result in summary["results"]:
            status_symbol = "✓" if result["status"] == "PASS" else "✗"
            status_color = Colors.OK if result["status"] == "PASS" else Colors.FAIL
            print(f"{status_color}{status_symbol} {result['test_name']}{Colors.RESET}")
        
        print("-" * 50)
        print(f"Total Tests: {summary['total_tests']}")
        print(f"{Colors.OK}Passed: {summary['passed']}{Colors.RESET}")
        print(f"{Colors.FAIL}Failed: {summary['failed']}{Colors.RESET}")
        print(f"Duration: {summary['duration_seconds']:.2f} seconds")
        
        # Final status
        if summary["failed"] == 0:
            print(f"\n{Colors.OK}READY FOR DEPLOYMENT{Colors.RESET}")
        else:
            print(f"\n{Colors.FAIL}BLOCKED — FIX REQUIRED{Colors.RESET}")
            print("Failed components:")
            for result in summary["results"]:
                if result["status"] == "FAIL":
                    print(f"  - {result['test_name']}: {result['details']}")

def main():
    parser = argparse.ArgumentParser(description="JobBuddy Smoke Test Runner")
    parser.add_argument("--base-url", default="http://localhost:8000", 
                       help="Base URL for the API (default: http://localhost:8000)")
    parser.add_argument("--skip-resume", action="store_true", 
                       help="Skip resume-related tests")
    parser.add_argument("--skip-stripe", action="store_true", 
                       help="Skip Stripe webhook tests")
    parser.add_argument("--skip-agents", action="store_true", 
                       help="Skip agent callback tests")
    parser.add_argument("--output-file", default="reports/smoke_report.json",
                       help="Output file for JSON report (default: reports/smoke_report.json)")
    
    args = parser.parse_args()
    
    # Create reports directory if it doesn't exist
    os.makedirs(os.path.dirname(args.output_file), exist_ok=True)
    
    # Run tests
    runner = SmokeTestRunner(base_url=args.base_url)
    summary = runner.run_tests(
        skip_resume=args.skip_resume,
        skip_stripe=args.skip_stripe,
        skip_agents=args.skip_agents
    )
    
    # Save JSON report
    with open(args.output_file, "w") as f:
        json.dump(summary, f, indent=2)
    
    # Print summary
    runner.print_summary(summary)
    
    # Exit with appropriate code
    if summary["failed"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()