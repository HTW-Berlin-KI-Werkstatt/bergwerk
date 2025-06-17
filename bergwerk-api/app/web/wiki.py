from fastapi import APIRouter, HTTPException
from  service import wiki as service_wiki
from  service import config as service_config
from  service import tracker as service_tracker 
from model.menu import MenuResponse
from model.textinput import TextInput
from model.menuinput import MenuInput
from model.configuration import ConfigItem
from error import MissingPage, MissingSection, MissingLanguage, MissingClassifier

router = APIRouter(prefix="/wiki")


@router.get("")
@router.get("/")
def wiki_endpoint() -> str:
    return "/wiki/"  # get_all?


@router.get("/config")
@router.get("/config/")
def get_config() -> list[ConfigItem]:
    try:
        return service_wiki.get_config()
    except MissingPage as exc:
        raise HTTPException(status_code=404, detail=exc.msg)
    except MissingSection as exc:
        raise HTTPException(status_code=404, detail=exc.msg)
    except MissingLanguage as exc:
        raise HTTPException(status_code=404, detail=exc.msg)


@router.get("/config/{configitem}")
@router.get("/config/{configitem}/")
def get_configitem(configitem: str) -> ConfigItem:
    try:
        return service_config.get_configitem(configitem=configitem)
    except MissingPage as exc:
        raise HTTPException(status_code=404, detail=exc.msg)
    except MissingSection as exc:
        raise HTTPException(status_code=404, detail=exc.msg)
    except MissingLanguage as exc:
        raise HTTPException(status_code=404, detail=exc.msg)


@router.post("/menuinput")
@router.post("/menuinput/")
def get_menuinput(data: MenuInput) -> MenuResponse:
    service_tracker.track_text(uid=data.uid, role="User", text="", buttons=data.menuinput, language=data.language)
    try:
        mr = service_wiki.get_page(page=data.menuinput, language=data.language)
        service_tracker.track_text(uid=data.uid, role="Assistant", text=mr.text, buttons=str(mr.menuitems), language=data.language)
        return mr
    except MissingPage as exc:
        raise HTTPException(status_code=404, detail=exc.msg)
    except MissingSection as exc:
        raise HTTPException(status_code=404, detail=exc.msg)
    except MissingLanguage as exc:
        raise HTTPException(status_code=404, detail=exc.msg)


@router.post("/textinput/")
@router.post("/textinput")
def get_textinput(data: TextInput) -> MenuResponse:
    service_tracker.track_text(uid=data.uid, role="User", text=data.textinput, buttons="", language=data.language)
    try:
        try:
            pc = service_wiki.predict(data.textinput)
        except MissingClassifier:
            return MenuResponse(title="No intent classifier.", text="No intent classifier.", menuitems=[])
        page = pc[0]
        mr = service_wiki.get_page(page=page.title, language=data.language)
        service_tracker.track_text(uid=data.uid, role="Assistant", text=mr.text, buttons=str(mr.menuitems),language=data.language)
        return mr
    except MissingPage as exc:
        raise HTTPException(status_code=404, detail=exc.msg)
    except MissingSection as exc:
        raise HTTPException(status_code=404, detail=exc.msg)
    except MissingLanguage as exc:
        raise HTTPException(status_code=404, detail=exc.msg)


