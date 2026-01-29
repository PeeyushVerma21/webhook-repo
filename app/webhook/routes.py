from flask import Blueprint, json, request

from app.extensions import mongo

webhook = Blueprint('Webhook', __name__, url_prefix='/webhook')

@webhook.route('/receiver', methods=["POST"])
def receiver():
    event_type = request.headers.get("X-GitHub-Event")
    payload = request.json

    if event_type == "push":
        data = {
            "request_id": payload.get("after"),
            "author": payload.get("pusher", {}).get("name"),
            "action": "PUSH",
            "from_branch": None,
            "to_branch": payload.get("ref", "").split("/")[-1],
            "timestamp": payload.get("head_commit", {}).get("timestamp")
        }

        mongo.db.events.insert_one(data)

        print("\n PUSH EVENT STORED IN DB")
        print(data)
        print("-------------------------\n")
    elif event_type == "pull_request":
        action = payload.get("action")

        if action == "opened":
            pr = payload.get("pull_request")

            data = {
                "request_id": str(pr.get("id")),
                "author": pr.get("user", {}).get("login"),
                "action": "PULL_REQUEST",
                "from_branch": pr.get("head", {}).get("ref"),
                "to_branch": pr.get("base", {}).get("ref"),
                "timestamp": pr.get("created_at")
            }

            mongo.db.events.insert_one(data)

            print("\n PULL REQUEST STORED IN DB")
            print(data)
            print("----------------------------\n")
        
                
        elif action == "closed" and payload.get("pull_request", {}).get("merged") is True:
            pr = payload.get("pull_request")

            data = {
                "request_id": str(pr.get("id")),
                "author": pr.get("user", {}).get("login"),
                "action": "MERGE",
                "from_branch": pr.get("head", {}).get("ref"),
                "to_branch": pr.get("base", {}).get("ref"),
                "timestamp": pr.get("merged_at")
            }

            mongo.db.events.insert_one(data)

            print("\n MERGE EVENT STORED IN DB")
            print(data)
            print("---------------------------\n")


    return {}, 200

@webhook.route('/events', methods=["GET"])
def get_events():
    events = mongo.db.events.find(
        {},
        {"_id": 0}  # exclude MongoDB internal id
    ).sort("timestamp", -1).limit(10)

    return {"events": list(events)}, 200

