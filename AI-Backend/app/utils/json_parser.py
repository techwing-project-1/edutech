import json
import json_repair
from app.core.logger import logger
from app.core.exceptions import InvalidLLMJSON, JSONRepairFailed, EmptyLLMResponse

class SafeJsonParser:
    """
    A production-grade JSON parser designed to handle malformed LLM outputs.
    Replaces fragile greedy regex with safe extraction and repair.
    """

    @staticmethod
    def safe_parse_llm_json(raw_response: str, provider: str = "Unknown", model: str = "Unknown", request_id: str = "Unknown") -> dict | list:
        if not raw_response or not raw_response.strip():
            logger.error("LLM returned an empty response.")
            raise EmptyLLMResponse("The LLM returned an empty response.", status_code=500, error_code="EMPTY_LLM_RESPONSE")

        # Step 1: Clean Markdown Fences
        cleaned = SafeJsonParser._strip_markdown(raw_response)

        # Step 2: Attempt standard JSON parsing first
        try:
            return json.loads(cleaned)
        except json.JSONDecodeError as e:
            logger.warning(f"[{request_id}] Standard JSON parsing failed. Attempting repair. Error: {str(e)}")

        # Step 3: Use json_repair for aggressive recovery
        try:
            repaired_json_str = json_repair.repair_json(cleaned, return_objects=False)
            parsed = json.loads(repaired_json_str)
            logger.info(f"[{request_id}] Successfully repaired JSON.")
            return parsed
        except Exception as e:
            logger.error(f"[{request_id}] JSON repair failed completely. Error: {str(e)}\nRaw Response: {raw_response[:500]}...")
            raise JSONRepairFailed(
                message="Failed to repair and parse LLM JSON output.",
                status_code=500,
                error_code="JSON_REPAIR_FAILED",
                details={
                    "raw_output": raw_response,
                    "error": str(e),
                    "provider": provider,
                    "model": model,
                    "request_id": request_id
                }
            )

    @staticmethod
    def _strip_markdown(content: str) -> str:
        """
        Safely removes markdown code blocks and conversational text from the edges.
        Does not use greedy regex.
        """
        content = content.strip()
        
        # Remove ```json and ```
        if content.startswith("```"):
            lines = content.split('\n')
            if len(lines) > 1 and lines[0].startswith("```"):
                lines = lines[1:]
            if len(lines) > 0 and lines[-1].strip() == "```":
                lines = lines[:-1]
            content = "\n".join(lines).strip()
            
        # Find the first [ or { and the last ] or }
        first_bracket = content.find('[')
        first_brace = content.find('{')
        
        last_bracket = content.rfind(']')
        last_brace = content.rfind('}')
        
        first_idx = -1
        if first_bracket != -1 and first_brace != -1:
            first_idx = min(first_bracket, first_brace)
        else:
            first_idx = max(first_bracket, first_brace)
            
        last_idx = max(last_bracket, last_brace)
        
        if first_idx != -1 and last_idx != -1 and last_idx >= first_idx:
            return content[first_idx:last_idx+1]
            
        return content
