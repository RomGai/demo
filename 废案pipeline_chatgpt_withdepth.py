import copy
from openai import OpenAI
import pipeline_actions as act
import pipeline_detection as det
import pipeline_window_control as wc
import pipeline_depth as dep
import re
import time

# 延迟五秒开始程序，需要在5s内打开游戏界面
time.sleep(5)

#初始化
max_step=5
client = OpenAI(api_key="", base_url="https://vip.apiyi.com/v1")
log_path="log_temp"
game_window_name="Minecraft 1.11.2"
last_decision=None
last_ls=None
x_aim=962
y_aim=534

for step in range(0,max_step):
    screenshot_path=log_path+"/"+game_window_name+"_screenshot_"+str(step)+".png"

    # 截屏
    wc.capture_window(game_window_name,output_folder=log_path,step=step)

    # 根据截屏计算必要视觉信息
    time.sleep(30)
    x_log,y_log=det.detect_trunk(image_path=screenshot_path,output_folder=log_path,x_aim=x_aim,y_aim=y_aim)
    x_log=int(x_log)
    y_log=int(y_log)
    # 得到深度图像
    # 本意想直接用DepthAnything，但用huggingface镜像下载不了他们的模型，因此用MiDaS替代
    dep.get_depth_map(image_path=screenshot_path,output_folder=log_path)

    ls=dep.check_depth(image_path=screenshot_path,log_folder=log_path,x=x_log,y=y_log)

    # win10系统默认UI布局，显示器分辨率为1920x1080，使MC为窗口模式并放大窗口。MC不能是全屏模式，会造成截图冲突。
    target_position = (x_log, y_log)
    crosshair_position = (x_aim, y_aim)
    print(ls)


    # 定义行为列表及其描述
    behavior_list = {
        "move_forward(duration)": "持续向前移动一段时间，若目标距离我大于5米，则duration必须为1.3；若距离我接近5米，则duration必须为0.8。若距离我小于5米，则duration必须为0.2。",
        "mine()": "靠近原木后进行伐木动作。",
        "turn_and_move_forward(duration, x, y)": "先转向目标，然后向前移动，x 和 y 是鼠标从准心位置到目标位置的像素距离。若目标距离我大于5米，则duration必须为1.3；若距离我接近5米，则duration必须为0.8。若距离我小于5米，则duration必须为0.2。",
        "turn(x, y)": "转动视角，x 和 y 是准心到目标的像素距离，分别对应水平方向和垂直方向的像素偏移量。"
    }

    # behavior_list = {
    #     "move_forward(duration)": "持续向前移动一段时间，若目标距离我大于5米，则duration必须为1.3；若距离我接近5米，则duration必须为0.8。若距离我小于5米，则duration必须为0.1。",
    #     "mine(duration)": "靠近原木后进行伐木动作。duration必须为5。",
    #     "turn_and_move_forward(duration, x, y)": "先转向目标，然后向前移动，x 和 y 是鼠标从准心位置到目标位置的像素距离。若目标距离我大于5米，则duration必须为1.3；若距离我接近5米，则duration必须为0.8。若距离我小于5米，则duration必须为0.1。",
    # }

    # 将行为描述转换为字符串
    behavior_description = "\n".join([f"- {key}: {value}" for key, value in behavior_list.items()])

    if(step==0):
        # 将这些变量转换为一个描述性文本
        input_text = f"""
        我正在《我的世界》游戏中伐木，我的目标是原木。原木的位置在屏幕的 {target_position}，而准心的位置在 {crosshair_position}。我的挖掘可触及距离为5米，原木距离我{ls}5米，我的移动速度为4.317米/秒。
        
        我可以执行的动作被定义为了函数，其形式与具体的描述如下：
        {behavior_description}
        
        请帮我决定下一步应该执行哪个动作，并根据现有条件计算传入的参数值？你必须只输出动作函数及其参数值，例如“turn(50,100)”，而不能输出其它任何内容。
        """
    else:
        input_text = f"""
        我正在《我的世界》游戏中伐木，我的目标是原木。原木的位置在屏幕的 {target_position}，而准心的位置在 {crosshair_position}。我的挖掘可触及距离为5米，目标距离我{ls}5米，我的移动速度为4.317米/秒。
    
        我可以执行的动作被定义为了函数，其形式与具体的描述如下：
        {behavior_description}
        
        你的上一步决策是{last_decision}，上一步目标距离我{last_ls}5米。
    
        请帮我决定下一步应该执行哪个动作，并根据现有条件计算传入的参数值？你必须只输出动作函数及其参数值，例如“turn(50,100)”，而不能输出其它任何内容。
        """


    # 将封装好的文本发送给 ChatGPT
    completion = client.chat.completions.create(
        model="gpt-3.5-turbo",
        stream=False,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": input_text}
        ]
    )


    decision = completion.choices[0].message.content
    print(f"ChatGPT 的决策输出: {decision}")
    last_decision=copy.deepcopy(decision)
    last_ls=copy.deepcopy(ls)


    # 使用正则表达式提取函数名称和参数
    match = re.match(r"(\w+)\((.*)\)", decision)
    if match:
        function_name = match.group(1)  # 获取函数名，例如 "turn"
        parameters = match.group(2)  # 获取参数，例如 "50, 100"

        # 将参数转换为数字
        param_list = [float(x.strip()) for x in parameters.split(",")]

        # 根据函数名动态调用对应的函数
        if function_name == "move_forward":
            act.move_forward(*param_list)  # 执行 move_forward(duration)
        elif function_name == "mine":
            act.mine(*param_list)  # 执行 mine(duration)
        elif function_name == "turn":
            act.turn(*param_list)  # 执行 turn(x, y)
        elif function_name == "turn_and_move_forward":
            act.turn_and_move_forward(*param_list)  # 执行 turn_and_move_forward(duration, x, y)
