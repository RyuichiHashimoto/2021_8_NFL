import requests
import json
import datetime
import os
from numpy import random

def send_massage(token,massage):
    url = 'https://slack.com/api/chat.postMessage'
    headers = {"Authorization": "Bearer " + token}
    channel = "notification"  # ユーザーを指定するとDMが送られる
    params = {
        'channel': channel,
        'text': massage,
        'as_user': True
    }
    return requests.post(url, headers=headers, data=params)

def send_massage_with_attenstion(token,massage,user_id):
    _massage = "<@"+user_id + ">\r\n" +massage;
    send_massage(token,_massage);


def notify_exec_with_date_and_attenstion(token, exec_function,setting_file,user_id):
    function_number = random.randint(1000, 9999);

    ### starting_process
    start_time = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
    starting_massage = "[ notification from *"+os.uname()[1]+"* ]\r\n";
    starting_massage = starting_massage + "  # function number: " + str(function_number) +"\r\n"
    starting_massage = starting_massage + "  start the function *" + exec_function.__name__ + "*\r\n";
    starting_massage = starting_massage + "   - start: " + start_time+ "\r\n"
    send_massage(token, starting_massage);

    try:
        exec_function(setting_file);
        finish_time = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
        finished_massage = "[ notification from *"+os.uname()[1]+"* ]\r\n";
        finished_massage = finished_massage + "  # function number: " + str(function_number) +"\r\n"
        finished_massage = finished_massage +  "  finish the function *" + exec_function.__name__ + "*\r\n";
        finished_massage = finished_massage + "   - start: " + start_time + "\r\n"
        finished_massage = finished_massage + "   - finish: " + finish_time+ "\r\n"

    except KeyboardInterrupt as es:
        import traceback
        finish_time = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
        finished_massage = "[ notification from *" + os.uname()[1] + "* ]\r\n";
        finished_massage = finished_massage + "  # function number: " + str(function_number) +"\r\n"
        finished_massage = finished_massage + "  An expected error has occurred *" + exec_function.__name__ + "*\r\n";
        finished_massage = finished_massage +  "\r\n>" + traceback.format_exc().replace("\r\n","\n").replace("\n","\n>") +"\r\n\r\n";

        finished_massage = finished_massage + "  finish the function *" + exec_function.__name__ + "*\r\n";
        finished_massage = finished_massage + "   - start: " + start_time + "\r\n"
        finished_massage = finished_massage + "   - finish: " + finish_time + "\r\n"
        traceback.print_exc()

    except Exception as e:
        import traceback
        finish_time = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
        finished_massage = "[ notification from *" + os.uname()[1] + "* ]\r\n";
        finished_massage = finished_massage + "  # function number: " + str(function_number) +"\r\n"
        finished_massage = finished_massage + "  An expected error has occurred *" + exec_function.__name__ + "*\r\n";
        finished_massage = finished_massage +  "\r\n>" + traceback.format_exc().replace("\r\n","\n").replace("\n","\n>") +"\r\n\r\n";

        finished_massage = finished_massage + "  finish the function *" + exec_function.__name__ + "*\r\n";
        finished_massage = finished_massage + "   - start: " + start_time + "\r\n"
        finished_massage = finished_massage + "   - finish: " + finish_time + "\r\n"
        traceback.print_exc()

    send_massage_with_attenstion(token, finished_massage,user_id);


def post_file_with_comments(token,comments,file):
    url = 'https://slack.com/api/files.upload'
    headers = {"Authorization": "Bearer " + token}
    channel = "notification"  # ユーザーを指定するとDMが送られる
    files = {'file': open(file, 'rb')}

    params = {
        'channels': channel,
        'initial_comment':comments,
        'title':"log"
    }
    requests.post(url, headers=headers, params=params,files = files)





if __name__ == "__main__":
    
    #credensialInfo_data_path = "../../setting/credential_information.json"

    #credential_info = json.load(open(credensialInfo_data_path, "r"));
    #token = "credential_info["Slack_API_token"]";
    token = "xoxb-1743094101558-1743160852854-cMMECMu5S8R1qmuDIJ3j56U5"
    #user_id = credential_info["MY_USER_ID"];
    
    b = send_massage(token=token,massage="test")

    print(b.text)
    posted_file = "./testfile.py";

    #send_massage_with_attenstion(token,"テストメッセージ",user_id)


