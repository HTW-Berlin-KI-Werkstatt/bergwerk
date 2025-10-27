import aiohttp
import asyncio
from . import utils
from . import state
from . import config
from json import loads
state = state.State()
config = config.Config()


async def handle_disconnect(sid):
    if state.get_state(sid, "inactivity_timer") is not None:
        #state.get_state(sid, "inactivity_timer").cancel()
        pass
        # del inactivity_timers[sid]


async def handle_user_message(sid, data, sio, host):
    async with aiohttp.ClientSession() as session:
        if state.check_uid(sid):
            #await reset_inactivity_timer(sid, sio)
            await process_user_input(sid, data, sio, session, host)
        else:
            await handle_initial_interaction(sid, data, sio, session, host)


async def process_user_input(sid, data, sio, session, host):
    if data['message'][0] == "/":
        await fetch_and_send_menu(sid, data, sio, session, host)
    else:
        await fetch_and_send_text_response(sid, data, sio, session, host)


async def fetch_and_send_menu(sid, data, sio, session, host):
    language = state.get_state(sid, "language")
    url = f"{host}/wiki/menuinput/"
    payload = {"menuinput": data['message'].replace(
        "/", ""), "language": language, "uid": sid}
    last_response = state.get_state(sid, "last_response")
    state.set_state(sid, "last_response", data['message'])

    try:
        async with session.post(url, json=payload, ssl=False) as response:
            r = await response.json()
            buttons = utils.create_buttons(r['menuitems'], last_response)
            state.set_state(sid, "current_buttons", buttons)
            await utils.send_text_with_buttons(sid, r['text'], buttons, sio)
    except:
        await utils.send_text_with_buttons(sid, config.get_value("error_message"), [], sio)


async def fetch_and_send_text_response(sid, data, sio, session, host):
    language = state.get_state(sid, "language")
    url = f"{host}/wiki/textinput"
    payload = {"textinput": data['message'], "language": language, "uid": sid}
    last_response = state.get_state(sid, "last_response")
    state.set_state(sid, "last_response", data['message'])
    try:
        async with session.post(url, json=payload, ssl=False) as response:
            r = await response.json()
            buttons = utils.create_buttons(r['menuitems'], last_response)
            state.set_state(sid, "current_buttons", buttons)
            await utils.send_text_with_buttons(sid, r['text'], buttons, sio)
    except:
        await utils.send_text_with_buttons(sid, config.get_value("error_message"), [], sio)


async def handle_initial_interaction(sid, data, sio, session, host):

    conf = loads(config.get_value("languages"))

    valid_payloads = {conf[l]['agree_payload']: {'language': l, 'button': conf[l]['agree_button']}    
                      for l in conf.keys()}


    if data['message'] not in valid_payloads:
        buttons = [
            {"title": conf[l]['agree_button'], "payload": conf[l]['agree_payload']} for l in conf.keys()
        ]
        await utils.send_text_with_buttons(sid, config.get_value("initial_greeting"), buttons, sio)
        
    else:
        language = valid_payloads[data['message']]['language']
        state.add_uid(sid)
        state.set_state(sid, "language", language)
        state.set_state(sid, "last_response", "/Home")
        url = f"{host}/wiki/menuinput/"
        payload = {"menuinput": "Start", "language": language, "uid": sid}

        async with session.post(url, json=payload, ssl=False) as response:
            r = await response.json()
            buttons = utils.create_buttons(r['menuitems'])
            await utils.send_text_with_buttons(sid, r['text'], buttons, sio)


async def reset_inactivity_timer(sid, sio):
    if state.get_state(sid, "inactivity_timer") is not None:
        state.get_state(sid, "inactivity_timer").cancel()
    state.set_state(sid, "inactivity_timer",
                    asyncio.create_task(inactivity_timer(sid, sio)))


async def inactivity_timer(sid, sio):
    try:
        await asyncio.sleep(int(config.get_value("inactivity_timer")))
        await send_thumbs_message(sid, sio)
    except asyncio.CancelledError:
        pass


async def send_thumbs_message(sid, sio) -> None:
    if state.get_state(sid, "feedback") is None:
        buttons = state.get_state(sid, "current_buttons")
        buttons.append({"title": "👍", "payload": "/feedback_positive"})
        buttons.append({"title": "👎", "payload": "/feedback_negative"})

        await utils.send_text_with_buttons(sid, "", buttons, sio)
        state.set_state(sid, "feedback", True)
