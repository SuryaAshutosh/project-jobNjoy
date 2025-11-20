#!/usr/bin/env python3

"""
System QA Guardian - Qoder Agent for JobBuddy Smoke Testing
Automated smoke testing with retry logic and detailed reporting
"""

import argparse
import json
import os
import subprocess
import sys
import time
from datetime import datetime
from typing import Dict, List, Tuple

class SystemQAGuardian:
    def __init__(self, max_retries: int = 3):
        self.max_retries = max_retries
        self.test_results = []
        self.retry_counts = {}
        
    def log_result(self, test_name: str, status: str, details: str = "", retry_count: int = 0):
        """Log test result with retry information"""
        result = {
            "timestamp": datetime.now().isoformat(),
            "test_name": test_name,
            "status": status,
            "details": details,
            "retry_count": retry_count
        }
        self.test_results.append(result)
        
    def run_command_with_retry(self, command: List[str], test_name: str) -> Tuple[bool, str]:
        """Run a command with retry logic"""
        for attempt in range(self.max_retries):
            try:
                # Run the command
                result = subprocess.run(
                    command,
                    capture_output=True,
                    text=True,
                    timeout=300  # 5 minute timeout
                )
                
                if result.returncode == 0:
                    self.log_result(test_name, "PASS", "Command executed successfully", attempt)
                    return True, result.stdout
                else:
                    error_msg = f"Command failed with return code {result.returncode}\nStderr: {result.stderr}"
                    if attempt < self.max_retries - 1:
                        print(f"Attempt {attempt + 1} failed for {test_name}. Retrying...")
                        time.sleep(2 ** attempt)  # Exponential backoff
                    else:
                        self.log_result(test_name, "FAIL", error_msg, attempt)
                        return False, result.stderr
                        
            except subprocess.TimeoutExpired:
                error_msg = f"Command timed out after 300 seconds"
                if attempt < self.max_retries - 1:
                    print(f"Attempt {attempt + 1} timed out for {test_name}. Retrying...")
                    time.sleep(2 ** attempt)
                else:
                    self.log_result(test_name, "FAIL", error_msg, attempt)
                    return False, error_msg
                    
            except Exception as e:
                error_msg = f"Unexpected error: {str(e)}"
                if attempt < self.max_retries - 1:
                    print(f"Attempt {attempt + 1} failed unexpectedly for {test_name}. Retrying...")
                    time.sleep(2 ** attempt)
                else:
                    self.log_result(test_name, "FAIL", error_msg, attempt)
                    return False, error_msg
        
        return False, "Max retries exceeded"
    
    def run_bash_smoke_test(self) -> bool:
        """Run the bash smoke test script"""
        print("Running Bash Smoke Test...")
        success, output = self.run_command_with_retry(
            ["bash", "scripts/full_smoke_test.sh"], 
            "Bash Smoke Test"
        )
        
        # Save bash test logs
        log_dir = "logs/smoke"
        os.makedirs(log_dir, exist_ok=True)
        with open(f"{log_dir}/bash_smoke_test.log", "w") as f:
            f.write(output)
            
        return success
    
    def run_python_smoke_test(self, skip_resume: bool = False, skip_stripe: bool = False, skip_agents: bool = False) -> bool:
        """Run the Python smoke test runner"""
        print("Running Python Smoke Test...")
        
        command = ["python3", "scripts/smoke_runner.py"]
        if skip_resume:
            command.append("--skip-resume")
        if skip_stripe:
            command.append("--skip-stripe")
        if skip_agents:
            command.append("--skip-agents")
            
        success, output = self.run_command_with_retry(command, "Python Smoke Test")
        
        # Save python test logs
        log_dir = "logs/smoke"
        os.makedirs(log_dir, exist_ok=True)
        with open(f"{log_dir}/python_smoke_test.log", "w") as f:
            f.write(output)
            
        return success
    
    def parse_results(self) -> Dict[str, any]:
        """Parse test results and generate summary"""
        passed = sum(1 for result in self.test_results if result["status"] == "PASS")
        failed = sum(1 for result in self.test_results if result["status"] == "FAIL")
        
        # Try to read the Python smoke test report for detailed results
        detailed_results = []
        try:
            with open("reports/smoke_report.json", "r") as f:
                detailed_results = json.load(f)
        except FileNotFoundError:
            pass
        except Exception as e:
            print(f"Warning: Could not read detailed results: {e}")
        
        summary = {
            "timestamp": datetime.now().isoformat(),
            "total_tests": len(self.test_results),
            "passed": passed,
            "failed": failed,
            "results": self.test_results,
            "detailed_results": detailed_results
        }
        
        return summary
    
    def recommend_fixes(self, summary: Dict[str, any]) -> List[str]:
        """Provide recommendations based on failed tests"""
        recommendations = []
        
        failed_tests = [result for result in summary["results"] if result["status"] == "FAIL"]
        
        for test in failed_tests:
            test_name = test["test_name"]
            details = test["details"]
            
            if "docker" in details.lower() or "connection" in details.lower():
                recommendations.append(f"✗ {test_name}: Check Docker services are running and accessible")
            elif "database" in details.lower():
                recommendations.append(f"✗ {test_name}: Check database connection and credentials")
            elif "auth" in details.lower() or "login" in details.lower():
                recommendations.append(f"✗ {test_name}: Check authentication service and user credentials")
            elif "resume" in details.lower():
                recommendations.append(f"✗ {test_name}: Check resume parsing service and file storage")
            elif "job" in details.lower():
                recommendations.append(f"✗ {test_name}: Check job service and database models")
            elif "application" in details.lower():
                recommendations.append(f"✗ {test_name}: Check application service and dependencies")
            elif "stripe" in details.lower() or "webhook" in details.lower():
                recommendations.append(f"✗ {test_name}: Check Stripe webhook configuration and secrets")
            else:
                recommendations.append(f"✗ {test_name}: {details}")
                
        return recommendations
    
    def generate_report(self, summary: Dict[str, any]) -> str:
        """Generate a clean final report"""
        report_lines = []
        report_lines.append("=" * 50)
        report_lines.append("System QA Guardian - Smoke Test Report")
        report_lines.append("=" * 50)
        report_lines.append(f"Timestamp: {summary['timestamp']}")
        report_lines.append(f"Total Tests: {summary['total_tests']}")
        report_lines.append(f"Passed: {summary['passed']}")
        report_lines.append(f"Failed: {summary['failed']}")
        report_lines.append("-" * 50)
        
        # Show test results
        for result in summary["results"]:
            status_symbol = "✔" if result["status"] == "PASS" else "✖"
            status_text = "Passed" if result["status"] == "PASS" else "Failed"
            report_lines.append(f"{status_symbol} {result['test_name']} ({status_text})")
            if result["status"] == "FAIL":
                report_lines.append(f"   Cause: {result['details']}")
                if result["retry_count"] > 0:
                    report_lines.append(f"   Retries: {result['retry_count']}")
        
        # Add recommendations if there are failures
        if summary["failed"] > 0:
            recommendations = self.recommend_fixes(summary)
            if recommendations:
                report_lines.append("-" * 50)
                report_lines.append("Recommended Fixes:")
                for rec in recommendations:
                    report_lines.append(rec)
        
        # Final status
        report_lines.append("-" * 50)
        if summary["failed"] == 0:
            report_lines.append("✔ READY FOR DEPLOYMENT")
        else:
            report_lines.append("✖ BLOCKED — FIX REQUIRED")
        
        return "\n".join(report_lines)
    
    def save_report(self, report_content: str) -> str:
        """Save report to file and return the file path"""
        reports_dir = "reports"
        os.makedirs(reports_dir, exist_ok=True)
        report_file = f"{reports_dir}/smoke_summary.txt"
        
        with open(report_file, "w") as f:
            f.write(report_content)
            
        return report_file

