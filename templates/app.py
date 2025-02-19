import streamlit as st
import json
from PDFQuizGenerator import PDFQuizGenerator  # Assuming your class is saved in this file

# Initialize the quiz generator
quiz_generator = PDFQuizGenerator()

# Streamlit app
st.title("PDF Quiz Generator")
st.write("Upload a PDF file to generate a quiz.")

# Step 1: File upload
uploaded_file = st.file_uploader("Upload a PDF file", type="pdf")

if uploaded_file:
    # Save the uploaded file temporarily
    with open("temp.pdf", "wb") as f:
        f.write(uploaded_file.read())
    
    st.success("PDF uploaded successfully! Generating quiz...")

    # Step 2: Generate quiz
    try:
        quiz_data = quiz_generator.generate_quiz("temp.pdf")
        
        if isinstance(quiz_data, dict) and "questions" in quiz_data:
            st.success("Quiz generated successfully!")
            st.write("Attempt the quiz below:")

            # Extract quiz questions
            quiz_questions = quiz_data["questions"]
            user_answers = {}

            # Step 3: Display questions with options and their values
            for idx, question in enumerate(quiz_questions, start=1):
                st.subheader(f"Q{idx}: {question['question']}")

    # Prepare the options with values
                options_with_values = [f"{key}: {value}" for key, value in question["options"].items()]

    # Display the options with values using radio buttons
                user_answers[idx] = st.radio(
                label=f"Select your answer for Q{idx}:",
                options=options_with_values,
                key=f"question_{idx}")


            
            # Step 4: Submit button
            if st.button("Submit Quiz"):
                correct_count = 0

                # Calculate score
                # Calculate score
                for idx, question in enumerate(quiz_questions, start=1):
                    correct_answer = question["correct_answer"]
                    selected_option = user_answers[idx].split(":")[0]  # Extract the option key (e.g., 'A')
                    if selected_option == correct_answer:
                        correct_count += 1


                total_questions = len(quiz_questions)
                score = (correct_count / total_questions) * 100

                # Display results
                st.success(f"**You scored: {score:.2f}% ({correct_count}/{total_questions} correct)**")
                
                # Show detailed feedback
                st.subheader("Detailed Results:")
                for idx, question in enumerate(quiz_questions, start=1):
                    st.write(f"**Q{idx}: {question['question']}**")
                    st.write(f"Your answer: {user_answers[idx]}")
                    st.write(f"Correct answer: {question['correct_answer']}")
                    st.write(f"Explanation: {question.get('explanation', 'No explanation provided')}")

        else:
            st.error("Failed to generate quiz. The output format is incorrect.")

    except Exception as e:
        st.error(f"An error occurred: {e}")
