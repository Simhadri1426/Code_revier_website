import os
import json
import time
from google import genai
import markdown2
from typing import Tuple
from google.api_core import exceptions as google_exceptions

def detect_language(code_text: str) -> str:
    """
    Detect the programming language based on code patterns and syntax.
    Returns the detected language or 'unknown' if unclear.
    """
    code_lower = code_text.lower()
    
    # Python indicators
    python_indicators = [
        'def ', 'import ', 'from ', 'if __name__', 'print(', 'range(', 
        'len(', 'append(', 'split(', 'strip()', 'lower()', 'upper()',
        'for ', 'in ', 'while ', 'try:', 'except:', 'finally:', 'with ',
        'class ', 'self.', 'lambda ', 'map(', 'filter(', 'list(', 'dict(',
        'set(', 'tuple(', 'enumerate(', 'zip(', 'sorted(', 'reversed('
    ]
    
    # JavaScript indicators
    js_indicators = [
        'function ', 'var ', 'let ', 'const ', 'console.log(', 'alert(',
        'document.', 'window.', 'addEventListener(', 'querySelector(',
        'getElementById(', 'innerHTML', 'style.', 'classList.',
        'fetch(', 'then(', 'catch(', 'async ', 'await ', 'Promise(',
        'setTimeout(', 'setInterval(', 'parseInt(', 'parseFloat(',
        'JSON.parse(', 'JSON.stringify(', 'localStorage.', 'sessionStorage.'
    ]
    
    # PHP indicators
    php_indicators = [
        '<?php', '<?=', 'echo ', 'print ', 'var_dump(', 'print_r(',
        '$', 'function ', 'class ', 'public ', 'private ', 'protected ',
        'static ', 'const ', 'namespace ', 'use ', 'require ', 'include ',
        'require_once ', 'include_once ', 'array(', 'count(', 'strlen(',
        'substr(', 'strpos(', 'explode(', 'implode(', 'trim(', 'strtolower(',
        'strtoupper(', 'ucfirst(', 'ucwords(', 'htmlspecialchars(',
        'mysqli_', 'pdo_', 'mysql_', 'session_start(', 'header(',
        'isset(', 'empty(', 'is_array(', 'is_string(', 'is_numeric('
    ]
    
    # Java indicators
    java_indicators = [
        'public class', 'public static void main', 'System.out.println',
        'import java.', 'package ', 'public ', 'private ', 'protected ',
        'static ', 'final ', 'class ', 'interface ', 'extends ', 'implements ',
        'new ', 'String ', 'int ', 'double ', 'boolean ', 'char ', 'byte ',
        'short ', 'long ', 'float ', 'void ', 'return ', 'if (', 'else ',
        'for (', 'while (', 'do {', 'switch (', 'case ', 'default:',
        'try {', 'catch (', 'finally {', 'throw ', 'throws ',
        'ArrayList<', 'HashMap<', 'LinkedList<', 'HashSet<', 'TreeSet<'
    ]
    
    # C++ indicators
    cpp_indicators = [
        '#include <', '#include "', 'using namespace std;', 'cout <<',
        'cin >>', 'endl;', 'int main()', 'class ', 'public:', 'private:',
        'protected:', 'virtual ', 'template<', 'typename ', 'const ',
        'static ', 'extern ', 'inline ', 'friend ', 'operator ', 'new ',
        'delete ', 'this->', 'std::', 'vector<', 'map<', 'set<', 'string ',
        'auto ', 'nullptr', 'override', 'final', 'noexcept', 'constexpr'
    ]
    
    # C indicators
    c_indicators = [
        '#include <', '#include "', '#define ', '#ifdef ', '#ifndef ',
        '#endif', '#pragma ', 'int main(', 'printf(', 'scanf(', 'malloc(',
        'free(', 'calloc(', 'realloc(', 'strcpy(', 'strcat(', 'strcmp(',
        'strlen(', 'strtok(', 'sprintf(', 'sscanf(', 'fopen(', 'fclose(',
        'fread(', 'fwrite(', 'fgets(', 'fputs(', 'struct ', 'union ',
        'enum ', 'typedef ', 'extern ', 'static ', 'register ', 'volatile '
    ]
    
    # Count matches for each language
    scores = {
        'python': sum(1 for indicator in python_indicators if indicator in code_lower),
        'javascript': sum(1 for indicator in js_indicators if indicator in code_lower),
        'php': sum(1 for indicator in php_indicators if indicator in code_lower),
        'java': sum(1 for indicator in java_indicators if indicator in code_lower),
        'cpp': sum(1 for indicator in cpp_indicators if indicator in code_lower),
        'c': sum(1 for indicator in c_indicators if indicator in code_lower)
    }
    
    # Get the language with the highest score
    if scores:
        detected_language = max(scores, key=scores.get)
        # Only return detected language if it has a reasonable number of matches
        if scores[detected_language] >= 2:
            return detected_language
    
    return 'unknown'

