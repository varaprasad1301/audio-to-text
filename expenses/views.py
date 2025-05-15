# #  Audio to text using the spacy and whispher library,// spacy is used for the parsing the text into the description and the whispher  is used to convert the audio file to text in the form of description  and the amount
# import os
# import tempfile
# import whisper
# import spacy
# import re
# from django.conf import settings
# from rest_framework.views import APIView
# from rest_framework.parsers import MultiPartParser
# from rest_framework.response import Response
# from .models import Expense

# # Load spaCy's English model
# nlp = spacy.load("en_core_web_sm")

# class AudioToExpenseView(APIView):
#     parser_classes = [MultiPartParser]

#     def post(self, request):
#         try:
#             # 1. Get audio file
#             audio_file = request.FILES.get("file")
#             if not audio_file:
#                 return Response({"error": "Audio file is required"}, status=400)

#             # 2. Save to temp file
#             with tempfile.NamedTemporaryFile(delete=False, suffix=".m4a") as temp_audio:
#                 for chunk in audio_file.chunks():
#                     temp_audio.write(chunk)
#                 temp_audio_path = temp_audio.name

#             # 3. Transcribe using Whisper
#             model = whisper.load_model("base")
#             result = model.transcribe(temp_audio_path)
#             transcript = result['text'].lower().strip()
#             print("Transcript:", transcript)

#             # 4. Parse transcript with spaCy for better extraction
#             doc = nlp(transcript)

#             # 5. Extract all amounts using regex and sum them up
#             amounts = re.findall(r"(\d+(\.\d{1,2})?)", transcript)
#             total_amount = sum(float(amount[0]) for amount in amounts)

#             # 6. Extract description using spaCy's noun chunks or sentence analysis
#             description = ""
#             for sent in doc.sents:
#                 if not any(token.like_num for token in sent):  # Skip sentences that only have numbers
#                     description += sent.text + " "

#             description = description.strip()
#             if not description:
#                 description = "General Expense"  # Default description if nothing was extracted

#             # 7. Save to database with the summed total amount
#             expense = Expense.objects.create(
#                 description=description,
#                 amount=total_amount
#             )

#             return Response({
#                 "message": "Expense created",
#                 "data": {
#                     "id": expense.id,
#                     "description": expense.description,
#                     "amount": expense.amount
#                 }
#             })

#         except Exception as e:
#             print("ERROR:", str(e))
#             return Response({"error": str(e)}, status=500)

#         finally:
#             if os.path.exists(temp_audio_path):
#                 os.remove(temp_audio_path)


# import os
# import tempfile
# import whisper
# import spacy
# import re
# from django.conf import settings
# from rest_framework.views import APIView
# from rest_framework.parsers import MultiPartParser
# from rest_framework.response import Response

# # Load spaCy model
# nlp = spacy.load("en_core_web_sm")

# class AudioToExpenseView(APIView):
#     parser_classes = [MultiPartParser]

#     def post(self, request):
#         try:
#             # 1. Get audio file
#             audio_file = request.FILES.get("file")
#             if not audio_file:
#                 return Response({"error": "Audio file is required"}, status=400)

#             # 2. Save to temp file
#             with tempfile.NamedTemporaryFile(delete=False, suffix=".m4a") as temp_audio:
#                 for chunk in audio_file.chunks():
#                     temp_audio.write(chunk)
#                 temp_audio_path = temp_audio.name

#             # 3. Transcribe using Whisper
#             model = whisper.load_model("base")
#             result = model.transcribe(temp_audio_path)
#             transcript = result['text'].lower().strip()
#             print("Transcript:", transcript)

#             # 4. spaCy NLP processing
#             doc = nlp(transcript)

#             # --- Extract Amount ---
#             amount_matches = re.findall(r"\b\d+(?:\.\d{1,2})?\b", transcript)
#             amount = float(amount_matches[0]) if amount_matches else 0.0

#             # --- Extract Payer ---
#             payer = ""
#             for ent in doc.ents:
#                 if ent.label_ == "PERSON":
#                     payer = ent.text.title()
#                     break
#             if not payer:
#                 payer = "Unknown"

#             # --- Extract Description ---
#             description = ""
#             for sent in doc.sents:
#                 if not any(token.like_num for token in sent):
#                     description += sent.text + " "
#             description = description.strip() or "General Expense"

#             # --- Extract People for Split ---
#             people = [ent.text.title() for ent in doc.ents if ent.label_ == "PERSON"]
#             split_with = [p for p in people if p != payer]
#             if not split_with:
#                 split_with = ["Unknown"]

