from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.request import Request
from rest_framework import status
from .models import TestModel


from django.http import JsonResponse
from django.apps import apps

from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json

#### #! DO NOT MODIFY THIS CODE #! ####

class TestView(APIView):
    """
    This is a test view for the app. It returns a list of all the records in the TestModel.
    """

    def get(self, request: Request) -> Response :
        f"""
        Get all the records from the TestModel and return them as a list of dictionaries.

        :param request: The HTTP request object.

        :return: A JSON response containing the list of records.
        :rtype: Response
        """
        records = TestModel.objects.all()
        return Response([record.to_dict() for record in records], status=status.HTTP_200_OK)

#### #! END OF DO NOT MODIFY THIS CODE #! ####

def chart_schema(request):
    """
    Return the schema for how medical charts are stored in the database.

    This endpoint introspects the MedicalNote model and returns its
    fields and their corresponding Django field types.

    :param request: Django HTTP request
    :return: JSON response describing the chart schema
    :rtype: JsonResponse
    """
    MedicalNote = apps.get_model("app", "MedicalNote")

    fields = {}
    for field in MedicalNote._meta.fields:
        fields[field.name] = field.get_internal_type()

    schema = {
        "table": MedicalNote._meta.db_table,
        "fields": fields,
    }

    return JsonResponse(schema)

@csrf_exempt
@require_http_methods(["POST"])
def upload_chart(request):
    """
    Upload a medical chart by persisting its notes into the database.

    Expects a JSON payload with a chart_id and a list of notes.
    Each note is stored as a MedicalNote row.
    """
    try:
        payload = json.loads(request.body)
        notes = payload.get("notes", [])
    except json.JSONDecodeError:
        return JsonResponse(
            {"error": "Invalid JSON payload"},
            status=400
        )

    inserted_count = 0

    from app.models import MedicalNote

    for note in notes:
        try:
            # Use get_or_create to avoid duplicate inserts
            _, created = MedicalNote.objects.get_or_create(
                note_id=note["note_id"],
                defaults={
                    "chart_id": note["chart_id"],
                    "note_type": note["note_type"],
                    "content": note["content"],
                }
            )
            if created:
                inserted_count += 1
        except KeyError as e:
            return JsonResponse(
                {"error": f"Missing required field: {str(e)}"},
                status=400
            )

    return JsonResponse(
        {
            "message": "Chart uploaded successfully",
            "notes_inserted": inserted_count
        }
    )


@require_http_methods(["GET"])
def list_charts(request):
    """
    List all medical notes stored in the database.

    :param request: Django HTTP request
    :return: JSON list of medical notes
    :rtype: JsonResponse
    """
    from app.models import MedicalNote

    notes = MedicalNote.objects.all()
    data = [note.to_dict() for note in notes]

    return JsonResponse(data, safe=False)


@csrf_exempt
@require_http_methods(["POST"])
def code_chart(request):
    """
    Code a chart by assigning the top-matching ICD-10 G code to each note using a vector store.
    Input: {"chart_id": "..."}
    Output: {"chart_id": "...", "results": [ ... one per note ... ]}
    """
    try:
        payload = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON payload"}, status=400)

    chart_id = payload.get("chart_id")
    if not chart_id:
        return JsonResponse({"error": "Missing required field: chart_id"}, status=400)

    from app.models import MedicalNote
    from app.vector_store import get_vectorstore

    notes = list(MedicalNote.objects.filter(chart_id=chart_id).order_by("id"))
    if not notes:
        return JsonResponse({"error": f"No notes found for chart_id={chart_id}"}, status=404)

    vs = get_vectorstore()

    results = []
    for note in notes:
        query = note.content or ""
        # Returns [(Document, score)] where score is a distance-like value in many configs
        matches = vs.similarity_search_with_score(query, k=1)

        if not matches:
            results.append({
                "note_id": note.note_id,
                "note_type": note.note_type,
                "icd_code": None,
                "score": None,
                "short_description": None,
                "long_description": None,
            })
            continue

        doc, score = matches[0]
        # Score semantics vary; keep raw score to be honest.
        # Provide a simple normalized similarity too
        normalized_similarity = None
        try:
            normalized_similarity = 1.0 / (1.0 + float(score))
        except Exception:
            pass

        results.append({
            "note_id": note.note_id,
            "note_type": note.note_type,
            "icd_code": doc.metadata.get("icd_code"),
            "short_description": doc.metadata.get("short_description"),
            "long_description": doc.page_content,
            "score": score,  # raw from Chroma/LangChain
            "normalized_similarity": normalized_similarity,
        })
    return JsonResponse({"chart_id": chart_id, "results": results})

