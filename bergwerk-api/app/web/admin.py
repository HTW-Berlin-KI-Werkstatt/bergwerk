import io
from fastapi import APIRouter, HTTPException, Response, UploadFile
from data import wiki as data_wiki
from error import Unauthorized
from datetime import datetime
import json
from icecream import ic

router = APIRouter(prefix="/admin")

@router.get("/build_intent_classifier")
@router.get("/build_intent_classifier/")
def build_intent_classifier() -> None:
    try:
        data_wiki.build_intent_classifier()
    except Unauthorized as exc:
        raise HTTPException(status_code=403, detail=exc.msg)


@router.get("/export")
@router.get("/export/")
def export_json():
    all_pages = data_wiki.get_all_pages_of_category("Content")
    export = {title: data_wiki.get_entire_page(title) for title in all_pages}
    json_data = json.dumps(export)

    date = datetime.now().strftime("%Y%m%d")
    headers = {
        'Content-Disposition': f'attachment; filename="export_{date}.json"'
    }

    return Response(content=json_data, media_type="application/json", headers=headers)


@router.post("/import")
@router.post("/import/")
async def import_json(file: UploadFile):
    file_content = await file.read()

    try:
        deserialized_data = json.loads(file_content)
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON file: {e}")

    for title, text in deserialized_data.items():
        print(f"Creating page {title}.")
        data_wiki.create_or_update_page(title, text)
