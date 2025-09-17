from django.shortcuts import render

import dropbox
import os
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from dotenv import load_dotenv
import uuid

load_dotenv()

ACCESS_TOKEN = os.getenv("DROPBOX_ACCESS_TOKEN")

dbx = dropbox.Dropbox(ACCESS_TOKEN)

@csrf_exempt
def upload_view(request):
    if request.method == 'POST':
        uploaded_file = request.FILES.get('file')
        problem_id = request.POST.get('problem_id')
        if not uploaded_file:
            return JsonResponse({'error': 'Nessun file inviato'}, status=400)
        if not problem_id or problem_id not in [str(i) for i in range(1, 11)]:
            return JsonResponse({'error': 'ID problema non valido'}, status=400)

        folder_name = f'p{problem_id}'
        
        # Estrai estensione originale
        ext = os.path.splitext(uploaded_file.name)[1]
        # Genera nome file univoco
        unique_filename = f"{uuid.uuid4().hex}{ext}"

        file_path = f'/{folder_name}/{unique_filename}'

        try:
            dbx.files_upload(uploaded_file.read(), file_path, mode=dropbox.files.WriteMode.overwrite)
            shared_link_metadata = dbx.sharing_create_shared_link_with_settings(file_path)
            return JsonResponse({'message': 'Caricamento riuscito', 'url': shared_link_metadata.url})
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)

    return JsonResponse({'error': 'Metodo non consentito'}, status=405)

