#!/usr/bin/python3
from flask import Flask, render_template, request, jsonify, redirect, session, url_for
import json

from custom_oauth import OAuthClient
import generic

config = {}
# setup config
with open("config/WEB_config.json") as j:
    config = json.load(j)

# We need to pass these on every render, and they are not going to change
g_background_color = config["color_web_background"]
g_header_color = config["color_web_header"]
g_logo_alt = config["logo_alt_name"]
g_logo_image = config["logo_image_path"]
g_header_table_color = config["color_header_table"]
g_text_header_table_color = config["color_text_header_table"]
g_button_modify_color = config["color_button_modify"]
g_base_uri = config["base_uri"]

# Launch flask
app = Flask(__name__)
app.secret_key = generic.randomString()

# Generate internal clients
auth_client = OAuthClient(config)

def refresh_session(refresh_token):
    print("Refreshing session")
    data = auth_client.refresh_token(refresh_token)
    print(data)
    err, code = generic.get_posible_errors(data)
    print(err)
    if err is "":
        print("Ok, writing new session data")
        session["access_token"] = data.get("access_token","")
        session["refresh_token"] = data.get("refresh_token","")
    
    return err, code

@app.route(g_base_uri+config["oauth_callback_path"])
def oauth_callback():
    code = request.args.get('code')
    try:
        response = auth_client.get_token(code)
    except Exception as e:
        print(str(e))
        return redirect(url_for('home'))

    session['access_token'] = response["access_token"]
    session['id_token'] = response["id_token"]
    session['refresh_token'] = response["refresh_token"]
    session[generic.ERR_CODE] = ""
    session[generic.ERR_MSG] = ""
    try:
        userinfo = auth_client.get_user_info(response["access_token"])
    except Exception as e:
        print(str(e))
        return redirect(url_for('home'))

    if userinfo != None:
        session['logged_in'] = True
        session['logged_user'] = userinfo["name"]

    if session.get('reminder') != None:
        redirect_url = session.get('reminder')
    else:
        redirect_url = 'home'
    return redirect(url_for(redirect_url))

@app.route(g_base_uri)
def home():
    logged_in = session.get('logged_in')
    refresh_token = session.get('refresh_token',"")
    if refresh_token is not "":
        refresh_session(refresh_token)

    return render_template("home.html",
    title = config["title"],
    username = session.get('logged_user'),
    logged_in = logged_in,
    color_web_background = g_background_color,
    color_web_header = g_header_color,
    logo_alt_name = g_logo_alt,
    logo_image_path = g_logo_image)

@app.route(g_base_uri+"/login")
def login():
    url = auth_client.get_login_url()
    return redirect(url)

@app.route(g_base_uri+"/logout")
def logout():
    session['logged_in'] = False
    session['logged_user'] = None
    session[generic.ERR_CODE] = ""
    session[generic.ERR_MSG] = ""
    token = session.get('id_token')
    if token:
        return redirect(auth_client.end_session_url(token))
    else:
        return redirect(url_for("home"))

@app.route(g_base_uri+"/profile_management/modify",methods=['POST'])
def modify_management():
    refresh_token = session.get('refresh_token')
    logged_in = session.get('logged_in')
    if not logged_in or refresh_token is None or refresh_token is "":
        session["reminder"] = 'resources'
        return redirect(url_for('login'))

    # Refresh session and execute
    session[generic.ERR_MSG], session[generic.ERR_CODE] = refresh_session(refresh_token)

    #FORM DATA
    if session[generic.ERR_MSG] is "" and request.form:
        
        for k,v in request.form.items():


        new_name = request.form['name']
        new_uri = request.form['uri']
        new_desc = request.form.get('description', new_desc)
        new_type = request.form.get('type',new_type)

        # Register
        payload = resource_manager.prepare_payload_register(new_uri,new_name,new_scopes,new_desc,new_type)
        print("Final payload -> " + str(payload))
        result = resource_manager.register(session["access_token"],payload)
        session[generic.ERR_MSG], session[generic.ERR_CODE] = generic.get_posible_errors(result)

    return redirect(url_for("profile_management"))

@app.route(g_base_uri+"/profile_management")
def profile_management():
    #err_msg = None
    #old_err_msg = session.get(generic.ERR_MSG, "")
    #err_code = session.get(generic.ERR_CODE, "")
    # Overwrite them to not let the user lock themselfs in an error
    #session[generic.ERR_MSG] = ""
    #session[generic.ERR_CODE] = ""
    
    #refresh_session(session.get('refresh_token',""))

    #token = session.get('access_token')
    #logged_in = session.get('logged_in')
    #if not logged_in or token is None or token is "":
        #session["reminder"] = 'profile_management'
        #return redirect(url_for('login'))

    return render_template("profile_management.html",
    title = config["title"],
    #username = session.get('logged_user'),
    #logged_in = logged_in,
    username = "Angel",
    logged_in = True,
    color_web_background = g_background_color,
    color_web_header = g_header_color,
    logo_alt_name = g_logo_alt,
    logo_image_path = g_logo_image,
    data = {
        "fixed":{"Username":"Angel"},
        "editable":{"lel":"AAAA"}
        }
    )

if __name__ == "__main__":
    app.run(
        debug=config["debug_mode"],
        threaded=config["use_threads"],
        port=config["service_port"],
        host=config["service_host"]
    )