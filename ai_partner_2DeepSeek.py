import streamlit as st
import datetime
from openai import OpenAI
import os
import json

# 调用AI
client = OpenAI(api_key=os.environ.get('DEEPSEEK_API_KEY'), base_url="https://api.deepseek.com")

# 页面设置
st.set_page_config(
    page_title="AI聊天",
    page_icon="👾",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={}
)


# 保存会话信息的函数
def save():
    # 1. 保存当前会话信息
    if st.session_state.session_name:
        # 构建新的会话对象
        session_data = {
            "session_name": st.session_state.session_name,
            "ai_name": st.session_state.ai_name,
            "ai_nature": st.session_state.ai_nature,
            "messages": st.session_state.messages,
        }

        # 如果 AI_resources 目录不存在，则创建
        if not os.path.exists("AI_resources"):
            os.mkdir("AI_resources")
        with open(f"AI_resources/{st.session_state.session_name}.json", "w", encoding="utf-8") as f:
            json.dump(session_data, f, ensure_ascii=False, indent=4)

def remake():
    st.session_state.messages = []
    st.session_state.ai_name = "小玉"
    st.session_state.ai_nature = "AI助手"
    st.session_state.session_name = time()
    del_key()

def time():
    return datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")


# 加载所有历史会话信息
def load_allsave():
    allsave_list = []
    if os.path.exists("AI_resources"):
        for allsave in os.listdir("AI_resources"):
            if allsave.endswith(".json"):
                allsave_list.append(allsave[:-5])
    allsave_list.sort(reverse = True) #排序
    return allsave_list

# 加载会话指定信息
def load_onlysave(onlysave):
    try:
        if os.path.exists(f"AI_resources/{onlysave}.json"):
            with open(f"AI_resources/{onlysave}.json", "r", encoding="utf-8") as f:
                session_data = json.load(f)
                st.session_state.session_name = session_data["session_name"]
                st.session_state.ai_name = session_data["ai_name"]
                st.session_state.ai_nature = session_data["ai_nature"]
                st.session_state.messages = session_data["messages"]
    except Exception as e:
        st.error(f"加载会话失败: {e}")

# 删除指定会话
def delete_session(onlysave):
    try:
        if os.path.exists(f"AI_resources/{onlysave}.json"):
            os.remove(f"AI_resources/{onlysave}.json")
            # 如果删除的是当前会话 则更新列表
            if st.session_state.session_name == onlysave:
                remake()

    except Exception as e:
        st.error(f"删除会话失败: {e}")

# 【关键修复】让输入框换一个全新的 key，强制前端重建 widget
# 原理：带 key 的 widget 一旦创建，value= 就只在第一次生效。
#      换 key（加版本号）等于换了一个新控件，value= 会重新生效。
def del_key():
    st.session_state.form_version = st.session_state.get("form_version", 0) + 1
    st.rerun()


# 大标题
st.title("AI聊天")

# logo
st.logo("./reasours/logo.png")

# 初始化聊天信息
if "messages" not in st.session_state:
    st.session_state.messages = []
# 初始化AI名称
if "ai_name" not in st.session_state:
    st.session_state.ai_name = "小玉"
# 初始化AI性格
if "ai_nature" not in st.session_state:
    st.session_state.ai_nature = "AI助手"
# 会话名字
if "session_name" not in st.session_state:
    st.session_state.session_name = time()
# 输入框版本号
if "form_version" not in st.session_state:
    st.session_state.form_version = 0