def analyze_code_with_gemini(code_text: str, language: str, max_retries: int = 3):
    """
    Analyze code with Gemini AI with retry logic for handling API errors.
    """
    # First, detect the actual language of the code
    detected_language = detect_language(code_text)
    
    # Check for language mismatch
    language_mismatch = False
    language_warning = ""
    
    if detected_language != 'unknown' and detected_language != language.lower():
        language_mismatch = True
        language_warning = f"⚠️ **Language Mismatch Detected:** The code appears to be {detected_language.upper()} but you selected {language.upper()}. Analysis will be performed for the detected language ({detected_language.upper()})."
        # Use the detected language for analysis
        analysis_language = detected_language
    else:
        analysis_language = language
    
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise Exception("GEMINI_API_KEY not found in environment variables")
    
    client = genai.Client(api_key=api_key)
    prompt = f"""
    Analyze the following {analysis_language} code and provide a structured review with the following format:

    Code:
    {code_text}

    Please format your response as follows:
    ---
    FEEDBACK:
    ## Overview
    <Brief overview of the code>

    ## Code Quality Assessment
    - **Strengths:**
      - <strength 1>
      - <strength 2>
      - <strength 3>
    
    - **Areas for Improvement:**
      - <improvement 1>
      - <improvement 2>
      - <improvement 3>

    ## Best Practices
    - **Followed:**
      - <good practice 1>
      - <good practice 2>
    
    - **Recommendations:**
      - <recommendation 1>
      - <recommendation 2>
      - <recommendation 3>

    ## Security Considerations
    - <security point 1>
    - <security point 2>
    - <security point 3>

    ## Performance Tips
    - <performance tip 1>
    - <performance tip 2>
    - <performance tip 3>

    ## Code Structure
    - <structure point 1>
    - <structure point 2>
    - <structure point 3>
    ---
    SCORE: <number>
    ---
    COMMENTS:
    <Inline commented code here>
    ---
    """
    
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            content = response.text
            
            # Parse the response for FEEDBACK, SCORE, COMMENTS
            feedback, score, comments = '', 50, ''
            try:
                sections = content.split('---')
                for section in sections:
                    if section.strip().startswith('FEEDBACK:'):
                        feedback = section.strip().replace('FEEDBACK:', '').strip()
                    elif section.strip().startswith('SCORE:'):
                        try:
                            score = int(section.strip().replace('SCORE:', '').strip())
                        except Exception:
                            score = 50
                    elif section.strip().startswith('COMMENTS:'):
                        comments = section.strip().replace('COMMENTS:', '').strip()
                if not feedback:
                    feedback = content.strip()
            except Exception:
                feedback = content.strip()
                score = 50
                comments = ''
            
            # Add language mismatch warning if applicable
            if language_mismatch:
                feedback = f"{language_warning}\n\n{feedback}"
            
            # Convert feedback to HTML using markdown2 for better formatting
            feedback_html = markdown2.markdown(feedback)
            return feedback_html, score, comments
            
        except google_exceptions.ServiceUnavailable as e:
            if attempt < max_retries - 1:
                wait_time = (2 ** attempt) + 1  # Exponential backoff: 1s, 3s, 7s
                time.sleep(wait_time)
                continue
            else:
                # Use fallback analysis when AI service is unavailable
                feedback, score, comments = basic_code_analysis(code_text, analysis_language)
                if language_mismatch:
                    feedback = f"{language_warning}\n\n{feedback}"
                feedback_html = markdown2.markdown(feedback)
                return feedback_html, score, comments
                
        except google_exceptions.ResourceExhausted as e:
            raise Exception("Gemini AI service quota exceeded. Please try again later or contact support.")
            
        except google_exceptions.InvalidArgument as e:
            raise Exception(f"Invalid request to Gemini AI: {str(e)}")
            
        except google_exceptions.PermissionDenied as e:
            raise Exception("Access denied to Gemini AI. Please check your API key and permissions.")
            
        except Exception as e:
            if "503" in str(e) or "UNAVAILABLE" in str(e):
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) + 1
                    time.sleep(wait_time)
                    continue
                else:
                    # Use fallback analysis when AI service is overloaded
                    feedback, score, comments = basic_code_analysis(code_text, analysis_language)
                    if language_mismatch:
                        feedback = f"{language_warning}\n\n{feedback}"
                    feedback_html = markdown2.markdown(feedback)
                    return feedback_html, score, comments
            else:
                raise Exception(f"Unexpected error occurred: {str(e)}")

