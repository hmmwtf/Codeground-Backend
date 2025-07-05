import httpx
import websockets
import json
from fastapi import HTTPException
from src.app.config.config import settings
from sqlalchemy.orm import Session
from src.app.domain.game.service import game_result_service


async def evaluate_code(language: str, code: str):
    payload = {
        "language": language,
        "code": code,
        "stdins": [],
        "timeLimit": 30000,
        "memoryLimit": 256,
        "token": None,
    }
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(settings.ONLINE_JUDGE_HOST_ENDPOINT, json=payload)
            response.raise_for_status()
            results = response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail="Judge request failed")
        except httpx.HTTPError:
            raise HTTPException(status_code=500, detail="Judge service unreachable")
    success = all(res.get("exitCode") == 0 for res in results)
    return {"result": "correct" if success else "wrong", "detail": results}


async def stream_evaluate_code(db: Session, user_id: int, match_id: int, language: str, code: str, problem_id: str):
    """Submit code to the judge service using /execute_v4 and stream results.

    This function returns an async generator yielding raw JSON messages received
    from the judge backend WebSocket. Each yielded value is a JSON formatted
    string representing either a progress or final message.
    """

    base_url = settings.ONLINE_JUDGE_HOST_ENDPOINT.rsplit("/", 1)[0]
    execute_url = f"{base_url}/execute_v4"
    payload = {
        "language": language,
        "code": code,
        "problemId": problem_id,
        "token": None,
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(execute_url, json=payload)
            response.raise_for_status()
            request_id = response.json().get("requestId")
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail="Judge request failed")
        except httpx.HTTPError:
            raise HTTPException(status_code=500, detail="Judge service unreachable")

    scheme, rest = execute_url.split("://", 1)
    ws_scheme = "wss" if scheme == "https" else "ws"
    ws_url = f"{ws_scheme}://{rest.split('/')[0]}/ws/progress/{request_id}"

    async with websockets.connect(ws_url) as websocket:  # type: ignore[attr-defined]
        async for message in websocket:
            yield message
            if '"type":"final"' in message or '"type": "final"' in message:
                # Parse the final message to extract the result
                final_message = json.loads(message)
                # Assuming 'result' is present in the final message from the judge service
                result = final_message.get("result")

                if result:
                    await game_result_service.update_user_log(db, match_id, user_id, result)
                break