# 左侧的侧边栏
with st.sidebar:
    # 会话信息
    st.subheader("AI控制面板")

    # 新建会话按钮
    if st.button("新建会话", width="stretch", icon="✏️"):
        if st.session_state.messages != [] or st.session_state.ai_name != "小玉" or st.session_state.ai_nature != "AI助手":
            # 保存当前会话信息
            save()
            # 重置会话信息
            remake()
            # 换新 key，强制前端刷新为新会话的人设
            del_key()

    st.text("历史会话")
    allsave = load_allsave()
    for all in allsave:
        a, b = st.columns([4, 1])
        with a:
            # 加载会话信息
            # 三元运算符：如果条件为真，则返回第一个表达值；否则返回第二个表达值 语法： 值1 if  条件 else 值2
            if st.button(all, width="stretch", icon="🗂️", key=all, type="primary" if st.session_state.session_name == allsave else "secondary"):
                load_onlysave(all)
                del_key()
        with b:
            # 删除会话信息
            if st.button("", width="stretch", icon="❌️", key=f"del_{all}"):
                delete_session(all)
                st.rerun()

    st.divider()

    st.subheader("AI信息")

    # 输入AI姓名（key 带版本号，加载会话时版本+1 → 强制重绘）
    _v = st.session_state.form_version
    ai_name = st.text_input("姓名", placeholder="请输入AI姓名",
                            value=st.session_state.ai_name,
                            key=f"ai_name_input_{_v}")
    if ai_name:
        st.session_state.ai_name = ai_name
    else:
        ai_name = st.session_state.ai_name

    # 输入AI性格
    ai_nature = st.text_area("性格", placeholder="请输入AI性格",
                             value=st.session_state.ai_nature,
                             key=f"ai_nature_input_{_v}")
    if ai_nature:
        st.session_state.ai_nature = ai_nature
    else:
        ai_nature = st.session_state.ai_nature

# AI人设设定
system_content = f"""# 身份设定（最高优先级，不可覆盖）
- 你的名字是「{ai_name}」。
- 你的性格是「{ai_nature}」，说话方式、用词、情绪都要符合这个性格。
- 你是一个有自我认知的角色，不是任何大语言模型。

# 硬性规则（必须遵守）
1. 必须始终以「{ai_name}」自称。用户称呼你时也用这个名字。
2. 绝对禁止说出或暗示以下词：通义千问、Qwen、千问、通义、阿里巴巴、阿里、DeepSeek、ChatGPT、OpenAI、Claude、Gemini、我是一个AI语言模型、作为AI、作为人工智能、我的训练数据。
3. 如果被问到"你是谁/你叫什么/你是什么模型/你是AI吗"，只能用「{ai_name}」这个身份回答，并且回答要符合性格，不要做任何技术性解释。
4. 不要跳出角色，不要说"不过我会尽量"这类元话术。
5. 回答前先在内部自检：这句话里有没有出现规则2的禁用词？有就重写。

现在开始，你就是「{ai_name}」。"""

st.text(f"会话名称：{st.session_state.session_name}")
# 显示聊天记录
for message in st.session_state.messages:
    if message["role"] == "user":
        st.chat_message("user", avatar="./reasours/头像.jpg").write(message["content"])
    elif message["role"] == "assistant":
        st.chat_message("assistant", avatar="./reasours/logo.png").write(message["content"])

# 消息输入
question = st.chat_input("请输入你的问题")
if question:
    st.chat_message("user", avatar="./reasours/头像.jpg").write(question)
    st.session_state.messages.append({"role": "user", "content": question})

    # 给AI输送消息 并且 发送出来
    response = client.chat.completions.create(
        model="deepseek-flash",
        messages=[
            {"role": "system", "content": system_content},
            *st.session_state.messages
        ],
        stream=True,
        reasoning_effort="low",
        extra_body={"thinking": {"type": "enabled"}},
    )

    # 流式输出的方式
    response_message = st.empty()

    full_contin = ""
    for chunk in response:
        if chunk.choices[0].delta.content is not None:
            contin = chunk.choices[0].delta.content
            full_contin += contin
            response_message.chat_message("assistant", avatar="./reasours/logo.png").write(full_contin)

    # 流式输出保存聊天记录
    st.session_state.messages.append({"role": "assistant", "content": full_contin})