def detect_plagiarism_hints(code_text: str) -> str:
    """
    Basic plagiarism detection using pattern matching.
    This is a simplified version - in production you'd use more sophisticated methods.
    """
    # Common patterns that might indicate copied code
    patterns = [
        "public static void main",
        "def main():",
        "if __name__ == '__main__':",
        "console.log(",
        "print(",
        "System.out.println"
    ]
    
    hints = []
    for pattern in patterns:
        if pattern in code_text:
            hints.append(f"Contains common pattern: {pattern}")
    
    if hints:
        return " | ".join(hints)
    return "No obvious patterns detected"

def basic_code_analysis(code_text: str, language: str) -> Tuple[str, int, str]:
    """
    Basic code analysis when AI service is unavailable.
    Provides simple metrics and suggestions based on code patterns.
    """
    lines = code_text.split('\n')
    total_lines = len(lines)
    comment_lines = sum(1 for line in lines if line.strip().startswith(('#', '//', '/*', '*/')))
    empty_lines = sum(1 for line in lines if not line.strip())
    code_lines = total_lines - comment_lines - empty_lines
    
    # Basic scoring based on code structure
    score = 50  # Base score
    
    # Adjust score based on code characteristics
    if comment_lines > 0 and code_lines > 0:
        comment_ratio = comment_lines / code_lines
        if 0.1 <= comment_ratio <= 0.3:
            score += 10  # Good comment ratio
        elif comment_ratio > 0.3:
            score += 5   # Too many comments
        else:
            score -= 5   # Too few comments
    
    if code_lines > 0:
        avg_line_length = sum(len(line) for line in lines if line.strip() and not line.strip().startswith(('#', '//', '/*', '*/'))) / code_lines
        if avg_line_length <= 80:
            score += 10  # Good line length
        elif avg_line_length > 120:
            score -= 10  # Lines too long
    
    # Check for common issues
    issues = []
    suggestions = []
    
    if language.lower() == 'python':
        if 'import *' in code_text:
            issues.append("Avoid wildcard imports")
            score -= 5
        if 'print(' in code_text and 'def ' in code_text:
            suggestions.append("Consider using logging instead of print statements in functions")
        if len(code_text) > 1000 and 'def ' not in code_text:
            suggestions.append("Consider breaking code into functions")
        if 'eval(' in code_text:
            issues.append("Avoid using eval() - security risk")
            score -= 15
        if 'exec(' in code_text:
            issues.append("Avoid using exec() - security risk")
            score -= 15
    
    elif language.lower() == 'javascript':
        if 'console.log(' in code_text and 'function ' in code_text:
            suggestions.append("Consider using proper logging instead of console.log in functions")
        if 'var ' in code_text:
            suggestions.append("Consider using 'let' or 'const' instead of 'var'")
            score -= 5
        if 'eval(' in code_text:
            issues.append("Avoid using eval() - security risk")
            score -= 15
        if 'innerHTML' in code_text and 'document.' in code_text:
            suggestions.append("Consider using textContent instead of innerHTML for security")
    
    elif language.lower() == 'php':
        if 'mysql_' in code_text:
            issues.append("mysql_* functions are deprecated, use PDO or mysqli")
            score -= 10
        if 'echo $_' in code_text or 'print $_' in code_text:
            issues.append("Sanitize user input before output")
            score -= 10
        if 'include $_' in code_text or 'require $_' in code_text:
            issues.append("Avoid dynamic includes with user input - security risk")
            score -= 15
        if '<?=' in code_text and 'htmlspecialchars' not in code_text:
            suggestions.append("Use htmlspecialchars() when outputting data")
    
    elif language.lower() == 'java':
        if 'System.out.println' in code_text and 'public static void main' in code_text:
            suggestions.append("Consider using proper logging framework instead of System.out.println")
        if 'catch (Exception e)' in code_text:
            suggestions.append("Catch specific exceptions instead of generic Exception")
        if 'new String(' in code_text:
            suggestions.append("Use string literals instead of new String()")
    
    elif language.lower() in ['cpp', 'c']:
        if 'using namespace std;' in code_text and language.lower() == 'cpp':
            suggestions.append("Consider avoiding 'using namespace std;' in header files")
        if 'malloc(' in code_text and 'free(' not in code_text:
            issues.append("Memory allocated but not freed")
            score -= 10
        if 'printf(' in code_text and 'scanf(' in code_text:
            suggestions.append("Consider using C++ streams (cout/cin) instead of printf/scanf")
    
    # Generate feedback
    feedback_parts = [
        f"## Overview",
        f"This is a basic analysis of your {language} code with {code_lines} lines of executable code.",
        "",
        f"## Code Quality Assessment",
        f"- **Strengths:**",
        f"  - Code has {comment_lines} comment lines for documentation",
        f"  - Average line length is {avg_line_length:.1f} characters",
        f"  - Good code-to-comment ratio" if 0.1 <= comment_lines/code_lines <= 0.3 else f"  - Code structure is well-organized",
        "",
        f"- **Areas for Improvement:**",
    ]
    
    if issues:
        for issue in issues:
            feedback_parts.append(f"  - {issue}")
    else:
        feedback_parts.append("  - No major issues detected")
    
    feedback_parts.extend([
        "",
        f"## Best Practices",
        f"- **Followed:**",
        f"  - Proper code formatting",
        f"  - Consistent indentation",
    ])
    
    if suggestions:
        feedback_parts.extend([
            f"- **Recommendations:**",
        ])
        for suggestion in suggestions:
            feedback_parts.append(f"  - {suggestion}")
    else:
        feedback_parts.append(f"  - Code follows most best practices")
    
    feedback_parts.extend([
        "",
        f"## Code Statistics",
        f"- Total lines: {total_lines}",
        f"- Code lines: {code_lines}",
        f"- Comment lines: {comment_lines}",
        f"- Empty lines: {empty_lines}",
        f"- Average line length: {avg_line_length:.1f} characters",
        "",
        f"**Score: {score}/100**",
        "",
        "*Note: This is a basic analysis. For detailed AI-powered review, please try again when the service is available.*"
    ])
    
    feedback = "\n".join(feedback_parts)
    comments = f"Basic analysis completed for {language} code ({code_lines} lines of code)"
    
    return feedback, score, comments