def main():
    parser = argparse.ArgumentParser(description="System QA Guardian - Automated Smoke Testing")
    parser.add_argument("--max-retries", type=int, default=3, 
                       help="Maximum number of retries for failed tests (default: 3)")
    parser.add_argument("--skip-resume", action="store_true", 
                       help="Skip resume-related tests")
    parser.add_argument("--skip-stripe", action="store_true", 
                       help="Skip Stripe webhook tests")
    parser.add_argument("--skip-agents", action="store_true", 
                       help="Skip agent callback tests")
    
    args = parser.parse_args()
    
    # Create logs and reports directories
    os.makedirs("logs/smoke", exist_ok=True)
    os.makedirs("reports", exist_ok=True)
    
    # Initialize the QA Guardian
    guardian = SystemQAGuardian(max_retries=args.max_retries)
    
    print("System QA Guardian Initializing...")
    print(f"Max retries: {args.max_retries}")
    
    # Run both smoke tests
    bash_success = guardian.run_bash_smoke_test()
    python_success = guardian.run_python_smoke_test(
        skip_resume=args.skip_resume,
        skip_stripe=args.skip_stripe,
        skip_agents=args.skip_agents
    )
    
    # Generate summary
    summary = guardian.parse_results()
    
    # Generate and save report
    report_content = guardian.generate_report(summary)
    report_file = guardian.save_report(report_content)
    
    # Print report
    print("\n" + report_content)
    print(f"\nDetailed report saved to: {report_file}")
    
    # Exit with appropriate code
    if summary["failed"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()