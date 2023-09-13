import streamlit as st
import imaplib
import time
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
import email
from email.header import decode_header
import numpy as np
import random

@st.cache_data
def send_email(email, password, array):
    # 构建邮件主体
    msg = MIMEMultipart()
    msg['From'] = email
    msg['To'] = email  # 收件人邮箱
    msg['Subject'] = fr'{dataset} Number of submissions'
    
    # 邮件正文
    string = ''.join([str(element) for element in array])
    text = MIMEText(string)
    msg.attach(text)
     
    # 发送邮件
    try:
        smtp = smtplib.SMTP('smtp.126.com')
        smtp.login(email, password)
        smtp.sendmail(email, email, msg.as_string())
        smtp.quit()
        print('提交次数发送成功')
    except smtplib.SMTPException as e:
        print('邮件发送失败，错误信息：', e)

@st.cache_data
def read_email(myemail, password):
    try:
        # 连接IMAP服务器
        mail = imaplib.IMAP4_SSL('imap.126.com')
        mail.login(myemail, password)
        mail.select('inbox')  # 选择收件箱
        # 搜索标题
        _, msg_nums = mail.search(None, fr'(SUBJECT "{dataset} Number of submissions")')

        if msg_nums[0]:
            latest_email_id = msg_nums[0].split()[-1]
            _, msg_data = mail.fetch(latest_email_id, '(RFC822)')
            raw_email = msg_data[0][1].decode('utf-8')

            # 解析邮件内容
            email_message = email.message_from_string(raw_email)
            subject, encoding = decode_header(email_message['subject'])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding)

            body = ""
            # 提取邮件正文
            if email_message.is_multipart():
                for part in email_message.walk():
                    content_type = part.get_content_type()
                    if "text/plain" in content_type:
                        body = part.get_payload(decode=True).decode()
                        break

        array = [int(char) for char in body]
        mail.logout()
        return array
    except Exception as e:
        st.error('网络问题，请刷新页面')

def read_email_(myemail, password):
    try:
        # 连接IMAP服务器
        mail = imaplib.IMAP4_SSL('imap.126.com')
        mail.login(myemail, password)
        mail.select('inbox')  # 选择收件箱
        # 搜索标题
        _, msg_nums = mail.search(None, fr'(SUBJECT "{dataset} Number of submissions")')

        if msg_nums[0]:
            latest_email_id = msg_nums[0].split()[-1]
            _, msg_data = mail.fetch(latest_email_id, '(RFC822)')
            raw_email = msg_data[0][1].decode('utf-8')

            # 解析邮件内容
            email_message = email.message_from_string(raw_email)
            subject, encoding = decode_header(email_message['subject'])[0]
            if isinstance(subject, bytes):
                subject = subject.decode(encoding)

            body = ""
            # 提取邮件正文
            if email_message.is_multipart():
                for part in email_message.walk():
                    content_type = part.get_content_type()
                    if "text/plain" in content_type:
                        body = part.get_payload(decode=True).decode()
                        break

        array = [int(char) for char in body]
        mail.logout()
        return array
    except Exception as e:
        st.error('网络问题，请刷新页面')


def instrunction():
    st.subheader("Instructions: ")
    text1 = 'Please watch the short videos (duration 4~7s) of two animated talking heads. \
            You need to choose the talking head (the :blue[left] or the :blue[right]) that moves more naturally in terms of the full :blue[face] and the :blue[lips]. '
    text2 = 'Please :blue[turn on the sound] on your computer while you are watching the videos.'
    st.markdown(text1)
    st.markdown(text2)

def QA(data_face, data_lip, num):
    # 定义问题和选项
    question_1 = "Comparing the two full :blue[faces], which one looks more :blue[realistic]?"
    options_1 = ["Left", "Right"]
    question_2 = "Comparing the :blue[lips] of two faces, which one is more :blue[in sync with audio]?"
    options_2 = ["Left", "Right"]

    # 显示问题并获取用户的答案
    answer_1 = st.radio(label=question_1, options=options_1, key=fr"button{num}.1")
    answer_2 = st.radio(label=question_2, options=options_2, key=fr"button{num}.2")

    # 以1/0数据保存
    ans1 = get_ans(answer_1)
    ans2 = get_ans(answer_2)

    # 保存结果到列表
    data_face[num-1] = ans1
    data_lip[num-1] = ans2

