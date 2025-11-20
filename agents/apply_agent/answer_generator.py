"""
AI-driven answer generator for Auto-Apply Agent
Generates tailored answers for open-ended questions using LLM
"""

import asyncio
import logging
import json
from typing import Dict, Any, List, Optional
from playwright.async_api import ElementHandle
import openai
from .utils.settings import settings
from .utils.retry_handler import retry_with_backoff

logger = logging.getLogger(__name__)

class AnswerGenerator:
    """Generates AI-powered answers for open-ended questions"""
    
    def __init__(self):
        """Initialize answer generator"""
        self.llm_provider = settings.get("llm.provider", "openai")
        self.llm_model = settings.get("llm.model", "gpt-3.5-turbo")
        self.llm_api_key = settings.get("llm.api_key", "")
        self.temperature = settings.get("llm.temperature", 0.7)
        self.max_tokens = settings.get("llm.max_tokens", 500)
        
        # Initialize OpenAI client if using OpenAI
        if self.llm_provider == "openai" and self.llm_api_key:
            openai.api_key = self.llm_api_key
            
    async def generate_answers(self, questions: List[Dict[str, Any]], resume_data: Dict[str, Any], 
                              job_data: Dict[str, Any]) -> Dict[ElementHandle, str]:
        """
        Generate answers for a list of questions
        
        Args:
            questions: List of question fields
            resume_data: Parsed resume data
            job_data: Job details
            
        Returns:
            Dictionary mapping question elements to generated answers
        """
        answers = {}
        
        try:
            # Generate answer for each question
            for question in questions:
                element = question["element"]
                question_text = question["question_text"]
                field_type = question["field_type"]
                confidence = question["confidence"]
                
                try:
                    # Generate answer using LLM
                    answer = await self._generate_answer_for_question(
                        question_text, resume_data, job_data
                    )
                    
                    if answer:
                        answers[element] = answer
                        logger.info(f"Generated answer for question: {question_text[:50]}...")
                    else:
                        logger.warning(f"Failed to generate answer for question: {question_text[:50]}...")
                        
                except Exception as e:
                    logger.error(f"Error generating answer for question '{question_text}': {e}")
                    # Use fallback answer
                    fallback_answer = self._get_fallback_answer(question_text)
                    if fallback_answer:
                        answers[element] = fallback_answer
                        logger.info(f"Used fallback answer for question: {question_text[:50]}...")
                        
        except Exception as e:
            logger.error(f"Error generating answers: {e}")
            
        return answers
        
    @retry_with_backoff(max_attempts=3, base_delay=1.0)
    async def _generate_answer_for_question(self, question_text: str, resume_data: Dict[str, Any], 
                                          job_data: Dict[str, Any]) -> Optional[str]:
        """
        Generate answer for a single question using LLM
        
        Args:
            question_text: The question to answer
            resume_data: Parsed resume data
            job_data: Job details
            
        Returns:
            Generated answer or None if failed
        """
        try:
            # Select appropriate prompt template based on question type
            prompt_template = self._select_prompt_template(question_text)
            
            # Format the prompt with actual data
            prompt = prompt_template.format(
                question=question_text,
                resume_data=json.dumps(resume_data, indent=2),
                job_description=job_data.get("description", ""),
                job_title=job_data.get("title", ""),
                company=job_data.get("company", "")
            )
            
            # Generate answer using LLM
            if self.llm_provider == "openai":
                return await self._generate_with_openai(prompt)
            else:
                # Fallback to simple template-based generation
                return self._generate_with_template(question_text, resume_data, job_data)
                
        except Exception as e:
            logger.error(f"Error generating answer with LLM: {e}")
            raise  # Re-raise to trigger retry
            
    async def _generate_with_openai(self, prompt: str) -> Optional[str]:
        """
        Generate answer using OpenAI API
        
        Args:
            prompt: Formatted prompt
            
        Returns:
            Generated answer or None if failed
        """
        try:
            response = await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: openai.ChatCompletion.create(
                    model=self.llm_model,
                    messages=[
                        {"role": "system", "content": "You are a helpful assistant that generates professional job application answers."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=self.temperature,
                    max_tokens=self.max_tokens
                )
            )
            
            answer = response.choices[0].message.content.strip()
            
            # Sanitize the answer (remove any PII that might have been generated)
            answer = self._sanitize_answer(answer)
            
            return answer
            
        except Exception as e:
            logger.error(f"Error generating answer with OpenAI: {e}")
            raise
            
    def _generate_with_template(self, question_text: str, resume_data: Dict[str, Any], 
                               job_data: Dict[str, Any]) -> Optional[str]:
        """
        Generate answer using template-based approach (fallback)
        
        Args:
            question_text: The question to answer
            resume_data: Parsed resume data
            job_data: Job details
            
        Returns:
            Generated answer or None if failed
        """
        # Simple template-based generation as fallback
        question_lower = question_text.lower()
        
        if "why" in question_lower and ("role" in question_lower or "position" in question_lower):
            return self._generate_why_this_role_answer(resume_data, job_data)
        elif "experience" in question_lower or "background" in question_lower:
            return self._generate_experience_answer(resume_data, job_data)
        elif "skill" in question_lower or "strength" in question_lower:
            return self._generate_skills_answer(resume_data)
        else:
            # Generic fallback
            return self._generate_generic_answer(resume_data, job_data)
            
    def _select_prompt_template(self, question_text: str) -> str:
        """
        Select appropriate prompt template based on question type
        
        Args:
            question_text: The question to analyze
            
        Returns:
            Prompt template
        """
        question_lower = question_text.lower()
        
        if "why" in question_lower and ("role" in question_lower or "position" in question_lower):
            return self._get_why_this_role_prompt()
        elif "experience" in question_lower or "background" in question_lower:
            return self._get_experience_prompt()
        elif "skill" in question_lower or "strength" in question_lower:
            return self._get_skills_prompt()
        elif "challenge" in question_lower or "difficulty" in question_lower:
            return self._get_challenge_prompt()
        elif "team" in question_lower or "collaborat" in question_lower:
            return self._get_teamwork_prompt()
        else:
            return self._get_generic_prompt()
            
    def _get_why_this_role_prompt(self) -> str:
        """Get prompt template for 'Why this role?' questions"""
        return """
        Based on the following resume data and job description, generate a compelling answer to this question:
        "{question}"
        
        Resume Data:
        {resume_data}
        
        Job Title: {job_title}
        Company: {company}
        Job Description: {job_description}
        
        Provide a concise, professional answer (2-3 sentences) that:
        1. Shows genuine interest in the role and company
        2. Connects your background to the job requirements
        3. Demonstrates research about the company
        4. Avoids generic statements
        
        Answer:
        """
        
    def _get_experience_prompt(self) -> str:
        """Get prompt template for experience-related questions"""
        return """
        Based on the following resume data and job description, generate a relevant answer to this question:
        "{question}"
        
        Resume Data:
        {resume_data}
        
        Job Title: {job_title}
        Company: {company}
        Job Description: {job_description}
        
        Provide a specific, concrete answer (2-4 sentences) that:
        1. Directly addresses the question
        2. Includes relevant examples from your experience
        3. Quantifies achievements when possible
        4. Connects your experience to the job requirements
        
        Answer:
        """
        
    def _get_skills_prompt(self) -> str:
        """Get prompt template for skills/strengths questions"""
        return """
        Based on the following resume data and job description, generate a targeted answer to this question:
        "{question}"
        
        Resume Data:
        {resume_data}
        
        Job Title: {job_title}
        Company: {company}
        Job Description: {job_description}
        
        Provide a focused answer (2-3 sentences) that:
        1. Mentions 2-3 key relevant skills
        2. Provides brief examples of how you've applied these skills
        3. Connects your skills to the job requirements
        4. Shows how these skills will benefit the company
        
        Answer:
        """
        
    def _get_challenge_prompt(self) -> str:
        """Get prompt template for challenge-related questions"""
        return """
        Based on the following resume data, generate a thoughtful answer to this question:
        "{question}"
        
        Resume Data:
        {resume_data}
        
        Provide a structured answer (3-4 sentences) that:
        1. Briefly describes a relevant challenge you faced
        2. Explains the actions you took to address it
        3. Describes the positive outcome or lessons learned
        4. Connects the experience to professional growth
        
        Answer:
        """
        
    def _get_teamwork_prompt(self) -> str:
        """Get prompt template for teamwork/collaboration questions"""
        return """
        Based on the following resume data, generate a collaborative answer to this question:
        "{question}"
        
        Resume Data:
        {resume_data}
        
        Provide a specific example (2-3 sentences) that:
        1. Describes a teamwork situation from your experience
        2. Highlights your role and contributions
        3. Shows positive results from the collaboration
        4. Demonstrates interpersonal skills
        
        Answer:
        """
        
    def _get_generic_prompt(self) -> str:
        """Get generic prompt template for other questions"""
        return """
        Based on the following resume data and job description, generate a professional answer to this question:
        "{question}"
        
        Resume Data:
        {resume_data}
        
        Job Title: {job_title}
        Company: {company}
        Job Description: {job_description}
        
        Provide a clear, relevant answer (2-3 sentences) that:
        1. Directly addresses the question
        2. Draws on your experience and qualifications
        3. Shows enthusiasm for the opportunity
        4. Maintains a professional tone
        
        Answer:
        """
        
    def _generate_why_this_role_answer(self, resume_data: Dict[str, Any], job_data: Dict[str, Any]) -> str:
        """Generate answer for 'Why this role?' question using template approach"""
        company = job_data.get("company", "the company")
        job_title = job_data.get("title", "this position")
        
        return (
            f"I'm excited about the {job_title} opportunity at {company} because it aligns "
            f"perfectly with my background in {self._get_primary_field(resume_data, 'experiences')}. "
            f"I'm particularly drawn to {company}'s mission and would love to contribute my skills "
            f"in {self._get_primary_field(resume_data, 'skills')} to help drive success in this role."
        )
        
    def _generate_experience_answer(self, resume_data: Dict[str, Any], job_data: Dict[str, Any]) -> str:
        """Generate answer for experience-related question using template approach"""
        experiences = resume_data.get("experiences", [])
        if experiences:
            exp = experiences[0]  # Most recent experience
            return (
                f"In my role as {exp.get('title', 'professional')}, I developed strong skills in "
                f"{self._get_primary_field(resume_data, 'skills')}. "
                f"For example, I {exp.get('bullets', ['contributed to key projects'])[0]}. "
                f"This experience has prepared me well for the requirements of this position."
            )
        else:
            return (
                f"Through my professional journey, I've developed expertise in "
                f"{self._get_primary_field(resume_data, 'skills')} and "
                f"{self._get_secondary_field(resume_data, 'skills')}. "
                f"I'm excited to bring these capabilities to this role."
            )
            
    def _generate_skills_answer(self, resume_data: Dict[str, Any]) -> str:
        """Generate answer for skills/strengths question using template approach"""
        skills = resume_data.get("skills", [])
        if len(skills) >= 2:
            primary_skill = skills[0].get("skill", "key skills")
            secondary_skill = skills[1].get("skill", "additional competencies")
            return (
                f"My key strengths include {primary_skill} and {secondary_skill}. "
                f"I've successfully applied these skills in various professional contexts, "
                f"consistently delivering results and contributing to team success."
            )
        elif skills:
            primary_skill = skills[0].get("skill", "relevant skills")
            return (
                f"I excel in {primary_skill}, which I've developed through "
                f"my professional experience. This strength enables me to effectively "
                f"tackle challenges and contribute meaningfully to projects."
            )
        else:
            return (
                f"I bring a strong work ethic, adaptability, and a commitment to excellence. "
                f"These qualities, combined with my technical skills, enable me to thrive "
                f"in dynamic professional environments."
            )
            
    def _generate_generic_answer(self, resume_data: Dict[str, Any], job_data: Dict[str, Any]) -> str:
        """Generate generic answer using template approach"""
        return (
            f"Based on my background in {self._get_primary_field(resume_data, 'experiences')} "
            f"and skills in {self._get_primary_field(resume_data, 'skills')}, "
            f"I believe I would be a valuable addition to the team. "
            f"I'm excited about the opportunity to contribute to {job_data.get('company', 'the organization')}'s success."
        )
        
    def _get_primary_field(self, resume_data: Dict[str, Any], field_type: str) -> str:
        """Get primary field value for template generation"""
        if field_type == "experiences":
            experiences = resume_data.get("experiences", [])
            if experiences:
                return experiences[0].get("title", "professional work")
        elif field_type == "skills":
            skills = resume_data.get("skills", [])
            if skills:
                return skills[0].get("skill", "relevant skills")
        return "my field"
        
    def _get_secondary_field(self, resume_data: Dict[str, Any], field_type: str) -> str:
        """Get secondary field value for template generation"""
        if field_type == "skills":
            skills = resume_data.get("skills", [])
            if len(skills) >= 2:
                return skills[1].get("skill", "additional skills")
        return "related areas"
        
    def _get_fallback_answer(self, question_text: str) -> Optional[str]:
        """Get fallback answer when LLM fails"""
        question_lower = question_text.lower()
        
        if "why" in question_lower:
            return "I'm excited about this opportunity because it aligns with my career goals and allows me to contribute my skills and experience to a dynamic team."
        elif "experience" in question_lower:
            return "I have relevant experience in this field that has prepared me well for this role. I've successfully handled similar responsibilities and am confident in my ability to contribute effectively."
        elif "skill" in question_lower or "strength" in question_lower:
            return "My key strengths include strong communication skills, problem-solving abilities, and a commitment to excellence. These qualities enable me to perform effectively in challenging environments."
        else:
            return "I believe my background and skills make me a strong candidate for this position. I'm eager to contribute to the team and help achieve the company's objectives."
            
    def _sanitize_answer(self, answer: str) -> str:
        """Sanitize answer to remove potential PII"""
        # Remove email addresses
        answer = re.sub(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]', answer)
        
        # Remove phone numbers
        answer = re.sub(r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', '[PHONE]', answer)
        
        # Remove social security numbers
        answer = re.sub(r'\b\d{3}-\d{2}-\d{4}\b', '[SSN]', answer)
        
        return answer
        
    async def fill_answers(self, answer_mapping: Dict[ElementHandle, str]) -> List[Dict[str, Any]]:
        """
        Fill question fields with generated answers
        
        Args:
            answer_mapping: Dictionary mapping question elements to answers
            
        Returns:
            List of fill results with metadata
        """
        results = []
        
        try:
            for element, answer in answer_mapping.items():
                try:
                    # Fill the textarea or input field with the generated answer
                    await element.fill(answer)
                    
                    # Trigger any onChange events
                    await element.press("Tab")
                    
                    results.append({
                        "element": element,
                        "answer": answer,
                        "success": True
                    })
                    
                    logger.info("Successfully filled question field with generated answer")
                    
                except Exception as e:
                    logger.error(f"Error filling question field: {e}")
                    results.append({
                        "element": element,
                        "answer": answer,
                        "success": False,
                        "error": str(e)
                    })
                    
            successful_fills = sum(1 for r in results if r["success"])
            logger.info(f"Filled {successful_fills}/{len(results)} question fields successfully")
            return results
            
        except Exception as e:
            logger.error(f"Error filling answers: {e}")
            return results