def generate_inline_comments(code_text: str, language: str, max_retries: int = 3) -> str:
    """
    Generate inline comments for code using Google Gemini AI with retry logic.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        return "Comments could not be generated - API key not available"
    
    client = genai.Client(api_key=api_key)
    prompt = f"""
    Add helpful inline comments to this {language} code. 
    Explain what each section does in simple terms.
    Return only the commented code:

    {code_text}
    """
    
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt
            )
            return response.text
            
        except google_exceptions.ServiceUnavailable as e:
            if attempt < max_retries - 1:
                wait_time = (2 ** attempt) + 1
                time.sleep(wait_time)
                continue
            else:
                return f"Comments could not be generated - Gemini AI service is currently unavailable. Please try again in a few minutes. (Attempt {attempt + 1}/{max_retries})"
                
        except google_exceptions.ResourceExhausted as e:
            return "Comments could not be generated - Gemini AI service quota exceeded. Please try again later."
            
        except google_exceptions.InvalidArgument as e:
            return f"Comments could not be generated - Invalid request: {str(e)}"
            
        except google_exceptions.PermissionDenied as e:
            return "Comments could not be generated - Access denied. Please check your API key and permissions."
            
        except Exception as e:
            if "503" in str(e) or "UNAVAILABLE" in str(e):
                if attempt < max_retries - 1:
                    wait_time = (2 ** attempt) + 1
                    time.sleep(wait_time)
                    continue
                else:
                    return f"Comments could not be generated - Gemini AI service is currently overloaded. Please try again in a few minutes. (Attempt {attempt + 1}/{max_retries})"
            else:
                return f"Comments could not be generated - Unexpected error: {str(e)}" 