import requests
import orm


async def quick_replies(sender_id, headers, params, state, **kwargs):
    print("quick_replies---------------------------")
    db = orm.SessionLocal()
    user = db.query(orm.User).filter(orm.User.fb_id == sender_id).one_or_none()
    print(user.state_id, 'inner------')
    sub_states = db.query(orm.State).filter(
        orm.State.parent_id == user.state_id
    ).all()
    if sub_states:
        data = {
            "recipient": {
                "id": user.fb_id
            },
            "messaging_type": "RESPONSE",
            "message": {
                "text": state.prompt or state.label,
                "quick_replies": [
                    {
                        "content_type": "text",
                        "title": sub_state.label,
                        "payload": sub_state.name,
                    }
                    for sub_state in sub_states
                ]
            }
        }
        db.close()
        requests.post(
            'https://graph.facebook.com/v10.0/me/messages',
            headers=headers,
            params=params,
            json=data
        )
