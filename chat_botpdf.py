import google.generativeai as genai
genai.configure(api_key="GEMINI API KEY")
model = genai.GenerativeModel("gemini-1.5-flash")
sample_pdf = genai.upload_file( r"D:\gemini\flaskapp\ModernDatabase10thEdition.pdf")
response = model.generate_content(["Give me summary of chapter6.", sample_pdf])
print(response.text)
