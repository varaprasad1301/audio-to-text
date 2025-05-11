#  Audio to text using the spacy and whispher library,// spacy is used for the parsing the text into the description and the whispher  is used to convert the audio file to text in the form of description  and the amount
import os
import tempfile
import whisper
import spacy
import re
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from .models import Expense

# Load spaCy's English model
nlp = spacy.load("en_core_web_sm")

class AudioToExpenseView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        try:
            # 1. Get audio file
            audio_file = request.FILES.get("file")
            if not audio_file:
                return Response({"error": "Audio file is required"}, status=400)

            # 2. Save to temp file
            with tempfile.NamedTemporaryFile(delete=False, suffix=".m4a") as temp_audio:
                for chunk in audio_file.chunks():
                    temp_audio.write(chunk)
                temp_audio_path = temp_audio.name

            # 3. Transcribe using Whisper
            model = whisper.load_model("base")
            result = model.transcribe(temp_audio_path)
            transcript = result['text'].lower().strip()
            print("Transcript:", transcript)

            # 4. Parse transcript with spaCy for better extraction
            doc = nlp(transcript)

            # 5. Extract all amounts using regex and sum them up
            amounts = re.findall(r"(\d+(\.\d{1,2})?)", transcript)
            total_amount = sum(float(amount[0]) for amount in amounts)

            # 6. Extract description using spaCy's noun chunks or sentence analysis
            description = ""
            for sent in doc.sents:
                if not any(token.like_num for token in sent):  # Skip sentences that only have numbers
                    description += sent.text + " "

            description = description.strip()
            if not description:
                description = "General Expense"  # Default description if nothing was extracted

            # 7. Save to database with the summed total amount
            expense = Expense.objects.create(
                description=description,
                amount=total_amount
            )

            return Response({
                "message": "Expense created",
                "data": {
                    "id": expense.id,
                    "description": expense.description,
                    "amount": expense.amount
                }
            })

        except Exception as e:
            print("ERROR:", str(e))
            return Response({"error": str(e)}, status=500)

        finally:
            if os.path.exists(temp_audio_path):
                os.remove(temp_audio_path)

