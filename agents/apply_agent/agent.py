"""
Main Auto-Apply Agent runner
Orchestrates the entire auto-apply process
"""

import asyncio
import logging
import base64
from typing import Dict, Any, List, Optional
from datetime import datetime
from playwright.async_api import async_playwright, Page

from .utils.settings import settings
from .utils.browser_pool import BrowserPool
from .form_detector import FormDetector
from .autofill_engine import AutofillEngine
from .answer_generator import AnswerGenerator
from .resume_uploader import ResumeUploader
from .exporters.backend_client import BackendClient
from .adapters.linkedin import LinkedInAdapter
from .adapters.indeed import IndeedAdapter
from .adapters.naukri import NaukriAdapter
from .utils.retry_handler import RetryHandler

logger = logging.getLogger(__name__)

class AutoApplyAgent:
    """Main Auto-Apply Agent that orchestrates the application process"""
    
    def __init__(self):
        """Initialize the Auto-Apply Agent"""
        self.backend_client = None
        self.browser_pool = None
        self.form_detector = FormDetector()
        self.autofill_engine = AutofillEngine()
        self.answer_generator = AnswerGenerator()
        self.resume_uploader = ResumeUploader()
        self.retry_handler = RetryHandler(
            max_attempts=settings.get("retry.max_attempts", 3),
            base_delay=settings.get("retry.base_delay", 1.0),
            jitter=settings.get("retry.jitter", True)
        )
        
        # Initialize site adapters
        self.adapters = {
            "linkedin": LinkedInAdapter(),
            "indeed": IndeedAdapter(),
            "naukri": NaukriAdapter()
        }
        
        # Tracking
        self.logs = []
        self.metrics = {
            "applications_attempted": 0,
            "applications_applied": 0,
            "applications_failed": 0,
            "captcha_detected": 0,
            "ai_answers_generated": 0
        }
        
    async def __aenter__(self):
        """Async context manager entry"""
        await self.initialize()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.cleanup()
        
    async def initialize(self):
        """Initialize agent components"""
        try:
            # Initialize backend client
            self.backend_client = BackendClient()
            await self.backend_client.__aenter__()
            
            # Initialize browser pool
            self.browser_pool = BrowserPool()
            await self.browser_pool.initialize()
            
            logger.info("Auto-Apply Agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Error initializing Auto-Apply Agent: {e}")
            raise
            
    async def cleanup(self):
        """Clean up agent components"""
        try:
            # Close browser pool
            if self.browser_pool:
                await self.browser_pool.close()
                
            # Close backend client
            if self.backend_client:
                await self.backend_client.__aexit__(None, None, None)
                
            logger.info("Auto-Apply Agent cleaned up successfully")
            
        except Exception as e:
            logger.error(f"Error cleaning up Auto-Apply Agent: {e}")
            
    async def run_auto_apply_cycle(self) -> Dict[str, Any]:
        """
        Run a complete auto-apply cycle
        
        Returns:
            Dictionary with cycle results and metrics
        """
        start_time = datetime.utcnow()
        logger.info("Starting auto-apply cycle")
        
        try:
            # Fetch pending applications
            applications = await self.backend_client.get_pending_applications()
            self.metrics["applications_attempted"] = len(applications)
            
            if not applications:
                logger.info("No pending applications found")
                return {
                    "status": "completed",
                    "applications_processed": 0,
                    "metrics": self.metrics,
                    "duration": 0
                }
                
            logger.info(f"Found {len(applications)} pending applications")
            
            # Process each application
            results = []
            for app_data in applications:
                try:
                    result = await self.process_application(app_data)
                    results.append(result)
                    
                    # Update metrics
                    if result["status"] == "applied":
                        self.metrics["applications_applied"] += 1
                    elif result["status"] == "failed":
                        self.metrics["applications_failed"] += 1
                    elif result["status"] == "manual_needed":
                        self.metrics["captcha_detected"] += 1
                        
                except Exception as e:
                    logger.error(f"Error processing application {app_data.get('id', 'unknown')}: {e}")
                    results.append({
                        "application_id": app_data.get("id", "unknown"),
                        "status": "failed",
                        "error": str(e)
                    })
                    self.metrics["applications_failed"] += 1
                    
            # Calculate duration
            end_time = datetime.utcnow()
            duration = (end_time - start_time).total_seconds()
            
            logger.info(f"Auto-apply cycle completed in {duration:.2f} seconds")
            
            return {
                "status": "completed",
                "applications_processed": len(applications),
                "results": results,
                "metrics": self.metrics,
                "duration": duration,
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error in auto-apply cycle: {e}")
            raise
            
    async def process_application(self, application_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a single job application
        
        Args:
            application_data: Application data from backend
            
        Returns:
            Dictionary with processing result
        """
        application_id = application_data.get("id", "unknown")
        job_id = application_data.get("job_id", "")
        resume_id = application_data.get("resume_id", "")
        
        logger.info(f"Processing application {application_id} for job {job_id}")
        
        # Add to logs
        self.logs.append(f"Processing application {application_id}")
        
        try:
            # Fetch job details
            job_data = await self.backend_client.get_job_details(job_id)
            if not job_data:
                error_msg = f"Failed to fetch job details for job {job_id}"
                logger.error(error_msg)
                await self._report_result(application_id, "failed", error_msg)
                return {
                    "application_id": application_id,
                    "status": "failed",
                    "error": error_msg
                }
                
            # Fetch resume data
            resume_data = await self.backend_client.get_resume_data(resume_id)
            if not resume_data:
                error_msg = f"Failed to fetch resume data for resume {resume_id}"
                logger.error(error_msg)
                await self._report_result(application_id, "failed", error_msg)
                return {
                    "application_id": application_id,
                    "status": "failed",
                    "error": error_msg
                }
                
            # Get browser context
            browser = await self.browser_pool.get_browser()
            context = await self.browser_pool.get_context(browser)
            
            try:
                # Create new page
                page = await context.new_page()
                
                # Process the application
                result = await self._apply_to_job(page, job_data, resume_data, application_id)
                
                # Close page
                await page.close()
                
                # Report result to backend
                await self._report_result(
                    application_id, 
                    result["status"], 
                    result.get("notes", ""),
                    result.get("logs", [])
                )
                
                return {
                    "application_id": application_id,
                    "status": result["status"],
                    "notes": result.get("notes", ""),
                    "logs": result.get("logs", [])
                }
                
            finally:
                # Close context
                await self.browser_pool.close_context(context)
                
        except Exception as e:
            error_msg = f"Error processing application {application_id}: {e}"
            logger.error(error_msg)
            await self._report_result(application_id, "failed", error_msg)
            return {
                "application_id": application_id,
                "status": "failed",
                "error": error_msg
            }
            
    async def _apply_to_job(self, page: Page, job_data: Dict[str, Any], 
                          resume_data: Dict[str, Any], application_id: str) -> Dict[str, Any]:
        """
        Apply to a job using browser automation
        
        Args:
            page: Playwright page object
            job_data: Job details
            resume_data: Resume data
            application_id: Application ID
            
        Returns:
            Dictionary with application result
        """
        job_url = job_data.get("url", "")
        job_source = job_data.get("source_name", "unknown")
        
        logger.info(f"Applying to job at {job_url} via {job_source}")
        
        try:
            # Navigate to job URL
            logger.info(f"Navigating to job URL: {job_url}")
            await page.goto(job_url)
            
            # Wait for page to load
            await page.wait_for_load_state("networkidle", timeout=30000)
            
            # Detect site adapter
            adapter = self.adapters.get(job_source.lower())
            if not adapter:
                # Try to detect adapter based on URL
                adapter = await self._detect_adapter_by_url(page)
                if not adapter:
                    error_msg = f"No adapter found for job source: {job_source}"
                    logger.error(error_msg)
                    return {
                        "status": "failed",
                        "notes": error_msg,
                        "logs": self.logs.copy()
                    }
                    
            # Handle login if needed
            if await adapter.detect_login_page(page):
                logger.info(f"Login page detected for {job_source}")
                self.logs.append(f"Login page detected for {job_source}")
                
                # Get credentials (in a real implementation, these would come from secure storage)
                credentials = {
                    "email": "user@example.com",
                    "password": "password123"
                }
                
                login_success = await adapter.handle_login(page, credentials)
                if not login_success:
                    error_msg = f"Failed to login to {job_source}"
                    logger.error(error_msg)
                    return {
                        "status": "failed",
                        "notes": error_msg,
                        "logs": self.logs.copy()
                    }
                    
                # Wait for navigation after login
                await page.wait_for_load_state("networkidle", timeout=30000)
                
            # Check for CAPTCHA
            page_content = await page.text_content("body") or ""
            if adapter.detect_captcha(page_content):
                self.metrics["captcha_detected"] += 1
                warning_msg = f"CAPTCHA detected for {job_source}, manual review needed"
                logger.warning(warning_msg)
                return {
                    "status": "manual_needed",
                    "notes": warning_msg,
                    "logs": self.logs.copy()
                }
                
            # Detect application form
            if not await adapter.detect_application_form(page):
                # Try to click apply button to reveal form
                await self._click_apply_button(page)
                
                # Wait and check again
                await page.wait_for_timeout(3000)
                if not await adapter.detect_application_form(page):
                    error_msg = f"No application form found for {job_source}"
                    logger.error(error_msg)
                    return {
                        "status": "failed",
                        "notes": error_msg,
                        "logs": self.logs.copy()
                    }
                    
            logger.info(f"Application form detected for {job_source}")
            self.logs.append(f"Application form detected for {job_source}")
            
            # Detect form fields
            form_fields = await self.form_detector.detect_form_fields(page)
            logger.info(f"Detected {len(form_fields)} form fields")
            self.logs.append(f"Detected {len(form_fields)} form fields")
            
            # Map resume data to fields
            field_mapping = self.autofill_engine.map_resume_to_fields(resume_data, form_fields)
            logger.info(f"Mapped values to {len(field_mapping)} fields")
            self.logs.append(f"Mapped values to {len(field_mapping)} fields")
            
            # Fill form fields
            fill_results = await self.autofill_engine.fill_fields(field_mapping)
            successful_fills = sum(1 for r in fill_results if r["success"])
            logger.info(f"Successfully filled {successful_fills}/{len(fill_results)} fields")
            self.logs.append(f"Successfully filled {successful_fills}/{len(fill_results)} fields")
            
            # Detect and handle questions
            questions = await self.form_detector.detect_questions(page)
            if questions:
                logger.info(f"Detected {len(questions)} question fields")
                self.logs.append(f"Detected {len(questions)} question fields")
                
                # Generate AI answers
                answer_mapping = await self.answer_generator.generate_answers(questions, resume_data, job_data)
                self.metrics["ai_answers_generated"] += len(answer_mapping)
                
                if answer_mapping:
                    # Fill question fields with generated answers
                    answer_results = await self.answer_generator.fill_answers(answer_mapping)
                    successful_answers = sum(1 for r in answer_results if r["success"])
                    logger.info(f"Successfully filled {successful_answers}/{len(answer_results)} question fields")
                    self.logs.append(f"Successfully filled {successful_answers}/{len(answer_results)} question fields")
                    
            # Handle resume upload
            file_fields = [f for f in form_fields if f["field_type"] == "file"]
            if file_fields:
                resume_path = "/path/to/resume.pdf"  # In real implementation, get actual path
                upload_results = await self.resume_uploader.upload_resume(file_fields, resume_path)
                successful_uploads = sum(1 for r in upload_results if r["success"])
                logger.info(f"Successfully uploaded resume to {successful_uploads}/{len(upload_results)} fields")
                self.logs.append(f"Successfully uploaded resume to {successful_uploads}/{len(upload_results)} fields")
                
            # Handle multi-step application process
            await adapter.handle_multi_step_application(page, adapter.max_steps)
            
            # Submit application
            submit_success = await self._submit_application(page, adapter)
            
            if submit_success:
                logger.info(f"Successfully submitted application for {job_source}")
                self.logs.append(f"Successfully submitted application for {job_source}")
                return {
                    "status": "applied",
                    "notes": "Application submitted successfully",
                    "logs": self.logs.copy()
                }
            else:
                error_msg = f"Failed to submit application for {job_source}"
                logger.error(error_msg)
                return {
                    "status": "failed",
                    "notes": error_msg,
                    "logs": self.logs.copy()
                }
                
        except Exception as e:
            error_msg = f"Error applying to job {job_url}: {e}"
            logger.error(error_msg)
            return {
                "status": "failed",
                "notes": error_msg,
                "logs": self.logs.copy()
            }
            
    async def _detect_adapter_by_url(self, page: Page) -> Optional[object]:
        """
        Detect appropriate adapter based on page URL
        
        Args:
            page: Playwright page object
            
        Returns:
            Adapter instance or None
        """
        try:
            url = page.url.lower()
            
            if "linkedin.com" in url:
                return self.adapters.get("linkedin")
            elif "indeed.com" in url:
                return self.adapters.get("indeed")
            elif "naukri.com" in url:
                return self.adapters.get("naukri")
            else:
                return None
                
        except Exception as e:
            logger.warning(f"Error detecting adapter by URL: {e}")
            return None
            
    async def _click_apply_button(self, page: Page):
        """
        Click common apply buttons to reveal application form
        
        Args:
            page: Playwright page object
        """
        apply_buttons = [
            "button:has-text('Apply')",
            "button:has-text('Easy Apply')",
            "a:has-text('Apply')",
            "button#applyButton",
            "button.jobs-apply-button"
        ]
        
        for selector in apply_buttons:
            try:
                button = await page.query_selector(selector)
                if button:
                    await button.click()
                    logger.info(f"Clicked apply button: {selector}")
                    break
            except Exception as e:
                logger.warning(f"Failed to click apply button {selector}: {e}")
                continue
                
    async def _submit_application(self, page: Page, adapter) -> bool:
        """
        Submit the application form
        
        Args:
            page: Playwright page object
            adapter: Site adapter
            
        Returns:
            True if submission successful, False otherwise
        """
        try:
            # Look for submit buttons
            submit_buttons = [
                "button[aria-label='Submit application']",
                "button#form-action-submit",
                "button#submitApplication",
                "button:has-text('Submit')",
                "button[type='submit']"
            ]
            
            for selector in submit_buttons:
                try:
                    button = await page.query_selector(selector)
                    if button:
                        await button.click()
                        logger.info(f"Clicked submit button: {selector}")
                        
                        # Wait for confirmation or navigation
                        try:
                            await page.wait_for_load_state("networkidle", timeout=10000)
                        except:
                            pass
                            
                        # Check for success indicators
                        if await self._verify_submission_success(page):
                            return True
                        break
                except Exception as e:
                    logger.warning(f"Failed to click submit button {selector}: {e}")
                    continue
                    
            return False
            
        except Exception as e:
            logger.error(f"Error submitting application: {e}")
            return False
            
    async def _verify_submission_success(self, page: Page) -> bool:
        """
        Verify that the application was submitted successfully
        
        Args:
            page: Playwright page object
            
        Returns:
            True if submission successful, False otherwise
        """
        try:
            # Look for success indicators
            success_indicators = [
                "div#ia-confirmation-screen",
                "div.success-message",
                "div.artdeco-modal__content:has-text('successfully')",
                "h2:has-text('Thank you')",
                "div:has-text('application has been submitted')"
            ]
            
            page_content = await page.text_content("body") or ""
            page_content_lower = page_content.lower()
            
            # Check for success elements
            for selector in success_indicators:
                try:
                    element = await page.query_selector(selector)
                    if element:
                        logger.info(f"Submission success detected by element: {selector}")
                        return True
                except:
                    continue
                    
            # Check page content for success keywords
            success_keywords = ["thank you", "application submitted", "successfully applied"]
            for keyword in success_keywords:
                if keyword in page_content_lower:
                    logger.info(f"Submission success detected by keyword: {keyword}")
                    return True
                    
            return False
            
        except Exception as e:
            logger.warning(f"Error verifying submission success: {e}")
            return False
            
    async def _report_result(self, application_id: str, status: str, 
                           notes: str = "", logs: List[str] = None):
        """
        Report application result to backend
        
        Args:
            application_id: Application ID
            status: Application status
            notes: Additional notes
            logs: Application logs
        """
        try:
            # Try to submit result using the new endpoint first
            success = await self.backend_client.submit_application_result(
                application_id, status, notes, logs or self.logs
            )
            
            if not success:
                # Fallback to old endpoint
                success = await self.backend_client.update_application_status(
                    application_id, status, notes
                )
                
            if success:
                logger.info(f"Successfully reported result for application {application_id}: {status}")
            else:
                logger.error(f"Failed to report result for application {application_id}")
                
        except Exception as e:
            logger.error(f"Error reporting result for application {application_id}: {e}")

# Convenience function to run the agent
async def run_auto_apply_agent() -> Dict[str, Any]:
    """
    Run the Auto-Apply Agent
    
    Returns:
        Dictionary with agent run results
    """
    async with AutoApplyAgent() as agent:
        return await agent.run_auto_apply_cycle()