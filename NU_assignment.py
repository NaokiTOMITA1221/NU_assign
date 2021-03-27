import requests as rq
from bs4 import BeautifulSoup as bs
import streamlit as st
import re
import pandas as pd


ses = rq.session()
NUID = ''
NUPW = ''

class_name = []

def login(ID,PW):#ログインいした後にホームのHTMLを返す
    url = 'https://auth.nagoya-u.ac.jp/cas/login?service=https%3A%2F%2Fct.nagoya-u.ac.jp%2Fsakai-login-tool%2Fcontainer'
    
    res = ses.get(url)
    soups = list(range(4))
    for i in range(4):
        l = i + 1
        info = {
            'username' : ID,
            'password' : PW,
            'lt' : 'e'+str(l)+'s1',
            '_eventId' : 'submit',
            'submit' : 'ログイン'
            }
        cookie =  res.cookies
        
        resp = ses.post(url ,data = info, cookies = cookie)
        
        soups[i] = resp.text
        
    presoup = list(set(soups))
    
    
    
    return presoup[0]



def classChecker(html):#please put html code：お気に入り登録済みの授業urlをリストで取得
    soup = bs(html,'html.parser')
    
    classObjectList = soup.find_all('a',attrs={'class':'link-container'})
    
    classList = []
    for item in classObjectList:
        if '20' in item.get('title'):
            classList.append(item.get('href'))
            class_name.append(item.get('title'))
    
    
    
    return classList


def homeworkChecker(url_):#課題一覧ページのテキストデータ取得
    ass_res = ses.get(url_)
    cookie = ass_res.cookies
        
    ass_resp = ses.post(url_, cookies = cookie)
    ass_soup = bs(ass_resp.text,'html.parser')
    ass = ass_soup.find('a', attrs={'class':'Mrphs-toolsNav__menuitem--link','title':'課題 - オンラインで課題を投稿したり，提出したり，採点したりするためのツールです．'})
    ass_url = ass.get('href')
    
    cookie = ass_res.cookies
    
    ass__resp = ses.post(ass_url, cookies = cookie)
    ass__soup = bs(ass__resp.text,'html.parser')
    all_ass = ass__soup.find_all('tr')
    del all_ass[0]
    return all_ass
    
  
def all_assignment_checker(ID,PW):
    class_dic = {}
    code = login(ID,PW)
    _list_ = classChecker(code)
    class_ass_list = []
    class_status_list = []
    class_limit_list = []
        

    for i in range(len(_list_)):
        
        check = homeworkChecker(_list_[i])
        

        class_ass_list.append('●「'+class_name[i]+'」')
        class_status_list.append(' ')
        class_limit_list.append(' ')
        count = 0

        for k in check:
            title_ = k.find('a')
            status_ = str(k.find('td',attrs={'headers':"status"}))
            status_ = re.sub('<td headers="status">','',status_)
            status_ = re.sub('\n','',status_)
            status_ = re.sub('</td>','',status_)
            limit_ = str(k.find('span',{'class':"highlight"}))
            limit_ = re.sub('<span class="highlight">','',limit_)
            limit_ = re.sub('\n','',limit_)
            limit_ = re.sub('</span>','',limit_)
            limit_ = limit_
            if '未提出' in status_:
                class_ass_list.append(title_.get('title'))
                class_status_list.append('未提出')
                class_limit_list.append(limit_)
                count = count + 1
        
        if count == 0:
            class_ass_list.append(' ')
            class_status_list.append('未提出課題はありません')
            class_limit_list.append(' ')
                
    class_dic = {
                '課題':class_ass_list,
                '提出状況':class_status_list,
                '提出期限':class_limit_list
                }
    
    return class_dic



st.title('未提出課題チェッカー')
st.write('あなたの未提出課題一覧')
st.write('※「お気に入り」の設定には今期履修する授業のみを登録しておいて下さい')

NUID = st.text_input('put your NUID')
NUPW = st.text_input('put your NUPW')

if NUID != '' and NUPW != '':
    st.write(
        pd.DataFrame(all_assignment_checker(NUID, NUPW))
        )







