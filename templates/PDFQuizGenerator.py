import os
from dotenv import load_dotenv
from langchain_google_genai import GoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_core.output_parsers import StrOutputParser
from langchain.prompts import PromptTemplate
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.vectorstores import DocArrayInMemorySearch
from operator import itemgetter
import json
import google.generativeai as genai
import time



class PDFQuizGenerator:
    def __init__(self, model_name="gemini-pro"):
        self.model_name = model_name
        self.setup_model()
        
    def setup_model(self):
        """Initialize the Gemini model and embeddings."""
        load_dotenv()
        
        GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
        if not GOOGLE_API_KEY:
            raise ValueError("GOOGLE_API_KEY not found in environment variables.")
            
        genai.configure(api_key=GOOGLE_API_KEY)
        
        # Initialize model with safety settings
        self.model = GoogleGenerativeAI(
            model=self.model_name,
            google_api_key=GOOGLE_API_KEY,
            temperature=0.3  # Lower temperature for more consistent output
        )
        
    def create_mcq_generation_chain(self):
        """Create a chain for generating MCQ questions."""
        template = """
        You are a quiz generator. Create exactly 5 multiple-choice questions based on the following content.
        
        Rules:
        1. Each question must have exactly 4 options labeled A, B, C, and D.
        2. Only one option should be correct.
        3. All options must be plausible.
        4. Include a brief explanation for the correct answer.
        
        Content to base questions on:
        {context}

        Respond with ONLY the following JSON structure and nothing else:
        {{
            "questions": [
                {{
                    "question": "Write the question here",
                    "options": {{
                        "A": "First option",
                        "B": "Second option",
                        "C": "Third option",
                        "D": "Fourth option"
                    }},
                    "correct_answer": "A",
                    "explanation": "Explain why this is correct"
                }}
            ]
        }}
        """
        
        prompt = PromptTemplate.from_template(template)
        return prompt | self.model | StrOutputParser()

    def clean_json_string(self, json_str):
        """Clean and validate JSON string."""
        start_idx = json_str.find('{')
        end_idx = json_str.rfind('}') + 1
        if start_idx == -1 or end_idx == 0:
            raise ValueError("No JSON object found in response.")
            
        json_str = json_str[start_idx:end_idx]
        try:
            return json.loads(json_str)
        except json.JSONDecodeError:
            json_str = json_str.replace('\n', ' ').replace('\r', '')
            json_str = json_str.replace('""', '"')
            return json.loads(json_str)

    def generate_quiz(self, pdf_path):
        """Generate MCQ quiz from a PDF document."""
        try:
            # Load PDF
            loader = PyPDFLoader(pdf_path)
            pages = loader.load_and_split()
            
            # Combine content
            full_context = "\n".join([page.page_content for page in pages])
            
            # Truncate if needed
            max_length = 25000
            if len(full_context) > max_length:
                full_context = full_context[:max_length]
            
            # Generate MCQs with retry logic
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    mcq_chain = self.create_mcq_generation_chain()
                    mcq_response = mcq_chain.invoke({"context": full_context})
                    
                    # Clean and parse JSON
                    quiz_data = self.clean_json_string(mcq_response)
                    
                    # Validate quiz data structure
                    if not isinstance(quiz_data, dict) or "questions" not in quiz_data:
                        raise ValueError("Invalid quiz data structure.")
                    
                    return quiz_data  # Return JSON directly
                    
                except Exception as e:
                    if attempt == max_retries - 1:
                        raise
                    time.sleep(2)  # Wait before retry
                    
        except Exception as e:
            return f"Failed to generate quiz: {str(e)}"

# Example usage with JSON output
if __name__ == "__main__":
    try:
        # Create quiz generator
        generator = PDFQuizGenerator()
        
        # Generate quiz
        print("Generating quiz... This may take a moment.")
        quiz_data = generator.generate_quiz("os_unit1.pdf")
        
        if isinstance(quiz_data, dict):
            # Save JSON output to a file
            json_output_file = "quiz.json"
            with open(json_output_file, "w", encoding="utf-8") as f:
                json.dump(quiz_data, f, indent=4)
            
            print("\nQuiz has been saved to 'quiz.json'")
            print("\nGenerated Quiz JSON:\n", json.dumps(quiz_data, indent=4))
        else:
            print("\nError:", quiz_data)
            
    except Exception as e:
        print(f"\nAn error occurred: {str(e)}")










# class PDFQuizGenerator:~
#     def __init__(self, model_name="gemini-pro"):
#         self.model_name = model_name
#         self.setup_model()
        
