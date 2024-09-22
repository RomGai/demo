import copy
from openai import OpenAI
import pipeline_actions as act
import pipeline_detection as det
import pipeline_window_control as wc
import pipeline_depth as dep
import re
import time

# 延迟五秒开始程序，需要在5s内打开游戏界面。使用win10系统默认UI布局，显示器分辨率为1920x1080，使MC为窗口模式并放大窗口。MC不能是全屏模式，会造成截图冲突。
# 游戏内设置：视场FOV=90，鼠标灵敏度74%
# 暂时没有写暂停游戏的函数，因为有些时候会手动开暂停，怕混淆。
time.sleep(5)

# 初始化
max_step=10
client = OpenAI(api_key="", base_url="https://vip.apiyi.com/v1") #需要使用自己的API，因为国内无法直连，可以使用国内中转服务商:https://www.apiyi.com/token
log_path="log_temp"
game_window_name="Minecraft 1.11.2"
last_decision="None"
last_ls="None"
x_aim=962
y_aim=534

for step in range(0,max_step):
    print("step"+str(step))
    screenshot_path=log_path+"/"+game_window_name+"_screenshot_"+str(step)+".png"

    # 截屏
    wc.capture_window(game_window_name,output_folder=log_path,step=step)

    # 调用api根据截屏计算必要视觉信息，需要自己注册一个账户获取api，这是免费的:https://app.roboflow.com/
    time.sleep(30) #疑似限流，所以每次访问之前sleep一段时间，但更可能是国内直连不稳定。另外，如果这里提示访问被关闭，需要重新手动运行一下。同时也得手动替换last_decision与last_ls。
    x_log,y_log,width,height=det.detect_trunk_with_wid_hi(image_path=screenshot_path,output_folder=log_path,x_aim=x_aim,y_aim=y_aim)

    # 贴的很近的时候可能检测不到树，所以直接挖掘，这部分逻辑可以进一步优化
    if(x_log==None):
        act.mine(5)
        last_decision="mine(5)"
        continue

    x_log=int(x_log)
    y_log=int(y_log)

    # 使用box宽度评估原木距离
    ls=dep.check_depth_by_box(width)

    target_position = (x_log, y_log)
    crosshair_position = (x_aim, y_aim)
    print(ls)

    x_diff=x_log-x_aim
    y_diff=y_log-y_aim
    x_diff_abs=abs(x_aim-x_log)
    y_diff_abs=abs(y_aim-y_log)

    # 定义行为列表及其描述。便于测试阶段调整，直接用的中文。
    behavior_list = {
        "move_forward(duration)": "持续向前移动一段时间，若目标距离我大于5米，则duration必须为1.0；若距离我接近5米，则duration必须为0.6。若距离我小于5米，则duration必须为0.3。",
        "mine(duration)": "靠近原木后进行伐木动作。duration必须为5。",
        "turn_and_move_forward(duration, x, y)": "先转向目标，然后向前移动，x 和 y 是鼠标从准心位置到目标位置的像素偏移量，分别对应水平方向和垂直方向，有正负的区别。若目标距离我大于5米，则duration必须为1.0；若距离我接近5米，则duration必须为0.6。若距离我小于5米，则duration必须为0.3。",
        "turn(x, y)": "转动视角，x 和 y 是准心到目标的像素偏移量，分别对应水平方向和垂直方向，有正负的区别。"
    }

    # behavior_list = {
    #     "move_forward(duration)": "持续向前移动一段时间，若目标距离我大于5米，则duration必须为1.3；若距离我接近5米，则duration必须为0.8。若距离我小于5米，则duration必须为0.3。",
    #     "mine(duration)": "靠近原木后进行伐木动作。duration必须为5。",
    #     "turn_and_move_forward(duration, x, y)": "先转向目标，然后向前移动，x 和 y 是鼠标从准心位置到目标位置的像素距离。若目标距离我大于5米，则duration必须为1.3；若距离我接近5米，则duration必须为0.8。若距离我小于5米，则duration必须为0.3。",
    # }

    # 将行为描述转换为字符串
    behavior_description = "\n".join([f"- {key}: {value}" for key, value in behavior_list.items()])

    # 将这些变量转换为一个描述性文本并封装以便输入。
    input_text = f"""
    我正在《我的世界》游戏中伐木，我的目标是原木。原木的位置在屏幕的 {target_position}，而准心的位置在 {crosshair_position}。当前步骤下我检测到的原木的位置在x方向上偏离准心{x_diff}像素，在y方向上偏离准心{y_diff}像素。我的挖掘可触及距离为5米，当前原木距离我{ls}5米。
    
    我可以执行的动作被定义为了函数，其形式与具体的描述如下：
    {behavior_description}
    
    你的上一次行动决策是{last_decision}。当且仅当你上一次行动决策是turn_and_move_forward(duration, x, y)或move_forward(duration)时，你必须遵守行为约束A，否则你无需遵守行为约束A。其中，duration、x与y是数字的形式。 
    在无需遵守行为约束A的前提下，当且仅当原木距离我大于或接近5米时，你必须遵守行为约束B。
    在无需遵守行为约束A的前提下，当且仅当原木距离我小于5米时，你必须遵守条行为约束C。
    请注意，你只能执行一条行为约束。
    行为约束A：忽视掉当前原木距离与我的关系。若{x_diff_abs}大于250在数学上是正确的，你必须执行mine(5)这一行为。若{y_diff_abs}大于250在数学上是正确的，你必须执行mine(5)这一行为。若{x_diff_abs}与{y_diff_abs}同时小于等于250在数学上是正确的，当且仅当原木距离我大于或接近5米时你必须遵守行为约束B，当且仅当原木距离我小于5米时你必须遵守行为约束C。
    行为约束B：如果准心与原木在x与y方向差异均小于30像素值时，请执行move_forward(duration)这一行为。否则，你需要使用turn_and_move_forward(duration, x, y)这一行为使准心与原木中心对齐并移动游戏角色。此外，由于我距离目标较远，此时mine(duration)与turn(x, y)这两个行为是被禁止使用的。
    行为约束C：如果准心与原木在x与y方向差异均小于30像素值时，请执行mine(5)这一行为。否则，你需要先使用turn这一行为使准心与原木中心对齐，再执行mine(5)。此外，由于我已经距离目标足够近，此时turn_and_move_forward(duration, x, y)以及move_forward(duration)这两个行为是被禁止使用的。
    
    首先，请你判断你应该执行哪一条行为约束。请帮我决定下一步应该执行哪个动作，并根据现有条件计算传入的参数值？你必须只输出行为约束编号、动作函数及其参数值，例如“C, mine(5)”，而不能输出其它任何内容。请注意，当你认为需要向前移动时，你需要牢记此时原木距离我{ls}5米，这对你在相关的动作函数中合适的参数非常重要。
    """

    print(input_text)

    # 这里目前还没有用到多模态的模型，要改的话直接改成多模态模型增加图像输入即可。
    # 将封装好的文本发送给gpt-4o
    completion = client.chat.completions.create(
        model="gpt-4o",
        stream=False,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": input_text}
        ]
    )
    # # 将封装好的文本发送给gpt-3.5-turbo
    # completion = client.chat.completions.create(
    #     model="gpt-3.5-turbo",
    #     stream=False,
    #     messages=[
    #         {"role": "system", "content": "You are a helpful assistant."},
    #         {"role": "user", "content": input_text}
    #     ]
    # )

    decision = completion.choices[0].message.content
    constraint, decision =decision.split(", ", 1)
    decision = decision.strip()
    constraint = constraint.strip()
    print(f"Agent的行为约束: {constraint}")
    print(f"Agent的决策: {decision}")
    last_decision=copy.deepcopy(decision)
    last_ls=copy.deepcopy(ls)
    last_target_position=copy.deepcopy(target_position)


    # 提取函数名及其参数
    match = re.match(r"(\w+)\((.*)\)", decision)
    if match:
        function_name = match.group(1)  # 获取行为函数名，形如 "turn"
        parameters = match.group(2)  # 获取参数，形如 "50, 100"

        # 参数to数字
        param_list = [float(x.strip()) for x in parameters.split(",")]

        # 调用函数
        if function_name == "move_forward":
            act.move_forward(*param_list)  # 执行 move_forward(duration)
        elif function_name == "mine":
            act.mine(*param_list)  # 执行 mine(duration)
        elif function_name == "turn":
            act.turn(*param_list)  # 执行 turn(x, y)
        elif function_name == "turn_and_move_forward":
            act.turn_and_move_forward(*param_list)  # 执行 turn_and_move_forward(duration, x, y)
