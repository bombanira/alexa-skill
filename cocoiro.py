"""6/16
This sample demonstrates a simple skill built with the Amazon Alexa Skills Kit.
The Intent Schema, Custom Slots, and Sample Utterances for this skill, as well
as testing instructions are located at http://amzn.to/1LzFrj6

For additional samples, visit the Alexa Skills Kit Getting Started guide at
http://amzn.to/1LGWsLG
"""
# json reference is here https://developer.amazon.com/ja/docs/custom-skills/request-and-response-json-reference.html

from __future__ import print_function
from scrape import get_new_topics_article, get_ranking_article, get_new_topics_title, get_ranking_title
import json
import time
import requests


# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        "playBehavior": "REPLACE_ALL",
        'card': {
            'type': 'Simple',
            'title': title,
            'content': output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


# --------------- Functions that control the skill's behavior ------------------
## -------------- Functions that start or end alexa skill ----------------------
def get_welcome_response():
    print("##### Into get_welcome_response #####")
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """
    session_attributes = {'state': 'welcome_end'}
    card_title = "ここいろスキルへようこそ"
    speech_output = "ここいろスキルへようこそ。新着記事もしくは人気記事を選んでください。" 
    reprompt_text = "新着記事もしくは人気記事を選んでください。"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def handle_session_end_request():
    print("##### Into handle_session_end_request #####")
    speech_output = "ここいろスキルを終了します。" 
    card_title = speech_output
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))
## --------------- start or end alexa skill end --------------------------------


def title_read_session(intent, session):
    print("##### Into title_read_session #####")
    card_title = None
    should_end_session = False
    titles = []
    success_match = False
    if intent.get('slots', {}) and intent['slots'].get('ArticleKind', {}):
        success_match = intent['slots']['ArticleKind']['resolutions']\
        ['resolutionsPerAuthority'][0]['status']['code'] == "ER_SUCCESS_MATCH"
    
    print(intent['slots']['ArticleKind'])
    if success_match is False and session['attributes']['state'] == 'title_end':
        return article_read_session(intent, session)
    if success_match is False and session['attributes']['state'] == 'read_end':
        return after_read_unexpected(session['attributes']['ArticleKind'])
    if ('ArticleKind' in intent['slots']) and success_match:
        article_kind = intent['slots']['ArticleKind']['resolutions']\
        ['resolutionsPerAuthority'][0]['values'][0]['value']['id']
    
        if article_kind == 'popular_article':
            article_kind_ja = '人気記事'
            ranking_titles = get_ranking_title(5)
            for i, title in enumerate(ranking_titles):
                titles.append(str(i + 1) + '。' + title)
        elif article_kind == 'new_article':
            article_kind_ja = '新着記事'
            new_topics_title = get_new_topics_title(5)
            for i, title in enumerate(new_topics_title):
                titles.append(str(i + 1) + '。' + title)
                
        speech_output = "ここいろの{}のタイトルを読み上げます。読んでほしい記事があったら"\
                    "記事の番号をおっしゃってください。{}".format(article_kind_ja, ''.join(titles))
            
        reprompt_text = "ここいろの{}のタイトルを読み上げます。読んでほしい記事があったら"\
                    "記事の番号をおっしゃってください。{}".format(article_kind_ja, ''.join(titles))
        session_attributes = {
            'state' : 'title_end',
            'ArticleKind': article_kind
        }
    else:
        speech_output = "新着記事もしくは人気記事から選んでください。"
        reprompt_text = "新着記事もしくは人気記事から選んでください。"
        session_attributes = {
            'state' : 'welcome_end'
        }
        session_attributes = None
    
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

# def article_read_session(event):
def article_read_session(intent, session):
    print("##### Into article_read_session #####")
    card_title = None
    session_attributes = {}
    should_end_session = False
    
    if intent.get('slots', {}) and intent['slots'].get('ArticleNumber', {}):
        success_match = intent['slots']['ArticleNumber']['resolutions']\
        ['resolutionsPerAuthority'][0]['status']['code'] == "ER_SUCCESS_MATCH"
    else:
        success_match = False
    print(session['attributes']['state'])
    if success_match is False and session['attributes']['state'] == 'read_end':
        return after_read_unexpected(session['attributes']['ArticleKind'])
    # 正常時
    if session.get('attributes', {}).get('ArticleKind', {}) and success_match: 
        article_number = int(intent['slots']['ArticleNumber']['resolutions']\
        ['resolutionsPerAuthority'][0]['values'][0]['value']['id'])
        article_kind = session['attributes']['ArticleKind']

        if article_kind == "popular_article":
            speech_output = "{}番目の人気記事を読み上げます。".format(article_number)
            title, sentences = get_ranking_article(article_number - 1)
            speech_output += max_text_adjust(title, sentences)
    
        elif article_kind == "new_article":
            speech_output = "{}番目の新着記事を読み上げます。".format(article_number)
            title, sentences = get_new_topics_article(article_number - 1)
            speech_output = max_text_adjust(title, sentences)
            
        reprompt_text = None    
        session_attributes = {
            'ArticleKind': session['attributes']['ArticleKind'],
            'state' : 'read_end'
        }
    # ここいろを開いた後、人気記事か新着記事の指定なく、すぐに番号を行った場合のエラー処理
    elif session.get('attributes', {}).get('ArticleKind', {}) == {}:
        speech_output = reprompt_text = "人気記事か新着記事のどちらかを選んでください"
        session_attributes = {'state': 'welcome_end' }
    # 数字以外のものを行った場合
    else:
        speech_output = "1から5の数字をおっしゃってください。"
        reprompt_text = "1から5の数字をおっしゃってください。"
        session_attributes = {
            'ArticleKind': session['attributes']['ArticleKind'],
            'state' : 'title_end'
        }
        
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))

def max_text_adjust(title, sentences):
    print("##### Into max_text_adjust #####")
    max_len = 2000
    rest_on_web = "続きはwebで"
    speech_output = 'タイトル。' + title + '。'
    for sentence in sentences:
        if len(speech_output + sentence + "。") >= max_len - len(rest_on_web):
            speech_output += rest_on_web + '。'
            break
        else:
            speech_output += sentence + '。'
        # if len(speech_output + sentence + "。") < max_len:
        #     speech_output += sentence + '。'
    print(len(speech_output))
    return speech_output

def progressive_response(event, message):
    print("##### Into progressive_response #####")
    endpoint = event['context']['System'].get('apiEndpoint')
    access_token =  event['context']['System'].get('apiAccessToken')
    request_id = event['request']['requestId']

    # エンドポイント情報が無い時(シミュレーター等)
    if not endpoint or not access_token:
        print('No Endpoint')
        return

    response = {
        "header": {
            "requestId": request_id
        },
        "directive": {
            "type": "VoicePlayer.Speak",
            "speech": message
        },
    }

    res = requests.post(
        endpoint + '/v1/directives',
        headers={
            'Authorization': 'Bearer {}'.format(access_token),
            'Content-Type': 'application/json'
        },
        data=json.dumps(response))

    if res.status_code != 200 and res.status_code != 204:
        print('Progressive Response Failed (status_code={})'
              .format(res.status_code))
# error func 
def after_read_unexpected(article_kind=None):
    card_title = "人気記事もしくは新着記事、または1~5の番号をおっしゃってください"
    speech_output = "人気記事もしくは新着記事、または1~5の番号をおっしゃってください"
    reprompt_text =  "人気記事もしくは新着記事、または1~5の番号をおっしゃってください"
    should_end_session = False
    session_attributes = {'state': 'read_end'}
    if article_kind is not None:
        session_attributes = {'state': 'read_end', 'ArticleKind' : article_kind}
    
    return build_response(session_attributes, 
    build_speechlet_response(card_title, speech_output, reprompt_text, should_end_session))
              
# --------------- Events ------------------

def on_session_started(session_started_request, session):
    print("##### Into on_session_started #####")
    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    print("##### Into on_launch #####")
    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(event):
    """ Called when the user specifies an intent for this skill """
    print("##### Into on_intent #####")
    intent_request = event['request']
    intent = intent_request['intent']
    intent_name = event['request']['intent']['name']
    session = event['session']
    print("intent = {0}".format(intent_name))
    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    # Dispatch to your skill's intent handlers
    if intent_name == "TitleReadIntent":
        return title_read_session(intent, session)
    elif intent_name == 'ArticleNumberIntent':
#        return article_read_session(event)
        return article_read_session(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    # elif event['session']['attributes']['state'] == 'welcome_end':
    #     return title_read_session(intent, session)
    # elif event['session']['attributes']['state'] == 'title_end':
    #     return article_read_session(event)
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("##### Into on_session_ended #####")
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    speech_output = "on_session_ended"
    card_title = "on_session_ended"
    reprompt_text = "on_session_ended"
    should_end_session = False
    
    session_attributes = {}
    build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))
    # add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event == {0}".format(event))
    print("context == {0}".format(context))
    
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])
    print("##### Into lambda_handler #####")

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")
    result = None
    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])
    if event['request']['type'] == "LaunchRequest":
        result = on_launch(event['request'], event['session'])
    #   return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        result = on_intent(event)
    #   return onintent(event)
    # elif event['request']['type'] == "SessionEndedRequest":
    else:
        result = on_session_ended(event['request'], event['session'])
    #   return on_session_ended(event['request'], event['session'])
    print("send alexa data is : {0}".format(result))
    if result == None:
        print("   ##### error raise #####")
    return result 