#     def setup_model(self):
#         """Initialize the Gemini model and embeddings"""
#         load_dotenv()
        
#         GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
#         if not GOOGLE_API_KEY:
#             raise ValueError("GOOGLE_API_KEY not found in environment variables")
            
#         genai.configure(api_key=GOOGLE_API_KEY)
        
#         # Initialize model with safety settings
#         self.model = GoogleGenerativeAI(
#             model=self.model_name,
#             google_api_key=GOOGLE_API_KEY,
#             temperature=0.3  # Lower temperature for more consistent output
#         )
        
#         # Initialize embeddings
#         self.embeddings = GoogleGenerativeAIEmbeddings(
#             model="models/embedding-001",
#             google_api_key=GOOGLE_API_KEY
#         )

#     def create_mcq_generation_chain(self):
#         """Create a chain for generating MCQ questions"""
#         template = """
#         You are a quiz generator. Create exactly 5 multiple-choice questions based on the following content.
        
#         Rules:
#         1. Each question must have exactly 4 options labeled A, B, C, and D
#         2. Only one option should be correct
#         3. All options must be plausible
#         4. Include a brief explanation for the correct answer
        
#         Content to base questions on:
#         {context}

#         Respond with ONLY the following JSON structure and nothing else:
#         {{
#             "questions": [
#                 {{
#                     "question": "Write the question here",
#                     "options": {{
#                         "A": "First option",
#                         "B": "Second option",
#                         "C": "Third option",
#                         "D": "Fourth option"
#                     }},
#                     "correct_answer": "A",
#                     "explanation": "Explain why this is correct"
#                 }}
#             ]
#         }}
#         """
        
#         prompt = PromptTemplate.from_template(template)
#         return prompt | self.model | StrOutputParser()

#     def clean_json_string(self, json_str):
#         """Clean and validate JSON string"""
#         # Remove any leading/trailing non-JSON content
#         start_idx = json_str.find('{')
#         end_idx = json_str.rfind('}') + 1
#         if start_idx == -1 or end_idx == 0:
#             raise ValueError("No JSON object found in response")
            
#         json_str = json_str[start_idx:end_idx]
        
#         # Validate JSON structure
#         try:
#             return json.loads(json_str)
#         except json.JSONDecodeError:
#             # If initial parsing fails, try to fix common issues
#             json_str = json_str.replace('\n', ' ').replace('\r', '')
#             json_str = json_str.replace('""', '"')
#             return json.loads(json_str)

#     def generate_quiz(self, pdf_path):

#      """Generate MCQ quiz from a PDF document"""
#         try:
#             # Load PDF
#             loader = PyPDFLoader(pdf_path)
#             pages = loader.load_and_split()
            
#             # Combine content
#             full_context = "\n".join([page.page_content for page in pages])
            
#             # Truncate if needed
#             max_length = 25000
#             if len(full_context) > max_length:
#                 full_context = full_context[:max_length]
            
#             # Generate MCQs with retry logic
#             max_retries = 3
#             for attempt in range(max_retries):
#                 try:
#                     mcq_chain = self.create_mcq_generation_chain()
#                     mcq_response = mcq_chain.invoke({"context": full_context})
                    
#                     # Clean and parse JSON
#                     quiz_data = self.clean_json_string(mcq_response)
                    
#                     # Validate quiz data structure
#                     if not isinstance(quiz_data, dict) or "questions" not in quiz_data:
#                         raise ValueError("Invalid quiz data structure")
                    
#                     return quiz_data  # Return JSON directly
                    
#                 except Exception as e:
#                     if attempt == max_retries - 1:
#                         raise
#                     time.sleep(2)  # Wait before retry
                    
#         except Exception as e:
#             return f"Failed to generate quiz: {str(e)}"

#     # Example usage with JSON output
#     if __name__ == "__main__":
#         try:
#             # Create quiz generator
#             generator = PDFQuizGenerator()
            
#             # Generate quiz
#             print("Generating quiz... This may take a moment.")
#             quiz_data = generator.generate_quiz("os_unit1.pdf")
            
#             if isinstance(quiz_data, dict):
#                 # Save JSON output to a file
#                 json_output_file = "quiz.json"
#                 with open(json_output_file, "w", encoding="utf-8") as f:
#                     json.dump(quiz_data, f, indent=4)
                
#                 print("\nQuiz has been saved to 'quiz.json'")
#                 print("\nGenerated Quiz JSON:\n", json.dumps(quiz_data, indent=4))
#             else:
#                 print("\nError:", quiz_data)
                
#         except Exception as e:
#             print(f"\nAn error occurred: {str(e)}")







