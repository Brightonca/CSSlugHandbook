import google.generativeai as genai
from dotenv import load_dotenv
import os
from state import state
from creatingState import Application

# Load environment variables and set up the API key.
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
# The Application.run() method automatically updates the shared state.
print("Updated shared state:", state.get())

def create_advisor_prompt(user_input):
    """
    Builds a comprehensive prompt by incorporating the given academic context
    and the user's query. The prompt ends with an open-ended question to let the user continue the conversation.
    """
    current_state = state.get()
    
    # Check if we have the required data in state
    if not current_state.get('user'):
        return "Error: User data not found in state. Please upload a transcript first."
    
    prompt = f"""You are an academic advisor chatbot for a student at the University of California, Santa Cruz,
majoring in Computer Science. Use the following context to provide course recommendations and clear academic advice.

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
    
    # Append the user's current question and an open-ended ending for further conversation.
    prompt += f"\nUser's Question: {user_input}\n"
    prompt += "\nBased on the above information, recommend courses for the upcoming quarter and provide clear, concise academic advice.\nWhat is your next question or concern regarding your academic plan?"
    return prompt

def get_academic_advice(user_input):
    """
    Uses the Gemini API to generate academic advising responses based on the context
    combined with the current user's input.
    """
    try:
        # Create the Gemini model instance
        model = genai.GenerativeModel('gemini-1.5-pro-latest')
        # Build the prompt by merging the context with the user's question.
        prompt = create_advisor_prompt(user_input)
        # Generate content using the Gemini model
        response = model.generate_content(prompt)
        
        # Update state with the Gemini response for reference in subsequent calls.
        state.update({'gemini_response': response.text})
        return response.text
    except Exception as e:
        # Capture errors and update the state so you can investigate further.
        state.update({'gemini_error': str(e)})
        return f"An error occurred: {e}"

if __name__ == "__main__":
    # Start a conversation loop with the academic advisor.
    print("Welcome to your academic advisor chatbot. Type 'exit' to quit.")
    while True:
        user_input = input("\nYour question (or type 'exit' to quit): ")
        if user_input.strip().lower() == "exit":
            print("Exiting academic advisor session. Goodbye!")
            break
        
        # Retrieve and print the advisor's response.
        advice = get_academic_advice(user_input)
        print("\nAcademic Advisor Response:\n", advice)
