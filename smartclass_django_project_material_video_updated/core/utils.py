import os

try:
    from google import genai
except Exception:
    genai = None


def calculate_performance_band(profile):
    avg_score = (
        float(profile.marks or 0)
        + float(profile.attendance_percentage or 0)
        + float(profile.quiz_average or 0)
        + float(profile.assignment_average or 0)
    ) / 4.0

    if avg_score >= 80:
        return "Excellent", "Low"
    elif avg_score >= 60:
        return "Good", "Medium"
    elif avg_score >= 40:
        return "Average", "Medium"
    return "At Risk", "High"


def fallback_suggestions(profile):
    suggestions = []

    if (profile.attendance_percentage or 0) < 75:
        suggestions.append("Improve attendance consistency and attend all lectures regularly.")
    if (profile.marks or 0) < 60:
        suggestions.append("Focus more on core subjects and revise weak topics weekly.")
    if (profile.quiz_average or 0) < 60:
        suggestions.append("Practice more MCQs and previous question papers.")
    if (profile.assignment_average or 0) < 60:
        suggestions.append("Submit assignments on time and improve answer quality.")
    if not profile.internship:
        suggestions.append("Try to apply for internship opportunities to improve practical exposure.")
    if not profile.skills:
        suggestions.append("Build technical and communication skills through small projects and presentations.")
    if not suggestions:
        suggestions.append("Performance is stable. Continue consistent study, revision, and project work.")

    return "\n".join(suggestions)


def generate_ai_performance_analysis(profile):
    api_key = "AIzaSyB8lXe_PFiUoTYmoTsSCl2u_PNKrumzYXs"

    predicted_band, risk_level = calculate_performance_band(profile)
    fallback_text = fallback_suggestions(profile)

    if not api_key or genai is None:
        return predicted_band, risk_level, fallback_text

    prompt = f"""
You are an academic performance advisor.

Analyze this student profile and return:
1. Predicted Performance Band
2. Risk Level
3. 5 short actionable suggestions

Student Data:
Name: {profile.student_name}
Roll Number: {profile.roll_number}
Division: {profile.division}
Batch: {profile.batch}
Department: {profile.department}
Semester: {profile.semester}
Internship: {profile.internship}
Internship Company: {profile.internship_company}
Internship Domain: {profile.internship_domain}
Marks: {profile.marks}
Attendance Percentage: {profile.attendance_percentage}
Quiz Average: {profile.quiz_average}
Assignment Average: {profile.assignment_average}
Skills: {profile.skills}
Strengths: {profile.strengths}
Improvement Areas: {profile.improvement_areas}
Career Goal: {profile.career_goal}

Also keep output simple and student-friendly.
"""

    try:
        client = genai.Client()
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt,
        )
        text = getattr(response, "text", "") or fallback_text
        return predicted_band, risk_level, text
    except Exception:
        return predicted_band, risk_level, fallback_text