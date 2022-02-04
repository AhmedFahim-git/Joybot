from faulthandler import disable
import streamlit as st
from streamlit_chat import message
import requests
import random
import json

# setting page title and favicon
st.set_page_config(page_title="Rasa chatbot")

def initialize():
    if "generated" not in st.session_state:
        st.session_state["generated"] = []

    if "past" not in st.session_state:
        st.session_state["past"] = []
    
    if "user" not in st.session_state:
        st.session_state['user'] = "user_" + str(random.randint(0, 1000))
    
    if 'button' not in st.session_state:
        st.session_state['button'] = {'pos':[], 'torf':[], 'titles':[]}
        
    if 'out' not in st.session_state:
        st.session_state['out'] = {}

initialize()

def query(payload):
    data = json.dumps(payload)
    response = requests.post(API_URL, data=data)
    return json.loads(response.content.decode("utf-8"))



def write_message(len_gen, len_user):
    len_gen = len_gen-1
    len_user = len_user-1
    
    while (len_user > -1) and (len_gen > -1):
        message(
            st.session_state["generated"][len_gen],
            key=random.randint(0,100000),
            seed = 11,
        )
        len_gen -= 1
        if len_gen+1 in st.session_state.button['pos']:
            message(
                st.session_state["generated"][len_gen],
                key=random.randint(0,100000),
                seed = 11,
            )
            
            ind = st.session_state.button['pos'].index(len_gen+1)
            for j, title in enumerate(st.session_state.button['titles'][ind]):
                st.checkbox(title, st.session_state.button['torf'][ind][j], disabled=True)
            
            
            len_gen -= 1
        
        message(
            st.session_state["past"][len_user],
            is_user=True,
            key=random.randint(0,100000)
        )
        len_user -= 1


st.image('https://omdena.com/wp-content/uploads/2021/08/Australia-Logo-e1637999150350.png',
         caption='Omdena Canberra')
st.title("Omdena Canberra Rasa chatbot")

st.header("Joybot")
st.markdown(
    """
Type your speech in the text box below and press **Enter**.
"""
)

API_URL = "http://20.115.18.160:8080/webhooks/rest/webhook/"


user_input = st.text_input("You: ", "", )


if user_input:
    
    if (len(st.session_state['generated']) not in st.session_state.button['pos']):
        output = query(
            {
                "sender": st.session_state["user"],
                "message": user_input
            }
        )
        
        st.session_state.past.append(user_input)
        st.session_state.generated.append(output[0]["text"])
        st.session_state.out = output
        
    else:
        output = st.session_state.out
    
    
    if 'buttons' in list(output[0].keys()):
        st.session_state.button['pos'].append(len(st.session_state["generated"]))
        placeholder = st.empty()
        
        button_data = {button['title']: button['payload'] for button in output[0]['buttons']}
        
        my_list = [False]*len(button_data.keys())
        
        with placeholder.container():
            message(output[0]["text"], seed=11)
            
            for i, title in enumerate(button_data.keys()):
                selected = st.checkbox(title)
                
                if selected:
                    
                    my_list[i] = True
                    
                    output = query(
                        {
                            "sender": st.session_state["user"],
                            "message": button_data[title]
                        }
                    )
                    st.session_state.out = output
                    st.session_state.generated.append(output[0]["text"])
                    
                    st.session_state.button['torf'].append(my_list)
                    st.session_state.button['titles'].append(list(button_data.keys()))
                
        if any(my_list):
            placeholder.empty()
            write_message(len(st.session_state["generated"]), len(st.session_state['past']))
            
        else:
            message(user_input, is_user=True)
            write_message(len(st.session_state["generated"])-1, len(st.session_state['past'])-1)
            
    else:
        
        write_message(len(st.session_state["generated"]), len(st.session_state['past']))



