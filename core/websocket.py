# # core/websocket.py

# from fastapi import WebSocket, WebSocketDisconnect
# from celery.result import AsyncResult
# import asyncio
# from utils.jwt_auth import get_user_from_ws


# from starlette.websockets import WebSocket, WebSocketDisconnect

# async def websocket_endpoint(websocket: WebSocket, task_id: str):
#     await websocket.accept()

#     try:
#         user = await get_user_from_ws(websocket)
#         username = user.get("sub")

#         if not task_id:
#             try:
#                 await websocket.send_json({"error": "Task ID is required"})
#             except RuntimeError:
#                 # connection already closed, ignore
#                 pass
#             try:
#                 await websocket.close()
#             except RuntimeError:
#                 pass
#             return

#         # Poll Celery task status
#         while True:
#             task = AsyncResult(task_id)
#             response = {
#                 "task_id": task_id,
#                 "status": task.state,
#                 "result": None,
#                 "error": None,
#             }

#             # Access Control:
#             # Only admin can see all task statuses
#             # Normal users should only see their own tasks
#             task_owner = task.result.get("username") if task.result and isinstance(task.result, dict) else None
#             if username != "synchroni" and username != task_owner:
#                 response["error"] = "Access denied for this task."
#                 try:
#                     await websocket.send_json(response)
#                 except RuntimeError:
#                     # connection closed already
#                     break
#                 try:
#                     await websocket.close()
#                 except RuntimeError:
#                     pass
#                 break

#             if task.state == "SUCCESS":
#                 response["result"] = task.result
#                 try:
#                     await websocket.send_json(response)
#                 except RuntimeError:
#                     break
#                 break

#             elif task.state == "FAILURE":
#                 response["error"] = str(task.info)
#                 try:
#                     await websocket.send_json(response)
#                 except RuntimeError:
#                     break
#                 break

#             else:
#                 try:
#                     await websocket.send_json(response)
#                 except RuntimeError:
#                     break

#             await asyncio.sleep(1)

#         try:
#             await websocket.close()
#         except RuntimeError:
#             pass

#     except WebSocketDisconnect:
#         print(f"WebSocket disconnected for task_id: {task_id}")

#     except Exception as e:
#         try:
#             await websocket.send_json({"error": str(e)})
#         except RuntimeError:
#             pass
#         try:
#             await websocket.close()
#         except RuntimeError:
#             pass




# core/websocket.py
 
from fastapi import WebSocket, WebSocketDisconnect

from celery.result import AsyncResult

import asyncio

from utils.jwt_auth import decode_jwt_token  # <- use this to verify RS256 token
 
from starlette.websockets import WebSocket, WebSocketDisconnect
 
async def websocket_endpoint(websocket: WebSocket, task_id: str):

    await websocket.accept()
 
    try:

        # ✅ Step 1: Wait for token in the first message

        initial_data = await websocket.receive_json()

        token = initial_data.get("token")
 
        if not token:

            await websocket.send_json({"error": "JWT token is required in the initial payload."})

            await websocket.close()

            return
 
        try:

            user = decode_jwt_token(token)

        except Exception as e:

            await websocket.send_json({"error": f"Token verification failed: {str(e)}"})

            await websocket.close()

            return
 
        username = user.get("sub")

        if not username:

            await websocket.send_json({"error": "Invalid token payload: missing 'sub'."})

            await websocket.close()

            return
 
        if not task_id:

            try:

                await websocket.send_json({"error": "Task ID is required"})

            except RuntimeError:

                pass

            try:

                await websocket.close()

            except RuntimeError:

                pass

            return
 
        # Poll Celery task status

        while True:

            task = AsyncResult(task_id)

            response = {

                "task_id": task_id,

                "status": task.state,

                "result": None,

                "error": None,

            }
 
            # Access Control

            task_owner = task.result.get("username") if task.result and isinstance(task.result, dict) else None

            if username != "synchroni" and username != task_owner:

                response["error"] = "Access denied for this task."

                try:

                    await websocket.send_json(response)

                except RuntimeError:

                    break

                try:

                    await websocket.close()

                except RuntimeError:

                    pass

                break
 
            if task.state == "SUCCESS":

                response["result"] = task.result

                try:

                    await websocket.send_json(response)

                except RuntimeError:

                    break

                break
 
            elif task.state == "FAILURE":

                response["error"] = str(task.info)

                try:

                    await websocket.send_json(response)

                except RuntimeError:

                    break

                break
 
            else:

                try:

                    await websocket.send_json(response)

                except RuntimeError:

                    break
 
            await asyncio.sleep(1)
 
        try:

            await websocket.close()

        except RuntimeError:

            pass
 
    except WebSocketDisconnect:

        print(f"WebSocket disconnected for task_id: {task_id}")
 
    except Exception as e:

        try:

            await websocket.send_json({"error": str(e)})

        except RuntimeError:

            pass

        try:

            await websocket.close()

        except RuntimeError:

            pass

 