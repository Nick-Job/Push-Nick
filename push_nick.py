import requests
import json
import configparser
from datetime import datetime

# 读取配置文件
config = configparser.ConfigParser()
config.read('config.txt')

# 获取 WxPusher 配置
app_token = config.get('WxPusher', 'app_token')
user_id = config.get('WxPusher', 'user_id')

# 获取天气配置
weather_api_key = config.get('Weather', 'api_key')
city = config.get('Weather', 'CITY')
lat = config.get('Weather', 'LAT')
lon = config.get('Weather', 'LON')

# 获取纪念日配置
love_day = config.get('Anniversary', 'love_day')

# 获取当前日期和星期几（中文）
today = datetime.now().strftime("%Y年%m月%d日")
weekday = datetime.now().strftime("%A")  # 英文星期几
weekday_cn = {
    "Monday": "星期一",
    "Tuesday": "星期二",
    "Wednesday": "星期三",
    "Thursday": "星期四",
    "Friday": "星期五",
    "Saturday": "星期六",
    "Sunday": "星期日"
}.get(weekday, "未知")

# 计算在一起的天数
love_date = datetime.strptime(love_day, "%Y-%m-%d")
days_together = (datetime.now() - love_date).days

# 获取天气数据
def get_weather():
    # 获取 3 天天气预报
    weather_url = f"https://devapi.qweather.com/v7/weather/3d?location={lon},{lat}&key={weather_api_key}"
    weather_response = requests.get(weather_url)
    print("天气 API 响应状态码:", weather_response.status_code)  # 打印状态码
    print("天气 API 响应内容:", weather_response.text)  # 打印响应内容
    weather_data = weather_response.json()

    # 获取空气质量
    air_url = f"https://devapi.qweather.com/v7/air/now?location={lon},{lat}&key={weather_api_key}"
    air_response = requests.get(air_url)
    print("空气质量 API 响应状态码:", air_response.status_code)  # 打印状态码
    print("空气质量 API 响应内容:", air_response.text)  # 打印响应内容
    air_data = air_response.json()

    # 获取天气预警
    warning_url = f"https://devapi.qweather.com/v7/warning/now?location={lon},{lat}&key={weather_api_key}"
    warning_response = requests.get(warning_url)
    print("天气预警 API 响应状态码:", warning_response.status_code)  # 打印状态码
    print("天气预警 API 响应内容:", warning_response.text)  # 打印响应内容
    warning_data = warning_response.json()

    # 获取太阳和月亮信息
    astro_url = f"https://devapi.qweather.com/v7/astronomy/sunmoon?location={lon},{lat}&date={datetime.now().strftime('%Y%m%d')}&key={weather_api_key}"
    astro_response = requests.get(astro_url)
    print("太阳和月亮 API 响应状态码:", astro_response.status_code)  # 打印状态码
    print("太阳和月亮 API 响应内容:", astro_response.text)  # 打印响应内容
    astro_data = astro_response.json()

    if weather_data.get('code') == '200' and air_data.get('code') == '200' and astro_data.get('code') == '200':
        today_weather = weather_data['daily'][0]
        today_air = air_data['now']
        today_warning = warning_data.get('warning', [])
        today_astro = astro_data

        # 格式化太阳和月亮时间（去掉日期部分）
        sunrise = today_astro['sunrise'].split('T')[-1][:5]  # 提取时间部分，去掉秒
        sunset = today_astro['sunset'].split('T')[-1][:5]
        moonrise = today_astro['moonrise'].split('T')[-1][:5]
        moonset = today_astro['moonset'].split('T')[-1][:5]

        return {
            'city': city,
            'day': today_weather['textDay'],
            'night': today_weather['textNight'],
            'temp_max': today_weather['tempMax'],
            'temp_min': today_weather['tempMin'],
            'air': today_air['category'],  # 空气质量
            'aqi': today_air['aqi'],  # AQI 指数
            'warning': today_warning,  # 天气预警
            'sunrise': sunrise,  # 日出时间
            'sunset': sunset,  # 日落时间
            'moonrise': moonrise,  # 月出时间
            'moonset': moonset,  # 月落时间
        }
    else:
        return None

# 获取每日一言（从在线 API 获取）
def get_daily_quote():
    try:
        url = "https://v1.hitokoto.cn/"  # 一言 API
        response = requests.get(url)
        print("每日一言 API 响应状态码:", response.status_code)  # 打印状态码
        print("每日一言 API 响应内容:", response.text)  # 打印响应内容
        data = response.json()
        return f"{data['hitokoto']} ——{data['from']}"
    except Exception as e:
        print("获取每日一言失败：", e)
        return "今日无名言"

# 获取土味情话（从在线 API 获取）
def get_love_quote():
    try:
        url = "https://api.lovelive.tools/api/SweetNothings"  # 土味情话 API
        response = requests.get(url)
        print("土味情话 API 响应状态码:", response.status_code)  # 打印状态码
        print("土味情话 API 响应内容:", response.text)  # 打印响应内容
        return response.text
    except Exception as e:
        print("获取土味情话失败：", e)
        return "今天的土味情话被风吹走了~"

