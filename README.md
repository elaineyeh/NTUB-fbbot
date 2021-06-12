# NTUB-fbbot
## Start ngrok
```shell=
ngrok http 8000 --region ap
```

## Start FastAPI
```shell=
uvicorn main:app --reload
```

### Start Ngrok and FastAPI, copy Ngrok https url to verify the fbbot scepter

# Init persistent_menu
### Delete `persistent_menu` if exists
```
curl -X DELETE 'https://graph.facebook.com/v10.0/me/custom_user_settings?psid=<PSID>&params=[%22persistent_menu%22]&access_token=<PAGE_ACCESS_TOKEN>'
```

### Init `get_started` before `init_menu`
```
curl -X POST -H "Content-Type: application/json" -d '{
  "get_started": {"payload": "Hi I am UB jun"}
}' "https://graph.facebook.com/v2.6/me/messenger_profile?access_token=<PAGE_ACCESS_TOKEN>"
```

### Init menu with `init_menu`
    Call function in init_menu.py
