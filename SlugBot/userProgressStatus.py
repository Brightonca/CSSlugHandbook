import re
from pypdf import PdfReader

# Get the whole text from your PDF file
def print_pdf_content_as_text(pdf_path):
    # Open and read the PDF file
    reader = PdfReader(pdf_path)
    textdata = ""
    
    # Iterate over each page in the PDF and extract text
    for page_num, page in enumerate(reader.pages, start=1):
        text = page.extract_text()
        if text:
            textdata += text
    return textdata  # Return the accumulated text

# Define the classes
class User:
    def __init__(self, name, credits_taken=0, classes_taken=None, gpa=0.0):
        self.name = name
        self.credits_taken = credits_taken
        self.classes_taken = classes_taken if classes_taken is not None else []
        self.gpa = gpa

    def add_course(self, course):
        """Add a course to the user's taken courses and update credits"""
        self.classes_taken.append(course)

    def get_courses_by_quarter(self, quarter):
        """Get all courses taken in a specific quarter"""
        return [course for course in self.classes_taken if course.quarter == quarter]

    def __str__(self):
        courses_str = "\n".join([f"- {course}" for course in self.classes_taken])
        return (
            f"User: {self.name}\n"
            f"Credits Taken: {self.credits_taken}\n"
            f"GPA: {self.gpa}\n"
            f"Courses Taken:\n{courses_str}"
        )

class Course:
    def __init__(self, code, quarter, credits):
        self.code = code      # e.g., "CSE16" or "CMPM 80K"
        self.quarter = quarter  # e.g., "2024 Summer Quarter"
        self.credits = credits  # e.g., 5.00

    def __str__(self):
        return f"{self.code} - {self.quarter} ({self.credits} credits)"

# ------------------------------------------------------------------------------
# Main parsing logic
if __name__ == '__main__':
    # Get user input for the PDF file path
    pdf_file = input("Enter the PDF file path: ")
    
    # Extract text from the PDF
    text = print_pdf_content_as_text(pdf_file)
    
    # --- 1. Extract the student's name ---
    # Look for a line that begins with "Name:".
    name_match = re.search(r"Name:\s*(.+)", text)
    if name_match:
        full_name = name_match.group(1).strip()
    else:
        full_name = "Unknown"
    
    # Create the user instance
    user = User(name=full_name)
    
    # --- 2. Prepare to extract courses by quarters ---
    current_quarter = None
    lines = text.splitlines()
    
    # Assume a quarter header is in the format: "YYYY <Quarter> Quarter"
    quarter_pattern = re.compile(r'^(\d{4}\s+(Summer|Fall|Winter|Spring)\s+Quarter)')
    
    # Assume a course line starts with a course code, followed by a course description,
    # then two numeric fields (attempted credits and earned credits), a grade, and a points value.
    # For example: "CMPM 80K FoundationsGameDesgn 5.00 5.00 A 20.000"
    course_pattern = re.compile(
        r'^([A-Z]+\s*[0-9A-Z]+)\s+[\w:,&\-]+(?:\s+[\w:,&\-]+)*\s+([\d]+\.[\d]+)\s+([\d]+\.[\d]+)\s+[A-F][+-]?\s+[\d]+\.[\d]+'
    )
    
    # --- 3. Loop over each line to extract quarter headers and course entries ---
    for line in lines:
        line = line.strip()
        
        # Check if the line indicates a new quarter
        quarter_match = quarter_pattern.match(line)
        if quarter_match:
            current_quarter = quarter_match.group(0)  # e.g., "2024 Summer Quarter"
            continue  # move to the next line
        
        # Check if the line matches a course line and if a current quarter is active
        course_match = course_pattern.match(line)
        if course_match and current_quarter:
            course_code = course_match.group(1)
            # Use the first numeric field (attempted credits)
            credits = float(course_match.group(2))
            
            # Create a Course object and add it to the user
            course = Course(code=course_code, quarter=current_quarter, credits=credits)
            user.add_course(course)
    
    # --- 4. Extract the overall cumulative GPA and credits from the last quarter ---
    # Use re.findall to grab all occurrences and then choose the last one.
    # The pattern captures the GPA and the first cumulative credit value after "Cum Totals"
    cumulative_matches = re.findall(
        r'Cum GPA\s+([\d.]+).*?Cum Totals\s+([\d.]+)', 
        text, 
        flags=re.DOTALL
    )
    if cumulative_matches:
        last_gpa, last_credits = cumulative_matches[-1]
        user.gpa = float(last_gpa)
        user.credits_taken = float(last_credits)
    
    # Print out the extracted user details
    print(user)