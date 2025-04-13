import google.generativeai as genai
from dotenv import load_dotenv
import os
from state import state
from creatingState import Application

load_dotenv()
api_key = os.getenv('API_KEY')
genai.configure(api_key=api_key)

# ------------------------------
# Upload and run the creating state file
# ------------------------------
# Instantiate the Application (from creatingState.py) and run its workflow.
# This will prompt you for the PDF file path and process transcript, schedule, and professor data.
app = Application()
app.run()

# ------------------------------
# Update the state
# ------------------------------
# The Application.run() method updates the shared state automatically.
# You can verify this by printing the current state.
print("Updated shared state:", state.get())

def create_advisor_prompt(user_input):
    """
    Builds a comprehensive prompt by incorporating the given academic context
    and the user's query.
    """
    current_state = state.get()
    
    # Check if we have the required data in state
    if not current_state.get('user'):
        return "Error: User data not found in state. Please upload a transcript first."
    
    prompt = f"""You are an academic advisor chatbot for the user at University of California, Santa Cruz for a student majoring in Computer Science. Use the following context to provide course recommendations and academic advice.

User Information:
- Name: {current_state['user']['name']}
- GPA: {current_state['user']['gpa']}
- Credits Taken: {current_state['user']['credits_taken']}
- Courses Taken: {', '.join(current_state['user']['courses_taken'])}
"""
    if current_state.get('eligible_schedule'):
        prompt += "\nEligible Schedule (Course - Section: Instructor):\n"
        for course, sections in current_state["eligible_schedule"].items():
            course_info = []
            for section, instructor in sections.items():
                if instructor:
                    course_info.append(f"{section} ({instructor})")
            prompt += f"\n- {course}: " + ", ".join(course_info)
    
    if current_state.get('professors'):
        prompt += "\n\nProfessors Information (Course - Section details):\n"
        for course, sections in current_state["professors"].items():
            prompt += f"\nCourse: {course}\n"
            for section, info in sections.items():
                if info:
                    prompt += f"  Section {section}: {info['name']} (Rating: {info['rating']}, Difficulty: {info['difficulty']}, Take Again: {info['take_again']})\n"
    
    prompt += f"\nUser's Question: {user_input}\n"
    prompt += "\nBased on the above information, recommend courses for the upcoming quarter and provide clear, concise academic advice."
    return prompt

def get_academic_advice(user_input):
    """
    Uses the Gemini API to generate academic advising responses based on the context.
    """
    try:
        # Create the Gemini model instance
        model = genai.GenerativeModel('gemini-1.5-pro-latest')
        # Build the prompt by merging context with the user's query
        prompt = create_advisor_prompt(user_input)
        # Generate content using the Gemini model
        response = model.generate_content(prompt)
        
        # Update state with the response from Gemini
        state.update({'gemini_response': response.text})
        return response.text
    except Exception as e:
        # Update state with error details in case something goes wrong
        state.update({'gemini_error': str(e)})
        return f"An error occurred: {e}"

if __name__ == "__main__":
    # Example: Ask the chatbot for course recommendations for the next quarter.
    user_input = "I am looking for course recommendations and advice for planning my next quarter based on my current academic record."
    advice = get_academic_advice(user_input)
    print("Academic Advisor Response:\n", advice)