# 添加周末提醒功能
def get_weekend_reminder():
    today = datetime.now()
    weekday = today.weekday()  # 0-6 分别表示周一到周日
    if weekday < 5:  # 0-4 表示周一到周五
        delta = 5 - weekday
        return f"距离周末还有{delta}天"
    elif weekday == 5:  # 5 表示周六
        return "今天是周六，好好休息！"
    else:  # 6 表示周日
        return "今天是周日，明天又要上班啦~"

# 推送消息
def send_wxpusher_message(content):
    url = "https://wxpusher.zjiecode.com/api/send/message"
    headers = {"Content-Type": "application/json"}
    data = {
        "appToken": app_token,
        "content": content,
        "contentType": 2,  # 设置为 2，表示 HTML 格式
        "uids": [user_id]
    }
    response = requests.post(url, headers=headers, data=json.dumps(data))
    print("WxPusher API 响应状态码:", response.status_code)  # 打印状态码
    print("WxPusher API 响应内容:", response.text)  # 打印响应内容
    return response.json()

# 主函数
def main():
    # 获取天气
    weather = get_weather()
    if not weather:
        print("获取天气失败")
        return

    # 获取每日一言
    quote = get_daily_quote()

    # 获取土味情话
    love_quote = get_love_quote()

    # 获取周末提醒
    weekend_reminder = get_weekend_reminder()

    # 生成天气预警信息
    warning_info = "无预警信息"
    if weather['warning']:
        warning_info = "\n".join([f"{w['title']}: {w['text']}" for w in weather['warning']])

    # 生成推送内容
    content = f"""
    <div style="
        background: linear-gradient(to right, #86efac, #3b82f6, #9333ea);
        border-radius: 12px;
        padding: 2px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        transition: box-shadow 0.3s ease;
        width: 90%;  /* 宽度设置为屏幕宽度的90%，适配手机 */
        max-width: 400px;  /* 最大宽度限制，避免在大屏幕上过宽 */
        margin: 0 auto;  /* 居中显示 */
    ">
        <div style="
            background: #ffffff;
            border-radius: 10px;
            padding: 12px;  /* 适当减少内边距，适配手机 */
        ">
            <!-- 日期 -->
            <p style="font-size: 12px; color: #666666; margin: 0 0 8px 0;">
                {today}
            </p>

            <!-- 标题 -->
            <h3 style="font-size: 16px; font-weight: bold; color: #333333; margin: 0 0 8px 0;">
                每日推送 | {weekday_cn}
            </h3>

            <!-- 天气信息 -->
            <div style="margin-bottom: 12px;">
                <p style="font-size: 14px; color: #666666; margin: 0 0 4px 0;">
                    <b>城市</b>: {weather['city']}
                </p>
                <p style="font-size: 14px; color: #666666; margin: 0 0 4px 0;">
                    <b>今日天气预报</b>:
                </p>
                <p style="font-size: 14px; color: #666666; margin: 0 0 4px 0;">
                    白天：{weather['day']}，夜间：{weather['night']}
                </p>
                <p style="font-size: 14px; color: #666666; margin: 0 0 4px 0;">
                    <b>温度</b>: {weather['temp_min']}°C ~ {weather['temp_max']}°C
                </p>
            </div>

            <!-- 空气质量 -->
            <div style="margin-bottom: 12px;">
                <p style="font-size: 14px; color: #666666; margin: 0 0 4px 0;">
                    <b>空气质量</b>: {weather['air']} (AQI: {weather['aqi']})
                </p>
            </div>

            <!-- 天气预警 -->
            <div style="margin-bottom: 12px;">
                <p style="font-size: 14px; color: #666666; margin: 0 0 4px 0;">
                    <b>天气预警</b>: {warning_info}
                </p>
            </div>

            <!-- 太阳和月亮 -->
            <div style="margin-bottom: 12px;">
                <p style="font-size: 14px; color: #666666; margin: 0 0 4px 0;">
                    <b>太阳和月亮</b>:
                </p>
                <p style="font-size: 14px; color: #666666; margin: 0 0 4px 0;">
                    日出：{weather['sunrise']}，日落：{weather['sunset']}，月出：{weather['moonrise']}，月落：{weather['moonset']}
                </p>
            </div>

            <!-- 今日一言 -->
            <div style="margin-bottom: 12px;">
                <p style="font-size: 14px; color: #666666; margin: 0 0 4px 0;">
                    <b>今日一言</b>:
                </p>
                <p style="font-size: 14px; color: #666666; margin: 0 0 4px 0;">
                    {quote}
                </p>
            </div>

            <!-- 土味情话 -->
            <div style="margin-bottom: 12px;">
                <p style="font-size: 14px; color: #666666; margin: 0 0 4px 0;">
                    <b>土味情话</b>:
                </p>
                <p style="font-size: 14px; color: #666666; margin: 0 0 4px 0;">
                    {love_quote}
                </p>
            </div>

            <!-- 纪念日 -->
            <div style="background: #fff0f0; padding: 8px; border-radius: 8px;">
                <p style="font-size: 14px; color: #333333; margin: 0;">
                    <b>纪念日</b>: 今天是我们在一起的第 {days_together} 天 ❤️
                </p>
            </div>
        </div>
    </div>
    """

    # 发送推送
    result = send_wxpusher_message(content)
    if result.get('code') == 1000:
        print("推送成功！")
    else:
        print("推送失败：", result)

if __name__ == "__main__":
    main()