#             # --- Detect Split Type ---
#             if "equally" in transcript or "equal" in transcript:
#                 split_type = "equal"
#             elif "percent" in transcript or "percentage" in transcript:
#                 split_type = "percentage"
#             elif "custom" in transcript:
#                 split_type = "custom"
#             else:
#                 split_type = "equal"

#             return Response({
#                 "payer": payer,
#                 "amount": amount,
#                 "description": description,
#                 "split_with": split_with,
#                 "split_type": split_type
#             })

#         except Exception as e:
#             print("ERROR:", str(e))
#             return Response({"error": str(e)}, status=500)

#         finally:
#             if os.path.exists(temp_audio_path):
#                 os.remove(temp_audio_path)

import os
import tempfile
import whisper
import spacy
import re
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from expenses.models import Expense
from django.utils import timezone

# Load spaCy model
nlp = spacy.load("en_core_web_sm")

class AudioToExpenseView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request):
        temp_audio_path = ""
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

            # 4. spaCy NLP processing
            doc = nlp(transcript)

            # --- Extract Amount ---
            amount_matches = re.findall(r"\b\d+(?:\.\d{1,2})?\b", transcript)
            amount = float(amount_matches[0]) if amount_matches else 0.0

            # --- Extract Payer ---
            payer = ""
            for ent in doc.ents:
                if ent.label_ == "PERSON":
                    payer = ent.text.title()
                    break
            if not payer:
                payer = "Unknown"

            # --- Extract Description ---
            description = ""
            for sent in doc.sents:
                if not any(token.like_num for token in sent):
                    description += sent.text + " "
            description = description.strip() or "General Expense"

            expense = Expense(
                description=description,
                amount=amount,
                payer=payer,
                created_at=timezone.now()
            )
            expense.save()

            # --- Extract People for Split ---
            people = [ent.text.title() for ent in doc.ents if ent.label_ == "PERSON"]
            split_with = [p for p in people if p != payer]
            if not split_with:
                split_with = ["Unknown"]

            # --- Detect Split Type ---
            if "percent" in transcript or "percentage" in transcript:
                split_type = "percentage"
            elif "custom" in transcript:
                split_type = "custom"
            else:
                split_type = "equal"

            # --- Calculate Split Values ---
            split_values = {}
            if split_type == "equal":
                share = round(amount / len(split_with), 2)
                split_values = {name: share for name in split_with}

            elif split_type == "percentage":
                percent = round(100 / len(split_with), 2)
                split_values = {
                    name: round((amount * percent) / 100, 2)
                    for name in split_with
                }

            elif split_type == "custom":
                # For now, use equal split (custom parsing can be added later)
                custom_share = round(amount / len(split_with), 2)
                split_values = {name: custom_share for name in split_with}

            return Response({
                "payer": payer,
                "amount": amount,
                "description": description,
                "split_with": split_with,
                "split_type": split_type,
                "split_values": split_values
            })

        except Exception as e:
            print("ERROR:", str(e))
            return Response({"error": str(e)}, status=500)

        finally:
            if temp_audio_path and os.path.exists(temp_audio_path):
                os.remove(temp_audio_path)
# To extract the text from the image
# expense/views.py

import base64
from io import BytesIO
from PIL import Image
import numpy as np
import re

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from paddleocr import PaddleOCR

ocr_model = PaddleOCR(use_angle_cls=True, lang='en')  # Initialize once

@csrf_exempt
def scan_receipt(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Invalid request method'}, status=405)

    image_file = request.FILES.get('image')
    image_base64 = request.POST.get('image_base64')

    if not image_file and not image_base64:
        return JsonResponse({'error': 'No image provided'}, status=400)

    try:
        if image_file:
            image = Image.open(image_file).convert('RGB')
        else:
            if ';base64,' in image_base64:
                _, imgstr = image_base64.split(';base64,')
            else:
                imgstr = image_base64
            image_data = base64.b64decode(imgstr)
            image = Image.open(BytesIO(image_data)).convert('RGB')

        image_np = np.array(image)
        results = ocr_model.ocr(image_np, cls=True)

        if not results or not results[0]:
            return JsonResponse({'text': '', 'message': 'No text detected'})

        extracted_lines = []
        items_with_amounts = []

        for line in results[0]:
            text = line[1][0]
            extracted_lines.append(text)

            match = re.match(r'(.+?)\s*[\.:\-]*\s*(\d+\.\d{1,2}|\d+)$', text)
            if match:
                description = match.group(1).strip()
                amount = match.group(2).strip()
                items_with_amounts.append(f"Description: {description}, Amount: {amount}")

        extracted_text = "\n".join(extracted_lines)

        return JsonResponse({
            'text': extracted_text,
            'items': items_with_amounts,
            'message': 'OCR success with items extracted'
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
