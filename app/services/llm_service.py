import json
from typing import Dict, Any, Optional, List, Type
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from pydantic import BaseModel
from app.config import settings
from app.utils.logger import get_logger
from app.utils.formatters import clean_json_response

logger = get_logger("llm_service")


class LLMService:
    """Service for interacting with OpenAI GPT-4o-mini using LangChain"""
    
    def __init__(self):
        self.api_key = settings.OPENAI_API_KEY
        self.model_name = settings.OPENAI_MODEL
        self.temperature = settings.OPENAI_TEMPERATURE
        self.max_tokens = settings.OPENAI_MAX_TOKENS
        self._initialized = False
        self.llm = None
    
    def initialize(self):
        """Initialize OpenAI LLM"""
        if self._initialized:
            return
        
        try:
            self.llm = ChatOpenAI(
                model=self.model_name,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                openai_api_key=self.api_key
            )
            self._initialized = True
            logger.info(f"LLM service initialized with model: {self.model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize LLM service: {e}")
            raise
    
    def _escape_prompt_braces(self, text: str) -> str:
        """
        Escape curly braces in prompts for LangChain compatibility
        Doubles all { and } to prevent them from being treated as template variables
        """
        return text.replace("{", "{{").replace("}", "}}")
    
    async def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        temperature: Optional[float] = None
    ) -> str:
        """
        Generate text response from prompt
        
        Args:
            prompt: Input prompt (will be escaped automatically)
            system_instruction: Optional system instruction (will be escaped automatically)
            temperature: Optional temperature override
            
        Returns:
            Generated text
        """
        if not self._initialized:
            self.initialize()
        
        try:
            llm = self.llm
            if temperature is not None:
                llm = ChatOpenAI(
                    model=self.model_name,
                    temperature=temperature,
                    max_tokens=self.max_tokens,
                    openai_api_key=self.api_key
                )
            
            messages = []
            if system_instruction:
                messages.append(SystemMessage(content=system_instruction))
            messages.append(HumanMessage(content=prompt))
            
            response = llm.invoke(messages)
            
            if not response or not response.content:
                logger.warning("Empty response from LLM")
                return ""
            
            return response.content.strip()
            
        except Exception as e:
            logger.error(f"LLM generation failed: {e}")
            raise
    
    async def generate_structured_output(
        self,
        prompt: str,
        schema: Type[BaseModel],
        system_instruction: Optional[str] = None,
        max_retries: int = 3
    ) -> BaseModel:
        """
        Generate structured output conforming to a Pydantic schema using LangChain
        
        Args:
            prompt: Input prompt (will be escaped automatically)
            schema: Pydantic model class for output structure
            system_instruction: Optional system instruction (will be escaped automatically)
            max_retries: Maximum number of retry attempts
            
        Returns:
            Parsed Pydantic model instance
        """
        if not self._initialized:
            self.initialize()
        
        try:
            structured_llm = self.llm.with_structured_output(schema)
            messages = []
            if system_instruction:
                messages.append(SystemMessage(content=system_instruction))
            messages.append(HumanMessage(content=prompt))
            result = structured_llm.invoke(messages)
            
            logger.debug(f"Successfully generated structured output of type {schema.__name__}")
            return result
            
        except Exception as e:
            logger.error(f"Structured output generation failed: {e}")
            if max_retries > 0:
                logger.info("Attempting fallback with manual JSON parsing")
                return await self._fallback_structured_output(
                    prompt, schema, system_instruction, max_retries
                )
            raise
    
    async def _fallback_structured_output(
        self,
        prompt: str,
        schema: Type[BaseModel],
        system_instruction: Optional[str] = None,
        max_retries: int = 3
    ) -> BaseModel:
        """
        Fallback method for structured output using manual JSON parsing
        """
        schema_description = schema.model_json_schema()
        
        structured_prompt = f"""{prompt}

You must respond with ONLY valid JSON matching this exact schema. Do not include any markdown formatting, backticks, or explanatory text.

Schema:
{json.dumps(schema_description, indent=2)}

Return ONLY the JSON object, nothing else."""
        
        for attempt in range(max_retries):
            try:
                response_text = await self.generate_text(
                    structured_prompt,
                    system_instruction=system_instruction
                )
                
                cleaned_response = clean_json_response(response_text)
                json_data = json.loads(cleaned_response)
                
                return schema(**json_data)
                
            except json.JSONDecodeError as e:
                logger.warning(f"JSON parsing failed (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt == max_retries - 1:
                    logger.error(f"Failed to parse JSON after {max_retries} attempts")
                    raise
            except Exception as e:
                logger.error(f"Fallback structured output generation failed: {e}")
                if attempt == max_retries - 1:
                    raise
        
        raise Exception("Failed to generate structured output")
    

llm_service = LLMService()


def get_llm_service() -> LLMService:
    """Get LLM service instance"""
    if not llm_service._initialized:
        llm_service.initialize()
    return llm_service