# 将用户的答案转化为1/0
def get_ans(answer_str):
    if "Left" in answer_str:
        return "1"
    elif "Right" in answer_str:
        return "0"
    
@st.cache_data
def play_video(file_name):
    video_bytes = open(file_name, 'rb').read()
    return video_bytes

@st.cache_data
def data_collection(email, password, data_face, data_lip, random_num):
    # 发送内容
    data1 = ''.join(str(x) for x in data_face)
    data2 = ''.join(str(x) for x in data_lip)
    string = "face:" + data1 + "\n" + "lip:" + data2
    localtime = time.strftime(f'%Y-%m-%d %H-%M-%S', time.localtime())
    # 打开文件并指定写模式
    file_name = dataset + ' ' + str(random_num+1) + ' ' + localtime + ".txt"
    file = open(file_name, "w")
    # 将字符串写入文件
    file.write(string)
    # 关闭文件
    file.close()

    # 构建邮件主体
    msg = MIMEMultipart()
    msg['From'] = email
    msg['To'] = email  # 收件人邮箱
    msg['Subject'] = dataset + ' ' + str(random_num+1) + ' ' + localtime

    # 邮件正文
    text = MIMEText(string)
    msg.attach(text)

    # 添加附件
    with open(file_name, 'rb') as f:
        attachment = MIMEApplication(f.read())
        attachment.add_header('Content-Disposition', 'attachment', filename=file_name)
        msg.attach(attachment)

    # 发送邮件
    try:
        smtp = smtplib.SMTP('smtp.126.com')
        smtp.login(email, password)
        smtp.sendmail(email, email, msg.as_string())
        smtp.quit()
        print('数据发送成功')
    except smtplib.SMTPException as e:
        print('邮件发送失败，错误信息：', e)

def page(random_num):
    instrunction()
    file = open(fr"filenames_{dataset}.txt", "r", encoding='utf-8') 
    file_list = file.readlines()
    file.close()

    if "button_clicked" not in st.session_state:
        st.session_state.button_clicked = False
        
    for num in range(15):
        # 显示页面内容
        st.write(f'这是第{num+1+random_num*15}个视频，名称为{file_list[num+random_num*15].rstrip()}')
        st.subheader(fr"Video {num+1}")
        video_bytes = play_video(file_list[num+random_num*15].rstrip())
        st.video(video_bytes)

        st.write("Please answer the following questions, after you watch the video. ")
        QA(data_face, data_lip, num+1)

    if not st.session_state.button_clicked:
        if st.button("Submit results"):
            st.write('It will take about 10 seconds, please be patient and wait.')
            array = read_email_(myemail, password)
            print('第二次：', array)
            array[random_num]+=1
            print('提交：', array)
            send_email(myemail, password, array)
            data_collection(myemail, password, data_face, data_lip, random_num)
            st.session_state.button_clicked = True 

    if st.session_state.button_clicked == True:
        st.cache_data.clear()
        st.success("Successfully submitted the results. Thank you for using it. Now you can exit the system.")


if __name__ == '__main__':
    dataset = 'BIWI' 
    st.set_page_config(page_title="userstudy")
    #st.cache_data.clear() # 初始化
    myemail = st.secrets["my_email"]["email"]  
    password =  st.secrets["my_email"]["password"]  
    
    array = read_email(myemail, password)
    print('第一次：', array)
    if all(element == 3 for element in array):
        array = [0] * 10

    if "data_face" and "data_lip" not in st.session_state:
        # 初始化data变量
        data_face = [1 for x in range(15)]
        data_lip = [1 for x in range(15)]
    else:
        data_face = st.session_state["data_face"]
        data_lip = st.session_state["data_lip"]
    random_num = 0

    if 'random_num' not in st.session_state:
        st.session_state.random_num = random.randint(0, 9)
        if array[st.session_state.random_num] == 3 or array[st.session_state.random_num] > 3 :
            while True:
                st.session_state.random_num = random.randint(0, 9)
                if array[st.session_state.random_num] < 3 :
                    break

    random_num = st.session_state.random_num
    page(random_num)
